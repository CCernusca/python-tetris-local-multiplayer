
import numpy as np

COLORS = [
    (0, 0, 0),
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255)
]

class TetrisGame:

    def __init__(self) -> None:
        self.board = np.zeros((20, 10))
        self.current_piece = None
        self.current_piece_x = 0
        self.current_piece_y = 0
        self.current_piece_rotation = 0
        self.current_piece_color = 0
    
    def update(self):
        ...
