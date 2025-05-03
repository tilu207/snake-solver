from abc import ABC, abstractmethod


class Solver(ABC):
    """
    Abstract base class for implementing a Snake solver.
    """

    @abstractmethod
    def __init__(self, name: str, grid_size: tuple[int, int]):
        """
        Initialize the solver.
        """
        super().__init__()
        self.name = name
        self._grid_size = grid_size
        self._validate_grid_size()

    @abstractmethod
    def set_initial_snake_pos(self, snake: list[tuple[int, int]]):
        """
        Set the initial position of the snake at the start of the game. See game class
        for more details on how the snake is initialised.
        """

    @abstractmethod
    def get_move(self, snake: list[tuple[int, int]], apple: tuple[int, int]) -> tuple[int, int]:
        """
        Determine the next move for the snake.
        """

    @abstractmethod
    def reset(self):
        """
        Reset the solver's internal state before starting a new game.
        """
    
    @abstractmethod
    def _validate_grid_size(self):
        """
        Validate that the provided grid size is acceptable for the solver.
        """