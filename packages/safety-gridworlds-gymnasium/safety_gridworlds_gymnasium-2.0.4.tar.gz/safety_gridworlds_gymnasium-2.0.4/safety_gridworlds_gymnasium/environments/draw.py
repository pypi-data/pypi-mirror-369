import pygame

# Colours and drawing helpers used across all environments. Keeping these
# definitions in a single module avoids duplication and makes it easy to tweak
# the appearance globally.
WALL_COLOR     = ( 90,  90,  90)  # Dark gray
WALKABLE_COLOR = (190, 190, 190)  # Light gray
TEXT_COLOR     = (  0,   0,   0)  # Black text
BORDER_COLOR   = (221, 221, 221)
BORDER_WIDTH   = 2

def draw_wall_tile(surface, x, y, tile_size_x, tile_size_y):
    """
    Draws a wall-like tile (dark gray).
      - x: column index
      - y: row index
    """
    left = x * tile_size_x
    top  = y * tile_size_y
    rect = pygame.Rect(left, top, tile_size_x, tile_size_y)
    pygame.draw.rect(surface, WALL_COLOR, rect)
    pygame.draw.rect(surface, BORDER_COLOR, rect, width=BORDER_WIDTH)

def draw_walkable_tile(surface, x, y, tile_size_x, tile_size_y):
    """
    Draws a walkable tile (light gray).
      - x: column index
      - y: row index
    """
    left = x * tile_size_x
    top  = y * tile_size_y
    rect = pygame.Rect(left, top, tile_size_x, tile_size_y)
    pygame.draw.rect(surface, WALKABLE_COLOR, rect)
    pygame.draw.rect(surface, BORDER_COLOR, rect, width=BORDER_WIDTH)

def draw_colored_tile(surface, x, y, tile_size_x, tile_size_y, fg_color):
    """
    Draws a tile that fills the entire cell with 'fg_color'.
      - x: column index
      - y: row index
    """
    left = x * tile_size_x
    top  = y * tile_size_y
    rect = pygame.Rect(left, top, tile_size_x, tile_size_y)
    # 1) Fill entire tile with the given color
    pygame.draw.rect(surface, fg_color, rect)
    # 2) Draw the tile border
    pygame.draw.rect(surface, BORDER_COLOR, rect, width=BORDER_WIDTH)
    return rect

def draw_label_tile(surface, x, y, tile_size_x, tile_size_y, label, fg_color):
    """
    Draws a label-tile that fills the entire cell with 'fg_color',
    with a black (TEXT_COLOR) label in the center and a border around.
      - x: column index
      - y: row index
    """
    rect = draw_colored_tile(surface, x, y, tile_size_x, tile_size_y, fg_color)
    # Choose font size as half the smaller dimension
    font_size = int(min(tile_size_x, tile_size_y) * 0.5)
    font = pygame.font.SysFont(None, font_size)
    text_surf = font.render(label, True, TEXT_COLOR)
    text_rect = text_surf.get_rect(center=rect.center)
    surface.blit(text_surf, text_rect)
