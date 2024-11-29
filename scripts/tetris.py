
import numpy as np

COLORS = [
    (0, 0, 0),
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255)
]

PIECES = [
    [[0, 0, 0, 0], 
     [0, 1, 1, 0], 
     [0, 1, 1, 0], 
     [0, 0, 0, 0]],
]

class TetrisGame:

    def __init__(self) -> None:
        self.board = np.zeros((20, 10), dtype=np.uint8)
        self.current_piece_id = None
        self.current_piece_rotation = 0
        self.piece_colors = {}
    
    def check_overlap(self, piece, offset):
        row_offset, col_offset = offset
        small_rows, small_cols = piece.shape
        big_rows, big_cols = self.board.shape
        
        # Ensure the smaller mask fits within the larger mask at the given offset
        if (row_offset < 0 or col_offset < 0 or 
            row_offset + small_rows > big_rows or 
            col_offset + small_cols > big_cols):
            return False  # Out of bounds

        # Extract the region of the big mask that corresponds to the small mask
        board_region = self.board[row_offset:row_offset + small_rows, col_offset:col_offset + small_cols]
        
        # Check for overlap
        print(board_region, piece)
        return np.any(np.bitwise_and(board_region, piece))
    
    def spawn_piece(self):
        piece_id = 0
        while piece_id in self.board:
            piece_id += 1
        piece = np.asarray(PIECES[np.random.randint(0, len(PIECES))])
        spawn_x = 0
        while True:
            if spawn_x > self.board.shape[1] - piece.shape[1]:
                raise Exception("Game over")
            if not self.check_overlap(piece, (0, spawn_x)):
                break
            spawn_x += 1
            
        self.board[0:piece.shape[0], spawn_x:spawn_x + piece.shape[1]][self.board[0:piece.shape[0], spawn_x:spawn_x + piece.shape[1]] == 0] = piece[self.board[0:piece.shape[0], spawn_x:spawn_x + piece.shape[1]] == 0]
        self.current_piece_id = piece_id

    def drop_piece(self, piece_id):
        ...
    
    def update(self):
        ...
