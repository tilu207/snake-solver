import random
import time
import json
import zlib
import base64
import pickle

from solvers.solver import Solver


class Game:
    """
    Simulates the Snake game on a square grid.
    The initial snake will always have a length of 3, and will be placed
    as centrally as possible while facing upwards.
    """

    def __init__(self, grid_size: tuple[int, int]):
        """
        Initialize the game environment.
        """
        self._grid_size = grid_size
        self.max_moves = (self._grid_size[0] * self._grid_size[1]) ** 2
        self._all_fields = {(x, y) for x in range(self._grid_size[0]) for y in range(self._grid_size[1])}

        self._validate_grid_size()

    def play_game(self, solver: Solver, save_path: str = "", log: bool = False) -> dict:
        """
        Runs a full game simulation using the specified solver.

        The solver is responsible for controlling the snake's movement.
        The final game state is returned as a dictionary and optionally saved.
        """
        self._solver = solver
        self._reset()

        move = None

        start_time = time.time()

        solver.set_initial_snake_pos(self._snake)
        
        while True:
            try:
                move = solver.get_move(self._snake, self._apple)
                self._apply_move(move)
                self._is_game_over, self._game_over_reason = self._get_game_status()

            except Exception as e: # game crashed due to solver
                self._is_game_over = True
                self._game_over_reason = f"Error while getting move {e}"
            
            if log:
                print(f"Current move: {self._moves}")

            if self._is_game_over:
                end_time = time.time()
                self._total_time += end_time - start_time

                game_dict = self._create_game_dict()
                    
                self._save_game(save_path, game_dict)

                return game_dict
            
    def set_seed(self, seed: int):
        """
        Sets the seed of the game for reproducability.
        """
        self._seed = seed
        random.seed(self._seed)

    def get_grid_size(self) -> tuple[int, int]:
        return self._grid_size

    def _reset(self):
        width, height = self._grid_size
        center_x = width // 2
        center_y = height // 2
        
        self._snake = [(center_x, center_y + i - 1) for i in range(3)]  # (tail, ..., head)
        self._snake_set = set(self._snake)
        self._initial_snake = self._snake[:]

        self._moves = 0
        self._move_history = []
        self._apple_history = []
        self._total_time = 0
        self._game_over_reason = None
        self._is_game_over = False
        
        self._drop_new_apple()

    def _get_game_status(self) -> tuple[bool, str]:
        # Not ideal returning strings as the reason... would be better to use ints here which then have a certain meaning
        if self._moves >= self.max_moves:
            return True, "Reached max number of moves."

        if self._snake[-1][0] >= self._grid_size[0] or self._snake[-1][1] >= self._grid_size[1] or self._snake[-1][0] < 0 or self._snake[-1][1] < 0:
            return True, "Move out of bounds."
        
        if abs(self._snake[-1][0] - self._snake[-2][0]) + abs(self._snake[-1][1] - self._snake[-2][1]) > 1:
            return True, "Step size is larger than 1."

        if len(self._snake) != len(self._snake_set):
            return True, "Snake killed itself."

        if len(self._snake) == self._grid_size[0]*self._grid_size[1]:
            return True, "Reached max length."
        
        return False, None

    def _apply_move(self, move: tuple[int, int]):
        self._moves += 1
        self._move_history.append(move)

        if move == self._apple:
            self._snake = self._snake + [move]
            self._snake_set.add(move)
            self._drop_new_apple()
        else:
            tail = self._snake.pop(0)
            self._snake_set.remove(tail)
            self._snake.append(move)
            self._snake_set.add(move)

    def _drop_new_apple(self):
        snake_set = set(self._snake)
        open_field = list(self._all_fields - snake_set)
        
        if len(open_field) > 0:
            self._apple = random.choice(open_field)
            self._apple_history.append(self._apple)

    def _create_game_dict(self) -> dict:
        width, height = self._grid_size

        def pos_to_index(pos):
            x, y = pos
            return x + y * width

        game_dict = {
            "grid_size": self._grid_size,
            "game_seed": getattr(self, '_seed', None),
            "solver_name": self._solver.name,
            "solver_type": type(self._solver).__name__,
            "snake_length": len(set(self._snake)),
            "total_moves": self._moves,
            "game_over_reason": self._game_over_reason,
            "total_time": round(self._total_time, 2),
            "initial_snake": [pos_to_index(p) for p in self._initial_snake],
            "move_history": [pos_to_index(p) for p in self._move_history],
            "apple_history": [pos_to_index(p) for p in self._apple_history]
        }

        return game_dict

    def _save_game(self, save_path: str, result: dict):
        if not save_path:
            return

        # compress result
        moves = result['move_history']
        compressed_moves = zlib.compress(pickle.dumps(moves))
        result['move_history'] = base64.b64encode(compressed_moves).decode()

        apples = result['apple_history']
        compressed_apples = zlib.compress(pickle.dumps(apples))
        result['apple_history'] = base64.b64encode(compressed_apples).decode()

        with open(save_path, "w") as file:
            json.dump(result, file, indent=2)

    def _validate_grid_size(self):
        if self._grid_size[0] < 4 or self._grid_size[1] < 4:
            raise ValueError("Grid Size too small. Needs to be at least (4, 4).")