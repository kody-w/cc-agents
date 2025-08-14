"""
Real-time visualization for the Code Optimization Game
"""
import time
import threading
from typing import Dict, List
from datetime import datetime
import os
import sys


class GameVisualizer:
    """Real-time visualization for the optimization game"""
    
    def __init__(self):
        self.frame_count = 0
        self.animation_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, round_num: int, max_rounds: int):
        """Print game header"""
        print("╔" + "═" * 58 + "╗")
        print(f"║{'CODE OPTIMIZATION BATTLE ARENA':^58}║")
        print(f"║{'Round ' + str(round_num) + '/' + str(max_rounds):^58}║")
        print("╚" + "═" * 58 + "╝")
    
    def print_agent_status(self, agents: List, current_agent: str = None):
        """Print agent status with animations"""
        print("\n🤖 AGENTS IN COMPETITION:")
        print("─" * 60)
        
        for agent in agents:
            status = "🔄" if agent.name == current_agent else "⏸️"
            health_bar = self._create_progress_bar(agent.score / 100, 20)
            print(f"{status} {agent.name:20} {health_bar} Score: {agent.score:.1f}")
    
    def _create_progress_bar(self, percentage: float, width: int) -> str:
        """Create a visual progress bar"""
        filled = int(width * min(1.0, max(0.0, percentage)))
        empty = width - filled
        return f"[{'█' * filled}{'░' * empty}]"
    
    def animate_optimization(self, agent_name: str, optimization_type: str):
        """Animate an optimization being applied"""
        frames = [
            f"⚡ {agent_name} applying {optimization_type}...",
            f"⚡ {agent_name} APPLYING {optimization_type}...",
            f"💥 {agent_name} APPLIED {optimization_type}!"
        ]
        
        for frame in frames:
            print(f"\r{frame}", end="", flush=True)
            time.sleep(0.3)
        print()
    
    def show_code_diff(self, before_lines: int, after_lines: int, 
                      complexity_before: int, complexity_after: int):
        """Show code changes visualization"""
        print("\n📊 CODE METRICS:")
        print("─" * 40)
        
        # Lines of code
        loc_change = after_lines - before_lines
        loc_arrow = "↓" if loc_change < 0 else "↑" if loc_change > 0 else "→"
        loc_color = "🟢" if loc_change < 0 else "🔴" if loc_change > 0 else "🟡"
        print(f"Lines of Code: {before_lines} {loc_arrow} {after_lines} {loc_color}")
        
        # Complexity
        comp_change = complexity_after - complexity_before
        comp_arrow = "↓" if comp_change < 0 else "↑" if comp_change > 0 else "→"
        comp_color = "🟢" if comp_change < 0 else "🔴" if comp_change > 0 else "🟡"
        print(f"Complexity:    {complexity_before} {comp_arrow} {complexity_after} {comp_color}")
    
    def show_leaderboard(self, leaderboard: Dict[str, float], animated: bool = True):
        """Display animated leaderboard"""
        print("\n🏆 LEADERBOARD 🏆")
        print("═" * 40)
        
        sorted_agents = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)
        
        for i, (name, score) in enumerate(sorted_agents, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
            
            if animated:
                # Animate score counting up
                for s in range(0, int(score), max(1, int(score/10))):
                    print(f"\r{medal} {i}. {name:20} {s:8.2f} pts", end="", flush=True)
                    time.sleep(0.05)
            
            print(f"\r{medal} {i}. {name:20} {score:8.2f} pts")
    
    def show_battle_animation(self, agent1: str, agent2: str):
        """Show battle animation between agents"""
        battle_frames = [
            f"{agent1} ⚔️  {agent2}",
            f"{agent1}  ⚔️ {agent2}",
            f"{agent1}   ⚔️{agent2}",
            f"{agent1}  ⚔️ {agent2}",
            f"{agent1} ⚔️  {agent2}",
        ]
        
        for _ in range(2):
            for frame in battle_frames:
                print(f"\r{frame:^60}", end="", flush=True)
                time.sleep(0.1)
        print()
    
    def show_optimization_feed(self, moves: List):
        """Show live feed of optimizations"""
        print("\n📜 OPTIMIZATION FEED:")
        print("─" * 60)
        
        for move in moves[-5:]:  # Show last 5 moves
            status = "✅" if move.success else "❌"
            timestamp = move.timestamp.strftime("%H:%M:%S")
            print(f"{status} [{timestamp}] {move.agent_name}: {move.optimization_type}")
    
    def show_winner_celebration(self, winner: str, final_score: float):
        """Animated winner celebration"""
        self.clear_screen()
        
        celebration = [
            "    🎊🎊🎊🎊🎊    ",
            "   🎊 WINNER! 🎊   ",
            f"   🏆 {winner} 🏆   ",
            f"  Score: {final_score:.2f}  ",
            "    🎊🎊🎊🎊🎊    "
        ]
        
        # Animate celebration
        for _ in range(3):
            for i in range(len(celebration)):
                self.clear_screen()
                for j, line in enumerate(celebration):
                    if j <= i:
                        print(line.center(60))
                time.sleep(0.2)
        
        # Final display
        print("\n" + "=" * 60)
        for line in celebration:
            print(line.center(60))
        print("=" * 60)


class LiveGameMonitor:
    """Live monitoring dashboard for the game"""
    
    def __init__(self, game):
        self.game = game
        self.visualizer = GameVisualizer()
        self.running = False
        self.update_thread = None
    
    def start(self):
        """Start live monitoring"""
        self.running = True
        self.update_thread = threading.Thread(target=self._update_loop)
        self.update_thread.daemon = True
        self.update_thread.start()
    
    def stop(self):
        """Stop monitoring"""
        self.running = False
        if self.update_thread:
            self.update_thread.join()
    
    def _update_loop(self):
        """Main update loop for live display"""
        while self.running:
            self.visualizer.clear_screen()
            
            # Show header
            self.visualizer.print_header(
                self.game.round_number, 
                self.game.max_rounds
            )
            
            # Show agent status
            self.visualizer.print_agent_status(self.game.agents)
            
            # Show leaderboard
            if self.game.leaderboard:
                self.visualizer.show_leaderboard(
                    self.game.leaderboard, 
                    animated=False
                )
            
            # Show recent moves
            if self.game.game_history:
                latest_round = self.game.game_history[-1]
                if 'moves' in latest_round:
                    self.visualizer.show_optimization_feed(
                        latest_round['moves']
                    )
            
            time.sleep(1)  # Update every second
    
    def show_round_summary(self, round_results: Dict):
        """Display round summary with animations"""
        self.visualizer.clear_screen()
        
        print(f"\n🎯 ROUND {round_results['round']} COMPLETE!")
        print("=" * 60)
        
        # Animate each move
        for move in round_results['moves']:
            self.visualizer.animate_optimization(
                move.agent_name,
                move.optimization_type
            )
        
        # Show updated leaderboard with animation
        self.visualizer.show_leaderboard(round_results['scores'])
        
        # Pause for dramatic effect
        time.sleep(2)