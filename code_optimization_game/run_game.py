#!/usr/bin/env python3
"""
Main runner for the Code Optimization Game
"""
import sys
import time
import random
from game import CodeOptimizationGame
from agents import (
    PerformanceOptimizer,
    ReadabilityRefactorer,
    MemoryOptimizer,
    AlgorithmOptimizer,
    MinimalistReducer
)
from visualizer import GameVisualizer, LiveGameMonitor
from example_codes import EXAMPLE_CODES, TEST_SUITES


def run_tournament(code_name: str = "fibonacci", rounds: int = 5, visualize: bool = True):
    """Run a tournament with all agents"""
    
    # Get code and test suite
    if code_name not in EXAMPLE_CODES:
        print(f"Available code examples: {list(EXAMPLE_CODES.keys())}")
        return
    
    initial_code = EXAMPLE_CODES[code_name]
    test_suite = TEST_SUITES.get(code_name, None)
    
    # Create game instance
    game = CodeOptimizationGame(
        initial_code=initial_code,
        test_suite=test_suite,
        max_rounds=rounds,
        time_limit_per_round=5.0
    )
    
    # Register all agents
    agents = [
        PerformanceOptimizer(),
        ReadabilityRefactorer(),
        MemoryOptimizer(),
        AlgorithmOptimizer(),
        MinimalistReducer()
    ]
    
    for agent in agents:
        game.register_agent(agent)
    
    # Setup visualization if requested
    visualizer = None
    monitor = None
    if visualize:
        visualizer = GameVisualizer()
        monitor = LiveGameMonitor(game)
    
    # Start the game
    print("\n" + "=" * 60)
    print("🎮 CODE OPTIMIZATION BATTLE ARENA 🎮".center(60))
    print("=" * 60)
    print(f"\n📝 Optimizing: {code_name}")
    print(f"🔄 Rounds: {rounds}")
    print(f"🤖 Agents: {len(agents)}")
    if visualize and sys.stdin.isatty():
        print("\nPress Enter to start the battle...")
        try:
            input()
        except EOFError:
            pass
    
    if visualizer:
        visualizer.clear_screen()
    
    # Run the tournament
    game.start_game()
    
    # Save results
    game.save_game_history(f"game_history_{code_name}_{int(time.time())}.json")
    
    return game


def run_single_battle(agent1_class, agent2_class, code_name: str = "data_processing"):
    """Run a battle between two specific agents"""
    
    initial_code = EXAMPLE_CODES[code_name]
    test_suite = TEST_SUITES.get(code_name, None)
    
    # Create game with just 2 agents
    game = CodeOptimizationGame(
        initial_code=initial_code,
        test_suite=test_suite,
        max_rounds=3,
        time_limit_per_round=5.0
    )
    
    agent1 = agent1_class()
    agent2 = agent2_class()
    
    game.register_agent(agent1)
    game.register_agent(agent2)
    
    visualizer = GameVisualizer()
    
    print("\n" + "=" * 60)
    print("⚔️  HEAD-TO-HEAD BATTLE ⚔️".center(60))
    print("=" * 60)
    print(f"\n{agent1.name} VS {agent2.name}")
    
    # Show battle animation
    visualizer.show_battle_animation(agent1.name, agent2.name)
    
    time.sleep(2)
    
    # Run the battle
    game.start_game()
    
    return game


def interactive_mode():
    """Interactive mode for selecting agents and code"""
    
    visualizer = GameVisualizer()
    visualizer.clear_screen()
    
    print("🎮 WELCOME TO CODE OPTIMIZATION BATTLE ARENA 🎮")
    print("=" * 60)
    
    # Select code to optimize
    print("\n📝 Select code to optimize:")
    code_options = list(EXAMPLE_CODES.keys())
    for i, code in enumerate(code_options, 1):
        print(f"  {i}. {code}")
    
    choice = input("\nEnter choice (1-{}): ".format(len(code_options)))
    try:
        code_name = code_options[int(choice) - 1]
    except:
        code_name = "fibonacci"
    
    # Select game mode
    print("\n🎯 Select game mode:")
    print("  1. Full Tournament (All agents)")
    print("  2. Head-to-Head Battle (2 agents)")
    print("  3. Custom Selection")
    
    mode = input("\nEnter choice (1-3): ")
    
    if mode == "1":
        rounds = input("Number of rounds (default 5): ")
        rounds = int(rounds) if rounds.isdigit() else 5
        run_tournament(code_name, rounds, visualize=True)
    
    elif mode == "2":
        agent_classes = [
            PerformanceOptimizer,
            ReadabilityRefactorer,
            MemoryOptimizer,
            AlgorithmOptimizer,
            MinimalistReducer
        ]
        
        print("\n🤖 Select first agent:")
        for i, agent_class in enumerate(agent_classes, 1):
            print(f"  {i}. {agent_class.__name__}")
        
        choice1 = input("Enter choice: ")
        agent1 = agent_classes[int(choice1) - 1] if choice1.isdigit() else agent_classes[0]
        
        print("\n🤖 Select second agent:")
        for i, agent_class in enumerate(agent_classes, 1):
            print(f"  {i}. {agent_class.__name__}")
        
        choice2 = input("Enter choice: ")
        agent2 = agent_classes[int(choice2) - 1] if choice2.isdigit() else agent_classes[1]
        
        run_single_battle(agent1, agent2, code_name)
    
    else:
        # Custom selection
        print("\n🤖 Select agents to compete:")
        agent_classes = [
            PerformanceOptimizer,
            ReadabilityRefactorer,
            MemoryOptimizer,
            AlgorithmOptimizer,
            MinimalistReducer
        ]
        
        selected_agents = []
        for i, agent_class in enumerate(agent_classes, 1):
            print(f"  {i}. {agent_class.__name__}")
        
        selections = input("\nEnter agent numbers (comma-separated): ")
        for num in selections.split(','):
            try:
                idx = int(num.strip()) - 1
                if 0 <= idx < len(agent_classes):
                    selected_agents.append(agent_classes[idx]())
            except:
                pass
        
        if len(selected_agents) < 2:
            print("Need at least 2 agents. Adding default agents...")
            selected_agents = [PerformanceOptimizer(), ReadabilityRefactorer()]
        
        # Create and run game
        initial_code = EXAMPLE_CODES[code_name]
        test_suite = TEST_SUITES.get(code_name, None)
        
        game = CodeOptimizationGame(
            initial_code=initial_code,
            test_suite=test_suite,
            max_rounds=5,
            time_limit_per_round=5.0
        )
        
        for agent in selected_agents:
            game.register_agent(agent)
        
        game.start_game()


def demo_mode():
    """Run a quick demo of the game"""
    
    print("\n🎬 DEMO MODE - Quick Battle!")
    print("=" * 60)
    
    # Run a quick 3-round tournament with fibonacci code
    game = run_tournament("fibonacci", rounds=3, visualize=True)
    
    print("\n" + "=" * 60)
    print("Demo complete! Run in interactive mode for full experience.")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "demo":
            demo_mode()
        elif sys.argv[1] == "tournament":
            code = sys.argv[2] if len(sys.argv) > 2 else "fibonacci"
            rounds = int(sys.argv[3]) if len(sys.argv) > 3 else 5
            run_tournament(code, rounds)
        elif sys.argv[1] == "battle":
            run_single_battle(PerformanceOptimizer, AlgorithmOptimizer)
        else:
            interactive_mode()
    else:
        # Default to interactive mode
        interactive_mode()