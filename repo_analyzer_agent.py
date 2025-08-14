"""
GitHub Repository Analyzer Agent
Generates comprehensive architectural documentation and dependency graphs from any codebase.
"""

import os
import json
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict
import re
import ast
import hashlib
from datetime import datetime
from agents.basic_agent import BasicAgent
from dataclasses import dataclass

@dataclass
class AgentCapability:
    name: str
    description: str
    tool_name: str
    parameters: dict


class RepoAnalyzerAgent(BasicAgent):
    """Agent that analyzes GitHub repositories to generate architectural documentation and dependency graphs."""
    
    def __init__(self):
        metadata = {
            "name": "RepoAnalyzer",
            "description": "Analyzes codebases to generate architectural documentation and dependency graphs",
            "capabilities": [{
                "name": "analyze_repository",
                "description": "Analyze a GitHub repository and generate comprehensive documentation",
                "parameters": {
                    "repo_url": "GitHub repository URL or local path",
                    "output_format": "Output format (json, markdown, html)",
                    "include_graphs": "Include dependency graphs (true/false)",
                    "max_depth": "Maximum depth for dependency analysis"
                }
            }]
        }
        super().__init__("RepoAnalyzer", metadata)
        
        self.language_parsers = {
            '.py': self._parse_python,
            '.js': self._parse_javascript,
            '.ts': self._parse_typescript,
            '.java': self._parse_java,
            '.go': self._parse_go,
            '.rs': self._parse_rust,
            '.cpp': self._parse_cpp,
            '.cs': self._parse_csharp,
            '.rb': self._parse_ruby,
            '.php': self._parse_php
        }
        
        self.config_files = {
            'package.json': 'nodejs',
            'requirements.txt': 'python',
            'Pipfile': 'python',
            'pyproject.toml': 'python',
            'pom.xml': 'java',
            'build.gradle': 'java',
            'go.mod': 'go',
            'Cargo.toml': 'rust',
            'composer.json': 'php',
            'Gemfile': 'ruby',
            '.csproj': 'csharp'
        }
    
    async def analyze_repository(self, repo_url: str, output_format: str = "markdown", 
                                 include_graphs: bool = True, max_depth: int = 3) -> Dict[str, Any]:
        """Analyze a repository and generate documentation."""
        try:
            # Clone or use local repository
            repo_path = await self._prepare_repository(repo_url)
            
            # Analyze repository structure
            structure = self._analyze_structure(repo_path)
            
            # Detect technologies and frameworks
            tech_stack = self._detect_tech_stack(repo_path)
            
            # Extract dependencies
            dependencies = self._extract_dependencies(repo_path, tech_stack)
            
            # Analyze code architecture
            architecture = self._analyze_architecture(repo_path, max_depth)
            
            # Generate dependency graph
            dep_graph = None
            if include_graphs:
                dep_graph = self._generate_dependency_graph(architecture, dependencies)
            
            # Calculate metrics
            metrics = self._calculate_metrics(repo_path)
            
            # Generate documentation
            documentation = self._generate_documentation(
                structure, tech_stack, dependencies, architecture, dep_graph, metrics
            )
            
            # Format output
            output = self._format_output(documentation, output_format, dep_graph)
            
            return {
                "status": "success",
                "repository": repo_url,
                "analyzed_at": datetime.now().isoformat(),
                "documentation": output,
                "metrics": metrics,
                "tech_stack": tech_stack,
                "dependency_graph": dep_graph
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _prepare_repository(self, repo_url: str) -> Path:
        """Clone repository or use local path."""
        if os.path.exists(repo_url):
            return Path(repo_url)
        
        # Clone from GitHub
        temp_dir = tempfile.mkdtemp(prefix="repo_analyzer_")
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", repo_url, temp_dir],
                check=True,
                capture_output=True
            )
            return Path(temp_dir)
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to clone repository: {e}")
    
    def _analyze_structure(self, repo_path: Path) -> Dict[str, Any]:
        """Analyze repository structure."""
        structure = {
            "directories": {},
            "files": {},
            "total_files": 0,
            "total_dirs": 0,
            "file_types": defaultdict(int)
        }
        
        for root, dirs, files in os.walk(repo_path):
            # Skip hidden and vendor directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'vendor', '__pycache__']]
            
            rel_path = os.path.relpath(root, repo_path)
            structure["total_dirs"] += 1
            
            for file in files:
                if file.startswith('.'):
                    continue
                    
                file_path = Path(root) / file
                ext = file_path.suffix
                
                structure["total_files"] += 1
                structure["file_types"][ext] += 1
                
                # Store file info
                rel_file_path = os.path.relpath(file_path, repo_path)
                structure["files"][rel_file_path] = {
                    "size": file_path.stat().st_size,
                    "extension": ext,
                    "directory": rel_path
                }
        
        return structure
    
    def _detect_tech_stack(self, repo_path: Path) -> Dict[str, Any]:
        """Detect technologies and frameworks used."""
        tech_stack = {
            "languages": set(),
            "frameworks": set(),
            "databases": set(),
            "tools": set(),
            "package_managers": set()
        }
        
        # Check for configuration files
        for config_file, tech in self.config_files.items():
            if (repo_path / config_file).exists() or list(repo_path.glob(f"**/{config_file}")):
                tech_stack["languages"].add(tech)
                
                # Detect package manager
                if config_file in ['package.json', 'yarn.lock']:
                    tech_stack["package_managers"].add('npm' if config_file == 'package.json' else 'yarn')
                elif config_file in ['requirements.txt', 'Pipfile', 'pyproject.toml']:
                    tech_stack["package_managers"].add('pip' if config_file == 'requirements.txt' else 'pipenv')
        
        # Detect frameworks from package files
        self._detect_frameworks(repo_path, tech_stack)
        
        # Detect from file extensions
        for file_path in repo_path.rglob("*"):
            if file_path.is_file():
                ext = file_path.suffix
                if ext == '.py':
                    tech_stack["languages"].add('python')
                elif ext in ['.js', '.jsx']:
                    tech_stack["languages"].add('javascript')
                elif ext in ['.ts', '.tsx']:
                    tech_stack["languages"].add('typescript')
                elif ext == '.java':
                    tech_stack["languages"].add('java')
                elif ext == '.go':
                    tech_stack["languages"].add('go')
                elif ext == '.rs':
                    tech_stack["languages"].add('rust')
                elif ext in ['.cpp', '.cc', '.h']:
                    tech_stack["languages"].add('c++')
                elif ext == '.cs':
                    tech_stack["languages"].add('csharp')
                elif ext == '.rb':
                    tech_stack["languages"].add('ruby')
                elif ext == '.php':
                    tech_stack["languages"].add('php')
        
        # Convert sets to lists for JSON serialization
        return {k: list(v) if isinstance(v, set) else v for k, v in tech_stack.items()}
    
    def _detect_frameworks(self, repo_path: Path, tech_stack: Dict):
        """Detect specific frameworks from configuration files."""
        # Check package.json for JS frameworks
        package_json = repo_path / "package.json"
        if package_json.exists():
            with open(package_json) as f:
                data = json.load(f)
                deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                
                if "react" in deps:
                    tech_stack["frameworks"].add("React")
                if "vue" in deps:
                    tech_stack["frameworks"].add("Vue")
                if "angular" in deps or "@angular/core" in deps:
                    tech_stack["frameworks"].add("Angular")
                if "express" in deps:
                    tech_stack["frameworks"].add("Express")
                if "next" in deps:
                    tech_stack["frameworks"].add("Next.js")
        
        # Check Python requirements
        requirements = repo_path / "requirements.txt"
        if requirements.exists():
            content = requirements.read_text()
            if "django" in content.lower():
                tech_stack["frameworks"].add("Django")
            if "flask" in content.lower():
                tech_stack["frameworks"].add("Flask")
            if "fastapi" in content.lower():
                tech_stack["frameworks"].add("FastAPI")
            if "tensorflow" in content.lower() or "torch" in content.lower():
                tech_stack["frameworks"].add("ML/AI Framework")
    
    def _extract_dependencies(self, repo_path: Path, tech_stack: Dict) -> Dict[str, List[str]]:
        """Extract project dependencies."""
        dependencies = {
            "external": [],
            "internal": [],
            "dev": []
        }
        
        # Extract from package.json
        package_json = repo_path / "package.json"
        if package_json.exists():
            with open(package_json) as f:
                data = json.load(f)
                dependencies["external"].extend(data.get("dependencies", {}).keys())
                dependencies["dev"].extend(data.get("devDependencies", {}).keys())
        
        # Extract from requirements.txt
        requirements = repo_path / "requirements.txt"
        if requirements.exists():
            lines = requirements.read_text().splitlines()
            for line in lines:
                if line and not line.startswith('#'):
                    dep = line.split('==')[0].split('>=')[0].split('<=')[0].strip()
                    if dep:
                        dependencies["external"].append(dep)
        
        # Extract from go.mod
        go_mod = repo_path / "go.mod"
        if go_mod.exists():
            content = go_mod.read_text()
            for line in content.splitlines():
                if line.strip().startswith('require'):
                    continue
                if '\t' in line and not line.startswith('//'):
                    parts = line.split()
                    if len(parts) >= 1:
                        dependencies["external"].append(parts[0])
        
        return dependencies
    
    def _analyze_architecture(self, repo_path: Path, max_depth: int) -> Dict[str, Any]:
        """Analyze code architecture and relationships."""
        architecture = {
            "modules": {},
            "classes": {},
            "functions": {},
            "imports": defaultdict(list),
            "call_graph": defaultdict(list),
            "file_dependencies": defaultdict(set)
        }
        
        for file_path in repo_path.rglob("*"):
            if file_path.is_file() and file_path.suffix in self.language_parsers:
                rel_path = str(file_path.relative_to(repo_path))
                
                # Parse file based on language
                parser = self.language_parsers[file_path.suffix]
                file_info = parser(file_path, max_depth)
                
                if file_info:
                    architecture["modules"][rel_path] = file_info.get("module_info", {})
                    architecture["classes"].update(file_info.get("classes", {}))
                    architecture["functions"].update(file_info.get("functions", {}))
                    architecture["imports"][rel_path] = file_info.get("imports", [])
                    
                    # Build file dependency graph
                    for imp in file_info.get("imports", []):
                        if not imp.startswith('.'):
                            architecture["file_dependencies"][rel_path].add(imp)
        
        # Convert sets to lists for JSON serialization
        architecture["file_dependencies"] = {k: list(v) for k, v in architecture["file_dependencies"].items()}
        
        return architecture
    
    def _parse_python(self, file_path: Path, max_depth: int) -> Dict[str, Any]:
        """Parse Python files using AST."""
        try:
            content = file_path.read_text()
            tree = ast.parse(content)
            
            info = {
                "module_info": {"name": file_path.stem, "docstring": ast.get_docstring(tree)},
                "classes": {},
                "functions": {},
                "imports": []
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    info["classes"][node.name] = {
                        "methods": [m.name for m in node.body if isinstance(m, ast.FunctionDef)],
                        "docstring": ast.get_docstring(node),
                        "line": node.lineno
                    }
                elif isinstance(node, ast.FunctionDef):
                    if not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree)):
                        info["functions"][node.name] = {
                            "params": [arg.arg for arg in node.args.args],
                            "docstring": ast.get_docstring(node),
                            "line": node.lineno
                        }
                elif isinstance(node, ast.Import):
                    info["imports"].extend([n.name for n in node.names])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        info["imports"].append(node.module)
            
            return info
            
        except Exception:
            return None
    
    def _parse_javascript(self, file_path: Path, max_depth: int) -> Dict[str, Any]:
        """Parse JavaScript files using regex patterns."""
        try:
            content = file_path.read_text()
            
            info = {
                "module_info": {"name": file_path.stem},
                "classes": {},
                "functions": {},
                "imports": []
            }
            
            # Extract imports
            import_pattern = r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]'
            info["imports"] = re.findall(import_pattern, content)
            
            # Extract functions
            func_pattern = r'(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:async\s+)?(?:\([^)]*\)|[^=])\s*=>)'
            for match in re.finditer(func_pattern, content):
                func_name = match.group(1) or match.group(2)
                if func_name:
                    info["functions"][func_name] = {"line": content[:match.start()].count('\n') + 1}
            
            # Extract classes
            class_pattern = r'class\s+(\w+)'
            for match in re.finditer(class_pattern, content):
                info["classes"][match.group(1)] = {"line": content[:match.start()].count('\n') + 1}
            
            return info
            
        except Exception:
            return None
    
    def _parse_typescript(self, file_path: Path, max_depth: int) -> Dict[str, Any]:
        """Parse TypeScript files (similar to JavaScript)."""
        return self._parse_javascript(file_path, max_depth)
    
    def _parse_java(self, file_path: Path, max_depth: int) -> Dict[str, Any]:
        """Parse Java files using regex patterns."""
        try:
            content = file_path.read_text()
            
            info = {
                "module_info": {"name": file_path.stem},
                "classes": {},
                "functions": {},
                "imports": []
            }
            
            # Extract imports
            import_pattern = r'import\s+([\w.]+);'
            info["imports"] = re.findall(import_pattern, content)
            
            # Extract classes
            class_pattern = r'(?:public\s+)?(?:abstract\s+)?(?:final\s+)?class\s+(\w+)'
            for match in re.finditer(class_pattern, content):
                info["classes"][match.group(1)] = {"line": content[:match.start()].count('\n') + 1}
            
            return info
            
        except Exception:
            return None
    
    def _parse_go(self, file_path: Path, max_depth: int) -> Dict[str, Any]:
        """Parse Go files using regex patterns."""
        try:
            content = file_path.read_text()
            
            info = {
                "module_info": {"name": file_path.stem},
                "classes": {},
                "functions": {},
                "imports": []
            }
            
            # Extract imports
            import_pattern = r'import\s+(?:\(([^)]+)\)|"([^"]+)")'
            for match in re.finditer(import_pattern, content):
                if match.group(1):
                    imports = match.group(1).replace('"', '').split('\n')
                    info["imports"].extend([i.strip() for i in imports if i.strip()])
                else:
                    info["imports"].append(match.group(2))
            
            # Extract functions
            func_pattern = r'func\s+(?:\(\w+\s+\*?\w+\)\s+)?(\w+)\s*\('
            for match in re.finditer(func_pattern, content):
                info["functions"][match.group(1)] = {"line": content[:match.start()].count('\n') + 1}
            
            # Extract structs (Go's classes)
            struct_pattern = r'type\s+(\w+)\s+struct'
            for match in re.finditer(struct_pattern, content):
                info["classes"][match.group(1)] = {"line": content[:match.start()].count('\n') + 1}
            
            return info
            
        except Exception:
            return None
    
    def _parse_rust(self, file_path: Path, max_depth: int) -> Dict[str, Any]:
        """Parse Rust files using regex patterns."""
        try:
            content = file_path.read_text()
            
            info = {
                "module_info": {"name": file_path.stem},
                "classes": {},
                "functions": {},
                "imports": []
            }
            
            # Extract use statements
            use_pattern = r'use\s+([\w:]+);'
            info["imports"] = re.findall(use_pattern, content)
            
            # Extract functions
            func_pattern = r'(?:pub\s+)?fn\s+(\w+)'
            for match in re.finditer(func_pattern, content):
                info["functions"][match.group(1)] = {"line": content[:match.start()].count('\n') + 1}
            
            # Extract structs
            struct_pattern = r'(?:pub\s+)?struct\s+(\w+)'
            for match in re.finditer(struct_pattern, content):
                info["classes"][match.group(1)] = {"line": content[:match.start()].count('\n') + 1}
            
            return info
            
        except Exception:
            return None
    
    def _parse_cpp(self, file_path: Path, max_depth: int) -> Dict[str, Any]:
        """Parse C++ files using regex patterns."""
        try:
            content = file_path.read_text()
            
            info = {
                "module_info": {"name": file_path.stem},
                "classes": {},
                "functions": {},
                "imports": []
            }
            
            # Extract includes
            include_pattern = r'#include\s+[<"]([^>"]+)[>"]'
            info["imports"] = re.findall(include_pattern, content)
            
            # Extract classes
            class_pattern = r'class\s+(\w+)'
            for match in re.finditer(class_pattern, content):
                info["classes"][match.group(1)] = {"line": content[:match.start()].count('\n') + 1}
            
            return info
            
        except Exception:
            return None
    
    def _parse_csharp(self, file_path: Path, max_depth: int) -> Dict[str, Any]:
        """Parse C# files using regex patterns."""
        try:
            content = file_path.read_text()
            
            info = {
                "module_info": {"name": file_path.stem},
                "classes": {},
                "functions": {},
                "imports": []
            }
            
            # Extract using statements
            using_pattern = r'using\s+([\w.]+);'
            info["imports"] = re.findall(using_pattern, content)
            
            # Extract classes
            class_pattern = r'(?:public\s+)?(?:abstract\s+)?(?:sealed\s+)?class\s+(\w+)'
            for match in re.finditer(class_pattern, content):
                info["classes"][match.group(1)] = {"line": content[:match.start()].count('\n') + 1}
            
            return info
            
        except Exception:
            return None
    
    def _parse_ruby(self, file_path: Path, max_depth: int) -> Dict[str, Any]:
        """Parse Ruby files using regex patterns."""
        try:
            content = file_path.read_text()
            
            info = {
                "module_info": {"name": file_path.stem},
                "classes": {},
                "functions": {},
                "imports": []
            }
            
            # Extract requires
            require_pattern = r'require\s+[\'"]([^\'"]+)[\'"]'
            info["imports"] = re.findall(require_pattern, content)
            
            # Extract classes
            class_pattern = r'class\s+(\w+)'
            for match in re.finditer(class_pattern, content):
                info["classes"][match.group(1)] = {"line": content[:match.start()].count('\n') + 1}
            
            # Extract methods
            method_pattern = r'def\s+(\w+)'
            for match in re.finditer(method_pattern, content):
                info["functions"][match.group(1)] = {"line": content[:match.start()].count('\n') + 1}
            
            return info
            
        except Exception:
            return None
    
    def _parse_php(self, file_path: Path, max_depth: int) -> Dict[str, Any]:
        """Parse PHP files using regex patterns."""
        try:
            content = file_path.read_text()
            
            info = {
                "module_info": {"name": file_path.stem},
                "classes": {},
                "functions": {},
                "imports": []
            }
            
            # Extract use statements
            use_pattern = r'use\s+([\w\\]+);'
            info["imports"] = re.findall(use_pattern, content)
            
            # Extract classes
            class_pattern = r'class\s+(\w+)'
            for match in re.finditer(class_pattern, content):
                info["classes"][match.group(1)] = {"line": content[:match.start()].count('\n') + 1}
            
            # Extract functions
            func_pattern = r'function\s+(\w+)\s*\('
            for match in re.finditer(func_pattern, content):
                info["functions"][match.group(1)] = {"line": content[:match.start()].count('\n') + 1}
            
            return info
            
        except Exception:
            return None
    
    def _generate_dependency_graph(self, architecture: Dict, dependencies: Dict) -> Dict[str, Any]:
        """Generate dependency graph data."""
        graph = {
            "nodes": [],
            "edges": [],
            "clusters": defaultdict(list)
        }
        
        # Create nodes for modules
        for module_path, module_info in architecture["modules"].items():
            node_id = hashlib.md5(module_path.encode()).hexdigest()[:8]
            graph["nodes"].append({
                "id": node_id,
                "label": module_path,
                "type": "module",
                "size": len(architecture["classes"].get(module_path, {})) + len(architecture["functions"].get(module_path, {}))
            })
            
            # Group by directory
            dir_name = os.path.dirname(module_path) or "root"
            graph["clusters"][dir_name].append(node_id)
        
        # Create edges for dependencies
        for source, imports in architecture["imports"].items():
            source_id = hashlib.md5(source.encode()).hexdigest()[:8]
            for target in imports:
                # Try to find internal module
                for module in architecture["modules"]:
                    if target in module or module.endswith(f"/{target}.py"):
                        target_id = hashlib.md5(module.encode()).hexdigest()[:8]
                        graph["edges"].append({
                            "source": source_id,
                            "target": target_id,
                            "type": "import"
                        })
                        break
        
        # Add external dependencies as nodes
        for dep in dependencies["external"][:20]:  # Limit to top 20 for readability
            node_id = hashlib.md5(dep.encode()).hexdigest()[:8]
            graph["nodes"].append({
                "id": node_id,
                "label": dep,
                "type": "external",
                "size": 1
            })
        
        return graph
    
    def _calculate_metrics(self, repo_path: Path) -> Dict[str, Any]:
        """Calculate code metrics."""
        metrics = {
            "lines_of_code": 0,
            "files_count": 0,
            "avg_file_size": 0,
            "languages": defaultdict(int),
            "complexity": {},
            "documentation_coverage": 0
        }
        
        total_size = 0
        doc_files = 0
        code_files = 0
        
        for file_path in repo_path.rglob("*"):
            if file_path.is_file() and not any(part.startswith('.') for part in file_path.parts):
                try:
                    content = file_path.read_text()
                    lines = len(content.splitlines())
                    
                    metrics["lines_of_code"] += lines
                    metrics["files_count"] += 1
                    total_size += file_path.stat().st_size
                    
                    # Count by language
                    ext = file_path.suffix
                    if ext:
                        metrics["languages"][ext] += lines
                    
                    # Check for documentation
                    if file_path.name.lower() in ['readme.md', 'readme.txt', 'readme']:
                        doc_files += 1
                    if ext in ['.py', '.js', '.java', '.go', '.rs']:
                        code_files += 1
                        
                except Exception:
                    pass
        
        if metrics["files_count"] > 0:
            metrics["avg_file_size"] = total_size / metrics["files_count"]
        
        if code_files > 0:
            metrics["documentation_coverage"] = (doc_files / code_files) * 100
        
        # Convert defaultdict to regular dict
        metrics["languages"] = dict(metrics["languages"])
        
        return metrics
    
    def _generate_documentation(self, structure: Dict, tech_stack: Dict, dependencies: Dict,
                               architecture: Dict, dep_graph: Optional[Dict], metrics: Dict) -> Dict[str, Any]:
        """Generate comprehensive documentation."""
        doc = {
            "overview": {
                "description": "Repository Analysis Report",
                "generated_at": datetime.now().isoformat(),
                "repository_stats": {
                    "total_files": structure["total_files"],
                    "total_directories": structure["total_dirs"],
                    "lines_of_code": metrics["lines_of_code"],
                    "primary_language": max(metrics["languages"].items(), key=lambda x: x[1])[0] if metrics["languages"] else "Unknown"
                }
            },
            "technology_stack": tech_stack,
            "project_structure": {
                "file_distribution": dict(structure["file_types"]),
                "key_directories": self._identify_key_directories(structure)
            },
            "dependencies": {
                "external": dependencies["external"][:50],  # Limit for readability
                "dev": dependencies["dev"][:20],
                "total_count": len(dependencies["external"]) + len(dependencies["dev"])
            },
            "architecture": {
                "modules_count": len(architecture["modules"]),
                "classes_count": len(architecture["classes"]),
                "functions_count": len(architecture["functions"]),
                "key_modules": self._identify_key_modules(architecture),
                "entry_points": self._identify_entry_points(structure, architecture)
            },
            "code_quality": {
                "documentation_coverage": f"{metrics['documentation_coverage']:.1f}%",
                "average_file_size": f"{metrics['avg_file_size']:.0f} bytes",
                "languages_distribution": metrics["languages"]
            },
            "recommendations": self._generate_recommendations(structure, tech_stack, metrics)
        }
        
        if dep_graph:
            doc["dependency_visualization"] = {
                "nodes_count": len(dep_graph["nodes"]),
                "edges_count": len(dep_graph["edges"]),
                "clusters": len(dep_graph["clusters"]),
                "graph_data": dep_graph
            }
        
        return doc
    
    def _identify_key_directories(self, structure: Dict) -> List[str]:
        """Identify important directories in the project."""
        key_dirs = []
        
        common_important_dirs = ['src', 'lib', 'app', 'api', 'core', 'components', 'services',
                                 'models', 'controllers', 'views', 'utils', 'helpers', 'tests']
        
        for dir_path in structure["directories"]:
            dir_name = os.path.basename(dir_path)
            if dir_name.lower() in common_important_dirs:
                key_dirs.append(dir_path)
        
        return key_dirs[:10]  # Return top 10
    
    def _identify_key_modules(self, architecture: Dict) -> List[Dict]:
        """Identify the most important modules."""
        key_modules = []
        
        for module_path, module_info in list(architecture["modules"].items())[:10]:
            # Count connections
            import_count = len(architecture["imports"].get(module_path, []))
            imported_by = sum(1 for imports in architecture["imports"].values() if module_path in imports)
            
            key_modules.append({
                "path": module_path,
                "imports": import_count,
                "imported_by": imported_by,
                "classes": len([c for c in architecture["classes"] if module_path in c]),
                "functions": len([f for f in architecture["functions"] if module_path in f])
            })
        
        # Sort by importance (imported_by count)
        key_modules.sort(key=lambda x: x["imported_by"], reverse=True)
        
        return key_modules[:10]
    
    def _identify_entry_points(self, structure: Dict, architecture: Dict) -> List[str]:
        """Identify project entry points."""
        entry_points = []
        
        common_entry_files = ['main.py', 'app.py', 'index.js', 'server.js', 'main.go',
                             'main.rs', 'Program.cs', 'index.php', 'main.java']
        
        for file_path in structure["files"]:
            file_name = os.path.basename(file_path)
            if file_name in common_entry_files:
                entry_points.append(file_path)
            elif file_name == '__main__.py':
                entry_points.append(file_path)
            elif 'main' in file_name.lower() and file_path.endswith(('.py', '.js', '.go', '.rs', '.java')):
                entry_points.append(file_path)
        
        return entry_points[:5]
    
    def _generate_recommendations(self, structure: Dict, tech_stack: Dict, metrics: Dict) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        # Documentation recommendations
        if metrics["documentation_coverage"] < 30:
            recommendations.append("Consider adding more documentation (README, docs folder, inline comments)")
        
        # Structure recommendations
        if structure["total_files"] > 100 and len([d for d in structure["directories"] if 'test' in d.lower()]) == 0:
            recommendations.append("Consider adding test directories for better code quality")
        
        # Dependency recommendations
        if 'package.json' in str(structure["files"]):
            recommendations.append("Ensure dependencies are up to date and check for security vulnerabilities")
        
        # Code organization
        if metrics["avg_file_size"] > 50000:
            recommendations.append("Some files are very large; consider refactoring for better maintainability")
        
        # Language-specific recommendations
        if 'python' in tech_stack["languages"] and 'requirements.txt' not in str(structure["files"]):
            recommendations.append("Add requirements.txt or use a dependency management tool like Poetry")
        
        return recommendations
    
    def _format_output(self, documentation: Dict, output_format: str, dep_graph: Optional[Dict]) -> str:
        """Format documentation in the requested format."""
        if output_format == "json":
            return json.dumps(documentation, indent=2)
        
        elif output_format == "markdown":
            md = []
            md.append("# Repository Analysis Report")
            md.append(f"\n*Generated: {documentation['overview']['generated_at']}*\n")
            
            # Overview
            md.append("## Overview")
            stats = documentation['overview']['repository_stats']
            md.append(f"- **Total Files**: {stats['total_files']}")
            md.append(f"- **Total Directories**: {stats['total_directories']}")
            md.append(f"- **Lines of Code**: {stats['lines_of_code']:,}")
            md.append(f"- **Primary Language**: {stats['primary_language']}")
            
            # Technology Stack
            md.append("\n## Technology Stack")
            md.append("### Languages")
            for lang in documentation['technology_stack']['languages']:
                md.append(f"- {lang}")
            
            if documentation['technology_stack']['frameworks']:
                md.append("### Frameworks")
                for fw in documentation['technology_stack']['frameworks']:
                    md.append(f"- {fw}")
            
            # Dependencies
            md.append("\n## Dependencies")
            md.append(f"**Total Dependencies**: {documentation['dependencies']['total_count']}")
            md.append("\n### Key External Dependencies")
            for dep in documentation['dependencies']['external'][:10]:
                md.append(f"- {dep}")
            
            # Architecture
            md.append("\n## Architecture")
            arch = documentation['architecture']
            md.append(f"- **Modules**: {arch['modules_count']}")
            md.append(f"- **Classes**: {arch['classes_count']}")
            md.append(f"- **Functions**: {arch['functions_count']}")
            
            if arch['entry_points']:
                md.append("\n### Entry Points")
                for ep in arch['entry_points']:
                    md.append(f"- `{ep}`")
            
            # Key Modules
            if arch['key_modules']:
                md.append("\n### Key Modules")
                md.append("| Module | Imports | Imported By | Classes | Functions |")
                md.append("|--------|---------|-------------|---------|-----------|")
                for module in arch['key_modules'][:5]:
                    md.append(f"| {module['path']} | {module['imports']} | {module['imported_by']} | {module['classes']} | {module['functions']} |")
            
            # Code Quality
            md.append("\n## Code Quality Metrics")
            quality = documentation['code_quality']
            md.append(f"- **Documentation Coverage**: {quality['documentation_coverage']}")
            md.append(f"- **Average File Size**: {quality['average_file_size']}")
            
            # Recommendations
            if documentation['recommendations']:
                md.append("\n## Recommendations")
                for rec in documentation['recommendations']:
                    md.append(f"- {rec}")
            
            # Dependency Graph
            if dep_graph:
                md.append("\n## Dependency Graph")
                md.append(f"- **Nodes**: {dep_graph['nodes_count']}")
                md.append(f"- **Edges**: {dep_graph['edges_count']}")
                md.append(f"- **Clusters**: {dep_graph['clusters']}")
                md.append("\n*Note: Full graph data available in JSON format*")
            
            return "\n".join(md)
        
        elif output_format == "html":
            html = []
            html.append("<!DOCTYPE html>")
            html.append("<html><head>")
            html.append("<title>Repository Analysis Report</title>")
            html.append("<style>")
            html.append("body { font-family: Arial, sans-serif; margin: 40px; }")
            html.append("h1 { color: #333; }")
            html.append("h2 { color: #666; border-bottom: 2px solid #eee; padding-bottom: 5px; }")
            html.append("h3 { color: #888; }")
            html.append(".metric { display: inline-block; margin: 10px 20px; }")
            html.append(".metric-label { font-weight: bold; }")
            html.append("table { border-collapse: collapse; width: 100%; }")
            html.append("th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }")
            html.append("th { background-color: #f2f2f2; }")
            html.append(".recommendation { background: #fffbf0; padding: 10px; margin: 5px 0; border-left: 4px solid #ffa500; }")
            html.append("</style>")
            html.append("</head><body>")
            
            html.append("<h1>Repository Analysis Report</h1>")
            html.append(f"<p><em>Generated: {documentation['overview']['generated_at']}</em></p>")
            
            # Overview section
            html.append("<h2>Overview</h2>")
            stats = documentation['overview']['repository_stats']
            html.append("<div class='metrics'>")
            for key, value in stats.items():
                label = key.replace('_', ' ').title()
                html.append(f"<div class='metric'><span class='metric-label'>{label}:</span> {value}</div>")
            html.append("</div>")
            
            # Technology Stack
            html.append("<h2>Technology Stack</h2>")
            html.append("<h3>Languages</h3>")
            html.append("<ul>")
            for lang in documentation['technology_stack']['languages']:
                html.append(f"<li>{lang}</li>")
            html.append("</ul>")
            
            if documentation['technology_stack']['frameworks']:
                html.append("<h3>Frameworks</h3>")
                html.append("<ul>")
                for fw in documentation['technology_stack']['frameworks']:
                    html.append(f"<li>{fw}</li>")
                html.append("</ul>")
            
            # Architecture
            html.append("<h2>Architecture</h2>")
            arch = documentation['architecture']
            
            if arch['key_modules']:
                html.append("<h3>Key Modules</h3>")
                html.append("<table>")
                html.append("<tr><th>Module</th><th>Imports</th><th>Imported By</th><th>Classes</th><th>Functions</th></tr>")
                for module in arch['key_modules'][:10]:
                    html.append(f"<tr><td>{module['path']}</td><td>{module['imports']}</td><td>{module['imported_by']}</td><td>{module['classes']}</td><td>{module['functions']}</td></tr>")
                html.append("</table>")
            
            # Recommendations
            if documentation['recommendations']:
                html.append("<h2>Recommendations</h2>")
                for rec in documentation['recommendations']:
                    html.append(f"<div class='recommendation'>{rec}</div>")
            
            html.append("</body></html>")
            
            return "\n".join(html)
        
        return json.dumps(documentation, indent=2)
    
    def perform(self, **kwargs) -> str:
        """Execute the repository analysis."""
        import asyncio
        
        repo_url = kwargs.get('repo_url', '')
        output_format = kwargs.get('output_format', 'markdown')
        include_graphs = kwargs.get('include_graphs', True)
        max_depth = kwargs.get('max_depth', 3)
        
        if not repo_url:
            return json.dumps({"status": "error", "message": "repo_url parameter is required"})
        
        result = asyncio.run(self.analyze_repository(repo_url, output_format, include_graphs, max_depth))
        
        if result["status"] == "success":
            return result["documentation"]
        else:
            return json.dumps({"status": "error", "message": result["message"]})
    
    async def process_request(self, request: str, context: Dict[str, Any]) -> str:
        """Process natural language requests about repository analysis."""
        # Extract repository URL or path from request
        repo_match = re.search(r'(https://github\.com/[\w-]+/[\w-]+|/[\w/]+)', request)
        
        if repo_match:
            repo_url = repo_match.group(1)
            
            # Determine output format
            output_format = "markdown"
            if "json" in request.lower():
                output_format = "json"
            elif "html" in request.lower():
                output_format = "html"
            
            # Check for graph inclusion
            include_graphs = "graph" in request.lower() or "visual" in request.lower()
            
            result = await self.analyze_repository(repo_url, output_format, include_graphs)
            
            if result["status"] == "success":
                return result["documentation"]
            else:
                return f"Error analyzing repository: {result['message']}"
        
        return "Please provide a GitHub repository URL or local path to analyze."


def lambda_handler(event, context):
    """AWS Lambda handler function."""
    agent = RepoAnalyzerAgent()
    
    # Extract parameters from event
    repo_url = event.get('repo_url', '')
    output_format = event.get('output_format', 'markdown')
    include_graphs = event.get('include_graphs', True)
    max_depth = event.get('max_depth', 3)
    
    if not repo_url:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'repo_url parameter is required'})
        }
    
    # Run analysis
    import asyncio
    result = asyncio.run(agent.analyze_repository(repo_url, output_format, include_graphs, max_depth))
    
    if result['status'] == 'success':
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    else:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': result['message']})
        }


if __name__ == "__main__":
    # Test the agent locally
    import asyncio
    
    agent = RepoAnalyzerAgent()
    
    # Test with a sample repository
    test_repo = "https://github.com/django/django"
    
    print("Analyzing repository:", test_repo)
    result = asyncio.run(agent.analyze_repository(test_repo, "markdown", include_graphs=True))
    
    if result["status"] == "success":
        print("\n" + result["documentation"])
        print(f"\nAnalysis complete!")
        print(f"Technology Stack: {result['tech_stack']}")
        print(f"Metrics: {result['metrics']}")
    else:
        print(f"Error: {result['message']}")