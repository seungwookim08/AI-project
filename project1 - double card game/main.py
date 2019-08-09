from BoardGrid import *
from BoardPiece import *
from GameUtilities import *
import os


# "Controller" of players can be configured here via function name
entry_mode = {
    0: manual_entry,
    1: manual_entry
}


# Main loop, pretty self-explanatory
def __main__():
    cards_left = 24
    board_length = 12
    board_width = 8
    player_turn = 1
    game_over = False
    placed_pieces = list()
    trace_mode = False
    node_owner = None

    visual_grid = BoardGrid(1280, 720, board_width, board_length)
    local_player_turn = 0
    i = 1
    while os.path.isfile('./tracemm{}.txt'.format(i)):
        i += 1
    while True:
        trace = input("Do you wish to generate trace of minimax? (Y/N):")
        if trace.lower() == 'y':
            trace_mode = True
        # player_1 choice AI or human
        player1_choice = input("AI plays as the first player enter: 1, otherwise, enter anything (i.e. 0):")
        if player1_choice == "1":
            player1_choice = 1
            entry_mode = {
                1: AI_entry,
                0: manual_entry
            }
            print("Now AI plays first")
        else:
            entry_mode = {
                1: manual_entry,
                0: AI_entry
            }
            print("Now AI plays second")

        # player choice color is 0 and dot is 1
        player_choice = input('Player 1 will play colors(0) or dots(1)?')
        if player_choice.lower() in ("0", "colors"):
            player_choice = 0
            break
        elif player_choice.lower() in ("1", "dots"):
            player_choice = 1
            break
        else:
            print('You have entered wrong input! try colors or 0 or dots or 1')
    if player1_choice == 1:
        node_owner = "max" if player_choice == 0 else "min"
    else:
        node_owner = "min" if player_choice == 0 else "max"

    while not (game_over or player_turn > 40):
        local_player_turn = 1 if player_turn % 2 is 1 else 0
        
        print('====Turn {}===='.format(player_turn))
        print('player {}\'s turn'.format(1 if local_player_turn is 1 else 2))
        if cards_left <= 0:
            placed_pieces, grid = entry_mode[local_player_turn](placed_pieces, recycle=True, trace_mode=trace_mode,
                                                                moves_left=41-player_turn, node_owner=node_owner, i=i)
        else:
            placed_pieces, grid = entry_mode[local_player_turn](placed_pieces, recycle=False, trace_mode=trace_mode, 
                                                                moves_left=41-player_turn, node_owner=node_owner, i=i)

        game_over, winner_list = check_winning(grid)
        cards_left -= 1
        player_turn += 1
        visual_grid.refresh(placed_pieces)

    print("Game Over")
    if player_turn > 40:
        print('No one wins! it is a draw game!')
    elif (winner_list[0] + winner_list[1] > 0) and (winner_list[2] + winner_list[3] > 0):
        print('player {} won!'.format(1 if local_player_turn is 1 else 2))
    elif player_choice == 0 and (winner_list[0] == 1 or winner_list[1] == 1):
        print('player {} won! congratulation!'.format(1))
    elif player_choice == 1 and (winner_list[2] == 1 or winner_list[3] == 1):
        print('player {} won! congratulation!'.format(1))
    else:
        print('player {} won! congratulation!'.format(2))

    print(winner_list)
    input("PRESS ENTER TO END GAME")


if __name__ == "__main__":
    __main__()
