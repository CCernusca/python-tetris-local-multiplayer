
import pygame as pg
from scripts.tetris import TetrisGame, COLORS

def display_game(display: pg.Surface, game: TetrisGame) -> None:
    tile_height, tile_width = game.board.shape
    px_width, px_height = display.get_size()
    width_tile = px_width // tile_width
    height_tile = px_height // tile_height
    display.fill((0, 0, 0))
    for y in range(tile_height):
        for x in range(tile_width):
            color = COLORS[game.board[y][x]]
            pg.draw.rect(display, color, (x * width_tile, y * height_tile, width_tile, height_tile))
    pg.display.update()
