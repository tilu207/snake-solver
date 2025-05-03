"""
This module provides implementations of several variants of the A* (A-Star) algorithm
for the Snake game. While some code duplication is present, this structure was
chosen to allow for high flexibility throughout testing different A* strategies.
For future development, it is highly recommended to refactor the module.
"""

import heapq
from utils.utils import DIRECTION_TO_IDX, IDX_TO_DIRECTION

def manhatten_distance(a: tuple[int, int], b: tuple[int, int], weight: int = 1) -> int | float:
    """
    Calculates the Manhattan distance between two points in a 2D grid.
    """
    return (abs(a[0] - b[0]) + abs(a[1] - b[1])) * weight

def manhatten_distance_many(a: tuple[int, int], goals: list[tuple[int, int]], weight: int = 1) -> int | float:
    """
    Calculates the Manhattan distance between a given point and the closest point 
    from a list of goal positions.
    """
    min_distance = float('inf')

    for g in goals:
        distance = abs(a[0] - g[0]) + abs(a[1] - g[1])
        if distance < min_distance:
            min_distance = distance
            if min_distance == 1:
                return weight

    return min_distance * weight

def shortest_path(grid_size: tuple[int, int], 
                  start: tuple[int, int], 
                  goal: tuple[int, int], 
                  obstacles: list[tuple[int, int]]) -> list[tuple[int, int]] | None:
    """
    Implements the A*-algorithm.
    """
    width, height = grid_size

    obstacles = set(obstacles)

    open_set = []
    heapq.heappush(open_set, (manhatten_distance(start, goal), 0, start, [start]))

    visited = set()

    while open_set:
        _, g, current, path = heapq.heappop(open_set)

        if current in visited:
            continue
        visited.add(current)

        if current == goal:
            return path
        
        for dx, dy in IDX_TO_DIRECTION:
            neighbor = (current[0] + dx, current[1] + dy)

            if (0 <= neighbor[0] < width and 0 <= neighbor[1] < height and 
                neighbor not in visited and neighbor not in obstacles):
                
                heapq.heappush(open_set, (g+1+manhatten_distance(neighbor, goal), g+1, neighbor, path + [neighbor]))

    return None

def shortest_path_wmo(grid_size: tuple[int, int], 
                      start: tuple[int, int], goal: tuple[int, int], 
                      obstacles: list[tuple[int, int]], 
                      fixed_obstacles: set = set()) -> list[tuple[int, int]] | None:
    """
    Implements the A*-algorithm with moving obstacles.
    """
    width, height = grid_size

    open_set = []
    heapq.heappush(open_set, (0 + manhatten_distance(start, goal), 0, start, obstacles, [start]))

    visited = set()

    while open_set:
        _, g, current, obstacles, path = heapq.heappop(open_set)

        if current in visited:
            continue
        visited.add(current)

        if current == goal:
            return path
        
        for dx, dy in IDX_TO_DIRECTION:
            neighbor = (current[0] + dx, current[1] + dy)

            if (0 <= neighbor[0] < width and 0 <= neighbor[1] < height and 
                neighbor not in visited and neighbor not in obstacles and neighbor not in fixed_obstacles):
                
                new_g = g + 1
                heapq.heappush(open_set, (new_g + manhatten_distance(neighbor, goal), new_g, neighbor, obstacles[1:], path + [neighbor]))

    return None

def shortest_path_wmo_many(grid_size: tuple[int, int], 
                           start: tuple[int, int], 
                           goals: list[tuple[int, int]], 
                           obstacles: list[tuple[int, int]]) -> list[tuple[int, int]] | None:
    """
    Implements the A*-algorithm with moving obstacles and multiple goals.
    """
    width, height = grid_size

    open_set = []
    heapq.heappush(open_set, (0 + manhatten_distance_many(start, goals), 0, start, obstacles, [start]))

    visited = set()

    while open_set:
        _, g, current, obstacles, path = heapq.heappop(open_set)

        if current in visited:
            continue
        visited.add(current)

        if current in goals:
            return path
        
        for dx, dy in IDX_TO_DIRECTION:
            neighbor = (current[0] + dx, current[1] + dy)

            if (0 <= neighbor[0] < width and 0 <= neighbor[1] < height and 
                neighbor not in visited and neighbor not in obstacles):
                
                new_g = g + 1
                heapq.heappush(open_set, (new_g + manhatten_distance_many(neighbor, goals), new_g, neighbor, obstacles[1:], path + [neighbor]))

    return None

def shortest_path_ct_wmo(grid_size: int, 
                         start: tuple[int, int], 
                         goal: tuple[int, int], 
                         initial_direction: tuple[int, int], 
                         obstacles: list[tuple[int, int]], 
                         neighbour_dict: dict, 
                         wall_bonus: float = 0, 
                         snake_wall_bonus: float = 0, 
                         turn_pen: float = 0) -> list[tuple[int, int]] | None:
    """
    Implements the A*-algorithm with moving obstacles following the cell-tree rules.
    """
    def get_wall_bonus(a):
        x, y = a

        if x == 0 or y == 0 or x == grid_size-1 or y == grid_size-1:
            return -wall_bonus

        return 0
    
    def get_snake_wall_bonus(a, obstacles):
        if snake_wall_bonus == 0:
            return 0

        for x, y in IDX_TO_DIRECTION:
            nx, ny = x + a[0], y + a[1]

            if (nx, ny) in obstacles:
                return -snake_wall_bonus
            
        return 0
    
    def get_turn_penalty(old_d, new_d):
        if old_d != new_d:
            return turn_pen
        return 0

    obstacles_per_step = {}

    initial_direction = DIRECTION_TO_IDX[initial_direction]

    open_set = []
    heapq.heappush(open_set, (0 + manhatten_distance(start, goal), 0, start, initial_direction, [start]))

    visited = set()

    while open_set:
        _, g, current, direction, path = heapq.heappop(open_set)

        if current in visited:
            continue
        visited.add(current)

        if current == goal:
            return path
        
        for data in neighbour_dict[(current[0], current[1], direction)]:
            neighbor = (data[0], data[1])
            new_direction = data[2]
            if neighbor not in visited:
                step = len(path) - 1
                curr_obstacles = []

                if step < len(obstacles):
                    if step not in obstacles_per_step.keys():
                        obstacle_set = set(obstacles[step:])
                        obstacles_per_step[step] = obstacle_set

                    curr_obstacles = obstacles_per_step[step]

                    if neighbor in obstacles_per_step[step]:
                        continue
                
                turn_penalty = get_turn_penalty(direction, new_direction)
                wall_bonus = get_wall_bonus(neighbor)
                snake_wall_bonus = get_snake_wall_bonus(neighbor, curr_obstacles)

                step_cost = 1 + turn_penalty + wall_bonus + snake_wall_bonus
                new_g = g + step_cost
                f = new_g + manhatten_distance(neighbor, goal)

                heapq.heappush(open_set, (f, new_g, neighbor, new_direction, path + [neighbor]))

    return None

def shortest_path_ct_wmo_many(grid_size: int, 
                              start: tuple[int, int], 
                              goals: list[tuple[int, int]], 
                              initial_direction: tuple[int, int], 
                              obstacles: list[tuple[int, int]], 
                              neighbour_dict: dict) -> list[tuple[int, int]] | None:
    """
    Implements the A*-algorithm with moving obstacles following the cell-tree rules for multiple goals.
    """
    obstacles_per_step = {}

    initial_direction = DIRECTION_TO_IDX[initial_direction]

    open_set = []
    heapq.heappush(open_set, (0 + manhatten_distance_many(start, goals), 0, start, initial_direction, [start]))

    visited = set()

    while open_set:
        _, g, current, direction, path = heapq.heappop(open_set)

        if current in visited:
            continue
        visited.add(current)

        if current in goals:
            return path
        
        for data in neighbour_dict[(current[0], current[1], direction)]:
            neighbor = (data[0], data[1])
            new_direction = data[2]
            if neighbor not in visited:
                step = len(path) - 1
                curr_obstacles = []

                if step < len(obstacles):
                    
                    if step not in obstacles_per_step.keys():
                        obstacle_set = set(obstacles[step:])
                        obstacles_per_step[step] = obstacle_set

                    curr_obstacles = obstacles_per_step[step]

                    if neighbor in obstacles_per_step[step]:
                        continue

                step_cost = 1
                new_g = g + step_cost
                f = new_g + manhatten_distance_many(neighbor, goals)

                heapq.heappush(open_set, (f, new_g, neighbor, new_direction, path + [neighbor]))

    return None

# def shortest_path_ct_wmo(grid_size, start, goal, initial_direction, obstacles, neighbour_dict):
#     """
#     Implements the A*-algorithm for a grid and manhatten distance,
#     while following the cell-tree rules. Also uses moving obstacles.
#     """
#     obstacles_per_step = {}

#     initial_direction = DIRECTION_TO_IDX[initial_direction]

#     open_set = []
#     heapq.heappush(open_set, (0 + manhatten_distance(start, goal), 0, start, initial_direction, [start]))

#     visited = set()

#     while open_set:
#         _, g, current, direction, path = heapq.heappop(open_set)

#         if current in visited:
#             continue
#         visited.add(current)

#         if current == goal:
#             return path
        
#         for data in neighbour_dict[(current[0], current[1], direction)]:
#             neighbor = (data[0], data[1])
#             direction = data[2]
#             if neighbor not in visited:
#                 step = len(path) - 1

#                 if step < len(obstacles):
#                     if step not in obstacles_per_step.keys():
#                         obstacle_set = set(obstacles[step:])
#                         obstacles_per_step[step] = obstacle_set

#                     if neighbor in obstacles_per_step[step]:
#                         continue
                
#                 new_g = g + 1
#                 heapq.heappush(open_set, (new_g + manhatten_distance(neighbor, goal), new_g, neighbor, direction, path + [neighbor]))

#     return None


# def shortest_path_ct_wmo_many(grid_size, start, goals, initial_direction, obstacles, neighbour_dict):
#     """
#     Implements the A*-algorithm for a grid and manhatten distance,
#     while following the cell-tree rules. Also uses moving obstacles and multiple goals.
#     """
#     obstacles_per_step = {}

#     initial_direction = DIRECTION_TO_IDX[initial_direction]

#     open_set = []
#     heapq.heappush(open_set, (0 + manhatten_distance_many(start, goals), 0, start, initial_direction, [start]))

#     visited = set()

#     while open_set:
#         _, g, current, direction, path = heapq.heappop(open_set)

#         if current in visited:
#             continue
#         visited.add(current)

#         if current in goals:
#             return path
        
#         for data in neighbour_dict[(current[0], current[1], direction)]:
#             neighbor = (data[0], data[1])
#             direction = data[2]
#             if neighbor not in visited:
#                 step = len(path) - 1

#                 if step < len(obstacles):
#                     if step not in obstacles_per_step.keys():
#                         obstacle_set = set(obstacles[step:])
#                         obstacles_per_step[step] = obstacle_set

#                     if neighbor in obstacles_per_step[step]:
#                         continue
                
#                 new_g = g + 1
#                 heapq.heappush(open_set, (new_g + manhatten_distance_many(neighbor, goals), new_g, neighbor, direction, path + [neighbor]))

#     return None