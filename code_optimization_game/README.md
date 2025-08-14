# Code Optimization Battle Arena 🎮

A competitive coding game where multiple AI agents compete to optimize the same codebase using different strategies. Watch as agents with different optimization philosophies battle it out in real-time!

## Features

- **Multiple AI Agents**: 5 unique agents with different optimization strategies
  - **PerformanceBot**: Focuses on speed and performance optimizations
  - **ReadabilityBot**: Improves code clarity and maintainability
  - **MemoryBot**: Reduces memory usage and improves efficiency
  - **AlgorithmBot**: Implements better algorithms and data structures
  - **MinimalistBot**: Reduces code size and complexity

- **Real-time Competition**: Watch agents compete round by round
- **Scoring System**: Multi-factor scoring based on:
  - Lines of code
  - Cyclomatic complexity
  - Execution time
  - Memory usage
  - Readability score
  - Test coverage
  - Performance score

- **Multiple Game Modes**:
  - Tournament mode (all agents)
  - Head-to-head battles
  - Custom agent selection
  - Demo mode for quick preview

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd code_optimization_game

# No additional dependencies required - uses Python standard library
```

## Usage

### Quick Demo
```bash
python run_game.py demo
```

### Interactive Mode (Default)
```bash
python run_game.py
```
This allows you to:
- Choose which code to optimize
- Select game mode (tournament, battle, custom)
- Configure number of rounds
- Select specific agents

### Tournament Mode
```bash
# Run a full tournament with all agents
python run_game.py tournament [code_name] [rounds]

# Example: 
python run_game.py tournament fibonacci 10
```

### Head-to-Head Battle
```bash
python run_game.py battle
```

## Available Code Examples

The game includes several code examples for optimization:

1. **fibonacci**: Recursive Fibonacci implementation
2. **data_processing**: Data filtering and processing functions
3. **string_operations**: String manipulation utilities
4. **sorting_searching**: Sorting and searching algorithms
5. **class_based**: Object-oriented code with classes
6. **file_processing**: File and text processing functions

## How It Works

1. **Initial Code**: The game starts with an unoptimized code snippet
2. **Agent Turns**: Each agent analyzes the code and applies their optimization strategy
3. **Validation**: Optimizations are validated using AST parsing and test suites
4. **Scoring**: Improvements are scored based on multiple metrics
5. **Competition**: Agents compete over multiple rounds
6. **Winner**: The agent with the highest cumulative score wins

## Agent Strategies

### PerformanceBot
- Converts loops to list comprehensions
- Uses built-in functions (sum, map, filter)
- Adds caching decorators
- Optimizes hot paths

### ReadabilityBot
- Adds docstrings and comments
- Improves variable naming
- Breaks long lines
- Simplifies complex expressions

### MemoryBot
- Converts lists to generators
- Uses __slots__ in classes
- Implements lazy evaluation
- Cleans up unused variables

### AlgorithmBot
- Replaces O(n²) with O(n log n) algorithms
- Uses better data structures (sets for lookups)
- Implements memoization
- Adds early returns

### MinimalistBot
- Removes redundant code
- Simplifies boolean expressions
- Uses ternary operators
- Combines statements

## Game Metrics

The scoring system evaluates code based on:

- **Lines of Code** (15%): Fewer is better
- **Cyclomatic Complexity** (10%): Lower is better
- **Execution Time** (10%): Faster is better
- **Memory Usage** (10%): Less is better
- **Readability Score** (20%): Higher is better
- **Test Coverage** (30%): Higher is better
- **Performance Score** (50%): Higher is better

## Output Files

The game saves history to JSON files:
```
game_history_<code_name>_<timestamp>.json
```

These files contain:
- Round-by-round moves
- Agent scores
- Optimization types applied
- Success/failure status

## Extending the Game

### Adding New Agents

Create a new agent by extending `CodeOptimizationAgent`:

```python
from game import CodeOptimizationAgent

class MyCustomAgent(CodeOptimizationAgent):
    def __init__(self):
        super().__init__("MyBot", "Custom-Strategy")
    
    def analyze_code(self, code: str):
        # Analyze code for optimization opportunities
        pass
    
    def optimize(self, code: str, metrics):
        # Apply optimizations
        return optimized_code, "optimization_type"
```

### Adding New Code Examples

Add to `example_codes.py`:

```python
EXAMPLE_CODES["my_code"] = """
# Your code here
"""

TEST_SUITES["my_code"] = """
# Test cases
"""
```

## Tips for Watching Games

- The visualization shows real-time agent moves
- Green indicators (🟢) mean improvements
- Red indicators (🔴) mean degradation
- Watch the leaderboard for score changes
- Failed moves show error messages

## Future Enhancements

Potential improvements:
- Web-based visualization
- Network multiplayer
- Custom agent upload
- More sophisticated scoring
- Code coverage analysis
- Performance profiling
- Tournament brackets
- Agent learning/evolution

## License

MIT License - Feel free to modify and extend!

## Contributing

Contributions welcome! Ideas for new agents, optimization strategies, or game features are appreciated.