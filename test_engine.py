# test_engine.py
from objects import Board
from engine import Engine
import time

def snapshot(board):
    pieces = {
        pos: (str(piece), piece.row, piece.column, piece.has_moved)
        for pos, piece in board.position_dictionary.items()
    }
    return (
        [[str(cell) for cell in row] for row in board.board],   # the grid
        pieces,                                                  # the dictionary, with each piece's own attributes
        board.turn_count,
        board.enpessant_tracker,
        board.white_king_po,
        board.black_king_po,
    )
def first_test():
    board = Board()
    engine = Engine(board)
    #get all the possible move 

    #check how many moves it haves at the start
    print(f"current moves: {len(engine.get_candidates())}") #expected 22

    #move white pawn to (1, 4) to (3, 4) and black pawn form (6, 3) to (4, 3)
    print(board.position_dictionary[(1, 4)].move((3,4), board)) #white pawn moves 2 square
    print(board.position_dictionary[(6, 3)].move((4,3), board)) #black pawn moves 2 square
    print(board.position_dictionary[(3, 4)].move((4, 4), board)) #white pawn moves one sqaure up
    print(board.position_dictionary[(7, 6)].move((5, 5), board)) #black horse moves so the pawn can capture
    print(board.position_dictionary[(1, 2)].move((3, 2), board)) #white pawn move so pawn can capture pawn
    print(board.position_dictionary[(6, 7)].move((5, 7), board)) #random black pawn move
    print()

    #check the move ordering 
    for move in engine.get_candidates()[0:5]:
        print(move)
    print()

    #check before and after snapshot
    before = snapshot(board)
    print()
    #check which move is best
    print(f'best move: {engine.best_candidate()}')
    print()
    #print after
    after = snapshot(board)

    if before == after:
        print("snapshot = TRUE")
    else:
        print("snapshot = FALSE")

    #test if it works
    print(f'{engine.nodes}')

def second_test(): #test negamax
    board = Board()
    engine = Engine(board)
    #fools mate
    print(board.position_dictionary[(1, 5)].move((2,5), board)) 
    print(board.position_dictionary[(6, 4)].move((4,4), board)) 
    print(board.position_dictionary[(1, 6)].move((3, 6), board))

    print(engine.best_candidate())
    print(engine.negamax(2))

def third_test(): #count how many nodes searched after negamax and check which is the best move, alpha beta prune 96% in this test while returning same result
    board = Board()
    engine = Engine(board)

    #move white pawn to (1, 4) to (3, 4) and black pawn form (6, 3) to (4, 3)
    print(board.position_dictionary[(1, 4)].move((3,4), board)) #white pawn moves 2 square
    print(board.position_dictionary[(6, 3)].move((4,3), board)) #black pawn moves 2 square
    print(board.position_dictionary[(3, 4)].move((4, 4), board)) #white pawn moves one sqaure up
    print(board.position_dictionary[(7, 6)].move((5, 5), board)) #black horse moves so the pawn can capture
    print(board.position_dictionary[(1, 2)].move((3, 2), board)) #white pawn move so pawn can capture pawn
    print(board.position_dictionary[(6, 7)].move((5, 7), board)) #random black pawn move
    print()

    #test with the alpha beta prune and test without (by commenting out the break int eh if alpha > beta break)
    best_candidate = engine.best_candidate()
    print(engine.nodes, best_candidate)

def fourth_test(): #test pst
    board = Board()
    keep = [(0,4), (7,4), (1,6), (6,6), (0,3), (7,3)]
    copy = board.position_dictionary.copy()
    for position in copy:
        if position not in keep:
            board.board[position[0]][position[1]] = " "
            del board.position_dictionary[position]
    
    print(board.evaluate_board())

def fifth_test(): #test the mobility thing
    board = Board()
    engine = Engine(board)
    keep = [
    # white
        (0, 4), (0, 3), (0, 2),          # king, boxed-in queen, bishop
        (1, 2), (1, 3), (1, 4),          # pawns around the queen
        # black
        (7, 4), (7, 3), (7, 5),          # king, free queen, bishop
        (6, 5), (6, 6), (6, 7),          # pawns on f7, g7, h7
]
    copy = board.position_dictionary.copy()
    for position in copy:
        if position not in keep:
            board.board[position[0]][position[1]] = " "
            del board.position_dictionary[position]

    print(board.evaluate_mobility())
    print(board.evaluate_board())
    print(engine.best_candidate(), engine.nodes, engine.qsearch_nodes)
    #q search checks 27% more position when tested this, q search nodes is total amount fo nodes + nodes visited

def sixth_test(): #testing SHALLOW iterative deepening and see if it saves much
    board = Board()
    engine = Engine(board)
    keep = [
    # white
        (0, 4), (0, 3), (0, 2),          # king, boxed-in queen, bishop
        (1, 2), (1, 3), (1, 4),          # pawns around the queen
        # black
        (7, 4), (7, 3), (7, 5),          # king, free queen, bishop
        (6, 5), (6, 6), (6, 7),          # pawns on f7, g7, h7
]
    copy = board.position_dictionary.copy()
    for position in copy:
        if position not in keep:
            board.board[position[0]][position[1]] = " "
            del board.position_dictionary[position]
    
    print(engine.best_candidate(), engine.nodes, engine.qsearch_nodes)
    
    #first test without iterative deepening (♛, (7, 3)) nodes: 84807 qsearch: 217638 (depth of 6)
    #next test with iterative deepening (iterative depth of 3)  (♛, (7, 3)) nodes: 160872 qsearch: 436853
    #another test iterative depth of 2 (♛, (7, 3)) 157988 407597

    """
    next set of test another value
    iterative (0), search depth (5) (♟, (2, 4)) 90542 164833
    iterative (3), search depth (5) (♟, (2, 4)) 106703 195006
    iterative (2), search depth (5) (♟, (2, 4)) 97797 177812
    iterative (1), search depth (5) (♟, (2, 4)) 92269 168318
    """

def seventh_test(): #iterative deepening now with tranposition table
    board = Board()
    engine = Engine(board)
    keep = [
    # white
        (0, 4), (0, 3), (0, 2),          # king, boxed-in queen, bishop
        (1, 2), (1, 3), (1, 4),          # pawns around the queen
        # black
        (7, 4), (7, 3), (7, 5),          # king, free queen, bishop
        (6, 5), (6, 6), (6, 7),          # pawns on f7, g7, h7
]
    copy = board.position_dictionary.copy()
    for position in copy:
        if position not in keep:
            board.board[position[0]][position[1]] = " "
            del board.position_dictionary[position]
    
    before = time.perf_counter()
    print(engine.best_candidate(), engine.nodes, engine.qsearch_nodes)
    after = time.perf_counter()
    print(f"time: {after- before}")
    #iterative depth: 4, main depth 6, nodes: 334381 qsearch_nodes: 381249, time: 15.213
    #iterative depth (removed the move ordering at the start): 4, main depth: 6, nodes:1044248, qsearch:1221998
    #prunes almost 60% more of the nodes AMAZING

def eight_test(): #iterative deepening now with tranposition table, now new position
    
    board = Board()
    engine = Engine(board)
    moves = [
    ((1,4),(3,4)), ((6,4),(4,4)),
    ((0,6),(2,5)), ((7,1),(5,2)),
    ((0,5),(3,2)), ((7,5),(4,2)),
    ((1,2),(2,2)), ((7,6),(5,5)),
    ((1,3),(2,3)), ((6,3),(5,3)),
    ((0,4),(0,6)), ((7,4),(7,6)),
    ((0,1),(1,3)), ((6,0),(5,0)),
    ((3,2),(2,1)), ((4,2),(6,0)),
    ((1,7),(2,7)), ((6,7),(5,7)),
    ((0,5),(0,4)), ((7,5),(7,4)),
]
    for move in moves:
        start = move[0]
        end = move[1]
        chesspiece = board.position_dictionary.get(start)
        chesspiece.move(end, board)

    before = time.perf_counter()
    print(engine.best_candidate(), engine.nodes, engine.qsearch_nodes)
    after = time.perf_counter()
    print(f"time: {after- before}")
    #iterative depth: 3, main depth 5, best_move: (♟, (3, 0)) nodes: 90563 qsearch nodes: 334801, time: 25.290
    #no iterative depth, main depth 5, best_move: (♟, (3, 0)) nodes: 245454 qsearch nodes: 942481 time 70.5334667

    #NMP depth-1, iterative depth: 3, main depth: 5, best_move: (♟, (3, 0)) nodes: 127918 qsearch nodes: 443731 time: 33.20096116702189
    #NMP depth -3, iterative depth: 3, main depth: 5, best_move: (♟, (3, 0)) nodes: 76278 qsearch nodes: 316978 time: 24.04341124999337
    #No NMP iterative depth: 3, main_depth: 5, best_move: (♟, (3, 0)) nodes: 90563 q search nodes: 334801 time: 25.531

    #conclusioon NMP prunes about 15 % more of the nodes

    #try to use pypy
    #with NMP, iterative depth, main depth the same
    #(♟, (3, 0)) 76278 316978 time: 10.777626667026198
    #increasing iterative deptha and main depth by 1 each (♞, (3, 2)) 105605 520325 time: 16.601462000020547

    #tested against intermediate board (1500 elo), win 
    #tested against advanced bot (2000 elo), 

def main():
    eight_test()

if __name__ == "__main__":
    main()

