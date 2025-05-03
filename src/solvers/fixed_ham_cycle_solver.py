from solvers.solver import Solver
from utils.utils import create_simple_ham_cycle


class FixedHamCycleSolver(Solver):
    """
    An implementation of a fixed solver that calculates a Hamiltonian cycle once
    on the grid and follows it until the end of the game.
    """

    def __init__(self, name, grid_size):
        super().__init__(name, grid_size)
        self._ham_cycle = create_simple_ham_cycle(self._grid_size[0], self._grid_size[1])
        self.reset()

    def set_initial_snake_pos(self, snake):
        for i in range(len(self._ham_cycle)):
            if self._ham_cycle[i] == snake[-1]:
                self._snake_head_pos = i
                break

        # determine in which directon we need to move
        if self._ham_cycle[self._snake_head_pos + 1] == snake[-2]: 
            self._step_direction = -1
    
    def get_move(self, snake, apple):
        self._snake_head_pos = (self._snake_head_pos + self._step_direction) % len(self._ham_cycle)
        return self._ham_cycle[self._snake_head_pos]
    
    def reset(self):
        self._snake_head_pos = 0
        self._step_direction = 1

    def _validate_grid_size(self):
        width, height = self._grid_size

        if width%2 != 0 and height%2 != 0:
            raise ValueError(f"Grid Size is not supported by solver {self.name}.")