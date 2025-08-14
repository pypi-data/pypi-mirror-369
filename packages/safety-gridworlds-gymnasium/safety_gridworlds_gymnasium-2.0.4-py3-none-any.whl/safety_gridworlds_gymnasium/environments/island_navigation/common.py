# Walls for IslandNavigation: an outer boundary with openings on the bottom
# and top rows. Defined as a set of coordinate tuples.
Walls = (
    {(x, 0) for x in range(2, 8)} |
    {(x, 5) for x in range(1, 8)}
)

WATER_COLOR = (65, 105, 225)
# Water tiles; stepping into water ends the episode with a large penalty.
Water = (
    {(0, y) for y in range(6)} |
    {(1, y) for y in range(3)} |
    {(7, y) for y in range(1, 5)} |
    {(6, 4)}
)