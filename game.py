from objects import Board, ChessPiece, King, Horse, Bishop, Queen, Rook, Pawn, Player
from engine import Engine
#create a board and players
board = Board()
engine = Engine(board)
player1 = Player('w', 100)
player2 = Player('b', 100)

while True:
    human_player = input("Enter your color (w/b): ")
    if human_player in ['w', 'b']:
        ai_player = 'b' if human_player == 'w' else 'w'
        break

def main():

    print_board(board, player1, player2)

    while not board.is_end_game():
        turn = color_turn(board, player1, player2)
        #get the move and move the piece
        capture_piece = get_move(turn, board)
        #given player 1 is the maximising and player 2 is the minimising
        odds = difference(player1, player2, capture_piece)
        print_board(board, player1, player2)

    winner = board.winner()
    who_won = {-1: "black", 1: "white", 0: "stalemate"}
    print(who_won[winner])


def difference(player1, player2, capture_piece):
    if capture_piece is not None:
        you = player1 if capture_piece.color != player1.color else player2
        opp = player2 if capture_piece.color != player1.color else player1

        you.captured_pieces.append(capture_piece)
        opp.weight -= capture_piece.weight

    different = player1.weight - player2.weight
    print(f'difference: {different}')
    return different

#an undo test function NOT IN USE

"""
undo_mode = input("wld you like undo mode? if yes (y/n) ").lower()
        if undo_mode == 'y':
            start_undo_mode(board)
            
def start_undo_mode(board):
    while True:
        undo = input(f'{board.turn_count} undo/do/quit? ')
        if undo == "undo":
            if board.undo_move():
                print('move undoed')
                print_board(board, player1, player2)
            else:
                print('end reached')
        elif undo == "do":
            if board.redo_move():
                print('moved baord')
                print_board(board, player1, player2)

            else:
                print('end_reached')
        elif undo == "quit":
            break
        else:
            print("try again")
"""
        
#move function 
def get_move(player_turn, board):
    while True:
        print(f'turn: {player_turn}')
        if player_turn.color == human_player:
        #get the positio to move from and to
            start_row = input("Enter the start row: ")
            start_col = input("Enter the start col: ")
            end_row = input("Enter the end row: ")
            end_col = input("Enter the end col: ")
            print('\n')
            if start_row.isdigit() and start_col.isdigit() and end_row.isdigit() and end_col.isdigit():
                start_position = (int(start_row), int(start_col))
                end_position = (int(end_row), int(end_col))

                #get the piece
                chesspiece = board.position_dictionary.get(start_position, None)
                end_capture = board.position_dictionary.get(end_position, None)

                #check if its enpessant capture
                if isinstance(chesspiece, Pawn) and board.enpessant_tracker is not None:
                    if end_position == board.enpessant_tracker:
                        enpessant_row = board.enpessant_tracker[0] - 1 if chesspiece.color == 'w' else board.enpessant_tracker[0] + 1
                        capture_position = (enpessant_row, end_position[1])
                        end_capture = board.position_dictionary.get(capture_position, None)

                if chesspiece is not None:
                    if chesspiece.color == player_turn.color: 
                        #check if its pawn
                        if isinstance(chesspiece, Pawn) and chesspiece.reached_promotion_row(end_position) and chesspiece.validate_move(end_position, board):
                            while True:
                                piece_change = input("Enter your piece to change to: ").lower()
                                if piece_change in ["horse", "rook", "queen", "bishop"]:
                                    break
                                else:
                                    print("invalid piece")
                            if chesspiece.move(end_position, board, piece_change):
                                new_piece = board.board[end_position[0]][end_position[1]]
                                player_turn.weight += (new_piece.weight - 1)
                                break
                        
                        if chesspiece.move(end_position, board):
                            break
                print('invalid chess position, try again\n')
            else:
                print('invalid row/column, try again \n')
    
        else:
            best_move = engine.best_candidate()
            bot_piece, end_pos = best_move[0], best_move[1]

            end_capture = board.position_dictionary.get(end_pos, None)
            #check if its enpessant capture
            if isinstance(bot_piece, Pawn) and board.enpessant_tracker is not None:
                if end_pos == board.enpessant_tracker:
                    enpessant_row = board.enpessant_tracker[0] - 1 if bot_piece.color == 'w' else board.enpessant_tracker[0] + 1
                    capture_position = (enpessant_row, end_pos[1])
                    end_capture = board.position_dictionary.get(capture_position, None)

            if bot_piece.move(end_pos, board):
                print('successful move')
                break
            else:
                print('board failure')
                
    return end_capture
            
    
#print board function
def print_board(board, player1, player2):
    print(f'white captured_pieces: {player1.captured_pieces}')
    print(f'black captured_pieces: {player2.captured_pieces}')
    print('  ' + ' '.join(str(column) for column in range(8)))
    row_num = 0
    for row in board.board:
        line = ''
        line += f"{row_num}"
        row_num += 1
        for cell in row:
            to_add = '.' if str(cell) == ' ' else str(cell)
            line+= ' ' + to_add
        print(line)

#check whos turn
def color_turn(board, player1, player2):
    if board.whos_turn() == 'w':
        turn = player1
    else:
        turn = player2
    return turn

if __name__ == "__main__":
    main()


