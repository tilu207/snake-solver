from solvers.solver import Solver
from collections import deque
from algorithms import astar


class SimpleGreedySolver(Solver):
    """
    A very simple and greedy solver that always takes the shortest path towards the apple.
    Once no such path exists anymore, it kills itself.
    """

    def __init__(self, name, grid_size):
        super().__init__(name, grid_size)
        self.reset()

    def set_initial_snake_pos(self, snake):
        pass
    
    def get_move(self, snake, apple):
        if not self._movement_buffer:
            self._compute_next_step(snake, apple)

        move = self._movement_buffer.popleft()
        return move
    
    def reset(self):
        self._movement_buffer = deque()

    def _compute_next_step(self, snake, apple):
        shortest_path = astar.shortest_path_wmo(self._grid_size, snake[-1], apple, snake[1:])
        if shortest_path is not None:
            self._movement_buffer.extend(shortest_path[1:])
        else:
            self._movement_buffer.append((-1, -1))

    def _validate_grid_size(self):
        pass