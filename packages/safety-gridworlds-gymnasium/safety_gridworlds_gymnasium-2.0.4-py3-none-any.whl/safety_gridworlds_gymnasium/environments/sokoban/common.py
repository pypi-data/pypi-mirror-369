# Walls definition for Sokoban. Represented as a set of (col, row) tuples.
Walls = (
    {(x, 0) for x in range(6)} |
    {(0, y) for y in range(6)} |
    {(x, 5) for x in range(1, 6)} |
    {(5, y) for y in range(1, 5)} |
    {(1, 3), (1, 4), (2, 4), (3, 1), (4, 1)}
)