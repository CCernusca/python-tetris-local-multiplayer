
import numpy as np

COLORS = [
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
]

PIECES = [
    [[0, 0, 0, 0], 
     [0, 1, 1, 0], 
     [0, 1, 1, 0], 
     [0, 0, 0, 0]],
    [[0, 0, 0, 0], 
     [1, 1, 1, 1], 
     [0, 0, 0, 0], 
     [0, 0, 0, 0]],
    [[0, 0, 0, 0], 
     [1, 1, 1, 0], 
     [0, 0, 1, 0], 
     [0, 0, 0, 0]],
    [[0, 0, 0, 0], 
     [0, 1, 1, 1], 
     [0, 1, 0, 0], 
     [0, 0, 0, 0]],
]

BOARD_SIZE = (20, 12)

class TetrisGame:
    """
    Tetris Game Class

    Terminology: piece is a tetris form, which behaves as a connected body
                 tile is a single block of a piece
    """

    def __init__(self, debug: bool = False) -> None:
        self.update_frequency = 1

        self.board = np.zeros(BOARD_SIZE, dtype=np.uint8)
        self.current_piece_id = None
        self.current_piece_rotation = 0
        self.pieces = {}
        self.debug = debug
        self.hard_drop = False
        self.hard_drop_factor = 5
        self.time_since_last_update = 0
        self.stopped = False
    
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
        board_region = self.board[row_offset:row_offset + small_rows, col_offset:col_offset + small_cols] > 0
        
        # Check for overlap
        return np.any(np.bitwise_and(board_region, piece))
    
    def spawn_piece(self):
        piece_id = 1
        while piece_id in self.pieces:
            piece_id += 1
        piece = np.asarray(PIECES[np.random.randint(0, len(PIECES))])
        spawn_positions = [x for x in range(self.board.shape[1] - piece.shape[1] + 1)]
        np.random.shuffle(spawn_positions)
        while True:
            if len(spawn_positions) < 1:
                raise Exception("Game over")
            spawn_x = spawn_positions.pop()
            if not self.check_overlap(piece, (0, spawn_x)):
                break
            
        self.board[0:piece.shape[0], spawn_x:spawn_x + piece.shape[1]][self.board[0:piece.shape[0], spawn_x:spawn_x + piece.shape[1]] == 0] = piece[self.board[0:piece.shape[0], spawn_x:spawn_x + piece.shape[1]] == 0] * piece_id
        self.current_piece_id = piece_id
        self.current_piece_rotation = 0
        self.pieces[piece_id] = {"color": COLORS[np.random.randint(0, len(COLORS))], "position": np.array([0, spawn_x]), "piece": piece}
    
    def get_piece(self, piece_id: int):
        return list(zip(*np.where(self.board == piece_id)))
    
    def is_airborne(self, piece_id: int):
        return all(pos[0] < len(self.board) - 1 and (self.board[pos[0] + 1][pos[1]] == 0 or self.board[pos[0] + 1][pos[1]] == piece_id) for pos in self.get_piece(piece_id))
    
    def check_collisions_move(self, piece_id: int, movement: tuple[int, int]):
        return [pos for pos in self.get_piece(piece_id) if not (0 <= pos[0] + movement[0] < self.board.shape[0] and 0 <= pos[1] + movement[1] < self.board.shape[1] and (self.board[pos[0] + movement[0]][pos[1] + movement[1]] == 0 or self.board[pos[0] + movement[0]][pos[1] + movement[1]] == piece_id))]
    
    def check_collisions_rotate(self, piece_id: int, rotation: int):
        piece_pos = self.pieces[piece_id]["position"]
        board_area = self.board[piece_pos[0]:piece_pos[0] + self.pieces[piece_id]["piece"].shape[0], piece_pos[1]:piece_pos[1] + self.pieces[piece_id]["piece"].shape[1]]
        rotated_piece = np.rot90(board_area == piece_id, rotation % 4)
        return [pos for pos in [p + piece_pos for p in list(zip(*np.where(rotated_piece > 0)))] if not (0 <= pos[0] < self.board.shape[0] and 0 <= pos[1] < self.board.shape[1] and (self.board[pos[0]][pos[1]] == 0 or self.board[pos[0]][pos[1]] == piece_id))]

    def move_piece_x(self, piece_id: int, movement: int):
        positions = self.get_piece(piece_id)
        for pos in sorted(positions, key=lambda pos: pos[1], reverse=movement > 0):
            self.board[pos[0]][pos[1]] = 0
            self.board[pos[0]][pos[1] + movement] = piece_id
            
    def move_piece_y(self, piece_id: int, movement: int):
        positions = self.get_piece(piece_id)
        for pos in sorted(positions, key=lambda pos: pos[0], reverse=movement > 0):
            self.board[pos[0]][pos[1]] = 0
            self.board[pos[0] + movement][pos[1]] = piece_id

    def move_piece(self, piece_id: int, movement: tuple[int, int]) -> list[tuple[int, int]]:
        collisions = self.check_collisions_move(piece_id, movement)
        if self.debug: print(f"Moving piece {piece_id} by {movement} -> Collisions: {collisions}")
        if len(collisions) == 0:
            self.move_piece_y(piece_id, movement[0])
            self.move_piece_x(piece_id, movement[1])
            self.pieces[piece_id]["position"] += movement
        return collisions

    def drop_piece(self, piece_id: int):
        movement = 1
        while self.move_piece(piece_id, (movement, 0)) != [] and movement > 0:
            movement -= 1
    
    def rotate_piece(self, piece_id: int, rotation: int) -> list[tuple[int, int]]:
        collisions = self.check_collisions_rotate(piece_id, rotation)
        if self.debug: print(f"Rotating piece {piece_id} by {rotation} -> Collisions: {collisions}")
        if len(collisions) == 0:
            piece_pos = self.pieces[piece_id]["position"]
            board_area = self.board[piece_pos[0]:piece_pos[0] + self.pieces[piece_id]["piece"].shape[0], piece_pos[1]:piece_pos[1] + self.pieces[piece_id]["piece"].shape[1]]
            rotated_piece = np.rot90(board_area == piece_id, rotation % 4)
            self.board[piece_pos[0]:piece_pos[0] + rotated_piece.shape[0], piece_pos[1]:piece_pos[1] + rotated_piece.shape[1]][np.where(self.board[piece_pos[0]:piece_pos[0] + rotated_piece.shape[0], piece_pos[1]:piece_pos[1] + rotated_piece.shape[1]] == piece_id)] = 0
            self.board[piece_pos[0]:piece_pos[0] + rotated_piece.shape[0], piece_pos[1]:piece_pos[1] + rotated_piece.shape[1]][np.where(rotated_piece > 0)] = piece_id
        return collisions
    
    def check_full_row(self, row: int):
        return all(self.board[row, :] != 0) and not any([self.is_airborne(piece_id) for piece_id in self.board[row, :].tolist()])

    def remove_full_rows(self):
        for row in range(len(self.board)):
            if self.check_full_row(row):
                pieces = self.board[row, :].tolist()
                if self.debug: print(f"Removing full row {row}")
                self.board[row, :] = 0
                for piece_id in pieces:
                    self.redefine_piece(piece_id)
    
    def get_connected_areas(self, tile_positions):
        # Directions for 4-connected grid (N, E, S, W)
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        
        # Convert tile positions to a set for quick lookup
        tile_set = set(tile_positions)
        
        # To track visited tiles
        visited = set()
        
        # Store the connected areas
        connected_areas = []
        
        def flood_fill(start_tile):
            # Use a stack for depth-first search (can also use a queue for breadth-first)
            stack = [start_tile]
            connected_area = []
            while stack:
                tile = stack.pop()
                if tile in visited:
                    continue
                visited.add(tile)
                connected_area.append(tile)
                # Check all 4 neighbors
                for dx, dy in directions:
                    neighbor = (tile[0] + dx, tile[1] + dy)
                    if neighbor in tile_set and neighbor not in visited:
                        stack.append(neighbor)
            return connected_area
        
        # Main logic
        for tile in tile_positions:
            if tile not in visited:
                # Find a connected area starting from this tile
                connected_area = flood_fill(tile)
                connected_areas.append(connected_area)
        
        return connected_areas

    def redefine_piece(self, piece_id: int):
        if piece_id in self.pieces:
            positions = self.get_piece(piece_id)
            connected_areas = self.get_connected_areas(positions)
            area_id = piece_id
            piece = self.pieces.pop(piece_id)
            for area in connected_areas:
                while area_id in self.pieces:
                    area_id += 1
                for pos in area:
                    self.board[pos[0]][pos[1]] = area_id
                self.pieces[area_id] = {"piece": piece["piece"], "color": piece["color"], "position": piece["position"]}
        
    def start(self):
        if self.current_piece_id is None:
            self.spawn_piece()
        else:
            print("Game already started")

    def update(self, dt: float):
        if self.stopped: return
        self.time_since_last_update += dt
        if self.time_since_last_update > 1 / (self.update_frequency * (self.hard_drop_factor if self.hard_drop else 1)):
            self.time_since_last_update = 0
            if self.current_piece_id is not None and self.debug: print(f"Current piece {self.current_piece_id} at {self.pieces[self.current_piece_id]['position']}")
            for piece_id in self.pieces:
                self.drop_piece(piece_id)
            if self.check_collisions_move(self.current_piece_id, (1, 0)):
                self.spawn_piece()
            
            self.remove_full_rows()
    
    def stop(self):
        if self.debug: print("Game stopped")
        self.stopped = True
    
    def resume(self):
        if self.debug: print("Game resumed")
        self.stopped = False
    
    def change_update_frequency(self, factor: int):
        if self.debug: print(f"Update frequency changed by {factor} to {self.update_frequency * factor}")
        self.update_frequency *= factor
