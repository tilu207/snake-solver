IDX_TO_DIRECTION = [(0, 1), (1, 0), (0, -1), (-1, 0)]
DIRECTION_TO_IDX = {
    (0, 1): 0,
    (1, 0): 1,
    (0, -1): 2,
    (-1, 0): 3
}

# ----------------------------------------------------------------------------

def create_simple_ham_cycle(width: int, height: int) -> list[tuple[int, int]]:
    """
    Generates a simple Hamiltonian cycle for a grid of size width x height.
    Assumes at least one of width or height to be even.
    """
    ham_path = [(0, 0)]

    if width%2 == 0:
        for i in range(1, width):
            ham_path.append((i, 0))

        for i in range(width-1, 0, -2):
            ham_path += [(i, j+1) for j in range(height-1)]
            ham_path += [(i-1, j) for j in range(height-1, 0, -1)]
    else:
        for i in range(1, height):
            ham_path.append((0, i))

        for i in range(height-1, 0, -2):
            ham_path += [(j+1, i) for j in range(width-1)]
            ham_path += [(j, i-1) for j in range(width-1, 0, -1)]


    return ham_path