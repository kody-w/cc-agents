"""
Tech Spec Generator: Converts agent requirements to formal technical specifications
"""

import json
from typing import List, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import os


@dataclass
class TechSpec:
    agent_name: str
    version: str
    created_at: str
    purpose: str
    overview: str
    
    # Technical Details
    architecture: Dict[str, Any]
    capabilities: List[Dict[str, Any]]
    data_flow: Dict[str, Any]
    
    # Implementation
    dependencies: List[str]
    interfaces: Dict[str, Any]
    algorithms: List[Dict[str, Any]]
    
    # Configuration
    config_schema: Dict[str, Any]
    environment_requirements: Dict[str, Any]
    
    # Testing & Validation
    test_cases: List[Dict[str, Any]]
    performance_metrics: Dict[str, Any]
    validation_criteria: List[str]
    
    # Deployment
    deployment_strategy: Dict[str, Any]
    monitoring: Dict[str, Any]
    
    # Metadata
    source_requirement: str
    priority: str
    estimated_complexity: str


class TechSpecGenerator:
    def __init__(self):
        self.capability_templates = {
            "analyze": {
                "type": "analytical",
                "methods": ["statistical_analysis", "pattern_recognition", "anomaly_detection"],
                "required_libs": ["pandas", "numpy", "scipy"]
            },
            "process": {
                "type": "transformation",
                "methods": ["data_cleaning", "normalization", "aggregation"],
                "required_libs": ["pandas", "numpy"]
            },
            "generate": {
                "type": "creative",
                "methods": ["template_rendering", "content_synthesis", "report_generation"],
                "required_libs": ["jinja2", "reportlab"]
            },
            "monitor": {
                "type": "observational",
                "methods": ["event_tracking", "metric_collection", "alerting"],
                "required_libs": ["prometheus_client", "asyncio"]
            },
            "integrate": {
                "type": "connective",
                "methods": ["api_calls", "data_sync", "webhook_handling"],
                "required_libs": ["requests", "aiohttp"]
            }
        }
        
        self.architecture_patterns = {
            "simple": {
                "pattern": "pipeline",
                "components": ["input_handler", "processor", "output_handler"],
                "complexity": "low"
            },
            "moderate": {
                "pattern": "microservice",
                "components": ["api_gateway", "core_service", "data_store", "message_queue"],
                "complexity": "medium"
            },
            "complex": {
                "pattern": "event_driven",
                "components": ["event_bus", "workers", "orchestrator", "state_manager", "api_layer"],
                "complexity": "high"
            }
        }

    def generate_tech_spec(self, requirement: Dict[str, Any]) -> TechSpec:
        """Generate a complete technical specification from an agent requirement"""
        
        # Determine complexity and architecture
        complexity = self._determine_complexity(requirement)
        architecture = self._design_architecture(requirement, complexity)
        
        # Generate capability specifications
        capabilities = self._generate_capabilities(requirement)
        
        # Design data flow
        data_flow = self._design_data_flow(requirement, architecture)
        
        # Determine dependencies
        dependencies = self._determine_dependencies(requirement, capabilities)
        
        # Design interfaces
        interfaces = self._design_interfaces(requirement)
        
        # Generate algorithms
        algorithms = self._generate_algorithms(requirement, capabilities)
        
        # Create configuration schema
        config_schema = self._generate_config_schema(requirement)
        
        # Define environment requirements
        env_requirements = self._define_environment_requirements(complexity)
        
        # Generate test cases
        test_cases = self._generate_test_cases(requirement)
        
        # Define performance metrics
        performance_metrics = self._define_performance_metrics(requirement)
        
        # Create deployment strategy
        deployment_strategy = self._create_deployment_strategy(complexity)
        
        # Define monitoring
        monitoring = self._define_monitoring(requirement)
        
        return TechSpec(
            agent_name=requirement.get('name', 'unnamed_agent'),
            version="1.0.0",
            created_at=datetime.now().isoformat(),
            purpose=requirement.get('purpose', ''),
            overview=self._generate_overview(requirement),
            architecture=architecture,
            capabilities=capabilities,
            data_flow=data_flow,
            dependencies=dependencies,
            interfaces=interfaces,
            algorithms=algorithms,
            config_schema=config_schema,
            environment_requirements=env_requirements,
            test_cases=test_cases,
            performance_metrics=performance_metrics,
            validation_criteria=self._generate_validation_criteria(requirement),
            deployment_strategy=deployment_strategy,
            monitoring=monitoring,
            source_requirement=requirement.get('source_transcript', ''),
            priority=requirement.get('priority', 'medium'),
            estimated_complexity=complexity
        )

    def _determine_complexity(self, requirement: Dict) -> str:
        """Determine the complexity level of the agent"""
        capabilities = requirement.get('capabilities', [])
        constraints = requirement.get('constraints', [])
        
        complexity_score = len(capabilities) + len(constraints)
        
        if "real-time" in str(constraints) or "scale" in str(constraints):
            complexity_score += 3
        
        if complexity_score <= 3:
            return "low"
        elif complexity_score <= 6:
            return "medium"
        else:
            return "high"

    def _design_architecture(self, requirement: Dict, complexity: str) -> Dict[str, Any]:
        """Design the agent architecture"""
        if complexity == "low":
            pattern = self.architecture_patterns["simple"]
        elif complexity == "medium":
            pattern = self.architecture_patterns["moderate"]
        else:
            pattern = self.architecture_patterns["complex"]
        
        return {
            "pattern": pattern["pattern"],
            "components": [
                {
                    "name": comp,
                    "responsibility": self._get_component_responsibility(comp),
                    "interfaces": self._get_component_interfaces(comp)
                }
                for comp in pattern["components"]
            ],
            "communication": self._get_communication_pattern(pattern["pattern"]),
            "scalability": self._get_scalability_approach(complexity)
        }

    def _generate_capabilities(self, requirement: Dict) -> List[Dict[str, Any]]:
        """Generate detailed capability specifications"""
        capabilities = []
        
        for cap_name in requirement.get('capabilities', []):
            template = self.capability_templates.get(cap_name, {})
            
            capability = {
                "name": cap_name,
                "type": template.get("type", "generic"),
                "description": f"Capability to {cap_name} data and produce results",
                "methods": template.get("methods", ["process"]),
                "inputs": self._get_capability_inputs(cap_name, requirement),
                "outputs": self._get_capability_outputs(cap_name, requirement),
                "error_handling": self._get_error_handling(cap_name),
                "performance_requirements": self._get_performance_requirements(cap_name)
            }
            
            capabilities.append(capability)
        
        return capabilities

    def _design_data_flow(self, requirement: Dict, architecture: Dict) -> Dict[str, Any]:
        """Design the data flow through the agent"""
        return {
            "input_sources": requirement.get('inputs', ['data']),
            "processing_stages": [
                {
                    "stage": f"stage_{i}",
                    "operation": cap,
                    "transforms": self._get_transforms(cap)
                }
                for i, cap in enumerate(requirement.get('capabilities', []))
            ],
            "output_destinations": requirement.get('outputs', ['results']),
            "data_formats": {
                "input": self._determine_data_format(requirement.get('inputs', [])),
                "internal": "json",
                "output": self._determine_data_format(requirement.get('outputs', []))
            },
            "buffering": self._determine_buffering_strategy(requirement)
        }

    def _determine_dependencies(self, requirement: Dict, capabilities: List[Dict]) -> List[str]:
        """Determine required dependencies"""
        deps = set(["python>=3.8"])
        
        for cap in capabilities:
            cap_name = cap.get("name", "")
            if cap_name in self.capability_templates:
                deps.update(self.capability_templates[cap_name].get("required_libs", []))
        
        # Add common dependencies
        deps.update(["pydantic", "asyncio", "logging", "pytest"])
        
        return sorted(list(deps))

    def _design_interfaces(self, requirement: Dict) -> Dict[str, Any]:
        """Design the agent's interfaces"""
        return {
            "api": {
                "type": "REST",
                "endpoints": [
                    {
                        "path": "/process",
                        "method": "POST",
                        "description": "Main processing endpoint",
                        "request_schema": self._generate_request_schema(requirement),
                        "response_schema": self._generate_response_schema(requirement)
                    },
                    {
                        "path": "/status",
                        "method": "GET",
                        "description": "Agent status endpoint"
                    },
                    {
                        "path": "/health",
                        "method": "GET",
                        "description": "Health check endpoint"
                    }
                ]
            },
            "cli": {
                "commands": [
                    {
                        "name": "run",
                        "description": "Run the agent",
                        "arguments": self._generate_cli_arguments(requirement)
                    }
                ]
            },
            "sdk": {
                "language": "python",
                "class_name": self._to_class_name(requirement.get('name', 'Agent')),
                "methods": self._generate_sdk_methods(requirement)
            }
        }

    def _generate_algorithms(self, requirement: Dict, capabilities: List[Dict]) -> List[Dict[str, Any]]:
        """Generate algorithm specifications"""
        algorithms = []
        
        for cap in capabilities:
            for method in cap.get("methods", []):
                algorithm = {
                    "name": method,
                    "purpose": f"Algorithm for {method}",
                    "type": self._get_algorithm_type(method),
                    "complexity": self._get_algorithm_complexity(method),
                    "pseudocode": self._generate_pseudocode(method, cap),
                    "optimization_hints": self._get_optimization_hints(method)
                }
                algorithms.append(algorithm)
        
        return algorithms

    def _generate_config_schema(self, requirement: Dict) -> Dict[str, Any]:
        """Generate configuration schema"""
        return {
            "type": "object",
            "properties": {
                "agent_id": {"type": "string", "description": "Unique agent identifier"},
                "mode": {"type": "string", "enum": ["development", "production"], "default": "development"},
                "logging": {
                    "type": "object",
                    "properties": {
                        "level": {"type": "string", "enum": ["DEBUG", "INFO", "WARNING", "ERROR"]},
                        "format": {"type": "string"}
                    }
                },
                "performance": {
                    "type": "object",
                    "properties": {
                        "max_workers": {"type": "integer", "minimum": 1, "default": 4},
                        "timeout": {"type": "integer", "minimum": 1, "default": 30},
                        "batch_size": {"type": "integer", "minimum": 1, "default": 100}
                    }
                },
                "features": {
                    "type": "object",
                    "additionalProperties": {"type": "boolean"}
                }
            },
            "required": ["agent_id"]
        }

    def _define_environment_requirements(self, complexity: str) -> Dict[str, Any]:
        """Define environment requirements based on complexity"""
        base_requirements = {
            "os": ["linux", "macos", "windows"],
            "python_version": ">=3.8",
            "memory": "512MB",
            "cpu": "1 core",
            "disk": "100MB"
        }
        
        if complexity == "medium":
            base_requirements.update({
                "memory": "2GB",
                "cpu": "2 cores",
                "disk": "500MB"
            })
        elif complexity == "high":
            base_requirements.update({
                "memory": "8GB",
                "cpu": "4 cores",
                "disk": "2GB",
                "gpu": "optional"
            })
        
        return base_requirements

    def _generate_test_cases(self, requirement: Dict) -> List[Dict[str, Any]]:
        """Generate test cases"""
        test_cases = [
            {
                "id": "test_001",
                "name": "Basic functionality test",
                "type": "unit",
                "description": "Test basic agent functionality",
                "input": {"data": "sample_input"},
                "expected_output": {"status": "success"},
                "assertions": ["output is not None", "no errors raised"]
            },
            {
                "id": "test_002",
                "name": "Error handling test",
                "type": "unit",
                "description": "Test error handling",
                "input": {"data": None},
                "expected_output": {"status": "error"},
                "assertions": ["appropriate error message", "graceful failure"]
            },
            {
                "id": "test_003",
                "name": "Performance test",
                "type": "performance",
                "description": "Test agent performance",
                "input": {"data": "large_dataset"},
                "performance_criteria": {
                    "max_latency": "1s",
                    "throughput": "100 req/s"
                }
            }
        ]
        
        # Add capability-specific tests
        for cap in requirement.get('capabilities', []):
            test_cases.append({
                "id": f"test_cap_{cap}",
                "name": f"Test {cap} capability",
                "type": "integration",
                "description": f"Test the {cap} capability",
                "scenario": f"Execute {cap} operation on sample data"
            })
        
        return test_cases

    def _define_performance_metrics(self, requirement: Dict) -> Dict[str, Any]:
        """Define performance metrics"""
        return {
            "latency": {
                "p50": "100ms",
                "p95": "500ms",
                "p99": "1s"
            },
            "throughput": {
                "minimum": "10 req/s",
                "target": "100 req/s",
                "maximum": "1000 req/s"
            },
            "resource_usage": {
                "cpu": {"average": "50%", "peak": "80%"},
                "memory": {"average": "200MB", "peak": "500MB"}
            },
            "availability": {
                "uptime": "99.9%",
                "mttr": "5 minutes"
            }
        }

    def _generate_validation_criteria(self, requirement: Dict) -> List[str]:
        """Generate validation criteria"""
        criteria = [
            "All unit tests pass",
            "Code coverage > 80%",
            "No critical security vulnerabilities",
            "Documentation complete",
            "Performance metrics met"
        ]
        
        # Add requirement-specific criteria
        if "real-time" in str(requirement.get('constraints', [])):
            criteria.append("Real-time processing latency < 100ms")
        
        if "scale" in str(requirement.get('constraints', [])):
            criteria.append("Successfully handles 10x expected load")
        
        return criteria

    def _create_deployment_strategy(self, complexity: str) -> Dict[str, Any]:
        """Create deployment strategy"""
        if complexity == "low":
            return {
                "type": "simple",
                "method": "direct",
                "environment": "single_instance",
                "ci_cd": "github_actions"
            }
        elif complexity == "medium":
            return {
                "type": "containerized",
                "method": "docker",
                "environment": "kubernetes",
                "ci_cd": "jenkins",
                "scaling": "horizontal"
            }
        else:
            return {
                "type": "microservices",
                "method": "helm",
                "environment": "kubernetes",
                "ci_cd": "gitlab",
                "scaling": "auto",
                "load_balancing": "required"
            }

    def _define_monitoring(self, requirement: Dict) -> Dict[str, Any]:
        """Define monitoring requirements"""
        return {
            "metrics": [
                "request_count",
                "error_rate",
                "response_time",
                "cpu_usage",
                "memory_usage"
            ],
            "logging": {
                "level": "INFO",
                "destinations": ["console", "file", "elasticsearch"],
                "retention": "30 days"
            },
            "alerting": {
                "channels": ["email", "slack"],
                "rules": [
                    {"metric": "error_rate", "threshold": "5%", "action": "alert"},
                    {"metric": "response_time", "threshold": "2s", "action": "warn"},
                    {"metric": "availability", "threshold": "99%", "action": "alert"}
                ]
            },
            "dashboards": [
                "overview",
                "performance",
                "errors",
                "business_metrics"
            ]
        }

    # Helper methods
    def _generate_overview(self, requirement: Dict) -> str:
        purpose = requirement.get('purpose', 'Process data')
        capabilities = requirement.get('capabilities', [])
        
        cap_str = ", ".join(capabilities) if capabilities else "various operations"
        
        return f"This agent is designed to {purpose.lower()}. It provides capabilities for {cap_str} with automated processing and intelligent decision making."

    def _get_component_responsibility(self, component: str) -> str:
        responsibilities = {
            "input_handler": "Receive and validate input data",
            "processor": "Core processing logic",
            "output_handler": "Format and deliver results",
            "api_gateway": "Route requests and handle authentication",
            "core_service": "Business logic implementation",
            "data_store": "Persist and retrieve data",
            "message_queue": "Asynchronous communication",
            "event_bus": "Event distribution and handling",
            "workers": "Process tasks in parallel",
            "orchestrator": "Coordinate workflow execution",
            "state_manager": "Maintain system state",
            "api_layer": "External API interface"
        }
        return responsibilities.get(component, "Component responsibility")

    def _get_component_interfaces(self, component: str) -> List[str]:
        interfaces = {
            "input_handler": ["HTTP", "WebSocket", "File"],
            "processor": ["Internal API"],
            "output_handler": ["HTTP", "File", "Stream"],
            "api_gateway": ["REST", "GraphQL"],
            "core_service": ["gRPC", "REST"],
            "data_store": ["SQL", "NoSQL"],
            "message_queue": ["AMQP", "Kafka"],
            "event_bus": ["Pub/Sub"],
            "workers": ["Task Queue"],
            "orchestrator": ["Workflow API"],
            "state_manager": ["State API"],
            "api_layer": ["REST", "WebSocket"]
        }
        return interfaces.get(component, ["Generic"])

    def _get_communication_pattern(self, pattern: str) -> str:
        patterns = {
            "pipeline": "Sequential processing with data transformation at each stage",
            "microservice": "Service-to-service communication via REST/gRPC",
            "event_driven": "Asynchronous event-based communication"
        }
        return patterns.get(pattern, "Direct communication")

    def _get_scalability_approach(self, complexity: str) -> str:
        if complexity == "low":
            return "Vertical scaling"
        elif complexity == "medium":
            return "Horizontal scaling with load balancing"
        else:
            return "Auto-scaling with container orchestration"

    def _get_capability_inputs(self, cap_name: str, requirement: Dict) -> List[str]:
        return requirement.get('inputs', ['data'])

    def _get_capability_outputs(self, cap_name: str, requirement: Dict) -> List[str]:
        return requirement.get('outputs', ['results'])

    def _get_error_handling(self, cap_name: str) -> Dict[str, str]:
        return {
            "strategy": "graceful_degradation",
            "retry_policy": "exponential_backoff",
            "fallback": "default_response"
        }

    def _get_performance_requirements(self, cap_name: str) -> Dict[str, str]:
        return {
            "latency": "< 500ms",
            "throughput": "> 100 ops/sec",
            "accuracy": "> 95%"
        }

    def _get_transforms(self, capability: str) -> List[str]:
        transforms = {
            "analyze": ["normalize", "aggregate", "calculate"],
            "process": ["clean", "transform", "validate"],
            "generate": ["template", "format", "render"],
            "monitor": ["collect", "aggregate", "alert"],
            "integrate": ["map", "convert", "sync"]
        }
        return transforms.get(capability, ["transform"])

    def _determine_data_format(self, io_list: List[str]) -> str:
        if "file" in str(io_list).lower():
            return "file"
        elif "api" in str(io_list).lower():
            return "json"
        elif "database" in str(io_list).lower():
            return "sql"
        else:
            return "json"

    def _determine_buffering_strategy(self, requirement: Dict) -> str:
        if "real-time" in str(requirement.get('constraints', [])):
            return "minimal"
        elif "large" in str(requirement.get('constraints', [])):
            return "chunked"
        else:
            return "standard"

    def _generate_request_schema(self, requirement: Dict) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "data": {"type": "object"},
                "options": {"type": "object"}
            },
            "required": ["data"]
        }

    def _generate_response_schema(self, requirement: Dict) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "result": {"type": "object"},
                "metadata": {"type": "object"}
            },
            "required": ["status", "result"]
        }

    def _generate_cli_arguments(self, requirement: Dict) -> List[Dict[str, str]]:
        return [
            {"name": "--input", "type": "string", "description": "Input data or file path"},
            {"name": "--output", "type": "string", "description": "Output file path"},
            {"name": "--config", "type": "string", "description": "Configuration file path"},
            {"name": "--verbose", "type": "boolean", "description": "Enable verbose output"}
        ]

    def _to_class_name(self, name: str) -> str:
        parts = name.replace("_agent", "").split("_")
        return "".join(part.capitalize() for part in parts) + "Agent"

    def _generate_sdk_methods(self, requirement: Dict) -> List[Dict[str, str]]:
        methods = [
            {"name": "process", "description": "Main processing method"},
            {"name": "validate", "description": "Validate input data"},
            {"name": "configure", "description": "Configure agent settings"}
        ]
        
        for cap in requirement.get('capabilities', []):
            methods.append({
                "name": cap,
                "description": f"Execute {cap} operation"
            })
        
        return methods

    def _get_algorithm_type(self, method: str) -> str:
        types = {
            "statistical_analysis": "statistical",
            "pattern_recognition": "machine_learning",
            "data_cleaning": "preprocessing",
            "template_rendering": "templating",
            "api_calls": "networking"
        }
        return types.get(method, "generic")

    def _get_algorithm_complexity(self, method: str) -> str:
        complexities = {
            "statistical_analysis": "O(n)",
            "pattern_recognition": "O(n²)",
            "data_cleaning": "O(n)",
            "template_rendering": "O(1)",
            "api_calls": "O(1)"
        }
        return complexities.get(method, "O(n)")

    def _generate_pseudocode(self, method: str, capability: Dict) -> str:
        return f"""
        function {method}(input):
            validate(input)
            processed = preprocess(input)
            result = execute_{method}(processed)
            return postprocess(result)
        """

    def _get_optimization_hints(self, method: str) -> List[str]:
        return [
            "Use caching for repeated operations",
            "Implement batching for bulk processing",
            "Consider parallel processing where applicable"
        ]

    def save_tech_spec(self, spec: TechSpec, output_path: str):
        """Save tech spec to JSON file"""
        with open(output_path, 'w') as f:
            json.dump(asdict(spec), f, indent=2)

    def generate_markdown_spec(self, spec: TechSpec) -> str:
        """Generate markdown documentation from tech spec"""
        md = f"""# {spec.agent_name} Technical Specification

## Overview
**Version:** {spec.version}  
**Created:** {spec.created_at}  
**Priority:** {spec.priority}  
**Complexity:** {spec.estimated_complexity}  

### Purpose
{spec.purpose}

{spec.overview}

## Architecture

### Pattern: {spec.architecture['pattern']}

### Components
"""
        for comp in spec.architecture['components']:
            md += f"- **{comp['name']}**: {comp['responsibility']}\n"

        md += f"\n### Communication: {spec.architecture['communication']}\n"
        md += f"### Scalability: {spec.architecture['scalability']}\n\n"

        md += "## Capabilities\n"
        for cap in spec.capabilities:
            md += f"### {cap['name']}\n"
            md += f"- Type: {cap['type']}\n"
            md += f"- Description: {cap['description']}\n"
            md += f"- Methods: {', '.join(cap['methods'])}\n\n"

        md += "## Dependencies\n"
        for dep in spec.dependencies:
            md += f"- {dep}\n"

        md += "\n## Performance Metrics\n"
        md += f"- Latency: p50={spec.performance_metrics['latency']['p50']}, "
        md += f"p95={spec.performance_metrics['latency']['p95']}\n"
        md += f"- Throughput: {spec.performance_metrics['throughput']['target']}\n"

        md += "\n## Deployment Strategy\n"
        md += f"- Type: {spec.deployment_strategy['type']}\n"
        md += f"- Method: {spec.deployment_strategy['method']}\n"
        md += f"- Environment: {spec.deployment_strategy['environment']}\n"

        return md