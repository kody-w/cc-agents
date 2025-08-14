"""
Traffic capture module using mitmproxy for intercepting HTTP(S) requests.
"""

import json
import time
import logging
import threading
from typing import Dict, List, Optional, Callable, Set
from urllib.parse import urlparse, parse_qs
from pathlib import Path

from mitmproxy import http, options
from mitmproxy.tools.dump import DumpMaster
from mitmproxy.addons import script

from .types import APICall, CapturedRequest, CapturedResponse


class TrafficCapture:
    """
    Main class for capturing HTTP traffic using mitmproxy.
    """
    
    def __init__(self, 
                 port: int = 8080,
                 target_hosts: Optional[Set[str]] = None,
                 output_file: Optional[str] = None,
                 verbose: bool = False):
        """
        Initialize the traffic capture.
        
        Args:
            port: Port for the proxy server
            target_hosts: Set of hostnames to capture (None = capture all)
            output_file: File to save captured data
            verbose: Enable verbose logging
        """
        self.port = port
        self.target_hosts = target_hosts or set()
        self.output_file = output_file
        self.verbose = verbose
        
        # Storage for captured API calls
        self.captured_calls: List[APICall] = []
        self.call_callbacks: List[Callable[[APICall], None]] = []
        
        # mitmproxy components
        self.master: Optional[DumpMaster] = None
        self.addon = None
        self.capture_thread: Optional[threading.Thread] = None
        self.is_running = False
        
        # Setup logging
        self._setup_logging()
        
    def _setup_logging(self):
        """Setup logging configuration."""
        level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def add_callback(self, callback: Callable[[APICall], None]):
        """Add a callback to be called when a new API call is captured."""
        self.call_callbacks.append(callback)
        
    def start_capture(self, background: bool = True) -> bool:
        """
        Start capturing traffic.
        
        Args:
            background: If True, run in background thread
            
        Returns:
            True if started successfully
        """
        try:
            # Create mitmproxy options
            opts = options.Options(
                listen_port=self.port,
                confdir=str(Path.home() / ".mitmproxy")
            )
            
            # Create the addon for handling requests
            self.addon = CaptureAddon(self)
            
            # Create master
            self.master = DumpMaster(opts)
            self.master.addons.add(self.addon)
            
            if background:
                self.capture_thread = threading.Thread(
                    target=self._run_capture,
                    daemon=True
                )
                self.capture_thread.start()
                self.logger.info(f"Started proxy server on port {self.port} (background)")
            else:
                self._run_capture()
                
            self.is_running = True
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start capture: {e}")
            return False
            
    def _run_capture(self):
        """Run the mitmproxy master."""
        try:
            self.master.run()
        except KeyboardInterrupt:
            self.logger.info("Capture stopped by user")
        except Exception as e:
            self.logger.error(f"Capture error: {e}")
        finally:
            self.is_running = False
            
    def stop_capture(self):
        """Stop capturing traffic."""
        if self.master:
            self.master.shutdown()
            self.is_running = False
            self.logger.info("Stopped traffic capture")
            
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=5)
            
    def get_captured_calls(self) -> List[APICall]:
        """Get all captured API calls."""
        return self.captured_calls.copy()
        
    def save_to_file(self, filename: Optional[str] = None):
        """Save captured calls to a JSON file."""
        output_file = filename or self.output_file
        if not output_file:
            raise ValueError("No output file specified")
            
        data = {
            "captured_at": time.time(),
            "total_calls": len(self.captured_calls),
            "calls": [self._serialize_call(call) for call in self.captured_calls]
        }
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
            
        self.logger.info(f"Saved {len(self.captured_calls)} calls to {output_file}")
        
    def load_from_file(self, filename: str):
        """Load captured calls from a JSON file."""
        with open(filename, 'r') as f:
            data = json.load(f)
            
        self.captured_calls = [
            self._deserialize_call(call_data) 
            for call_data in data.get("calls", [])
        ]
        
        self.logger.info(f"Loaded {len(self.captured_calls)} calls from {filename}")
        
    def _serialize_call(self, call: APICall) -> Dict:
        """Serialize an APICall to a dictionary."""
        return {
            "request": {
                "url": call.request.url,
                "method": call.request.method,
                "headers": call.request.headers,
                "query_params": call.request.query_params,
                "body": call.request.body,
                "timestamp": call.request.timestamp
            },
            "response": {
                "status_code": call.response.status_code,
                "headers": call.response.headers,
                "body": call.response.body,
                "content_type": call.response.content_type,
                "timestamp": call.response.timestamp
            },
            "duration_ms": call.duration_ms
        }
        
    def _deserialize_call(self, data: Dict) -> APICall:
        """Deserialize a dictionary to an APICall."""
        req_data = data["request"]
        resp_data = data["response"]
        
        request = CapturedRequest(
            url=req_data["url"],
            method=req_data["method"],
            headers=req_data["headers"],
            query_params=req_data["query_params"],
            body=req_data.get("body"),
            timestamp=req_data.get("timestamp")
        )
        
        response = CapturedResponse(
            status_code=resp_data["status_code"],
            headers=resp_data["headers"],
            body=resp_data.get("body"),
            content_type=resp_data.get("content_type"),
            timestamp=resp_data.get("timestamp")
        )
        
        return APICall(
            request=request,
            response=response,
            duration_ms=data.get("duration_ms")
        )
        
    def _should_capture_host(self, host: str) -> bool:
        """Check if we should capture traffic for this host."""
        if not self.target_hosts:
            return True
        return host in self.target_hosts
        
    def _handle_captured_call(self, call: APICall):
        """Handle a newly captured API call."""
        self.captured_calls.append(call)
        
        # Run callbacks
        for callback in self.call_callbacks:
            try:
                callback(call)
            except Exception as e:
                self.logger.error(f"Callback error: {e}")
                
        if self.verbose:
            self.logger.debug(
                f"Captured: {call.request.method} {call.request.url} "
                f"-> {call.response.status_code}"
            )


class CaptureAddon:
    """mitmproxy addon for capturing HTTP traffic."""
    
    def __init__(self, capture: TrafficCapture):
        self.capture = capture
        self.logger = logging.getLogger(__name__)
        
    def request(self, flow: http.HTTPFlow):
        """Handle incoming requests."""
        # Store request timestamp
        flow.request.timestamp_start = time.time()
        
    def response(self, flow: http.HTTPFlow):
        """Handle responses."""
        try:
            # Check if we should capture this host
            host = urlparse(flow.request.pretty_url).netloc
            if not self.capture._should_capture_host(host):
                return
                
            # Parse request
            request = self._parse_request(flow.request)
            
            # Parse response
            response = self._parse_response(flow.response)
            
            # Calculate duration
            start_time = getattr(flow.request, 'timestamp_start', None)
            duration_ms = None
            if start_time and response.timestamp:
                duration_ms = (response.timestamp - start_time) * 1000
                
            # Create API call
            api_call = APICall(
                request=request,
                response=response,
                duration_ms=duration_ms
            )
            
            # Handle the captured call
            self.capture._handle_captured_call(api_call)
            
        except Exception as e:
            self.logger.error(f"Error processing request/response: {e}")
            
    def _parse_request(self, request: http.HTTPRequest) -> CapturedRequest:
        """Parse mitmproxy request to CapturedRequest."""
        # Parse query parameters
        parsed_url = urlparse(request.pretty_url)
        query_params = parse_qs(parsed_url.query)
        
        # Flatten single-item lists in query params
        for key, value in query_params.items():
            if len(value) == 1:
                query_params[key] = value[0]
                
        # Get body content
        body = None
        if request.content:
            try:
                body = request.content.decode('utf-8')
            except UnicodeDecodeError:
                body = f"<binary data: {len(request.content)} bytes>"
                
        return CapturedRequest(
            url=request.pretty_url,
            method=request.method,
            headers=dict(request.headers),
            query_params=query_params,
            body=body,
            timestamp=getattr(request, 'timestamp_start', time.time())
        )
        
    def _parse_response(self, response: http.HTTPResponse) -> CapturedResponse:
        """Parse mitmproxy response to CapturedResponse."""
        # Get content type
        content_type = response.headers.get('content-type', '')
        
        # Get body content
        body = None
        if response.content:
            try:
                # Try to decode as text
                body = response.content.decode('utf-8')
            except UnicodeDecodeError:
                body = f"<binary data: {len(response.content)} bytes>"
                
        return CapturedResponse(
            status_code=response.status_code,
            headers=dict(response.headers),
            body=body,
            content_type=content_type,
            timestamp=time.time()
        )