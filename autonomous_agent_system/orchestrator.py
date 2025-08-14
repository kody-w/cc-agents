"""
Autonomous Agent System Orchestrator
Self-modifying system that continuously analyzes transcripts, generates specs, and builds agents
"""

import os
import json
import asyncio
import schedule
import time
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from core.transcript_analyzer import TranscriptAnalyzer
from core.tech_spec_generator import TechSpecGenerator
from core.agent_builder import AgentBuilder


class TranscriptWatcher(FileSystemEventHandler):
    """Watch for new transcript files"""
    
    def __init__(self, callback):
        self.callback = callback
        self.processed_files = set()
    
    def on_created(self, event):
        if not event.is_directory and event.src_path not in self.processed_files:
            if event.src_path.endswith(('.txt', '.json', '.log')):
                self.processed_files.add(event.src_path)
                self.callback(event.src_path)
    
    def on_modified(self, event):
        if not event.is_directory:
            if event.src_path.endswith(('.txt', '.json', '.log')):
                self.callback(event.src_path)


class AutonomousOrchestrator:
    """Main orchestrator for the autonomous agent system"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config = self._load_config(config_path)
        self.logger = self._setup_logger()
        
        # Initialize components
        self.transcript_analyzer = TranscriptAnalyzer()
        self.spec_generator = TechSpecGenerator()
        self.agent_builder = AgentBuilder(self.config.get('agents_output_dir', 'agents'))
        
        # Tracking
        self.processed_transcripts = set()
        self.generated_specs = {}
        self.built_agents = {}
        self.agent_registry = {}
        
        # Paths
        self.transcript_dir = Path(self.config.get('transcript_dir', 'transcripts'))
        self.specs_dir = Path(self.config.get('specs_dir', 'tech_specs'))
        self.agents_dir = Path(self.config.get('agents_dir', 'agents'))
        
        # Create directories
        self.transcript_dir.mkdir(exist_ok=True)
        self.specs_dir.mkdir(exist_ok=True)
        self.agents_dir.mkdir(exist_ok=True)
        
        # File watcher
        self.observer = None
        
        # Self-modification tracking
        self.evolution_history = []
        self.performance_metrics = {}
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from file or create default"""
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        
        # Default configuration
        default_config = {
            "transcript_dir": "transcripts",
            "specs_dir": "tech_specs",
            "agents_dir": "agents",
            "agents_output_dir": "agents",
            "auto_build": True,
            "auto_deploy": False,
            "watch_transcripts": True,
            "scan_interval": 60,
            "priority_threshold": "medium",
            "max_concurrent_builds": 3,
            "self_modification": {
                "enabled": True,
                "learning_rate": 0.1,
                "optimization_interval": 3600
            },
            "logging": {
                "level": "INFO",
                "file": "orchestrator.log"
            }
        }
        
        # Save default config
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        return default_config
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logging"""
        log_config = self.config.get('logging', {})
        
        logging.basicConfig(
            level=getattr(logging, log_config.get('level', 'INFO')),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_config.get('file', 'orchestrator.log')),
                logging.StreamHandler()
            ]
        )
        
        return logging.getLogger('AutonomousOrchestrator')
    
    async def start(self):
        """Start the autonomous orchestrator"""
        self.logger.info("Starting Autonomous Agent System Orchestrator")
        
        # Initial scan of existing transcripts
        await self.scan_transcripts()
        
        # Start file watcher if enabled
        if self.config.get('watch_transcripts', True):
            self.start_watcher()
        
        # Schedule periodic scans
        schedule.every(self.config.get('scan_interval', 60)).seconds.do(
            lambda: asyncio.create_task(self.scan_transcripts())
        )
        
        # Schedule self-optimization if enabled
        if self.config['self_modification']['enabled']:
            schedule.every(self.config['self_modification']['optimization_interval']).seconds.do(
                lambda: asyncio.create_task(self.self_optimize())
            )
        
        # Main loop
        try:
            while True:
                schedule.run_pending()
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Shutting down orchestrator")
            self.stop()
    
    def start_watcher(self):
        """Start watching transcript directory for new files"""
        self.logger.info(f"Starting file watcher on {self.transcript_dir}")
        
        event_handler = TranscriptWatcher(self.on_new_transcript)
        self.observer = Observer()
        self.observer.schedule(event_handler, str(self.transcript_dir), recursive=True)
        self.observer.start()
    
    def stop(self):
        """Stop the orchestrator"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
        
        # Save state
        self.save_state()
    
    def on_new_transcript(self, filepath: str):
        """Handle new transcript file"""
        self.logger.info(f"New transcript detected: {filepath}")
        asyncio.create_task(self.process_transcript(filepath))
    
    async def scan_transcripts(self):
        """Scan transcript directory for unprocessed files"""
        self.logger.info("Scanning for new transcripts...")
        
        transcript_files = list(self.transcript_dir.glob('**/*.txt')) + \
                          list(self.transcript_dir.glob('**/*.json')) + \
                          list(self.transcript_dir.glob('**/*.log'))
        
        new_files = [f for f in transcript_files if str(f) not in self.processed_transcripts]
        
        if new_files:
            self.logger.info(f"Found {len(new_files)} new transcript(s)")
            
            # Process in parallel with concurrency limit
            semaphore = asyncio.Semaphore(self.config.get('max_concurrent_builds', 3))
            
            async def process_with_limit(filepath):
                async with semaphore:
                    await self.process_transcript(str(filepath))
            
            await asyncio.gather(*[process_with_limit(f) for f in new_files])
        else:
            self.logger.debug("No new transcripts found")
    
    async def process_transcript(self, filepath: str):
        """Process a single transcript file"""
        try:
            self.logger.info(f"Processing transcript: {filepath}")
            
            # Analyze transcript for agent requirements
            requirements = self.transcript_analyzer.analyze_transcript(filepath)
            
            if not requirements:
                self.logger.info(f"No agent requirements found in {filepath}")
                self.processed_transcripts.add(filepath)
                return
            
            self.logger.info(f"Found {len(requirements)} agent requirement(s)")
            
            # Process each requirement
            for req in requirements:
                await self.process_requirement(req)
            
            # Mark as processed
            self.processed_transcripts.add(filepath)
            
            # Save requirements
            req_file = self.specs_dir / f"requirements_{Path(filepath).stem}.json"
            self.transcript_analyzer.save_requirements(requirements, str(req_file))
            
        except Exception as e:
            self.logger.error(f"Error processing transcript {filepath}: {str(e)}")
    
    async def process_requirement(self, requirement):
        """Process a single agent requirement"""
        try:
            # Check priority threshold
            if not self.meets_priority_threshold(requirement.priority):
                self.logger.info(f"Skipping {requirement.name} - priority too low")
                return
            
            self.logger.info(f"Processing requirement: {requirement.name}")
            
            # Generate technical specification
            req_dict = requirement.__dict__ if hasattr(requirement, '__dict__') else requirement
            tech_spec = self.spec_generator.generate_tech_spec(req_dict)
            
            # Save tech spec
            spec_file = self.specs_dir / f"{tech_spec.agent_name}_spec.json"
            self.spec_generator.save_tech_spec(tech_spec, str(spec_file))
            
            # Save markdown documentation
            md_file = self.specs_dir / f"{tech_spec.agent_name}_spec.md"
            with open(md_file, 'w') as f:
                f.write(self.spec_generator.generate_markdown_spec(tech_spec))
            
            self.generated_specs[tech_spec.agent_name] = tech_spec
            
            # Build agent if auto-build is enabled
            if self.config.get('auto_build', True):
                await self.build_agent(tech_spec)
            
        except Exception as e:
            self.logger.error(f"Error processing requirement {requirement.name}: {str(e)}")
    
    async def build_agent(self, tech_spec):
        """Build an agent from tech spec"""
        try:
            self.logger.info(f"Building agent: {tech_spec.agent_name}")
            
            # Convert tech spec to dict if needed
            spec_dict = tech_spec.__dict__ if hasattr(tech_spec, '__dict__') else tech_spec
            
            # Build the agent
            build_result = self.agent_builder.build_agent(spec_dict)
            
            # Validate build
            if self.agent_builder.validate_build(build_result):
                self.logger.info(f"Successfully built agent: {tech_spec.agent_name}")
                self.built_agents[tech_spec.agent_name] = build_result
                
                # Register agent
                self.register_agent(tech_spec.agent_name, build_result)
                
                # Run tests
                test_result = self.agent_builder.test_agent(build_result['agent_dir'])
                if test_result['status'] == 'passed':
                    self.logger.info(f"Tests passed for {tech_spec.agent_name}")
                    
                    # Deploy if auto-deploy is enabled
                    if self.config.get('auto_deploy', False):
                        await self.deploy_agent(tech_spec.agent_name, build_result)
                else:
                    self.logger.warning(f"Tests failed for {tech_spec.agent_name}")
            else:
                self.logger.error(f"Build validation failed for {tech_spec.agent_name}")
            
        except Exception as e:
            self.logger.error(f"Error building agent {tech_spec.agent_name}: {str(e)}")
    
    async def deploy_agent(self, agent_name: str, build_result: Dict):
        """Deploy an agent"""
        try:
            self.logger.info(f"Deploying agent: {agent_name}")
            
            # Run deployment script
            import subprocess
            deploy_script = Path(build_result['agent_dir']) / "deploy.sh"
            
            if deploy_script.exists():
                result = subprocess.run(
                    ["bash", str(deploy_script)],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    self.logger.info(f"Successfully deployed {agent_name}")
                    self.update_agent_status(agent_name, "deployed")
                else:
                    self.logger.error(f"Deployment failed for {agent_name}: {result.stderr}")
            else:
                self.logger.warning(f"No deployment script found for {agent_name}")
            
        except Exception as e:
            self.logger.error(f"Error deploying agent {agent_name}: {str(e)}")
    
    def register_agent(self, agent_name: str, build_result: Dict):
        """Register an agent in the system"""
        self.agent_registry[agent_name] = {
            "name": agent_name,
            "status": "built",
            "build_result": build_result,
            "created_at": datetime.now().isoformat(),
            "metrics": {},
            "version": "1.0.0"
        }
        
        # Save registry
        self.save_registry()
    
    def update_agent_status(self, agent_name: str, status: str):
        """Update agent status"""
        if agent_name in self.agent_registry:
            self.agent_registry[agent_name]["status"] = status
            self.agent_registry[agent_name]["updated_at"] = datetime.now().isoformat()
            self.save_registry()
    
    def meets_priority_threshold(self, priority: str) -> bool:
        """Check if priority meets threshold"""
        priority_levels = {"low": 0, "medium": 1, "high": 2}
        threshold = self.config.get('priority_threshold', 'medium')
        
        return priority_levels.get(priority, 0) >= priority_levels.get(threshold, 1)
    
    async def self_optimize(self):
        """Self-optimization routine"""
        self.logger.info("Running self-optimization...")
        
        try:
            # Analyze performance metrics
            performance = self.analyze_performance()
            
            # Identify optimization opportunities
            optimizations = self.identify_optimizations(performance)
            
            # Apply optimizations
            for optimization in optimizations:
                await self.apply_optimization(optimization)
            
            # Record evolution
            self.evolution_history.append({
                "timestamp": datetime.now().isoformat(),
                "performance": performance,
                "optimizations": optimizations
            })
            
            # Save evolution history
            self.save_evolution_history()
            
        except Exception as e:
            self.logger.error(f"Error during self-optimization: {str(e)}")
    
    def analyze_performance(self) -> Dict[str, Any]:
        """Analyze system performance"""
        return {
            "agents_built": len(self.built_agents),
            "success_rate": self.calculate_success_rate(),
            "average_build_time": self.calculate_avg_build_time(),
            "resource_usage": self.get_resource_usage()
        }
    
    def identify_optimizations(self, performance: Dict) -> List[Dict]:
        """Identify optimization opportunities"""
        optimizations = []
        
        # Check success rate
        if performance['success_rate'] < 0.8:
            optimizations.append({
                "type": "improve_error_handling",
                "reason": "Low success rate",
                "action": "enhance_validation"
            })
        
        # Check build time
        if performance['average_build_time'] > 300:  # 5 minutes
            optimizations.append({
                "type": "optimize_build_process",
                "reason": "Slow build times",
                "action": "parallel_processing"
            })
        
        return optimizations
    
    async def apply_optimization(self, optimization: Dict):
        """Apply an optimization"""
        self.logger.info(f"Applying optimization: {optimization['type']}")
        
        if optimization['type'] == 'improve_error_handling':
            # Enhance error handling in components
            self.config['validation_strict'] = True
        
        elif optimization['type'] == 'optimize_build_process':
            # Increase parallel processing
            self.config['max_concurrent_builds'] = min(
                self.config.get('max_concurrent_builds', 3) + 1,
                10
            )
        
        # Save updated config
        self.save_config()
    
    def calculate_success_rate(self) -> float:
        """Calculate build success rate"""
        if not self.built_agents:
            return 1.0
        
        successful = sum(1 for agent in self.built_agents.values() 
                        if agent.get('status') != 'error')
        return successful / len(self.built_agents)
    
    def calculate_avg_build_time(self) -> float:
        """Calculate average build time"""
        # Placeholder - would track actual build times
        return 120.0  # 2 minutes average
    
    def get_resource_usage(self) -> Dict:
        """Get current resource usage"""
        import psutil
        
        return {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent
        }
    
    def save_state(self):
        """Save orchestrator state"""
        state = {
            "processed_transcripts": list(self.processed_transcripts),
            "generated_specs": {k: v.__dict__ if hasattr(v, '__dict__') else v 
                              for k, v in self.generated_specs.items()},
            "built_agents": self.built_agents,
            "timestamp": datetime.now().isoformat()
        }
        
        with open('orchestrator_state.json', 'w') as f:
            json.dump(state, f, indent=2)
    
    def load_state(self):
        """Load orchestrator state"""
        if os.path.exists('orchestrator_state.json'):
            with open('orchestrator_state.json', 'r') as f:
                state = json.load(f)
                self.processed_transcripts = set(state.get('processed_transcripts', []))
                self.generated_specs = state.get('generated_specs', {})
                self.built_agents = state.get('built_agents', {})
    
    def save_registry(self):
        """Save agent registry"""
        with open('agent_registry.json', 'w') as f:
            json.dump(self.agent_registry, f, indent=2)
    
    def save_evolution_history(self):
        """Save evolution history"""
        with open('evolution_history.json', 'w') as f:
            json.dump(self.evolution_history, f, indent=2)
    
    def save_config(self):
        """Save configuration"""
        with open('config.json', 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get_status(self) -> Dict:
        """Get orchestrator status"""
        return {
            "status": "running",
            "processed_transcripts": len(self.processed_transcripts),
            "generated_specs": len(self.generated_specs),
            "built_agents": len(self.built_agents),
            "registered_agents": len(self.agent_registry),
            "config": self.config,
            "timestamp": datetime.now().isoformat()
        }


async def main():
    """Main entry point"""
    orchestrator = AutonomousOrchestrator()
    
    # Load previous state if exists
    orchestrator.load_state()
    
    # Start the orchestrator
    await orchestrator.start()


if __name__ == "__main__":
    asyncio.run(main())