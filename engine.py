from objects import Board, ChessPiece, Horse, Rook, Bishop, Pawn, Queen, King 


class Engine():
    def __init__(self, active_board):
        self.board = active_board
        self.nodes = 0
        self.qsearch_nodes = 0
        self.transposition_table = {}

    #get the how much u are winning by nega max
    def evaluate(self):
        score = self.board.evaluate_board()
        if self.board.whos_turn() == 'w':
            return score
        return -score
    

    def qsearch(self, alpha, beta): # q search function to check for noisy boards:
        self.qsearch_nodes +=1
        standpat_score = self.evaluate()
        board = self.board

        #if standpat score greater than beta means its the best possible one already
        if standpat_score >= beta:
            return standpat_score
        
        exchanges = [] #(chesspiece, (threaten_pos))
        #look for exchanges      
        for piece in board.position_dictionary.values():
            if piece.color == board.whos_turn():
                threats = piece.threaten(board) #list of all the threats
                for threat in threats:
                    have_threat = board.position_dictionary.get(threat, None)
                    if have_threat is not None:
                        if have_threat.color != piece.color:
                            exchanges.append((piece, (threat)))
        
        #check if got any exhcnages left, if none return the standpat_score
        if len(exchanges) == 0:
            return standpat_score
        exchanges.sort(key=self.mva_lvv, reverse=True)

        #this basically negamax,  standpat is the best score, 
        best_score = standpat_score
        if standpat_score > alpha:
            alpha = standpat_score

        for exchange in exchanges: 
            chesspiece, end_pos = exchange[0], exchange[1]
            if chesspiece.move(end_pos, board):
                move_score = self.qsearch(-beta, -alpha) * -1
                if move_score >alpha:
                    alpha = move_score
                if move_score > best_score:
                    best_score = move_score
                
                board.undo_move()
                if move_score >= beta:
                    break
        
        return best_score
    
    """
    qsearch does these things
    - KEY THING BETA IS THE MAX U ARE ALLOWED TO HAVE ok(BECAUSE THE OPPONENT WILL NEVER LET U REACH IT)
    - first it checks if the current board itself is >= beta (this means the position is too good that the opponent will never let you reach it) 
    - next it checks if theres exchanges by looping throguh the pos dictionary and append it to exhcanges (only the pieces whos turn it is to move)
    - if exchanges is none which means its a quiet board, it returns the standpat score (also we sort the exchanges based of MVV - LVA)
    - then best_score = standpat_score (beacuse standpat score is what we have now)
    - then it checks if standpatscore > alpha, alpha = standpatscore if it fufils the condition
    - then we check each exchange in exchanges, for each exchange (each move) we call q search recursively
      and we pass it the -beta and - alpha because negamax, and also the move_score = -1 * because its negamax
      the rest is similar to negamax
    - if move_score > alpha (alpha = move_score), if move score > best_score (best_score = move_score)
    - we (undo_move) because we need to go search the other child
    - then we check the normal alpha beta prune, if move_score >= beta then we break
    - return best_score
    """

    def get_candidates(self): #get all the pieces that can move whos turn, a queue of the moves
        list_of_possible_moves = []
        board = self.board
        all_pieces, whos_turn = list(board.position_dictionary.values()), board.whos_turn() 
        for chesspiece in all_pieces:
            if chesspiece.color == whos_turn:
                for chesspiece_move in chesspiece.legal_moves(board):
                    list_of_possible_moves.append((chesspiece, chesspiece_move))
        
        list_of_possible_moves.sort(key=self.mva_lvv, reverse=True) #for mva lvv
        return list_of_possible_moves
    
    def mva_lvv(self, chess_move):
        chesspiece, chesspiece_move = chess_move[0], chess_move[1] # get the moves first, sort based on the most valuable attacker least valuable victim
        chesspiece_weight = chesspiece.centipawn
        active_board = self.board
        if isinstance(chesspiece, Pawn) and chesspiece_move == active_board.enpessant_tracker:
            return 1000 - chesspiece_weight 
        if active_board.board[chesspiece_move[0]][chesspiece_move[1]] == " ":
            return 0
        else:
            return active_board.board[chesspiece_move[0]][chesspiece_move[1]].centipawn * 10 - chesspiece_weight
        
    def best_candidate(self): #basically we loop through every single move and get the one with the best score 
        iterative_moves, board = self.get_candidates(), self.board
        phase = board.get_phase()
        #for iterative deepening
        move_iterative_score = {} 
        iterative_best_score = -100000
        iterative_depth = 4 if phase > 12 else 5
        iterative_alpha, iterative_beta = -100000, 100000

        #for main search
        best_move = None
        best_score = -100000
        depth = 6 if phase > 12 else 7
        alpha, beta = -100000, 100000
        
        #iterative search first utilises the mvv lva
        for move in iterative_moves:
            chesspiece, end_pos = move[0], move[1]
            if chesspiece.move(end_pos, board): #for illegal moves it will return False legal moves will return True
                move_score = self.negamax(iterative_depth - 1, -iterative_beta, -iterative_alpha) * -1 #because after ur move its the opponent moves you have to flip the sign
                if move_score > iterative_best_score:
                    iterative_best_score = move_score
                
                if move_score > iterative_alpha:
                    iterative_alpha = move_score

                board.undo_move()

                #add the move and move_score to the move_iterative_score
                move_iterative_score[move] = move_score
        
        #sort the move_iterative (basically the moves) based on the iterative search
        sorted_moves = dict(sorted(move_iterative_score.items(), key=lambda x: x[1], reverse=True))
        moves = list(sorted_moves.keys())

        #main search
        for move in moves:
            chesspiece, end_pos = move[0], move[1]
            if chesspiece.move(end_pos, board): #for illegal moves it will return False legal moves will return True
                move_score = self.negamax(depth - 1, -beta, -alpha) * -1 #because after ur move its the opponent moves you have to flip the sign
                if move_score > best_score:
                    best_move = move
                    best_score = move_score
                
                if move_score > alpha:
                    alpha = move_score

                board.undo_move()
         
        if best_move is None: #this means got no move so its checkmate
            return None
        
        return best_move #else return the best move
    
    """
    runs shallow search before the main search to populate the TT
    following the shallow search, program sorts the root (the moves) at depth 1 based on the results from the shallow search
    main search also utilises the transposition table to reduce search count, 
    alpha beta pruning prunes (close to 96% of the trees)
    this method prunes close to 60 - 70% of the search count (shallow pass + tranpsoistion table)
    adaptive depth: search greater depth in the endgame than the midgame
    total prune: >= 99.9% of all search
    """

    
    def store_transposition(self, depth, best_move, score=None): #store the data in the TT
        zorbist_key = self.board.zorbist_key
        #check if the TT has an input with that zorbist key already
        already_exist = self.transposition_table.get(zorbist_key, None)
        if already_exist is None:
            self.transposition_table[zorbist_key] = {"depth": depth, "best_move":best_move, "score":score}
        else:
            initial_depth_searched = already_exist["depth"]
            if depth >= initial_depth_searched:
                self.transposition_table[zorbist_key] = {"depth": depth, "best_move":best_move, "score":score}
        

    def zorbist_table_lookup(self, depth):
        score_to_return, best_move_return = None, None

        #get the zorbist key for the current baord now and check if its inside (lookup)
        zorbist_key = self.board.zorbist_key
        if zorbist_key in self.transposition_table:
            data = self.transposition_table.get(zorbist_key)
            #first check if the search in transposition table is deeper than the search, if the depth stored(means how many nodes searched below) is greater than the depth we are going to cehck we can automatically use it
            if data["depth"] >= depth:
                #check if theres a score if theres a score we immediately return the best score (alpha), skipping the entire search 
                if data["score"] is not None:
                    score_to_return = data["score"]
                    best_move_return = data["best_move"]
                else:
                    #howevr now score means that opponent will never let this position happen so we can prune it by just changing moves to just the best move posisble, itll immediately call the if move_score >= beta, and break the loop adn return best_score
                    best_move_return = data["best_move"] 
            
            #however, if the depth stored is less than the depth it still pays to search the best move first
            else:
                best_move_return = data["best_move"]
        
        return score_to_return, best_move_return
    
    def null_move_check(self, beta, depth, board, from_null_move):
        if depth < 4:
            return False
        
        if board.current_check():
            return False
        
        if from_null_move is not None:
            return False
    
        if abs(beta) <= 31000 and abs(beta) >= 29000:
            return False
        
        #check if ur side still have any pieces (this doesnt include pawn, if u side only have pawn cannot NMP)
        whos_turn = board.whos_turn()
        has_piece = False
        for chesspiece in board.position_dictionary.values():
            if chesspiece.color == whos_turn and chesspiece.phase_number > 0:
                has_piece = True
                break
        
        if has_piece == False:
            return False
        
        return True
    
    def make_null_move(self): #literally just make no moves
        board = self.board
        initial_turn = board.whos_turn()
        initial_enpessant = board.enpessant_tracker

        #change the board things
        board.turn_increase()
        board.enpessant_tracker = None
        new_turn = board.whos_turn()

        #build a previous the zorbist key
        initial_data = {"zorbist_key": board.zorbist_key, "enpessant": initial_enpessant}
        
        #update zorbist key because of the enepssant and turn count
        zorbist_dict = board.zorbist_table
        if initial_enpessant is not None:
            board.zorbist_key ^= zorbist_dict["enpessant"][None]
            board.zorbist_key ^= zorbist_dict["enpessant"][initial_enpessant[1]]

        #update the zorbist key for the turn
        board.zorbist_key ^= zorbist_dict["move"][initial_turn]
        board.zorbist_key ^= zorbist_dict["move"][new_turn]

        return True, initial_data
    
    def undo_null_move(self, move_data): #undo all the zoribist key
        board = self.board
        board.turn_count -= 1
        board.zorbist_key, board.enpessant_tracker = move_data["zorbist_key"], move_data["enpessant"]
        
        
    def negamax(self, depth, alpha, beta, from_null_move=None): #recursive function that calls itself until it reaches the end sends the best score upwards then calls the next bracnh
        if depth == 0: #return the evaluation, end of depth
            self.nodes +=1
            return self.qsearch(alpha, beta)

        #so you moved already now its the other to move, we are just returning a score
        best_score = -100000
        board = self.board
        found_move = False
        transposition_data = self.zorbist_table_lookup(depth)

        #for null move pruning
        null_move_score = None

        #move and score data
        transposition_score = transposition_data[0]
        transposition_move = transposition_data[1]

        if transposition_score is not None:
            return transposition_score
        
        #Null move pruning, check if its allowed to make the null move
        if self.null_move_check(beta, depth, board, from_null_move):
            data = self.make_null_move()
            move, move_data = data[0], data[1] #data send in form of (boolean, {initial data})
            null_move_score = self.negamax(depth-3, -beta, -alpha, from_null_move=move) * -1
            self.undo_null_move(move_data) #replace the board back to its original position
        
        #if null move score >= beta
        if null_move_score is not None:
            if null_move_score >= beta:
                return null_move_score

        moves = self.get_candidates()
        if transposition_move is not None:
            best_move = (self.board.board[transposition_move[0][0]][transposition_move[0][1]], transposition_move[1])
            moves.remove(best_move)
            moves.insert(0, best_move)

        for move in moves:
            chesspiece, end_pos = move[0], move[1]
            initial_pos = (chesspiece.row, chesspiece.column)
            move_to_return = (initial_pos, end_pos)
            if chesspiece.move(end_pos, board): # I am checking it can move, if it can move, call the next negamax function
                found_move = True #avilable moves
                move_score = self.negamax(depth -1, -beta, -alpha) * -1 #going down the tree
                
            # i undo the move if it reaches the end of the tree it will only be undone when it hits the end of the tree
                board.undo_move() 

                if move_score > alpha:
                    if move_score < beta:
                        #a score above alpha and a score below beta means this is our best possible move allowed by the opponent so it can be stored (it might find better score next but since the zorbist key is the same itll over write it)
                        self.store_transposition(depth, move_to_return, move_score)
                    alpha = move_score
                if move_score > best_score:
                    best_score = move_score

                if move_score >= beta:
                    #we dont store the score because the opponent will never let us reach this move
                    self.store_transposition(depth, move_to_return)
                    break
            

        if found_move == False: #terminal case if check mate
            if board.current_check():
                return -30000 - depth
            else:
                return 0
            
        return best_score 
    
        # Alpha-beta pruning (minimax form)
        # - alpha: the best score the maximiser can already guarantee. It only goes up. (ALPHA IS THE LOWEST YOU CAN GO BECAUSE THE MAX PLAYER WILL NEVER LET U PICK LOWER THAN THAT)
        # - beta:  the best (lowest) score the minimiser can already guarantee. It only goes down. (BETA IS THE MAX U CAN GO BECAUSE THE MIN WILL NEVER LET U PICK HIGHER THAN THAT)
        # - A maximising node only ever changes alpha. A minimising node only ever changes beta.
        # - alpha and beta both get passed down to each child; best_score is local to each
        #   child and is the only thing returned up to the parent.
        # - Maximising: once alpha >= beta, break and return best_score (the best found so far).
        # - Minimising: once beta <= alpha (the score can't go lower than what the maximiser
        #   already has), break and return best_score.
        # - “return best_score sets alpha/beta” only changes anything if it beats the current bound. At a maximising node it raises alpha if it’s greater than alpha. At a minimising node it lowers beta if it’s smaller than beta.
        # - break only leaves that node's own loop. The parent carries on with its next child.
        # - A cutoff means the rest of that branch cannot change the final answer.
        # - negamax is just we alternate the color so alpha = -beta, beta = -alpha, then we only check for alpha >= beta

        # Transposition table (TT) lookup within Negamax:
        # - store_transposition(self, depth, best_move, score = None) (stores relevant data)
        # - We call the store function if the alpha < move score < beta(best posisble move allowed by the opponent)
        # - If we find new scores that is alpha (the previous move score saved) < new_score < beta, it will overwrite the data entry into the table and the best score will take the new score
        # - HOWEVER, WE OVERWRITE ONLY IF THE DEPTH at which the new_score is found >= (the depth storedof inside the TT)
        # - we gives the coordinates ((initial_row, initial_column) to (final_row, final_column)) instead of (move)
        # - move contains (chesspiece_object, (end_pos)) but the chesspiece object may not be the same so when we try to call the move() function, it dont work
        # - instead we get the CHESSPIECE at that (initial_row, initial_column) then we can call the move() function

        # - Depth (how its used)
        # - it needs the depth to check against the same positions later 
        # - (eg. if the DEPTH that YOU STORE >= depth it is at now)
        # - this means that the (PLIES searched when we store the data into the TRANSPOSITION TABLE) >= (PLIES we are currently searching in the Negamax) 
        # - this means we can use the BEST SCORE and the BEST MOVE becasue its reliable (PLIES search in TT >= PLIES to be searched in Search function)
        # - HOWEVER if the depth YOU STORE < depth to be search, (PLIES Searched in TT < PLIES to be searhced in FUNCTION)
        # - this means that the data not as relaibale but we can still utilise BEST MOVE to be searched first

        # - best_move (how its used)
        # - Best move is used in 2 cases the depth in the Transposition table < depth called in the search or when the score is None 
        # - in the first case depth(TT) < depth(search), we use the best move becasue it has a higher chance that we get a better alpha score to prune more nodes
        # - in the second case score is None, it means that the when the score was return it was good enough to prune the rest of the moves, so might as well try that move first it could potentially reduce no. of nodes search
        
        # - best score (how its use)
        # - if the depth(TT) >= depth(search) this means the data is reliable because (PLIES searched in TT) >= (PLIES searched in search function) and we can return the best_score immediately
        # - aso best score is always between the alpha and beta (the alpha before we incremment it to = best score)

        # Null move pruning (NMP)
        # - Idea: having the move is usually an advantage. If we pass our turn, give the opponent a free move,
        #   and our position is still good enough to reach beta, then a real move would be at least as good.
        #   So we skip all the real moves at this node and cut off.
        # - Where it runs: at the start of negamax, before the loop over real moves (when null_move_check allows it).
        #   We make the null move, search the resulting position with depth - 1, and flip the sign of the score.
        #   If the score is >= beta, we undo the null move and return it straight away.
        #   Otherwise we discard the result and search the real moves as normal.

        # from_null_move (optional parameter of negamax)
        # - True when the move that led to this node was a null move.
        # - Stops two null moves in a row.

        # null_move_check(beta, depth, board, from_null_move)
        #  - Returns True only if all of these hold:
        #   - depth >= 4, so the null search still has 3 plies left
        #   - the side to move is not in check (passing would leave the king attacked)
        #   - the previous move was not a null move
        #   - beta is not a mate score (29000 to 31000): mate lines depend on exact moves,
        #     so the result of a pass cannot be trusted (if we get a mate from Null Move its WRONG, we cannot use)
        #   - the side to move at least have a piece (excluding king and pawn)

        # make_null_move()
        # - saves the current Zobrist key and en passant square
        # - flips the turn and clears the en passant square
        # - updates the Zobrist key for both changes
        # - returns True (used as the from_null_move flag) and the saved data

        # undo_null_move(move_data)
        # - restores the turn, the Zobrist key and the en passant square from the saved data
        # - runs straight after the null search, before the score is checked
                



        
        
               
       

        

        
                    


                


        
    

            
    


        

        
    


    