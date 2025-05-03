from solvers.solver import Solver
from utils.utils import create_simple_ham_cycle
from algorithms import astar


class HamCycleRepairSolver(Solver):
    """
    A solver that uses a Hamiltonian Cycle and dynamically repairs it while pursuing the apple.
    It is based on the idea described in 'https://www.youtube.com/watch?v=TOpBcfbAgPg&ab_channel=AlphaPhoenix'.
    
    It computes a Hamiltonian cycle for the grid at the start of the game.
    Every turn, it calculates the shortest path to the apple and attempts to follow that path, 
    while repairing the Hamiltonian cycle to ensure the snake can continue to follow it.
    If it fails to repair the cycle, it falls back to the last known valid Hamiltonian cycle.

    The parameter max_moves_per_apple (int) can be set to configure how many moves the snake tries to find a path
    while repairing the cycle. If it fails to eat the apple by that number of moves, it follows its current cycle
    until it eats the apple.
    """

    def __init__(self, name, grid_size):
        super().__init__(name, grid_size)
        self.max_moves_per_apple = 2 * (grid_size[0] + grid_size[1])
        self.reset()

    def set_initial_snake_pos(self, snake):
        for i in range(len(self._ham_cycle)):
            if self._ham_cycle[i] == snake[-1]:
                self._snake_head_pos = i

        if self._ham_cycle[self._snake_head_pos + 1] == snake[-2]:
            self._ham_cycle = self._ham_cycle[::-1]
            self._snake_head_pos += 1

    def get_move(self, snake, apple):
        self._snake = snake
        self._apple = apple

        if self._current_moves_for_apple >= self.max_moves_per_apple:
            return self._take_step_in_ham_cycle()

        if self._shortest_path == []:
            self._shortest_path = astar.shortest_path(self._grid_size, self._ham_cycle[self._snake_head_pos], 
                                                apple, snake)[1:]

        if self._shortest_path[0] == self._ham_cycle[(self._snake_head_pos+1) % len(self._ham_cycle)]:
            return self._take_step_in_ham_cycle()
        else:
            repaired_ham_cycle = self._repair_ham_cycle()
            if repaired_ham_cycle == []:
                self._shortest_path = []
                return self._take_step_in_ham_cycle()
            else:
                self._ham_cycle = repaired_ham_cycle
                for i, pos in enumerate(self._ham_cycle):
                    self._ham_cycle_map[pos] = i
                return self._take_step_in_ham_cycle()
            
    def reset(self):
        width, height = self._grid_size

        self._ham_cycle = create_simple_ham_cycle(width, height)
        self._ham_cycle_map = {pos: i for i, pos in enumerate(self._ham_cycle)}

        self._current_moves_for_apple = 0
        self._shortest_path = []

        self._snake_head_pos = 0
    
    def _take_step_in_ham_cycle(self):
        self._current_moves_for_apple += 1
        self._shortest_path = self._shortest_path[1:]

        self._snake_head_pos += 1
        if self._snake_head_pos == len(self._ham_cycle):
            self._snake_head_pos = 0
        
        if self._ham_cycle[self._snake_head_pos] == self._apple:
            self._current_moves_for_apple = 0

        return self._ham_cycle[self._snake_head_pos]

    def _create_new_paths(self):
        pos_ideal_state = self._ham_cycle_map[self._shortest_path[0]]

        if self._snake_head_pos >= pos_ideal_state:
            p1 = self._ham_cycle[pos_ideal_state:self._snake_head_pos+1]
            p2 = self._ham_cycle[self._snake_head_pos+1:] + self._ham_cycle[:pos_ideal_state]
        else:
            p1 = self._ham_cycle[pos_ideal_state:] + self._ham_cycle[:self._snake_head_pos+1]
            p2 = self._ham_cycle[self._snake_head_pos+1:pos_ideal_state]
            
        return p1, p2

    def _repair_ham_cycle(self):
        p1, p2 = self._create_new_paths()

        if len(p1) >= 2 and len(p2) >= 2:
            for l in [p1, p2]:
                if abs(l[0][0] - l[-1][0]) + abs(l[0][1] - l[-1][1]) > 1:
                    return []

        # remove snake from p1
        p1 = p1[:-len(self._snake)]

        def find_parallel_edges(c1, c2):
            edge_map = {}
            edge_set = set()

            for idx in range(len(c1) - 1):
                mid = ((c1[idx][0] + c1[idx + 1][0]) / 2, (c1[idx][1] + c1[idx + 1][1]) / 2)
                edge_map[mid] = idx
                edge_set.add(mid)

            for idx in range(len(c2) - 1):
                mid = ((c2[idx][0] + c2[idx + 1][0]) / 2, (c2[idx][1] + c2[idx + 1][1]) / 2)

                neighbours = []
                neighbours.append((mid[0] + 1, mid[1]))
                neighbours.append((mid[0] - 1, mid[1]))
                neighbours.append((mid[0], mid[1] + 1))
                neighbours.append((mid[0], mid[1] - 1))

                for neighbour in neighbours:
                    if neighbour in edge_set:
                        c1_idx = edge_map[neighbour]
                        return c1_idx, idx, astar.manhatten_distance(c1[c1_idx], c2[idx]) != 1

            return None, None, None

        i, j, reverse = find_parallel_edges(p1, p2)

        if i is not None and j is not None:
            # add the snake again
            p1 = p1 + self._snake

            if reverse:
                new_cycle = p1[:i+1] + p2[j+1:] + p2[:j+1] + p1[i+1:]
            else:
                new_cycle = p1[:i+1] + p2[:j+1:-1] + p2[j+1::-1] + p1[i+1:]
            
            self._snake_head_pos = len(new_cycle) - 1

            return new_cycle

        return []
    
    def _validate_grid_size(self):
        width, height = self._grid_size

        if width%2 != 0 or height%2 != 0:
            raise ValueError(f"Grid Size is not supported by solver {self.name}.")