from solvers.solver import Solver
from collections import deque
from algorithms import astar


class TailChasingSolver(Solver):
    """
    Implementation of a solver where the snake always tries to make sure that a path 
    towards its tail still exists. This does, however, not guarantee a win, and the snake
    may end up on a loop. In that case the snake kills itself.
    """

    def __init__(self, name, grid_size):
        super().__init__(name, grid_size)
        self.reset()

    def set_initial_snake_pos(self, snake):
        pass
    
    def get_move(self, snake, apple):
        if not self._movement_buffer:
            self.counter = 0
            self._compute_next_step(snake, apple)

        move = self._movement_buffer.popleft()
        return move
    
    def reset(self):
        self._movement_buffer = deque()
        self._shortest_path_to_tail = []

    def _compute_next_step(self, snake, apple):
        self.counter += 1
        if self.counter > self._grid_size[0] * self._grid_size[1]:
            self._movement_buffer.append((-1, -1)) # we ended up on a loop, so we return an illegal move to end the game
            return

        shortest_path = astar.shortest_path_wmo(self._grid_size, snake[-1], apple, snake[1:])

        added_obstacles = []

        while shortest_path is not None:
            shortest_path = shortest_path[1:]

            if len(shortest_path) < len(snake):
                temp_snake = snake[len(shortest_path)-1:] + shortest_path
            elif len(shortest_path) == len(snake):
                temp_snake = [snake[-1]] + shortest_path
            else:
                temp_snake = shortest_path[-(len(snake)+1):]

            new_shortest_path_to_tail = astar.shortest_path(self._grid_size, temp_snake[-1], temp_snake[0], temp_snake[1:])

            if new_shortest_path_to_tail is not None:
                self._movement_buffer.extend(shortest_path)
                self._shortest_path_to_tail = new_shortest_path_to_tail[1:]
                return
            else:
                if len(shortest_path) > 1:
                    added_obstacles.append(shortest_path[-2])
                    shortest_path = astar.shortest_path(self._grid_size, snake[-1], apple, snake[1:] + added_obstacles)
                else:
                    break
        
        move = self._shortest_path_to_tail[0]
        self._shortest_path_to_tail = self._shortest_path_to_tail[1:] + [snake[1]]
        self._movement_buffer.append(move)
        self._compute_next_step(snake[1:] + [move], apple)

    def _validate_grid_size(self):
        pass