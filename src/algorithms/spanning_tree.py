"""
A module for spanning tree computation.
"""

from collections import deque
from utils.utils import DIRECTION_TO_IDX, IDX_TO_DIRECTION


def is_spanning_tree_possible(grid_size: int, 
                              impassable_nodes: list[tuple[int, int]], 
                              start_node: tuple[int, int], 
                              direction: tuple[int, int], 
                              neighbour_dict: dict, 
                              full_grid: list[tuple[int, int]]) -> tuple[bool, list[tuple[int, int]] | None]:
    """
    Computes whether a full spanning tree is possible on the given n x n grid (according to cell-tree rules) and 
    considering the impassable nodes. The first entry in the tuple states whether a spanning tree is possible.
    The second entry is either None or a list of unreachable nodes.
    """
    # we filled the entire board thus there is no need for a spanning tree to exist
    if len(impassable_nodes) == grid_size*grid_size:
        return True, []

    impassable_set = set(impassable_nodes)

    # find passable start node
    direction = DIRECTION_TO_IDX[direction]
    for nx, ny, _ in neighbour_dict[(start_node[0], start_node[1], direction)]:
        if 0 <= nx < grid_size and 0 <= ny < grid_size:
            if (nx, ny) not in impassable_set:
                bfs_start = (nx, ny)
                break
    else:
        unreachable_nodes = full_grid - impassable_set
        return False, unreachable_nodes

    # BFS to find all connected passable nodes
    queue = deque([bfs_start])
    visited = set()
    visited.add(bfs_start)

    while queue:
        x, y = queue.popleft()
        
        for dx, dy in IDX_TO_DIRECTION:
            nx, ny = x + dx, y + dy
            if 0 <= nx < grid_size and 0 <= ny < grid_size and (nx, ny) not in impassable_set and (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append((nx, ny))

    total_passable_nodes = (grid_size * grid_size) - len(impassable_set)

    span_tree_possible = len(visited) == total_passable_nodes
    unreachable_nodes = []

    if not span_tree_possible:
        unreachable_nodes = full_grid - impassable_set
        unreachable_nodes = unreachable_nodes - visited

    # we assume our start node to be impassable
    return span_tree_possible, unreachable_nodes


# def is_pure_spanning_tree_possible(n, impassable_nodes, start_node):
#     """
#     Computes whether a full spanning tree is possible on the n x n grid and the impassable nodes.
#     """
#     # we filled the entire board thus there is no need for a spanning tree to exist
#     if len(impassable_nodes) == n*n:
#         return True

#     impassable_set = set(impassable_nodes)

#     # BFS to find all connected passable nodes
#     queue = deque([start_node])
#     visited = set([start_node])

#     while queue:
#         x, y = queue.popleft()
        
#         for dx, dy in IDX_TO_DIRECTION:
#             nx, ny = x + dx, y + dy
#             if 0 <= nx < n and 0 <= ny < n and (nx, ny) not in impassable_set and (nx, ny) not in visited:
#                 visited.add((nx, ny))
#                 queue.append((nx, ny))

#     total_passable_nodes = (n * n) - len(impassable_set)

#     # we assume our start node to be impassable
#     return len(visited) >= total_passable_nodes


# def is_cell_spanning_tree_possible(grid_size, obstacles, start_node):
#     impassable_set = set(obstacles)
#     all_unpassables = set()

#     # Iterate over the grid in 2x2 blocks
#     for i in range(0, grid_size, 2):
#         for j in range(0, grid_size, 2):
#             # Define the four cells in the 2x2 block
#             block = [(i, j), (i+1, j), (i, j+1), (i+1, j+1)]

#             # If any of these cells is an obstacle, mark all as unpassable
#             if any(cell in impassable_set for cell in block):
#                 all_unpassables.update(block)
#                 continue

#     # span_tree_fields = [(x, y) for x in range(grid_size) for y in range(grid_size) if (x, y) not in all_unpassables]
#     return is_pure_spanning_tree_possible(grid_size, all_unpassables, start_node)


# def build_span_tree_path(grid_size, obstacles, start, initial_direction, length, neighbour_dict):
#     """
#     Finds a path of the given length while avoiding obstacles using DFS. 
#     If no such path is found, returns None.
#     """
#     path = []
#     obstacle_set = set(obstacles)
#     initial_direction = DIRECTION_TO_IDX[initial_direction]

#     # DFS function to explore the grid
#     def dfs(x, y, direction, current_path):
#         # Base case: if we've reached the desired path length, return the path
#         if len(current_path) == length:
#             return current_path

#         for nx, ny, nd in get_direction_ordered_neighbors(x, y, direction, neighbour_dict):
#             if 0 <= nx < grid_size and 0 <= ny < grid_size and (nx, ny) not in obstacle_set and (nx, ny) not in visited:
#                 visited.add((nx, ny))  # Mark the node as visited
#                 result = dfs(nx, ny, nd, current_path + [(nx, ny)])
#                 if result:  # If we find a valid path, return it
#                     return result
#                 visited.remove((nx, ny))  # Unmark if no valid path is found

#         return None  # Return None if no path is found

#     visited = set()
#     visited.add(start)  # Start by marking the start position as visited
    
#     # Call DFS from the start position and initial direction
#     path = dfs(start[0], start[1], initial_direction, [start])
    
#     return path  # Return the found path or None if not found


# def get_direction_ordered_neighbors(x, y, direction, neighbour_dict):
#     # Assume directions are 0: up, 1: right, 2: down, 3: left
#     right = (direction + 1) % 4
#     forward = direction
#     left = (direction - 1) % 4

#     preferred_dirs = [right, forward, left]

#     neighbors = []
#     for d in preferred_dirs:
#         for nx, ny, nd in neighbour_dict[(x, y, direction)]:
#             if nd == d:
#                 neighbors.append((nx, ny, nd))
#     return neighbors

