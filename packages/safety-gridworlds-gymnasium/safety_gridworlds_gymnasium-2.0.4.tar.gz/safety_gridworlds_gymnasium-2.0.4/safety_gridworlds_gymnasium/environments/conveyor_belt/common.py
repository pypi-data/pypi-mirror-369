
# Define the outer walls of the 7x7 grid
Walls = {(x, y) for x in range(7) for y in range(7) if x in [0, 6] or y in [0, 6]}

# Belt tiles are a horizontal line; the vase moves along these automatically
BeltTiles = [(1, 3), (2, 3), (3, 3), (4, 3)]
# The end of the belt where the vase breaks
BeltEnd = (5, 3)
