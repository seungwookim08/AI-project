import GameUtilities
from BoardPiece import *

# Creates a dictionary that maps columns to the first empty spot in that column
def check_front(grid):
    return_dict = {}
    for i in range(8):
        column = grid[0:12, i]
        for k in range(12):
            if column[k] != 0:
                return_dict[i + 1] = 13 - k
                break
            return_dict[i + 1] = 1
    return return_dict


def get_recycleables(placed_pieces, front):
    recycleables = list()

    # This way, the function can be called in both recycle mode and normal mode, allows for same logic flow
    if len(placed_pieces) < 24:
        return recycleables

    current_grid = GameUtilities.list2grid(placed_pieces)
    for front_x, front_y in front.items():
        # Unfortunately, not very fast, but due to constant board size, complexity should be OK
        # Also, doesn't consider most recently placed piece as this is *not allowed*
        for piece_index, piece in enumerate(placed_pieces[:-1]):
            # Only consider pieces that are one place below the front
            if (front_x, front_y - 1) in [(piece.white_pos_x, piece.white_pos_y), (piece.red_pos_x, piece.red_pos_y)]:
                # Further consideration needed for horizontal pieces
                if piece.rot_type in [1, 3, 5, 7]:
                    # Make sure matching position is not of piece already considered
                    if (front_x is piece.white_pos_x and piece.white_pos_x < piece.red_pos_x) or\
                            (front_x is piece.red_pos_x and piece.red_pos_x < piece.white_pos_x):
                        # If the front isn't the same, this implies that another piece is sitting on top
                        if front[front_x] == front[front_x + 1]:
                            intermediate_grid = current_grid.copy()
                            intermediate_grid[12 - piece.red_pos_y, piece.red_pos_x - 1] = 0
                            intermediate_grid[12 - piece.white_pos_y, piece.white_pos_x - 1] = 0
                            recycleables.append((piece, intermediate_grid, piece_index))
                            break
                # Automatically allow any vertical pieces
                elif piece.rot_type in [2, 4, 6, 8]:
                    intermediate_grid = current_grid.copy()
                    intermediate_grid[12 - piece.red_pos_y, piece.red_pos_x - 1] = 0
                    intermediate_grid[12 - piece.white_pos_y, piece.white_pos_x - 1] = 0
                    recycleables.append((piece, intermediate_grid, piece_index))
                    break
    return recycleables
