"""
Agent Builder: Automatically generates and builds agents from technical specifications
"""

import os
import json
import subprocess
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime
import textwrap


class AgentBuilder:
    def __init__(self, output_dir: str = "agents"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.code_templates = {
            "base_agent": self._get_base_agent_template(),
            "capability": self._get_capability_template(),
            "api_endpoint": self._get_api_endpoint_template(),
            "test": self._get_test_template(),
            "dockerfile": self._get_dockerfile_template(),
            "requirements": self._get_requirements_template()
        }

    def build_agent(self, tech_spec: Dict[str, Any]) -> Dict[str, str]:
        """Build a complete agent from a technical specification"""
        
        agent_name = tech_spec.get('agent_name', 'unnamed_agent')
        agent_dir = self.output_dir / agent_name
        agent_dir.mkdir(exist_ok=True)
        
        # Generate agent code
        agent_code = self._generate_agent_code(tech_spec)
        agent_file = agent_dir / f"{agent_name}.py"
        self._write_file(agent_file, agent_code)
        
        # Generate API server
        api_code = self._generate_api_code(tech_spec)
        api_file = agent_dir / "api_server.py"
        self._write_file(api_file, api_code)
        
        # Generate tests
        test_code = self._generate_test_code(tech_spec)
        test_file = agent_dir / f"test_{agent_name}.py"
        self._write_file(test_file, test_code)
        
        # Generate configuration
        config = self._generate_config(tech_spec)
        config_file = agent_dir / "config.json"
        self._write_file(config_file, json.dumps(config, indent=2))
        
        # Generate requirements.txt
        requirements = self._generate_requirements(tech_spec)
        req_file = agent_dir / "requirements.txt"
        self._write_file(req_file, requirements)
        
        # Generate Dockerfile
        dockerfile = self._generate_dockerfile(tech_spec)
        docker_file = agent_dir / "Dockerfile"
        self._write_file(docker_file, dockerfile)
        
        # Generate docker-compose.yml
        compose = self._generate_docker_compose(tech_spec)
        compose_file = agent_dir / "docker-compose.yml"
        self._write_file(compose_file, compose)
        
        # Generate README
        readme = self._generate_readme(tech_spec)
        readme_file = agent_dir / "README.md"
        self._write_file(readme_file, readme)
        
        # Generate deployment scripts
        deploy_script = self._generate_deployment_script(tech_spec)
        deploy_file = agent_dir / "deploy.sh"
        self._write_file(deploy_file, deploy_script)
        os.chmod(deploy_file, 0o755)
        
        return {
            "agent_name": agent_name,
            "agent_dir": str(agent_dir),
            "main_file": str(agent_file),
            "api_file": str(api_file),
            "test_file": str(test_file),
            "config_file": str(config_file),
            "status": "built",
            "timestamp": datetime.now().isoformat()
        }

    def _generate_agent_code(self, tech_spec: Dict) -> str:
        """Generate the main agent Python code"""
        
        agent_name = tech_spec.get('agent_name', 'unnamed_agent')
        class_name = self._to_class_name(agent_name)
        
        # Generate imports
        imports = self._generate_imports(tech_spec)
        
        # Generate capabilities methods
        capability_methods = []
        for cap in tech_spec.get('capabilities', []):
            method = self._generate_capability_method(cap)
            capability_methods.append(method)
        
        # Generate the main agent class
        code = f'''"""
{agent_name}: {tech_spec.get('purpose', 'Agent implementation')}
Generated on: {datetime.now().isoformat()}
"""

{imports}


class {class_name}:
    """
    {tech_spec.get('overview', 'Agent for automated processing')}
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the agent with configuration"""
        self.config = config or {{}}
        self.logger = self._setup_logger()
        self.metrics = {{}}
        self._initialize_components()
    
    def _setup_logger(self):
        """Setup logging configuration"""
        import logging
        logging.basicConfig(
            level=self.config.get('logging', {{}}).get('level', 'INFO'),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(self.__class__.__name__)
    
    def _initialize_components(self):
        """Initialize agent components based on architecture"""
        self.components = {{}}
        architecture = {tech_spec.get('architecture', {})}
        
        for component in architecture.get('components', []):
            comp_name = component.get('name')
            self.components[comp_name] = self._create_component(comp_name)
    
    def _create_component(self, name: str):
        """Create a component instance"""
        return {{"name": name, "status": "initialized"}}
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main processing method"""
        self.logger.info("Processing input data")
        
        try:
            # Validate input
            self._validate_input(input_data)
            
            # Execute processing pipeline
            result = input_data
            for capability in {tech_spec.get('capabilities', [])}:
                method_name = f"_execute_{{capability['name']}}"
                if hasattr(self, method_name):
                    result = await getattr(self, method_name)(result)
            
            # Generate output
            output = self._generate_output(result)
            
            self.logger.info("Processing completed successfully")
            return {{
                "status": "success",
                "result": output,
                "metadata": self._get_metadata()
            }}
            
        except Exception as e:
            self.logger.error(f"Processing failed: {{str(e)}}")
            return {{
                "status": "error",
                "error": str(e),
                "metadata": self._get_metadata()
            }}
    
    def _validate_input(self, input_data: Dict[str, Any]):
        """Validate input data"""
        if not input_data:
            raise ValueError("Input data is required")
        
        # Add specific validation based on requirements
        required_fields = {tech_spec.get('data_flow', {}).get('input_sources', [])}
        for field in required_fields:
            if field not in input_data and field != 'data':
                raise ValueError(f"Required field '{{field}}' is missing")
    
    def _generate_output(self, result: Any) -> Dict[str, Any]:
        """Generate output in the required format"""
        return {{
            "processed_data": result,
            "timestamp": datetime.now().isoformat(),
            "agent": self.__class__.__name__
        }}
    
    def _get_metadata(self) -> Dict[str, Any]:
        """Get processing metadata"""
        return {{
            "agent_version": "{tech_spec.get('version', '1.0.0')}",
            "processing_time": datetime.now().isoformat(),
            "metrics": self.metrics
        }}
    
    {''.join(capability_methods)}
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {{
            "status": "running",
            "components": self.components,
            "metrics": self.metrics,
            "config": self.config
        }}
    
    def health_check(self) -> Dict[str, str]:
        """Perform health check"""
        return {{
            "status": "healthy",
            "timestamp": datetime.now().isoformat()
        }}
'''
        
        return code

    def _generate_capability_method(self, capability: Dict) -> str:
        """Generate a method for a specific capability"""
        
        name = capability.get('name', 'process')
        methods = capability.get('methods', [])
        
        method_code = f'''
    async def _execute_{name}(self, data: Any) -> Any:
        """Execute {name} capability"""
        self.logger.debug(f"Executing {name} on data")
        
        try:
            # Implementation for {name}
            result = data
            
'''
        
        for method in methods:
            method_code += f'''            # {method}
            result = await self._{method}(result)
            
'''
        
        method_code += '''            return result
            
        except Exception as e:
            self.logger.error(f"Error in {name}: {str(e)}")
            raise
'''
        
        # Add helper methods for each sub-method
        for method in methods:
            method_code += f'''
    async def _{method}(self, data: Any) -> Any:
        """Perform {method} operation"""
        # TODO: Implement {method} logic
        return data
'''
        
        return method_code

    def _generate_api_code(self, tech_spec: Dict) -> str:
        """Generate API server code"""
        
        agent_name = tech_spec.get('agent_name', 'unnamed_agent')
        class_name = self._to_class_name(agent_name)
        
        code = f'''"""
API Server for {agent_name}
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
import asyncio
import json
from datetime import datetime
from {agent_name} import {class_name}


app = FastAPI(title="{agent_name} API", version="{tech_spec.get('version', '1.0.0')}")

# Initialize agent
with open("config.json") as f:
    config = json.load(f)

agent = {class_name}(config)


class ProcessRequest(BaseModel):
    data: Dict[str, Any]
    options: Optional[Dict[str, Any]] = None


class ProcessResponse(BaseModel):
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Dict[str, Any]


@app.get("/")
async def root():
    """Root endpoint"""
    return {{
        "name": "{agent_name}",
        "version": "{tech_spec.get('version', '1.0.0')}",
        "status": "running"
    }}


@app.post("/process", response_model=ProcessResponse)
async def process(request: ProcessRequest):
    """Main processing endpoint"""
    try:
        result = await agent.process(request.data)
        return ProcessResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def status():
    """Get agent status"""
    return agent.get_status()


@app.get("/health")
async def health():
    """Health check endpoint"""
    return agent.health_check()


@app.get("/metrics")
async def metrics():
    """Get agent metrics"""
    return agent.metrics


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
        
        return code

    def _generate_test_code(self, tech_spec: Dict) -> str:
        """Generate test code"""
        
        agent_name = tech_spec.get('agent_name', 'unnamed_agent')
        class_name = self._to_class_name(agent_name)
        
        code = f'''"""
Tests for {agent_name}
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from {agent_name} import {class_name}


@pytest.fixture
def agent():
    """Create agent instance for testing"""
    config = {{
        "mode": "test",
        "logging": {{"level": "DEBUG"}}
    }}
    return {class_name}(config)


@pytest.fixture
def sample_input():
    """Sample input data for testing"""
    return {{
        "data": "test_data",
        "timestamp": "2024-01-01T00:00:00"
    }}


class Test{class_name}:
    """Test suite for {class_name}"""
    
    def test_initialization(self, agent):
        """Test agent initialization"""
        assert agent is not None
        assert agent.config["mode"] == "test"
        assert agent.components is not None
    
    @pytest.mark.asyncio
    async def test_process_success(self, agent, sample_input):
        """Test successful processing"""
        result = await agent.process(sample_input)
        
        assert result["status"] == "success"
        assert "result" in result
        assert "metadata" in result
    
    @pytest.mark.asyncio
    async def test_process_empty_input(self, agent):
        """Test processing with empty input"""
        result = await agent.process({{}})
        
        assert result["status"] == "error"
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_process_invalid_input(self, agent):
        """Test processing with invalid input"""
        result = await agent.process(None)
        
        assert result["status"] == "error"
        assert "Input data is required" in result["error"]
    
    def test_health_check(self, agent):
        """Test health check"""
        health = agent.health_check()
        
        assert health["status"] == "healthy"
        assert "timestamp" in health
    
    def test_get_status(self, agent):
        """Test status retrieval"""
        status = agent.get_status()
        
        assert status["status"] == "running"
        assert "components" in status
        assert "metrics" in status
'''
        
        # Add tests for each capability
        for cap in tech_spec.get('capabilities', []):
            code += f'''
    
    @pytest.mark.asyncio
    async def test_capability_{cap['name']}(self, agent, sample_input):
        """Test {cap['name']} capability"""
        # Test the {cap['name']} functionality
        result = await agent._execute_{cap['name']}(sample_input)
        assert result is not None
'''
        
        # Add performance tests if specified
        if tech_spec.get('test_cases'):
            for test in tech_spec['test_cases']:
                if test.get('type') == 'performance':
                    code += f'''
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_performance_{test['id']}(self, agent, sample_input):
        """Performance test: {test['description']}"""
        import time
        
        start = time.time()
        result = await agent.process(sample_input)
        duration = time.time() - start
        
        assert result["status"] == "success"
        assert duration < 1.0  # Max 1 second
'''
        
        code += '''


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''
        
        return code

    def _generate_config(self, tech_spec: Dict) -> Dict[str, Any]:
        """Generate agent configuration"""
        
        config_schema = tech_spec.get('config_schema', {})
        
        config = {
            "agent_id": tech_spec.get('agent_name', 'unnamed_agent'),
            "version": tech_spec.get('version', '1.0.0'),
            "mode": "production",
            "logging": {
                "level": "INFO",
                "format": "json"
            },
            "performance": {
                "max_workers": 4,
                "timeout": 30,
                "batch_size": 100
            },
            "features": {}
        }
        
        # Add capability-specific configuration
        for cap in tech_spec.get('capabilities', []):
            config['features'][cap['name']] = True
        
        return config

    def _generate_requirements(self, tech_spec: Dict) -> str:
        """Generate requirements.txt"""
        
        deps = tech_spec.get('dependencies', [])
        
        # Add common dependencies
        common_deps = [
            "fastapi==0.104.1",
            "uvicorn==0.24.0",
            "pydantic==2.5.0",
            "pytest==7.4.3",
            "pytest-asyncio==0.21.1"
        ]
        
        # Combine and deduplicate
        all_deps = set()
        for dep in deps + common_deps:
            if "python" not in dep.lower():
                all_deps.add(dep)
        
        return "\n".join(sorted(all_deps))

    def _generate_dockerfile(self, tech_spec: Dict) -> str:
        """Generate Dockerfile"""
        
        agent_name = tech_spec.get('agent_name', 'unnamed_agent')
        
        dockerfile = f'''FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run the application
CMD ["python", "api_server.py"]
'''
        
        return dockerfile

    def _generate_docker_compose(self, tech_spec: Dict) -> str:
        """Generate docker-compose.yml"""
        
        agent_name = tech_spec.get('agent_name', 'unnamed_agent')
        
        compose = f'''version: '3.8'

services:
  {agent_name}:
    build: .
    container_name: {agent_name}
    ports:
      - "8000:8000"
    environment:
      - MODE=production
      - LOG_LEVEL=INFO
    volumes:
      - ./config.json:/app/config.json:ro
      - ./logs:/app/logs
    restart: unless-stopped
    networks:
      - agent_network

networks:
  agent_network:
    driver: bridge
'''
        
        return compose

    def _generate_readme(self, tech_spec: Dict) -> str:
        """Generate README.md"""
        
        agent_name = tech_spec.get('agent_name', 'unnamed_agent')
        
        readme = f'''# {agent_name}

## Overview
{tech_spec.get('overview', 'Agent for automated processing')}

**Version:** {tech_spec.get('version', '1.0.0')}  
**Priority:** {tech_spec.get('priority', 'medium')}  
**Complexity:** {tech_spec.get('estimated_complexity', 'medium')}  

## Purpose
{tech_spec.get('purpose', 'Automated agent for data processing')}

## Architecture
- **Pattern:** {tech_spec.get('architecture', {}).get('pattern', 'microservice')}
- **Scalability:** {tech_spec.get('architecture', {}).get('scalability', 'horizontal')}

## Capabilities
'''
        
        for cap in tech_spec.get('capabilities', []):
            readme += f"- **{cap['name']}**: {cap.get('description', 'Capability description')}\n"
        
        readme += f'''

## Installation

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Start the API server
python api_server.py
```

### Docker
```bash
# Build the image
docker-compose build

# Run the container
docker-compose up -d
```

## API Endpoints

- `POST /process` - Main processing endpoint
- `GET /status` - Get agent status
- `GET /health` - Health check
- `GET /metrics` - Get metrics

## Configuration

Edit `config.json` to customize agent behavior:

```json
{{
    "agent_id": "{agent_name}",
    "mode": "production",
    "logging": {{
        "level": "INFO"
    }}
}}
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov={agent_name}

# Run specific test
pytest test_{agent_name}.py::Test{self._to_class_name(agent_name)}::test_process_success
```

## Deployment

```bash
# Deploy using the provided script
./deploy.sh
```

## Performance Metrics

- **Latency:** < 500ms (p95)
- **Throughput:** > 100 req/s
- **Availability:** 99.9%

## Monitoring

The agent exposes metrics at `/metrics` endpoint for monitoring.

## License

Generated by Autonomous Agent System
'''
        
        return readme

    def _generate_deployment_script(self, tech_spec: Dict) -> str:
        """Generate deployment script"""
        
        agent_name = tech_spec.get('agent_name', 'unnamed_agent')
        deployment = tech_spec.get('deployment_strategy', {})
        
        script = f'''#!/bin/bash

# Deployment script for {agent_name}

set -e

echo "Deploying {agent_name}..."

# Build and test
echo "Running tests..."
pytest

echo "Building Docker image..."
docker-compose build

# Deploy based on strategy
DEPLOY_TYPE="{deployment.get('type', 'simple')}"

case $DEPLOY_TYPE in
    simple)
        echo "Starting container..."
        docker-compose up -d
        ;;
    
    containerized)
        echo "Deploying to Kubernetes..."
        kubectl apply -f k8s/
        ;;
    
    microservices)
        echo "Deploying with Helm..."
        helm upgrade --install {agent_name} ./helm-chart
        ;;
    
    *)
        echo "Unknown deployment type: $DEPLOY_TYPE"
        exit 1
        ;;
esac

# Verify deployment
echo "Verifying deployment..."
sleep 5

if curl -f http://localhost:8000/health; then
    echo "Deployment successful!"
else
    echo "Deployment failed!"
    exit 1
fi

echo "Agent {agent_name} deployed successfully!"
'''
        
        return script

    def _generate_imports(self, tech_spec: Dict) -> str:
        """Generate import statements based on dependencies"""
        
        imports = [
            "import asyncio",
            "import json",
            "from typing import Dict, Any, List, Optional",
            "from datetime import datetime",
            "from dataclasses import dataclass"
        ]
        
        # Add capability-specific imports
        for dep in tech_spec.get('dependencies', []):
            if dep.startswith('pandas'):
                imports.append("import pandas as pd")
            elif dep.startswith('numpy'):
                imports.append("import numpy as np")
            elif dep.startswith('requests'):
                imports.append("import requests")
            elif dep.startswith('aiohttp'):
                imports.append("import aiohttp")
        
        return "\n".join(imports)

    def _to_class_name(self, name: str) -> str:
        """Convert agent name to class name"""
        parts = name.replace("_agent", "").split("_")
        return "".join(part.capitalize() for part in parts) + "Agent"

    def _write_file(self, filepath: Path, content: str):
        """Write content to file"""
        with open(filepath, 'w') as f:
            f.write(content)

    def _get_base_agent_template(self) -> str:
        """Get base agent template"""
        return '''
class BaseAgent:
    def __init__(self, config):
        self.config = config
    
    async def process(self, data):
        raise NotImplementedError
'''

    def _get_capability_template(self) -> str:
        """Get capability template"""
        return '''
async def capability_{name}(self, data):
    """Execute {name} capability"""
    return data
'''

    def _get_api_endpoint_template(self) -> str:
        """Get API endpoint template"""
        return '''
@app.post("/{endpoint}")
async def {name}(request: Request):
    """Handle {endpoint} request"""
    return {{"status": "success"}}
'''

    def _get_test_template(self) -> str:
        """Get test template"""
        return '''
def test_{name}():
    """Test {name} functionality"""
    assert True
'''

    def _get_dockerfile_template(self) -> str:
        """Get Dockerfile template"""
        return '''FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
'''

    def _get_requirements_template(self) -> str:
        """Get requirements template"""
        return '''fastapi
uvicorn
pydantic
pytest
'''

    def validate_build(self, build_result: Dict) -> bool:
        """Validate that the build was successful"""
        
        required_files = [
            "main_file",
            "api_file",
            "test_file",
            "config_file"
        ]
        
        for file_key in required_files:
            if file_key not in build_result:
                return False
            
            filepath = Path(build_result[file_key])
            if not filepath.exists():
                return False
        
        return True

    def test_agent(self, agent_dir: str) -> Dict[str, Any]:
        """Run tests for the built agent"""
        
        try:
            result = subprocess.run(
                ["pytest", agent_dir, "-v"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                "status": "passed" if result.returncode == 0 else "failed",
                "output": result.stdout,
                "errors": result.stderr
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }