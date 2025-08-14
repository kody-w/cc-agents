"""
Different AI agents with unique optimization strategies
"""
import ast
import re
from typing import Dict, Any, Tuple, List
from game import CodeOptimizationAgent, OptimizationMetrics
import random


class PerformanceOptimizer(CodeOptimizationAgent):
    """Agent focused on performance optimization"""
    
    def __init__(self):
        super().__init__("PerformanceBot", "Performance-First")
    
    def analyze_code(self, code: str) -> Dict[str, Any]:
        analysis = {
            'loops': [],
            'list_comprehensions': [],
            'function_calls': [],
            'inefficiencies': []
        }
        
        try:
            tree = ast.parse(code)
            
            class PerformanceAnalyzer(ast.NodeVisitor):
                def visit_For(self, node):
                    analysis['loops'].append(ast.unparse(node))
                    self.generic_visit(node)
                
                def visit_While(self, node):
                    analysis['loops'].append(ast.unparse(node))
                    self.generic_visit(node)
                
                def visit_ListComp(self, node):
                    analysis['list_comprehensions'].append(ast.unparse(node))
                    self.generic_visit(node)
                
                def visit_Call(self, node):
                    if isinstance(node.func, ast.Name):
                        analysis['function_calls'].append(node.func.id)
                    self.generic_visit(node)
            
            analyzer = PerformanceAnalyzer()
            analyzer.visit(tree)
            
        except Exception as e:
            pass
        
        return analysis
    
    def optimize(self, code: str, metrics: OptimizationMetrics) -> Tuple[str, str]:
        optimizations = []
        optimized_code = code
        
        # Try to convert loops to list comprehensions
        if 'for ' in code and 'append' in code:
            lines = code.splitlines()
            new_lines = []
            i = 0
            while i < len(lines):
                line = lines[i]
                if 'for ' in line and i + 1 < len(lines) and 'append' in lines[i + 1]:
                    # Simple pattern matching for loop to list comprehension
                    if random.random() > 0.5:  # Sometimes apply optimization
                        optimizations.append("loop_to_comprehension")
                        # Skip the loop (simplified transformation)
                        i += 2
                        continue
                new_lines.append(line)
                i += 1
            
            if optimizations:
                optimized_code = '\n'.join(new_lines)
        
        # Try to use built-in functions instead of manual loops
        if 'sum_value = 0' in code:
            optimized_code = re.sub(
                r'sum_value = 0\n.*for.*in.*:\n.*sum_value.*\+=.*',
                'sum_value = sum(data)',
                optimized_code,
                flags=re.MULTILINE
            )
            optimizations.append("use_builtin_sum")
        
        # Cache function results
        if 'def ' in code and random.random() > 0.6:
            lines = optimized_code.splitlines()
            new_lines = []
            for line in lines:
                if line.strip().startswith('def ') and '@cache' not in code:
                    new_lines.append('from functools import cache')
                    new_lines.append('@cache')
                    optimizations.append("add_caching")
                new_lines.append(line)
            optimized_code = '\n'.join(new_lines)
        
        optimization_type = ', '.join(optimizations) if optimizations else "minor_tweaks"
        return optimized_code, optimization_type


class ReadabilityRefactorer(CodeOptimizationAgent):
    """Agent focused on code readability and maintainability"""
    
    def __init__(self):
        super().__init__("ReadabilityBot", "Clean-Code")
    
    def analyze_code(self, code: str) -> Dict[str, Any]:
        analysis = {
            'long_lines': [],
            'complex_expressions': [],
            'missing_docstrings': [],
            'variable_names': []
        }
        
        lines = code.splitlines()
        for i, line in enumerate(lines):
            if len(line) > 80:
                analysis['long_lines'].append(i)
            
            # Check for complex expressions
            if line.count('(') > 3 or line.count('[') > 2:
                analysis['complex_expressions'].append(i)
        
        # Check for docstrings
        if 'def ' in code and '"""' not in code:
            analysis['missing_docstrings'].append("functions need docstrings")
        
        # Check variable names
        for match in re.finditer(r'\b[a-z]\b\s*=', code):
            analysis['variable_names'].append(f"Single letter variable at position {match.start()}")
        
        return analysis
    
    def optimize(self, code: str, metrics: OptimizationMetrics) -> Tuple[str, str]:
        optimizations = []
        optimized_code = code
        
        # Add docstrings to functions
        if 'def ' in code and '"""' not in code:
            lines = optimized_code.splitlines()
            new_lines = []
            for line in lines:
                new_lines.append(line)
                if line.strip().startswith('def '):
                    func_name = re.search(r'def\s+(\w+)', line)
                    if func_name:
                        indent = len(line) - len(line.lstrip())
                        new_lines.append(' ' * (indent + 4) + f'"""Optimized function {func_name.group(1)}"""')
                        optimizations.append("add_docstrings")
            optimized_code = '\n'.join(new_lines)
        
        # Improve variable names
        single_letter_vars = re.findall(r'\b([a-z])\s*=', optimized_code)
        for var in set(single_letter_vars):
            if var in ['i', 'j', 'k', 'x', 'y', 'z']:  # Common loop variables
                continue
            new_name = {
                'n': 'number',
                's': 'string_value',
                'd': 'data',
                'l': 'list_items',
                'f': 'file_handle',
                'r': 'result'
            }.get(var, f'{var}_value')
            
            if random.random() > 0.5:  # Sometimes apply
                optimized_code = re.sub(rf'\b{var}\b', new_name, optimized_code)
                optimizations.append(f"rename_{var}_to_{new_name}")
        
        # Break long lines
        lines = optimized_code.splitlines()
        new_lines = []
        for line in lines:
            if len(line) > 100 and ',' in line:
                # Simple line breaking at commas
                parts = line.split(',')
                if len(parts) > 1:
                    indent = len(line) - len(line.lstrip())
                    new_lines.append(parts[0] + ',')
                    for part in parts[1:-1]:
                        new_lines.append(' ' * (indent + 4) + part.strip() + ',')
                    new_lines.append(' ' * (indent + 4) + parts[-1].strip())
                    optimizations.append("break_long_lines")
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        
        if optimizations:
            optimized_code = '\n'.join(new_lines)
        
        optimization_type = ', '.join(optimizations) if optimizations else "formatting"
        return optimized_code, optimization_type


class MemoryOptimizer(CodeOptimizationAgent):
    """Agent focused on memory efficiency"""
    
    def __init__(self):
        super().__init__("MemoryBot", "Memory-Efficient")
    
    def analyze_code(self, code: str) -> Dict[str, Any]:
        analysis = {
            'large_lists': [],
            'duplicated_data': [],
            'generators_possible': [],
            'memory_leaks': []
        }
        
        # Check for large list operations
        if 'range(1000' in code or 'range(10000' in code:
            analysis['large_lists'].append("Large ranges detected")
        
        # Check for potential generators
        if '[' in code and 'for' in code and 'in' in code:
            analysis['generators_possible'].append("List comprehensions could be generators")
        
        # Check for duplicated data structures
        list_count = code.count('[]')
        dict_count = code.count('{}')
        if list_count > 3:
            analysis['duplicated_data'].append(f"{list_count} list initializations")
        
        return analysis
    
    def optimize(self, code: str, metrics: OptimizationMetrics) -> Tuple[str, str]:
        optimizations = []
        optimized_code = code
        
        # Convert list comprehensions to generators where appropriate
        if '[' in code and 'for' in code and 'in' in code:
            # Simple pattern: [expr for var in iterable] -> (expr for var in iterable)
            pattern = r'\[([^]]+for[^]]+in[^]]+)\]'
            matches = re.findall(pattern, optimized_code)
            if matches and random.random() > 0.5:
                for match in matches[:1]:  # Replace one at a time
                    optimized_code = optimized_code.replace(f'[{match}]', f'({match})', 1)
                    optimizations.append("list_to_generator")
        
        # Use slots for classes
        if 'class ' in code and '__slots__' not in code:
            lines = optimized_code.splitlines()
            new_lines = []
            for i, line in enumerate(lines):
                new_lines.append(line)
                if line.strip().startswith('class '):
                    # Add __slots__ after class definition
                    if i + 1 < len(lines):
                        indent = len(lines[i + 1]) - len(lines[i + 1].lstrip())
                        if indent > 0:
                            new_lines.append(' ' * indent + "__slots__ = ['data']")
                            optimizations.append("add_slots")
            optimized_code = '\n'.join(new_lines)
        
        # Use itertools for memory efficiency
        if 'for ' in code and 'range' in code:
            if 'import itertools' not in optimized_code:
                optimized_code = 'import itertools\n' + optimized_code
                optimizations.append("import_itertools")
        
        # Clear unused variables
        if random.random() > 0.7:
            lines = optimized_code.splitlines()
            new_lines = lines.copy()
            # Add del statements for large variables (simplified)
            if 'large_data' in code or 'data' in code:
                new_lines.append('# Memory cleanup')
                new_lines.append('# del unused_vars')
                optimizations.append("memory_cleanup")
            optimized_code = '\n'.join(new_lines)
        
        optimization_type = ', '.join(optimizations) if optimizations else "memory_tweaks"
        return optimized_code, optimization_type


class AlgorithmOptimizer(CodeOptimizationAgent):
    """Agent focused on algorithmic improvements"""
    
    def __init__(self):
        super().__init__("AlgorithmBot", "Algorithm-Optimization")
    
    def analyze_code(self, code: str) -> Dict[str, Any]:
        analysis = {
            'nested_loops': [],
            'sorting': [],
            'searching': [],
            'complexity': None
        }
        
        # Detect nested loops (O(n²) or worse)
        lines = code.splitlines()
        for i, line in enumerate(lines):
            if 'for ' in line:
                # Check next few lines for another loop
                for j in range(i + 1, min(i + 5, len(lines))):
                    if 'for ' in lines[j]:
                        analysis['nested_loops'].append(f"Nested loop at lines {i}-{j}")
        
        # Detect sorting operations
        if 'sort' in code or 'sorted' in code:
            analysis['sorting'].append("Sorting detected")
        
        # Detect searching operations
        if ' in ' in code or 'find' in code or 'index' in code:
            analysis['searching'].append("Searching detected")
        
        return analysis
    
    def optimize(self, code: str, metrics: OptimizationMetrics) -> Tuple[str, str]:
        optimizations = []
        optimized_code = code
        
        # Optimize nested loops with better algorithms
        if 'for ' in code:
            loop_count = code.count('for ')
            if loop_count >= 2:
                # Try to use set for membership testing
                if ' in ' in code and 'list' in code.lower():
                    optimized_code = optimized_code.replace('= []', '= set()', 1)
                    optimized_code = optimized_code.replace('.append(', '.add(', 1)
                    optimizations.append("list_to_set_for_lookups")
        
        # Use binary search instead of linear search
        if 'in sorted' in code or 'sorted(' in code:
            if 'import bisect' not in optimized_code:
                optimized_code = 'import bisect\n' + optimized_code
                optimizations.append("prepare_binary_search")
        
        # Memoization for recursive functions
        if 'def ' in code and 'return' in code:
            if 'fibonacci' in code.lower() or 'factorial' in code.lower():
                lines = optimized_code.splitlines()
                new_lines = []
                for line in lines:
                    if line.strip().startswith('def ') and '@' not in optimized_code:
                        new_lines.append('from functools import lru_cache')
                        new_lines.append('@lru_cache(maxsize=None)')
                        optimizations.append("add_memoization")
                    new_lines.append(line)
                optimized_code = '\n'.join(new_lines)
        
        # Early returns to reduce complexity
        if 'if ' in code and 'else:' in code:
            if random.random() > 0.6:
                # Add early return pattern (simplified)
                optimizations.append("early_returns")
        
        # Use collections for better data structures
        if 'count' in code.lower() or 'frequency' in code.lower():
            if 'from collections import' not in optimized_code:
                optimized_code = 'from collections import Counter, defaultdict\n' + optimized_code
                optimizations.append("use_collections")
        
        optimization_type = ', '.join(optimizations) if optimizations else "algorithm_tweaks"
        return optimized_code, optimization_type


class MinimalistReducer(CodeOptimizationAgent):
    """Agent focused on reducing code size"""
    
    def __init__(self):
        super().__init__("MinimalistBot", "Code-Golf")
    
    def analyze_code(self, code: str) -> Dict[str, Any]:
        analysis = {
            'redundant_code': [],
            'verbose_patterns': [],
            'simplifiable': []
        }
        
        # Check for verbose patterns
        if 'if ' in code and '== True' in code:
            analysis['verbose_patterns'].append("Redundant boolean comparison")
        
        if 'return True' in code and 'return False' in code:
            analysis['simplifiable'].append("Boolean returns can be simplified")
        
        # Check for redundant code
        lines = code.splitlines()
        for i, line in enumerate(lines):
            if line.strip() == 'pass':
                analysis['redundant_code'].append(f"Unnecessary pass at line {i}")
        
        return analysis
    
    def optimize(self, code: str, metrics: OptimizationMetrics) -> Tuple[str, str]:
        optimizations = []
        optimized_code = code
        
        # Remove unnecessary comparisons
        optimized_code = optimized_code.replace(' == True', '')
        optimized_code = optimized_code.replace(' == False', ' not ')
        if ' == True' in code or ' == False' in code:
            optimizations.append("simplify_boolean")
        
        # Simplify if-else to ternary
        pattern = r'if (.+):\s*(\w+)\s*=\s*(.+)\s*else:\s*\2\s*=\s*(.+)'
        matches = re.findall(pattern, optimized_code)
        if matches and random.random() > 0.5:
            optimizations.append("if_to_ternary")
        
        # Use walrus operator (Python 3.8+)
        if ':=' not in code and 'while' in code:
            # Simple pattern for while loops
            if random.random() > 0.6:
                optimizations.append("use_walrus")
        
        # Combine multiple statements
        lines = optimized_code.splitlines()
        new_lines = []
        skip_next = False
        for i, line in enumerate(lines):
            if skip_next:
                skip_next = False
                continue
            
            # Combine variable assignments
            if '=' in line and i + 1 < len(lines) and '=' in lines[i + 1]:
                if ';' not in line and random.random() > 0.7:
                    combined = line.strip() + '; ' + lines[i + 1].strip()
                    if len(combined) < 80:
                        new_lines.append(combined)
                        skip_next = True
                        optimizations.append("combine_statements")
                        continue
            
            new_lines.append(line)
        
        if optimizations:
            optimized_code = '\n'.join(new_lines)
        
        # Remove comments and docstrings for minimal size
        if random.random() > 0.8:
            optimized_code = re.sub(r'#.*$', '', optimized_code, flags=re.MULTILINE)
            optimized_code = re.sub(r'"""[\s\S]*?"""', '', optimized_code)
            optimizations.append("remove_comments")
        
        optimization_type = ', '.join(optimizations) if optimizations else "minification"
        return optimized_code, optimization_type