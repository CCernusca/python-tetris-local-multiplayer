
import pygame as pg
from scripts.tetris import TetrisGame, COLORS

SPRITES_PATH = "assets/sprites/"

pg.init()
pg.display.set_mode((0, 0))
            
raw_tile = pg.image.load(SPRITES_PATH + "tile.png").convert()

def color_sprite(sprite: pg.Surface, color: list[int]) -> pg.Surface:
    colorized_sprite = sprite.copy()
    colorized_sprite.fill(color, special_flags=pg.BLEND_MULT)
    return colorized_sprite

colored_tiles = {
    color: color_sprite(raw_tile, color) for color in COLORS
}
colored_tiles[(0, 0, 0)] = color_sprite(raw_tile, (0, 0, 0))

pg.quit()

def display_game(display: pg.Surface, game: TetrisGame, show_ids: bool = False) -> None:
    tile_height, tile_width = game.board.shape
    px_width, px_height = display.get_size()
    width_tile = px_width // tile_width
    height_tile = px_height // tile_height
    display.fill((0, 0, 0))

    # Initialize font for rendering text
    font = pg.font.Font(None, min(width_tile, height_tile) // 2)  # Adjust font size based on tile size

    for y in range(tile_height):
        for x in range(tile_width):
            tile_id = game.board[y][x]
            
            # Draw the tile
            color = game.pieces[tile_id]["color"] if tile_id > 0 else (0, 0, 0)
            display.blit(pg.transform.scale(colored_tiles[color], (width_tile, height_tile)), pg.Rect((x * width_tile, y * height_tile, width_tile, height_tile)))
            
            if show_ids:
                # Draw id
                text_surface = font.render(str(tile_id), True, (255, 255, 255))  # White text
                text_rect = text_surface.get_rect(center=(x * width_tile + width_tile // 2,
                                                        y * height_tile + height_tile // 2))
                display.blit(text_surface, text_rect)

    pg.display.update()
