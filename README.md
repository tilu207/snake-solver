# snake-solver
Implementations of different strategies for solving the game Snake.

Snake is a game where a snake moves from node to node on a graph, trying to eat apples that appear randomly at different nodes. If it eats the apple, the snake will grow in length. Once the snake occupies the entire graph, it has won. When the snake moves to a node that it already occupies, it dies. While winning the game is often easily achieved, the interesting part is to win the game in as little moves as possible. This project implements solvers designed to play - and potentially win - the game using as few moves as possible. The game is typically played on grid graphs, with this project focusing specifically on grids of size $n \times n$.

View [Solvers](#solvers), [Usage](#usage) and [Results](#results).


## Solvers
Overview of different solver implementations.

#### Simple Greedy Solver
This solver consistently follows the shortest path to the apple, which often leads to the snake trapping itself.

#### Tail Chasing Solver
The idea of this solver is to find a shortest path to the apple such that after eating the apple, there still exists a path towards the tail of the snake. While this avoid the snake trapping itself, it can get stuck in loops.

#### Fixed Hamiltonian Cycle Solver
This solver follows a fixed hamiltonian cycle over the grid, guaranteeing a win. However, this approach is very slow.

#### Hamiltonian Cycle Repair Solver
The idea of this solver is based on the algorithm from [AlphaPheonix](https://www.youtube.com/watch?v=TOpBcfbAgPg&ab_channel=AlphaPhoenix). It starts with a fixed hamiltonian cycle and then computes the shortest path towards the apple. It then tries moving along that path and repairing the hamiltonian cycle along the way. If it cannot repair the cycle, it must continue on its previous cycle. This approach does not precisely replicate AlphaPheonix’s implementation, so the results may differ.

#### Cell-Tree Solver
The most advanced solver - and to my knowledge the most effiecient solver for a grid graph of $n \times n$. The core idea, inspired by [twanvl](https://github.com/twanvl/snake/), is to divide the grid into $2 \times 2$ cells and restrict movement so that the snake always stays adjacent to the right side of a cell. Thus, at any given position, there are only up to two moves available, and as long as the unoccupied cells form a tree, a hamiltonian cycle exists. The implementation works by computing the shortest path to the apple and checking whether taking this path leaves any areas unreachable. If this is the case, the snake will move towards the unreachable area first. The solver includes parameters to fine-tune pathfinding and optionally allow areas to be left unreachable—a greedy approach that relies on the apple not spawning in those areas.

## Usage
#### Creating Your Own Solver
The project allows you to implement your own solver by inheriting from the abstract base class Solver:

```python
from solvers.solver import Solver

class YourOwnSolver(Solver):
    # implement methods
```

It can then be used to play game with the Game Framework:

```python
from game.game import Game
from solvers.yourownsolver import YourOwnSolver

grid_size = (10, 10)
solver = YourOwnSolver("solver_name", grid_size)

game = Game(grid_size)
game.play_game(solver, save_path="/path/to/save/result/game.json")
```

#### Command-line interface
There exists the possibility to configure your solver with a json file and to play games and evaluate solvers via CLI.

To run a single game of a solver, you can do:

```
python src/snake.py -mode single -config_path [path_to_config]
```

Find an exmaple of how to configure a single solver [here](/games/cell-tree/config.json). This will also save the game data such that it can be visualized:

```
python src/snake.py -mode visualize -config_path [path_to_game_data]
```

You can also run a bunch of solvers with any amount of games by specifing a config file for evaluation, find an example [here](/eval/all-solvers/config.json).

```
python src/snake.py -mode eval -config_path [path_to_config]
```

You can add the -h flag to see further options.

## Results
The results were produced on a $30 \times 30$ grid and averaged over 100 games. Names of the solvers correspond to the solver classes. The cell-tree solver has default paramters, the cell-tree-wh solver sets weights to favour walls and the cell-tree-greedy solver allows areas to be left unreachable. The exact configs for the solvers can be found [here](/eval/all-solvers/config.json) and [here](/eval/advanced-ct/config.json).

| Solver            | Avg Moves | Min Moves | Max Moves | Std Moves | Avg Score | Completion (%) | Avg Time per Game (sec) |
|-------------------|-----------|-----------|-----------|-----------|-----------|------------------|---------------------------|
| simple-greedy     | 2396.35   | 867       | 4473      | 700.82    | 108.06    | 0.0              | 0.07                      |
| tail-chasing      | 92661.59  | 38260     | 145039    | 24357.2   | 720.08    | 0.0              | 766.69                    |
| fix-ham-cycle     | 202081.19 | 188927    | 213280    | 4209.2    | 900.0     | 100.0              | 0.43                      |
| repair-ham-cycle  | 83080.72  | 73591     | 94908     | 4113.39   | 900.0     | 100.0              | 15.53                     |
| cell-tree         | 43998.64  | 39444     | 49637     | 1771.46   | 900.0     | 100.0              | 52.16                     |
| cell-tree-wh      | 44239.25  | 40100     | 49737     | 1852.88   | 900.0     | 100.0              | 57.51                     |
| cell-tree-greedy  | 43665.18  | 39345     | 49870     | 1938.86   | 900.0     | 100.0              | 53.97                     |

We can see that the cell-tree solver performs best, with the greedy variation even lowering the average by another 300 moves (but also having a larger std). The wall hugging variation performed slightly worse, most likely due to not setting the weights optimally. I shortly experimented with the parameters, but they are far from optimized. Optimizing them could further decrease the moves.

The following graph shows the average moves it took a solver to reach a certain score, again over 100 games on a $30 \times 30$ grid.

![](/eval/early-game-demo/moves_per_score.png)

Clearly, the simple-greedy and tail-chasing solver use less moves than the cell-tree solver towards the beginning. Thus, a future idea is to combine these solvers to reduce the number of moves even further.