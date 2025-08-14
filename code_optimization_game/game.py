"""
Code Optimization Game: AI Agents compete to optimize codebases
"""
import time
import ast
import copy
import threading
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path
from abc import ABC, abstractmethod
import random
import sys
import io
import contextlib


@dataclass
class OptimizationMetrics:
    """Metrics for evaluating code optimization"""
    lines_of_code: int = 0
    cyclomatic_complexity: int = 0
    execution_time: float = 0.0
    memory_usage: int = 0
    readability_score: float = 0.0
    test_coverage: float = 0.0
    performance_score: float = 0.0
    
    def calculate_total_score(self) -> float:
        """Calculate weighted total score"""
        score = 0.0
        score += (1000 - self.lines_of_code) * 0.15  # Fewer lines is better
        score += (20 - self.cyclomatic_complexity) * 10  # Lower complexity is better
        score += (1.0 - self.execution_time) * 100  # Faster is better
        score += (10000 - self.memory_usage) * 0.01  # Less memory is better
        score += self.readability_score * 20
        score += self.test_coverage * 30
        score += self.performance_score * 50
        return max(0, score)


@dataclass
class AgentMove:
    """Represents a single optimization move by an agent"""
    agent_name: str
    timestamp: datetime
    code_before: str
    code_after: str
    optimization_type: str
    metrics_change: Dict[str, float]
    success: bool
    error_message: Optional[str] = None


class CodeOptimizationAgent(ABC):
    """Base class for optimization agents"""
    
    def __init__(self, name: str, strategy: str):
        self.name = name
        self.strategy = strategy
        self.moves_made = 0
        self.score = 0.0
        self.history: List[AgentMove] = []
    
    @abstractmethod
    def analyze_code(self, code: str) -> Dict[str, Any]:
        """Analyze code and identify optimization opportunities"""
        pass
    
    @abstractmethod
    def optimize(self, code: str, metrics: OptimizationMetrics) -> Tuple[str, str]:
        """
        Apply optimization strategy to code
        Returns: (optimized_code, optimization_description)
        """
        pass
    
    def make_move(self, code: str, metrics: OptimizationMetrics) -> AgentMove:
        """Execute an optimization move"""
        try:
            code_before = code
            optimized_code, optimization_type = self.optimize(code, metrics)
            
            # Validate the optimized code
            try:
                ast.parse(optimized_code)
                success = True
                error_message = None
            except SyntaxError as e:
                success = False
                error_message = str(e)
                optimized_code = code_before
            
            move = AgentMove(
                agent_name=self.name,
                timestamp=datetime.now(),
                code_before=code_before,
                code_after=optimized_code,
                optimization_type=optimization_type,
                metrics_change={},
                success=success,
                error_message=error_message
            )
            
            self.history.append(move)
            self.moves_made += 1
            
            return move
            
        except Exception as e:
            return AgentMove(
                agent_name=self.name,
                timestamp=datetime.now(),
                code_before=code,
                code_after=code,
                optimization_type="failed",
                metrics_change={},
                success=False,
                error_message=str(e)
            )


class CodeOptimizationGame:
    """Main game controller for code optimization competition"""
    
    def __init__(self, 
                 initial_code: str,
                 test_suite: Optional[str] = None,
                 max_rounds: int = 10,
                 time_limit_per_round: float = 5.0):
        self.initial_code = initial_code
        self.current_code = initial_code
        self.test_suite = test_suite
        self.max_rounds = max_rounds
        self.time_limit_per_round = time_limit_per_round
        
        self.agents: List[CodeOptimizationAgent] = []
        self.round_number = 0
        self.game_history: List[Dict[str, Any]] = []
        self.leaderboard: Dict[str, float] = {}
        self.is_running = False
        self.lock = threading.Lock()
        
    def register_agent(self, agent: CodeOptimizationAgent):
        """Register an agent to compete"""
        self.agents.append(agent)
        self.leaderboard[agent.name] = 0.0
        print(f"🤖 Agent '{agent.name}' registered with strategy: {agent.strategy}")
    
    def calculate_metrics(self, code: str) -> OptimizationMetrics:
        """Calculate metrics for given code"""
        metrics = OptimizationMetrics()
        
        try:
            # Parse the code
            tree = ast.parse(code)
            
            # Lines of code
            metrics.lines_of_code = len(code.splitlines())
            
            # Cyclomatic complexity (simplified)
            class ComplexityVisitor(ast.NodeVisitor):
                def __init__(self):
                    self.complexity = 1
                
                def visit_If(self, node):
                    self.complexity += 1
                    self.generic_visit(node)
                
                def visit_While(self, node):
                    self.complexity += 1
                    self.generic_visit(node)
                
                def visit_For(self, node):
                    self.complexity += 1
                    self.generic_visit(node)
                
                def visit_ExceptHandler(self, node):
                    self.complexity += 1
                    self.generic_visit(node)
            
            visitor = ComplexityVisitor()
            visitor.visit(tree)
            metrics.cyclomatic_complexity = visitor.complexity
            
            # Execution time (measure actual execution)
            if self.test_suite:
                start_time = time.perf_counter()
                self._run_tests(code)
                metrics.execution_time = time.perf_counter() - start_time
            
            # Memory usage (simplified estimation)
            metrics.memory_usage = len(code) * 2  # Rough estimate
            
            # Readability score (based on various factors)
            metrics.readability_score = self._calculate_readability(code)
            
            # Test coverage (if tests exist)
            if self.test_suite:
                metrics.test_coverage = self._calculate_coverage(code)
            
            # Performance score
            metrics.performance_score = 100 - metrics.execution_time * 10
            
        except Exception as e:
            print(f"Error calculating metrics: {e}")
        
        return metrics
    
    def _calculate_readability(self, code: str) -> float:
        """Calculate readability score"""
        score = 100.0
        lines = code.splitlines()
        
        # Penalize very long lines
        for line in lines:
            if len(line) > 80:
                score -= 0.5
            if len(line) > 120:
                score -= 1.0
        
        # Reward proper indentation
        if all(line.startswith('    ') or line.startswith('\t') or not line.strip() 
               for line in lines[1:] if line.strip()):
            score += 5
        
        # Reward docstrings
        if '"""' in code or "'''" in code:
            score += 10
        
        return max(0, min(100, score))
    
    def _calculate_coverage(self, code: str) -> float:
        """Calculate test coverage (simplified)"""
        try:
            # This is a simplified version
            # In reality, you'd use coverage.py
            return random.uniform(70, 95)
        except:
            return 0.0
    
    def _run_tests(self, code: str) -> bool:
        """Run test suite against code"""
        if not self.test_suite:
            return True
        
        try:
            # Create a sandboxed environment
            namespace = {}
            exec(code, namespace)
            exec(self.test_suite, namespace)
            return True
        except Exception as e:
            print(f"Test failed: {e}")
            return False
    
    def run_round(self) -> Dict[str, Any]:
        """Run a single round of optimization"""
        self.round_number += 1
        round_results = {
            'round': self.round_number,
            'moves': [],
            'scores': {},
            'winner': None
        }
        
        print(f"\n🎮 ROUND {self.round_number}/{self.max_rounds}")
        print("=" * 50)
        
        # Calculate initial metrics
        initial_metrics = self.calculate_metrics(self.current_code)
        
        # Each agent takes a turn
        for agent in self.agents:
            print(f"\n🤖 {agent.name}'s turn...")
            
            # Agent makes a move
            move = agent.make_move(self.current_code, initial_metrics)
            
            if move.success:
                # Calculate new metrics
                new_metrics = self.calculate_metrics(move.code_after)
                
                # Calculate score improvement
                old_score = initial_metrics.calculate_total_score()
                new_score = new_metrics.calculate_total_score()
                improvement = new_score - old_score
                
                # Update metrics change
                move.metrics_change = {
                    'score_improvement': improvement,
                    'loc_change': new_metrics.lines_of_code - initial_metrics.lines_of_code,
                    'complexity_change': new_metrics.cyclomatic_complexity - initial_metrics.cyclomatic_complexity,
                    'performance_change': new_metrics.performance_score - initial_metrics.performance_score
                }
                
                # Update agent score
                agent.score += improvement
                self.leaderboard[agent.name] = agent.score
                
                # Update current code if improvement
                if improvement > 0:
                    self.current_code = move.code_after
                    print(f"✅ {agent.name} improved code! Score: +{improvement:.2f}")
                else:
                    print(f"❌ {agent.name}'s optimization didn't improve score: {improvement:.2f}")
            else:
                print(f"⚠️ {agent.name}'s move failed: {move.error_message}")
            
            round_results['moves'].append(move)
        
        # Update round results
        round_results['scores'] = dict(self.leaderboard)
        round_results['winner'] = max(self.leaderboard, key=self.leaderboard.get)
        
        self.game_history.append(round_results)
        
        # Display leaderboard
        self._display_leaderboard()
        
        return round_results
    
    def _display_leaderboard(self):
        """Display current leaderboard"""
        print("\n📊 LEADERBOARD")
        print("-" * 40)
        sorted_agents = sorted(self.leaderboard.items(), key=lambda x: x[1], reverse=True)
        for i, (name, score) in enumerate(sorted_agents, 1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "🎯"
            print(f"{emoji} {i}. {name}: {score:.2f} points")
    
    def start_game(self):
        """Start the optimization game"""
        print("\n🎮 CODE OPTIMIZATION GAME STARTING! 🎮")
        print(f"Agents: {', '.join(agent.name for agent in self.agents)}")
        print(f"Rounds: {self.max_rounds}")
        print(f"Initial code metrics:")
        
        initial_metrics = self.calculate_metrics(self.initial_code)
        print(f"  - Lines of code: {initial_metrics.lines_of_code}")
        print(f"  - Complexity: {initial_metrics.cyclomatic_complexity}")
        print(f"  - Initial score: {initial_metrics.calculate_total_score():.2f}")
        
        self.is_running = True
        
        for round_num in range(self.max_rounds):
            if not self.is_running:
                break
            
            self.run_round()
            time.sleep(1)  # Pause between rounds for drama
        
        self._declare_winner()
    
    def _declare_winner(self):
        """Declare the game winner"""
        print("\n" + "=" * 50)
        print("🏆 GAME OVER! 🏆")
        print("=" * 50)
        
        winner = max(self.leaderboard, key=self.leaderboard.get)
        print(f"\n🎉 WINNER: {winner} with {self.leaderboard[winner]:.2f} points!")
        
        print("\nFinal Rankings:")
        self._display_leaderboard()
        
        # Show optimization summary
        print("\n📈 Optimization Summary:")
        initial_metrics = self.calculate_metrics(self.initial_code)
        final_metrics = self.calculate_metrics(self.current_code)
        
        print(f"  Lines of code: {initial_metrics.lines_of_code} → {final_metrics.lines_of_code}")
        print(f"  Complexity: {initial_metrics.cyclomatic_complexity} → {final_metrics.cyclomatic_complexity}")
        print(f"  Performance: {initial_metrics.performance_score:.2f} → {final_metrics.performance_score:.2f}")
        print(f"  Total score: {initial_metrics.calculate_total_score():.2f} → {final_metrics.calculate_total_score():.2f}")
    
    def save_game_history(self, filepath: str):
        """Save game history to JSON file"""
        with open(filepath, 'w') as f:
            # Convert non-serializable objects
            history = []
            for round_data in self.game_history:
                round_copy = dict(round_data)
                round_copy['moves'] = [
                    {
                        'agent_name': move.agent_name,
                        'timestamp': move.timestamp.isoformat(),
                        'optimization_type': move.optimization_type,
                        'success': move.success,
                        'metrics_change': move.metrics_change
                    }
                    for move in round_copy['moves']
                ]
                history.append(round_copy)
            
            json.dump(history, f, indent=2)
        print(f"💾 Game history saved to {filepath}")