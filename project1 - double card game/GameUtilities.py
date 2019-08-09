from string import ascii_lowercase
from string import ascii_uppercase
from BoardPiece import *
import Nodes
import numpy as np
import time


def isLegal(grid):
    rows = len(grid)
    cols = len(grid[0])
    for i in range(1,rows):
        for k in range(0,cols):
            if grid[i][k]==0 and grid[i-1][k]!=0:
                return False
    return True


def isOverlap(next_piece, placed_pieces):
    for piece in placed_pieces:
        if (next_piece.white_pos_x, next_piece.white_pos_y) in {(piece.white_pos_x, piece.white_pos_y), (piece.red_pos_x, piece.red_pos_y)} or \
                (next_piece.red_pos_x, next_piece.red_pos_y) in {(piece.white_pos_x, piece.white_pos_y), (piece.red_pos_x, piece.red_pos_y)}:
            return True
    return False


def check_continuous_element(row, value):
    count = 0
    for x in row:
        if x == value:
            count += 1
            if count >= 4:
                return True
        else:
            count = 0
    return False


# Faster method compared to check_winning method
def check_winning_fast(grid, placed_pieces):
    results = [0, 0, 0, 0]
    winning_flag = False

    if len(placed_pieces) is 0:
        return winning_flag, results

    last_piece = placed_pieces[-1]

    red_pos = (last_piece.red_pos_x, last_piece.red_pos_y)
    red_info = (red_pos, 1, 2)
    white_pos = (last_piece.white_pos_x, last_piece.white_pos_y)
    white_info = (white_pos, 3, 4)
    full_pos = red_pos if last_piece.rot_type < 5 else white_pos
    full_info = (full_pos, 1, 3)
    empty_pos = white_pos if last_piece.rot_type < 5 else red_pos
    empty_info = (empty_pos, 2, 4)

    potential_wins = [red_info, white_info, full_info, empty_info]

    directions = [
                     ((+0, -1), (+0, +1)),  # Vertical
                     ((-1, +0), (+1, +0)),  # Horizontal
                     ((+1, +1), (-1, -1)),  # Upper diagonal
                     ((-1, +1), (+1, -1)),  # Lower diagonal
                 ]

    result_index = 0
    for position, match_1, match_2 in potential_wins:

        for direction_1, direction_2 in directions:
            match_1_count = 0
            match_2_count = 0
            inc_pos1 = position
            inc_pos2 = position
            for step in range(0, 3):
                inc_pos1 = tuple(map(lambda x, y: x + y, inc_pos1, direction_1))
                inc_pos2 = tuple(map(lambda x, y: x + y, inc_pos2, direction_2))
                if 1 <= inc_pos1[0] <= 8 and 1 <= inc_pos1[1] <= 12:
                    if match_1_count is step and (grid[12 - inc_pos1[1], inc_pos1[0] - 1] in (match_1, match_2)):
                        match_1_count += 1
                if 1 <= inc_pos2[0] <= 8 and 1 <= inc_pos2[1] <= 12:
                    if match_2_count is step and (grid[12 - inc_pos2[1], inc_pos2[0] - 1] in (match_1, match_2)):
                        match_2_count += 1
            if (match_1_count + match_2_count) >= 3:
                winning_flag = True
                results[result_index] = 1
        result_index += 1
    return winning_flag, results

def check_winning(grid):
    '''
    :param grid: a 2d numpy array
    :return: (flag, [0,0,0,0])
    flag:
    the flag means whether some role wins, ture = someone wins, false means no one wins.
    eg: check_winning(grid)[0] return ture or false for some if-else statement in the future

    array[]:the array indicates the details you need.
    includes 0 0r 1 means lose or win.
    array[0]-array[3] represent, Red_Color,White_Color,Black_Dot,White_Dot, respectively.
    eg:check_winning(grid)[1] might return [1, 0, 1, 0] means someone wins, and Red_Color,Black_Dot win.

    eg:(True, [1, 0, 1, 0]) means someone wins, and Red_Color,Black_Dot win.
    )
    '''
    winning_flag = False
    #the third value is to check and record whether each item wins. 1 = win 0 = not win
    winning_conditions = {'Red_Color': [1, 2, 0],
                          'White_Color': [3, 4, 0],
                          'Black_Dot': [1, 3, 0],
                          'White_Dot': [2, 4, 0]}
    # TODO: Optimization, multi-threading
    # check each winning condition
    for key, item in winning_conditions.items():
        # change winning pair to -1
        replace_value = -1
        grid1 = np.where(grid == item[0], replace_value, grid)
        grid1 = np.where(grid1 == item[1], replace_value, grid1)

        # check horizontal and vertical
        for matrix in [grid1, np.transpose(grid1)]:
            for row in matrix:
                if check_continuous_element(row, value=replace_value):
                    # you can delete the print
                    # print("{} Won!".format(key))
                    winning_conditions[key][2] = 1
                    winning_flag = True
                # check diagonal and reverse diagonal
        for matrix in [grid1, np.fliplr(grid1)]:
            for k in range(-8, 5):
                if check_continuous_element(np.diag(matrix, k=k), value=replace_value):
                    # you can delete the print
                    # print("{} Won!".format(key))
                    winning_conditions[key][2] = 1
                    winning_flag = True

    results = [winning_conditions[key][2] for key in winning_conditions]
    return winning_flag, results


# Converts the list of placed board pieces into a grid to be used by legal move checks and winner check
def list2grid(placed_pieces, board_length=12, board_width=8):

    # Reset the grid every time. When we implement recycling, list2grid should just work as a result
    new_grid = np.zeros((board_length, board_width), dtype=int)
    for piece in placed_pieces:
        # index numbering is reversed on the grid for legal check
        # grid numbering scheme was matched from check_winning
        if piece.side is 1:
            new_grid[board_length - piece.red_pos_y, piece.red_pos_x - 1] = 1
            new_grid[board_length - piece.white_pos_y, piece.white_pos_x - 1] = 4
        else:
            new_grid[board_length - piece.red_pos_y, piece.red_pos_x - 1] = 2
            new_grid[board_length - piece.white_pos_y, piece.white_pos_x - 1] = 3
    return new_grid

########
def AI_entry(placed_pieces, moves_left, node_owner, recycle=False, trace_mode=False, i=1):
    start = time.time()
    # Dictionary simplifies conversion
    global alphabet2integer
    valid = False

    # We have to do something when trace_mode is on.

    if recycle:
        while not valid:
            # Prepare AI input
            MinMaxObj=Nodes.MinMaxNode(node_pieces=placed_pieces, node_command="root", moves_left=moves_left, node_owner=node_owner)
            text_input=MinMaxObj.minimax_depth()
            if trace_mode:
                MinMaxObj.trace(i)
            try:
                var_input = text_input.split()
                var_input[1], var_input[3], var_input[4], var_input[6] = int(var_input[1]), int(var_input[3]), int(
                    var_input[4]), int(var_input[6])
                var_input[0], var_input[2], var_input[5] = alphabet2integer[var_input[0]], alphabet2integer[
                    var_input[2]], alphabet2integer[var_input[5]]

                # recycling move to be in order. i.e. if D 10 D 9 1 D 9 => D 9 D 10 1 D 9
                if var_input[1] > var_input[3]:
                    old = text_input.split()
                    text_input = "{} {} {} {} {} {} {}".format(old[2], old[3], old[0], old[1], old[4], old[5], old[6])
                elif var_input[1] == var_input[3] and var_input[0] > var_input[2]:
                    old = text_input.split()
                    text_input = "{} {} {} {} {} {} {}".format(old[2], old[3], old[0], old[1], old[4], old[5], old[6])
            except:
                print("AI have entered invalid format of input. AI LOSE")
                exit()

            print("Recycle Input format: 'PosX PosY PosX PosY Type PosX PosY':{}".format(text_input))

            # Simplifies check later on
            if (var_input[0], var_input[1]) is (var_input[2], var_input[3]):
                print("AI move error: Invalid recycling coordinates. AI LOSE")
                valid = False
                exit()
            elif var_input[4] < 1 or var_input[4] > 8:
                print("AI move error: No such rotation.AI LOSE")
                valid = False
                exit()
            elif (var_input[4] in [1, 3, 5, 7] and (var_input[5] < 1 or var_input[5] >= 8 or var_input[6] > 12)) or (
                    var_input[4] in [2, 4, 6, 8] and (var_input[6] < 1 or var_input[6] >= 12 or var_input[5] > 8)):
                print("AI move error: You cannot have a block outside of the grid. AI LOSE")
                valid = False
                exit()

            next_piece = BoardPiece(pos_x=var_input[5], pos_y=var_input[6], rot_type=var_input[4])

            # Look for placed pieces that much recycle coordinates
            recycle_found = False
            recycle_index = -1
            for piece_index, piece in enumerate(placed_pieces):
                # Because we know explicitly (0, 1) != (2,3) from previous check, this check is sufficient
                if (var_input[0], var_input[1]) in {(piece.white_pos_x, piece.white_pos_y),
                                                    (piece.red_pos_x, piece.red_pos_y)} and \
                        (var_input[2], var_input[3]) in {(piece.white_pos_x, piece.white_pos_y),
                                                         (piece.red_pos_x, piece.red_pos_y)}:

                    if piece is placed_pieces[-1]:
                        print("AI move error: Cannot recycle most recently used piece. AI LOSE")
                        exit()
                    else:
                        recycle_found = True
                        recycle_index = piece_index

            # If a matching piece is found, we make sure the board is legal after removal and after placement
            if recycle_found:
                potential_pieces = placed_pieces.copy()
                old_piece = potential_pieces.pop(recycle_index)
                old_pieces = potential_pieces.copy()
                intermediate_grid = list2grid(potential_pieces)
                potential_pieces.append(next_piece)
                final_grid = list2grid(potential_pieces)

                if (next_piece.red_pos_x, next_piece.red_pos_y) == (old_piece.red_pos_x, old_piece.red_pos_y) and \
                        (next_piece.white_pos_x, next_piece.white_pos_y) == (
                        old_piece.white_pos_x, old_piece.white_pos_y) and \
                        (next_piece.side is old_piece.side and next_piece.angle is old_piece.angle):
                    print("AI move error: Cannot recycle a piece into exact same position. AI LOSE")
                    exit()
                elif isOverlap(next_piece, old_pieces):
                    print("AI move error: You cannot overlap the piece. AI LOSE")
                    exit()
                # Move is accepted if both checks are passed
                elif isLegal(intermediate_grid) and isLegal(final_grid):
                    end = time.time()
                    print("AI computational time: {}".format(end-start))
                    return potential_pieces, final_grid
                else:
                    print("AI move error: Resulting move is invalid. AI LOSE")
                    exit()
            else:
                print("AI move error: Could not find piece to recycle. AI LOSE")
                exit()
            valid = False
    else:
        while not valid:
            if moves_left > 21 and moves_left < 37:
                MinMaxObj=Nodes.MinMaxNode(node_pieces=placed_pieces, node_command="root", moves_left=moves_left, node_owner=node_owner, max_depth=4)
            else:
                MinMaxObj=Nodes.MinMaxNode(node_pieces=placed_pieces, node_command="root", moves_left=moves_left, node_owner=node_owner)
            text_input=MinMaxObj.minimax_depth()
            if trace_mode:
                MinMaxObj.trace(i)
            print("Input format: '0 Type PosX PosY':{}".format(text_input))

            # Acquire entry, split and convert (where necessary)
            try:
                var_input = text_input.split()
                var_input[1] = int(var_input[1])
                var_input[2] = alphabet2integer[var_input[2]]
                var_input[3] = int(var_input[3])
            except:
                print("AI move error: You have entered invalid format of input. AI LOSE")
                exit()
            if var_input[0] is not "0":
                print("AI move error: You are still in the regular move, AI LOSE")
            elif var_input[1] < 1 or var_input[1] > 8:
                print("AI move error: No such rotation.AI LOSE")
                valid = False
                exit()
            elif (var_input[1] in [1, 3, 5, 7] and (var_input[2] < 1 or var_input[2] >= 8 or var_input[3] > 12)) or (
                    var_input[1] in [2, 4, 6, 8] and (var_input[3] < 1 or var_input[3] >= 12 or var_input[2] > 8)):
                print("AI move error: You cannot have a block outside of the grid. AI LOSE")
                valid = False
                exit()

            # Note: Board pieces operate on a cartesian plane, (1, 1) is bottom left
            next_piece = BoardPiece(pos_x=var_input[2], pos_y=var_input[3], rot_type=var_input[1])

            if isOverlap(next_piece, placed_pieces):
                print("AI move error: Cannot overlap with another piece. AI LOSE")
                valid = False
                exit()
            else:
                placed_pieces.append(next_piece)
                new_grid = list2grid(placed_pieces)

                if isLegal(new_grid):
                    valid = True
                else:
                    valid = False
                    del placed_pieces[-1]
                    print("AI move error: Invalid input. AI LOSE")
                    exit()
        end = time.time()
        print("AI computational time: {}".format(end-start))            
        return placed_pieces, new_grid

###########
# the original manual_entry

# Min max function can be separated similarly
def manual_entry(placed_pieces, recycle=False, **kwargs):
    # Dictionary simplifies conversion
    global alphabet2integer
    valid = False

    if recycle:
        while not valid:
            # Prepare user input
            text_input = input("Recycle Input format: 'PosX PosY PosX PosY Type PosX PosY':")

            try:
                var_input = text_input.split()
                var_input[1], var_input[3], var_input[4], var_input[6] = int(var_input[1]), int(var_input[3]), int(
                    var_input[4]), int(var_input[6])
                var_input[0], var_input[2], var_input[5] = alphabet2integer[var_input[0]], alphabet2integer[
                    var_input[2]], alphabet2integer[var_input[5]]
            except:
                print("You have entered invalid format of input. Please try again!")
                continue

            # Simplifies check later on
            if (var_input[0], var_input[1]) is (var_input[2], var_input[3]):
                print("Invalid recycling coordinates")
                valid = False
                continue
            elif var_input[4] < 1 or var_input[4] > 8:
                print("No such rotation.")
                valid = False
                continue
            elif (var_input[4] in [1, 3, 5, 7] and (var_input[5] < 1 or var_input[5] >= 8 or var_input[6] > 12)) or (
                    var_input[4] in [2, 4, 6, 8] and (var_input[6] < 1 or var_input[6] >= 12 or var_input[5] > 8)):
                print("You cannot have a block outside of the grid")
                valid = False
                continue

            next_piece = BoardPiece(pos_x=var_input[5], pos_y=var_input[6], rot_type=var_input[4])

            # Look for placed pieces that much recycle coordinates
            recycle_found = False
            recycle_index = -1
            for piece_index, piece in enumerate(placed_pieces):
                # Because we know explicitly (0, 1) != (2,3) from previous check, this check is sufficient
                if (var_input[0], var_input[1]) in {(piece.white_pos_x, piece.white_pos_y),
                                                    (piece.red_pos_x, piece.red_pos_y)} and \
                        (var_input[2], var_input[3]) in {(piece.white_pos_x, piece.white_pos_y),
                                                         (piece.red_pos_x, piece.red_pos_y)}:

                    if piece is placed_pieces[-1]:
                        print("Cannot recycle most recently used piece.")
                    else:
                        recycle_found = True
                        recycle_index = piece_index

            # If a matching piece is found, we make sure the board is legal after removal and after placement
            if recycle_found:
                potential_pieces = placed_pieces.copy()
                old_piece = potential_pieces.pop(recycle_index)
                old_pieces = potential_pieces.copy()
                intermediate_grid = list2grid(potential_pieces)
                potential_pieces.append(next_piece)
                final_grid = list2grid(potential_pieces)

                if (next_piece.red_pos_x, next_piece.red_pos_y) == (old_piece.red_pos_x, old_piece.red_pos_y) and \
                        (next_piece.white_pos_x, next_piece.white_pos_y) == (
                old_piece.white_pos_x, old_piece.white_pos_y) and \
                        (next_piece.side is old_piece.side and next_piece.angle is old_piece.angle):
                    print("Cannot recycle a piece into exact same position")
                elif isOverlap(next_piece, old_pieces):
                    print("You cannot overlap the piece")
                # Move is accepted if both checks are passed
                elif isLegal(intermediate_grid) and isLegal(final_grid):
                    return potential_pieces, final_grid
                else:
                    print("Resulting move is invalid")
            else:
                print("Could not find piece to recycle")
            valid = False

    else:
        while not valid:
            text_input = input("Input format: '0 Type PosX PosY':")

            # Acquire entry, split and convert (where necessary)
            try:
                var_input = text_input.split()
                var_input[1] = int(var_input[1])
                var_input[2] = alphabet2integer[var_input[2]]
                var_input[3] = int(var_input[3])
            except:
                print("You have entered invalid format of input. Please try again!")
                continue
            if var_input[0] is not "0":
                print("You are still in the regular move, please start with number 0 to play with.")
            elif var_input[1] < 1 or var_input[1] > 8:
                print("No such rotation.")
                valid = False
                continue
            elif (var_input[1] in [1, 3, 5, 7] and (var_input[2] < 1 or var_input[2] >= 8 or var_input[3] > 12)) or (
                    var_input[1] in [2, 4, 6, 8] and (var_input[3] < 1 or var_input[3] >= 12 or var_input[2] > 8)):
                print("You cannot have a block outside of the grid")
                valid = False
                continue

            # Note: Board pieces operate on a cartesian plane, (1, 1) is bottom left
            next_piece = BoardPiece(pos_x=var_input[2], pos_y=var_input[3], rot_type=var_input[1])

            if isOverlap(next_piece, placed_pieces):
                print("Cannot overlap with another piece")
                valid = False
            else:
                placed_pieces.append(next_piece)
                new_grid = list2grid(placed_pieces)

                if isLegal(new_grid):
                    valid = True
                else:
                    valid = False
                    del placed_pieces[-1]
                    print("Invalid input")

        return placed_pieces, new_grid


# Global mapping via dictionary.
alphabet2integer = dict()
for index, letter in enumerate(ascii_lowercase):
    alphabet2integer[letter] = index + 1
for index, letter in enumerate(ascii_uppercase):
    alphabet2integer[letter] = index + 1
