import GameUtilities
from GenerationUtilities import *
import multiprocessing
import math

class MinMaxNode:

    # max_depth = 3
    # Replace player_type since we know if the choice is color or dot with node_owner (if max, AI is color)
    player_type = None
    nodes_generated = 0
    nodes_evaluated = 0

    def __init__(self, node_pieces, node_command, parent_node=None, moves_left=None, node_grid=None, node_owner="max", max_depth = 3):
        self.parent_node = parent_node
        self.depth = max_depth
        if self.parent_node is None:
            MinMaxNode.nodes_evaluated = 0
            MinMaxNode.nodes_generated = 1
            self.node_owner = node_owner
            self.root_owner = self.node_owner
            self.moves_left = moves_left
            self.node_depth = 1
            self.node_command = "root"
        else:
            MinMaxNode.nodes_generated += 1
            self.moves_left = self.parent_node.moves_left - 1
            self.node_depth = self.parent_node.node_depth + 1
            self.node_command = node_command
            if self.parent_node.node_owner is "max":
                self.node_owner = "min"
            else:
                self.node_owner = "max"
            self.root_owner = self.parent_node.root_owner
        self.placed_pieces = node_pieces.copy()

        if node_grid is None:
            self.grid = GameUtilities.list2grid(self.placed_pieces)
        else:
            self.grid = node_grid

        self.heuristic_eval = 0
        self.children = list()

    def generate_children(self, recycleables):
        if len(recycleables) is 0:
            generation_front = check_front(self.grid)
            choices = list()
            for front_x, front_y in generation_front.items():
                # Vertical pieces are placeable everywhere but at the top
                if front_y < 12:
                    for rotation in range(2, 9, 2):
                        next_command = "0 " + str(rotation) + " " + GameUtilities.ascii_uppercase[front_x - 1] + " " + str(front_y)
                        next_piece = BoardPiece(pos_x=front_x, pos_y=front_y, rot_type=rotation)
                        choices.append((next_command, next_piece))
                    # Horizontal pieces are placeable only where the next front is level with current front
                    if front_x < 8 and front_y is generation_front[front_x + 1]:
                        for rotation in range(1, 9, 2):
                            next_command = "0 " + str(rotation) + " " + GameUtilities.ascii_uppercase[front_x - 1] + " " + str(front_y)
                            next_piece = BoardPiece(pos_x=front_x, pos_y=front_y, rot_type=rotation)
                            choices.append((next_command, next_piece))
            for command, piece in choices:
                child_placed_pieces = self.placed_pieces.copy()
                child_placed_pieces.append(piece)
                child_node = MinMaxNode(node_pieces=child_placed_pieces, node_command=command, parent_node=self, max_depth=self.depth)
                self.children.append(child_node)

        else:
            choices = list()
            for piece, intermediate_grid, piece_index in recycleables:
                generation_front = check_front(intermediate_grid)
                for front_x, front_y in generation_front.items():
                    # Vertical pieces are placeable everywhere but at the top
                    if front_y < 12:
                        for rotation in range(2, 9, 2):
                            # Recycled placement must either be in a new position, or in a new rotation
                            if (front_x, front_y) not in [(piece.red_pos_x, piece.red_pos_y), (piece.white_pos_x, piece.white_pos_y)] or \
                                    rotation is not piece.rot_type:
                                next_command = "" + GameUtilities.ascii_uppercase[piece.red_pos_x - 1] + " " + str(piece.red_pos_y) + " " + GameUtilities.ascii_uppercase[piece.white_pos_x - 1] + " " + str(piece.white_pos_y) + " " + str(rotation) + " " + GameUtilities.ascii_uppercase[front_x - 1] + " " + str(front_y)
                                next_piece = BoardPiece(pos_x=front_x, pos_y=front_y, rot_type=rotation)
                                choices.append((next_command, next_piece, piece_index))
                        # Horizontal pieces are placeable only where the next front is level with current front
                        if front_x < 8 and front_y is generation_front[front_x + 1]:
                            for rotation in range(1, 9, 2):
                                # Recycled placement must either be in a new position, or in a new rotation
                                if (front_x, front_y) not in [(piece.red_pos_x, piece.red_pos_y), (piece.white_pos_x, piece.white_pos_y)] or \
                                        rotation is not piece.rot_type:
                                    next_command = "" + GameUtilities.ascii_uppercase[piece.red_pos_x - 1] + " " + str(piece.red_pos_y) + " " + GameUtilities.ascii_uppercase[piece.white_pos_x - 1] + " " + str(piece.white_pos_y) + " " + str(rotation) + " " + GameUtilities.ascii_uppercase[front_x - 1] + " " + str(front_y)
                                    next_piece = BoardPiece(pos_x=front_x, pos_y=front_y, rot_type=rotation)
                                    choices.append((next_command, next_piece, piece_index))

            for command, piece, piece_index in choices:
                child_placed_pieces = self.placed_pieces.copy()
                child_placed_pieces.pop(piece_index)
                child_placed_pieces.append(piece)
                child_node = MinMaxNode(node_pieces=child_placed_pieces, node_command=command, parent_node=self, max_depth=self.depth)
                self.children.append(child_node)

    def heuristic(self, n=4):
        # This n should be changed in terms of power of n
        
        results = [0, 0, 0, 0]
        heuristic_results = []

        if len(self.placed_pieces) == 0:
            return
        last_piece = self.placed_pieces[-1]

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
            type_matches = []
            for direction_1, direction_2 in directions:
                match_1_heuristic = 0
                match_2_heuristic = 0
                match_1_result = 0
                match_2_result = 0

                inc_pos1 = position
                inc_pos2 = position
                for step in range(0, 3):
                    inc_pos1 = tuple(map(lambda x, y: x + y, inc_pos1, direction_1))
                    inc_pos2 = tuple(map(lambda x, y: x + y, inc_pos2, direction_2))
                    if 1 <= inc_pos1[0] <= 8 and 1 <= inc_pos1[1] <= 12:
                        if match_1_result is step:
                            # Only currently placed pieces matter for winning checks
                            if self.grid[12 - inc_pos1[1], inc_pos1[0] - 1] in (match_1, match_2):
                                match_1_result += 1
                                match_1_heuristic += 1
                            # An open position for future placement matters for heuristic
                            elif self.grid[12 - inc_pos1[1], inc_pos1[0] - 1] == 0:
                                if (inc_pos1[1] == 12) or\
                                        (inc_pos1[1] <= 11 and self.grid[11 - inc_pos1[1], inc_pos1[0] - 1] != 0) or \
                                        (inc_pos1[1] <= 10 <= 8 and self.grid[10 - inc_pos1[1], inc_pos1[0] - 1] != 0):
                                    match_1_heuristic += 1

                    if 1 <= inc_pos2[0] <= 8 and 1 <= inc_pos2[1] <= 12:
                        if match_2_result is step:
                            if self.grid[12 - inc_pos2[1], inc_pos2[0] - 1] in (match_1, match_2):
                                match_2_result += 1
                                match_2_heuristic += 1
                            elif self.grid[12 - inc_pos2[1], inc_pos2[0] - 1] == 0:
                                # Special case dealing with vertical
                                if direction_1 == (+0, -1):
                                    match_2_heuristic += 1

                                elif (inc_pos2[1] == 12) or\
                                        (inc_pos2[1] <= 11 and self.grid[11 - inc_pos2[1], inc_pos2[0] - 1] != 0) or \
                                        (inc_pos2[1] <= 10 <= 8 and self.grid[10 - inc_pos2[1], inc_pos2[0] - 1] != 0):
                                    match_2_heuristic += 1
                if match_1_result + match_2_result >= 3:
                    results[result_index] = 1
                type_matches.append(match_1_heuristic + match_2_heuristic)
            heuristic_results.append(type_matches)
            result_index += 1

        # No winning results
        if all(result == 0 for result in results):
            # Designed to give the competitor an "advantage"
            if self.root_owner == "max":
                for index, heuristic_result in enumerate(heuristic_results):
                    for count in heuristic_result:
                        if index < 2:
                            self.heuristic_eval += pow(count + 1, n)
                        else:
                            self.heuristic_eval -= pow(count + 1, n) + 100
            else:
                for index, heuristic_result in enumerate(heuristic_results):
                    for count in heuristic_result:
                        if index < 2:
                            self.heuristic_eval += pow(count + 1, n) + 100
                        else:
                            self.heuristic_eval -= pow(count + 1, n)

            return False
        else:
            # parent node made the choice to get to this node, therefore ties go to parent node
            if self.parent_node.node_owner is "max":
                self.heuristic_eval = float("inf") if (results[0] + results[1] > 0) else float("-inf")
            else:
                self.heuristic_eval = float("-inf") if (results[2] + results[3] > 0) else float("inf")
            return True

    def minimax_depth(self):
        # First, check if this node is a winning/losing node
        game_over = self.heuristic()

        # Skip heuristic if game ends in tie before reaching max depth
        if not game_over and self.moves_left is 0:
            # Cut search early for a tie, and skip needless heuristic
            self.heuristic_eval = 0

        # Short circuit remaining if logic for game over or max depth
        elif game_over or self.node_depth is self.depth:
            return

        else:
            #############################################################################################
            # Generate children functionality moved into minimax() function to save function call costs #
            #############################################################################################
            node_front = check_front(self.grid)
            recycleables = get_recycleables(self.placed_pieces, node_front)
            if len(recycleables) is 0:
                generation_front = check_front(self.grid)
                choices = list()
                for front_x, front_y in generation_front.items():
                    # Vertical pieces are placeable everywhere but at the top
                    if front_y < 12:
                        for rotation in range(2, 9, 2):
                            next_command = "0 " + str(rotation) + " " + GameUtilities.ascii_uppercase[
                                front_x - 1] + " " + str(front_y)
                            next_piece = BoardPiece(pos_x=front_x, pos_y=front_y, rot_type=rotation)
                            choices.append((next_command, next_piece))
                        # Horizontal pieces are placeable only where the next front is level with current front
                        if front_x < 8 and front_y is generation_front[front_x + 1]:
                            for rotation in range(1, 9, 2):
                                next_command = "0 " + str(rotation) + " " + GameUtilities.ascii_uppercase[
                                    front_x - 1] + " " + str(front_y)
                                next_piece = BoardPiece(pos_x=front_x, pos_y=front_y, rot_type=rotation)
                                choices.append((next_command, next_piece))
                for command, piece in choices:
                    child_placed_pieces = self.placed_pieces.copy()
                    child_placed_pieces.append(piece)
                    child_node = MinMaxNode(node_pieces=child_placed_pieces, node_command=command, parent_node=self, max_depth=self.depth)
                    self.children.append(child_node)

            else:
                choices = list()
                for piece, intermediate_grid, piece_index in recycleables:
                    generation_front = check_front(intermediate_grid)
                    for front_x, front_y in generation_front.items():
                        # Vertical pieces are placeable everywhere but at the top
                        if front_y < 12:
                            for rotation in range(2, 9, 2):
                                # Recycled placement must either be in a new position, or in a new rotation
                                if (front_x, front_y) not in [(piece.red_pos_x, piece.red_pos_y),
                                                              (piece.white_pos_x, piece.white_pos_y)] or \
                                        rotation is not piece.rot_type:
                                    next_command = "" + GameUtilities.ascii_uppercase[piece.red_pos_x - 1] + " " + str(
                                        piece.red_pos_y) + " " + GameUtilities.ascii_uppercase[
                                                       piece.white_pos_x - 1] + " " + str(
                                        piece.white_pos_y) + " " + str(rotation) + " " + GameUtilities.ascii_uppercase[
                                                       front_x - 1] + " " + str(front_y)
                                    next_piece = BoardPiece(pos_x=front_x, pos_y=front_y, rot_type=rotation)
                                    choices.append((next_command, next_piece, piece_index))
                            # Horizontal pieces are placeable only where the next front is level with current front
                            if front_x < 8 and front_y is generation_front[front_x + 1]:
                                for rotation in range(1, 9, 2):
                                    # Recycled placement must either be in a new position, or in a new rotation
                                    if (front_x, front_y) not in [(piece.red_pos_x, piece.red_pos_y),
                                                                  (piece.white_pos_x, piece.white_pos_y)] or \
                                            rotation is not piece.rot_type:
                                        next_command = "" + GameUtilities.ascii_uppercase[
                                            piece.red_pos_x - 1] + " " + str(piece.red_pos_y) + " " + \
                                                       GameUtilities.ascii_uppercase[piece.white_pos_x - 1] + " " + str(
                                            piece.white_pos_y) + " " + str(rotation) + " " + \
                                                       GameUtilities.ascii_uppercase[front_x - 1] + " " + str(front_y)
                                        next_piece = BoardPiece(pos_x=front_x, pos_y=front_y, rot_type=rotation)
                                        choices.append((next_command, next_piece, piece_index))

                for command, piece, piece_index in choices:
                    child_placed_pieces = self.placed_pieces.copy()
                    child_placed_pieces.pop(piece_index)
                    child_placed_pieces.append(piece)
                    child_node = MinMaxNode(node_pieces=child_placed_pieces, node_command=command, parent_node=self, max_depth=self.depth)
                    self.children.append(child_node)
            ###########################################################################################################
            # End of generate_children code                                                                           #
            ###########################################################################################################
            node_owner_choice = ""

            # Root spools up sub-processes to speedup minimax
            if self.node_command is "root":
                num_procs = 8
                processes = multiprocessing.Pool(processes=num_procs)
                num_children = len(self.children)
                child_chunk_size = math.ceil(num_children / num_procs)
                partitioned_children = []

                # Partition the children for each sub-process
                for process in range(num_procs):
                    slice_start = process*child_chunk_size

                    # Accounts for num_children dividing perfectly into num_procs
                    if slice_start >= num_children:
                        continue
                    elif slice_start < num_children:
                        slice_end = slice_start + child_chunk_size
                    # Accounts for final case where num_children does *not* divide perfectly by num_procs
                    elif slice_start > num_children:
                        slice_end = slice_start + (num_children % child_chunk_size)

                    partitioned_children.append(self.children[slice_start:slice_end])

                # Blocking call, waits for all children processes to complete
                parallel_choices = processes.map(parallel_minimax, partitioned_children)
                processes.close()

                # Once all child processes are finished,
                for index, (heuristic_eval, command) in enumerate(parallel_choices):
                    if index is 0:
                        self.heuristic_eval = heuristic_eval
                        node_owner_choice = command
                    else:
                        if self.node_owner == "max" and heuristic_eval >= self.heuristic_eval:
                            self.heuristic_eval = heuristic_eval
                            node_owner_choice = command
                        elif self.node_owner == "min" and heuristic_eval <= self.heuristic_eval:
                            self.heuristic_eval = heuristic_eval
                            node_owner_choice = command

            # Non-root runs remaining computation on local thread
            else:
                for index, child in enumerate(self.children):
                    child.minimax_depth()
                    if index is 0:
                        self.heuristic_eval = child.heuristic_eval
                        node_owner_choice = child.node_command
                    else:
                        if self.node_owner == "max" and child.heuristic_eval >= self.heuristic_eval:
                            self.heuristic_eval = child.heuristic_eval
                            node_owner_choice = child.node_command
                        elif self.node_owner == "min" and child.heuristic_eval <= self.heuristic_eval:
                            self.heuristic_eval = child.heuristic_eval
                            node_owner_choice = child.node_command
            return node_owner_choice

    def trace(self, i=1):
        trace_file = open("tracemm{}.txt".format(i), "a+")
        trace_file.write("%d\n" % MinMaxNode.nodes_evaluated)
        trace_file.write("%.1f\n" % self.heuristic_eval)
        trace_file.write("\n")

        for child in self.children:
            trace_file.write("%.1f\n" % child.heuristic_eval)
        trace_file.write("\n")


def parallel_minimax(child_nodes):
    process_best = None
    process_choice = None
    root_owner = None

    if child_nodes[0].node_owner == "min":
        process_best = float("-inf")
        root_owner = "max"
    else:
        process_best = float("inf")
        root_owner = "min"

    for index, child in enumerate(child_nodes):
        child.minimax_depth()
        if index is 0:
            process_best = child.heuristic_eval
            process_choice = child.node_command
        else:
            if child.heuristic_eval >= process_best and root_owner == "max":
                process_best = child.heuristic_eval
                process_choice = child.node_command
            elif child.heuristic_eval <= process_best and root_owner == "min":
                process_best = child.heuristic_eval
                process_choice = child.node_command
        child = None
    return process_best, process_choice


def __main__():
    placed_pieces = list()

    # placed_pieces.append(BoardPiece(1,1,1))
    # placed_pieces.append(BoardPiece(3,1,1))
    # placed_pieces.append(BoardPiece(5,2,1))
    # placed_pieces.append(BoardPiece(7,2,1))

    print(GameUtilities.list2grid(placed_pieces))

    root_command = "root"

    test_root = MinMaxNode(node_pieces=placed_pieces, node_command=root_command, moves_left=60-len(placed_pieces), node_owner="max")
    choice = test_root.minimax_depth()
    print('choices', choice)
    print('node generated', test_root.nodes_generated)
    test_root.trace()

    print('node evaluated', test_root.nodes_evaluated)
    print('node heuristic eval', test_root.heuristic_eval)


if __name__ == "__main__":
    __main__()