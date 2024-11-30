
import pygame as pg
from scripts.tetris import TetrisGame, COLORS

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
            pg.draw.rect(display, color, (x * width_tile, y * height_tile, width_tile, height_tile))
            
            if show_ids:
                # Draw id
                text_surface = font.render(str(tile_id), True, (255, 255, 255))  # White text
                text_rect = text_surface.get_rect(center=(x * width_tile + width_tile // 2,
                                                        y * height_tile + height_tile // 2))
                display.blit(text_surface, text_rect)

    pg.display.update()
