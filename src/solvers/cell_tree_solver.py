from solvers.solver import Solver
from algorithms import astar
from algorithms.spanning_tree import is_spanning_tree_possible
from collections import deque
from utils.utils import IDX_TO_DIRECTION


class CellTreeSolver(Solver):
    """
    A solver that implements the idea of right-hand-side hugging while navigating the grid.
    It is based on the idea mentioned here: 'https://github.com/twanvl/snake/'. Therefore, the name Cell Tree solver.

    It offers several paramaters, the first three are for path finding:
    - wall_bonus (float): a bonus to nodes which have a fixed wall (the game border) adjacent
    - snake_wall_bonus (float): a bonus to nodes which have adjacent snake nodes
    - turn_pen (float): a penalty for taking a turn

    Secondly, it offers two parameters for leaving certain areas unreachable:
    - allowed_unreach_factor (float): the percentage of how much of the unoccupied playing field may be left unreachable
    - len_snake_unreach_factor (float): the percentage of how much the snake can fill the board until no more unreachable areas are allowed
    """

    def __init__(self, name, grid_size):
        super().__init__(name, grid_size)
        self._grid_size = grid_size[0] # we know that we have a square grid
        self.reset()
        self._precompute_ct_neighbour_dict()

        self._full_grid = set([(x, y) for x in range(self._grid_size) for y in range(self._grid_size)])

        # parameters choosable by the user
        self.wall_bonus = 0
        self.snake_wall_bonus = 0
        self.turn_pen = 0
        self.allowed_unreach_factor = 0
        self.len_snake_unreach_factor = 0
        
    def reset(self):
        self._movement_buffer = deque()
        self._shortest_path = []
        self._snake_head_pos = 0

    def set_initial_snake_pos(self, snake):
        pass
    
    def get_move(self, snake, apple):
        if not self._movement_buffer:
            self._compute_next_step(snake, apple, False, [])

        move = self._movement_buffer.popleft()
        return move

    def _compute_next_step(self, snake, apple, prev_span_tree_possible, prev_shortest_path):
        if snake[-1] == apple:
            return

        direction = (snake[-1][0] - snake[-2][0], snake[-1][1] - snake[-2][1])
        shortest_path = astar.shortest_path_ct_wmo(self._grid_size, snake[-1], apple, 
                                                   direction, snake[1:],
                                                   self._neighbour_dict, wall_bonus=self.wall_bonus,
                                                   snake_wall_bonus=self.snake_wall_bonus,
                                                   turn_pen=self.turn_pen)[1:]

        if len(shortest_path) < len(snake):
            temp_snake = snake[len(shortest_path)-1:] + shortest_path
        elif len(shortest_path) == len(snake):
            temp_snake = [snake[-1]] + shortest_path
        else:
            temp_snake = shortest_path[-(len(snake)+1):]

        temp_direction = (temp_snake[-1][0] - temp_snake[-2][0], temp_snake[-1][1] - temp_snake[-2][1])
        span_tree_possible, unreachable_area = is_spanning_tree_possible(self._grid_size, temp_snake, temp_snake[-1], 
                                                                         temp_direction, self._neighbour_dict,
                                                                         self._full_grid)

        min_distance_to_apple = abs(snake[-1][0] - apple[0]) + abs(snake[-1][1] - apple[1])

        unreach_allowed = (len(snake) < (self._grid_size * self._grid_size) * self.len_snake_unreach_factor and
                           len(unreachable_area) <= len(self._full_grid - set(snake)) * self.allowed_unreach_factor)

        if min_distance_to_apple == len(shortest_path) and (span_tree_possible or unreach_allowed):
            self._movement_buffer.extend(shortest_path)
        elif (span_tree_possible or unreach_allowed):
            self._movement_buffer.append(shortest_path[0])
            snake = snake[1:] + [shortest_path[0]]
            self._compute_next_step(snake, apple, True, shortest_path[1:])
        elif prev_span_tree_possible:
            self._movement_buffer.extend(prev_shortest_path)
        else:
            shortest_path_to_unreachables = astar.shortest_path_ct_wmo_many(self._grid_size, snake[-1], unreachable_area, 
                                                                            direction, snake[1:],
                                                                            self._neighbour_dict)[1:]

            move = shortest_path_to_unreachables[0]
            self._movement_buffer.append(move)
            snake = snake[1:] + [shortest_path_to_unreachables[0]]
            self._compute_next_step(snake, apple, False, None)

    def _precompute_ct_neighbour_dict(self):
        self._neighbour_dict = {}

        for i in range(self._grid_size):
            for j in range(self._grid_size):
                for direction in range(4):
                    current = (i, j)

                    if direction == 0:
                        is_left_move = (current[1]) % 2 != 0
                    elif direction == 1:
                        is_left_move = (current[0]) % 2 != 0
                    elif direction == 2:
                        is_left_move = (current[1]) % 2 == 0
                    else:
                        is_left_move = (current[0]) % 2 == 0

                    dx, dy = IDX_TO_DIRECTION[direction]
                    neighbor1 = (current[0] + dx, current[1] + dy, direction)

                    if is_left_move:
                        dx, dy = IDX_TO_DIRECTION[(direction-1) % 4]
                    else:
                        dx, dy = IDX_TO_DIRECTION[(direction+1) % 4]
                    neighbor2 = (current[0] + dx, current[1] + dy, (direction-1 if is_left_move else direction+1) % 4)

                    neighbours = []
                    if (0 <= neighbor1[0] < self._grid_size and 0 <= neighbor1[1] < self._grid_size):
                        neighbours.append(neighbor1)
                    if (0 <= neighbor2[0] < self._grid_size and 0 <= neighbor2[1] < self._grid_size):
                        neighbours.append(neighbor2)

                    self._neighbour_dict[(i, j, direction)] = neighbours

    def _validate_grid_size(self):
        width, height = self._grid_size

        if width%2 != 0 or height%2 != 0:
            raise ValueError(f"Grid Size is not supported by solver {self.name}.")