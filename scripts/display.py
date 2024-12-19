
import pygame as pg
import numpy as np
from scripts.tetris import COLORS

SPRITES_PATH = "assets/sprites/"

class GameDisplay:

    def __init__(self, game_count: int = 1, board_size: tuple[int, int] = (20, 12)) -> None:
        self.game_displays = [pg.Surface((board_size[1] * 20, board_size[0] * 20)) for _ in range(game_count)]
        self.debug = False
        self.buffer_pixels = 20

    def init_sprites(self) -> None:
        if self.debug: print("Initializing sprites")
                    
        self.raw_tile = pg.image.load(SPRITES_PATH + "tile.png").convert()

        def color_sprite(sprite: pg.Surface, color: list[int]) -> pg.Surface:
            colorized_sprite = sprite.copy()
            colorized_sprite.fill(color, special_flags=pg.BLEND_MULT)
            return colorized_sprite

        self.colored_tiles = {
            color: color_sprite(self.raw_tile, color) for color in COLORS
        }
        self.colored_tiles[(0, 0, 0)] = color_sprite(self.raw_tile, (0, 0, 0))

    def display_game(self, display_index: int, game_board: np.ndarray) -> None:
        if self.debug: print(f"Displaying game {display_index}")

        tile_height, tile_width = game_board.shape
        px_width, px_height = self.game_displays[display_index].get_size()
        width_tile = px_width // tile_width
        height_tile = px_height // tile_height
        self.game_displays[display_index].fill((0, 0, 0))

        # Initialize font for rendering text
        font = pg.font.Font(None, min(width_tile, height_tile) // 2)  # Adjust font size based on tile size

        for y in range(tile_height):
            for x in range(tile_width):
                tile_id = game_board[y][x]
                
                # Draw the tile
                color = COLORS[(tile_id - 1) % len(COLORS)] if tile_id != 0 else (0, 0, 0)
                self.game_displays[display_index].blit(pg.transform.scale(self.colored_tiles[color], (width_tile, height_tile)), pg.Rect((x * width_tile, y * height_tile, width_tile, height_tile)))
                
                if self.debug:
                    # Draw id
                    text_surface = font.render(str(tile_id), True, (255, 255, 255))  # White text
                    text_rect = text_surface.get_rect(center=(x * width_tile + width_tile // 2,
                                                            y * height_tile + height_tile // 2))
                    self.game_displays[display_index].blit(text_surface, text_rect)

        pg.display.update()
    
    def update_screen(self, surface: pg.Surface) -> None:
        if self.debug: print("Updating screen")

        display_width = (surface.get_width() - (len(self.game_displays) + 1) * self.buffer_pixels) // len(self.game_displays)
        display_height = display_width * self.game_displays[0].get_size()[1] // self.game_displays[0].get_size()[0]
        if display_height > surface.get_height() - self.buffer_pixels * 2:
            display_height = surface.get_height() - self.buffer_pixels * 2
            display_width = display_height * self.game_displays[0].get_size()[0] // self.game_displays[0].get_size()[1]

        surface.fill((50, 50, 50))

        for i, display in enumerate(self.game_displays):
            partition = (surface.get_width() - self.buffer_pixels) / len(self.game_displays)
            display_pos = (self.buffer_pixels // 2 + i * partition + partition // 2 - display_width // 2, surface.get_height() // 2 - display_height // 2)
            surface.blit(pg.transform.scale(display, (display_width, display_height)), display_pos)

        pg.display.update()
