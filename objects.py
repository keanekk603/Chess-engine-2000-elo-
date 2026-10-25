import random
#board
class Board():
    def __init__(self, height=8, width=8):
        self.turn_count = 1
        self.position_dictionary = {} 
        self.move_history = {} #key shld be turn and value shld be the move {1: [chesspiece, start position, endposition, capture]}
        self.height = height
        self.width = width
        self.enpessant_tracker = None
        self.board = []
        self.white_king_po = (0, 4)
        self.black_king_po = (7, 4)

        #create a 8 * 8 board
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(" ")
            self.board.append(row)

        #white king reference
        self.board[0][4] = King(row=0, column=4, color="w")
        self.position_dictionary[(0, 4)] = self.board[0][4]

        #black king reference
        self.board[7][4] = King(row=7, column=4, color='b')
        self.position_dictionary[(7, 4)] = self.board[7][4]

        #white rooks
        self.board[0][0] = Rook(row=0, column=0, color='w')
        self.position_dictionary[(0,0)] = self.board[0][0]

        self.board[0][7] = Rook(row=0, column=7, color='w')
        self.position_dictionary[(0, 7)] = self.board[0][7]

        #black rooks
        self.board[7][0] = Rook(row=7, column=0, color='b')
        self.position_dictionary[(7,0)] = self.board[7][0]

        self.board[7][7] = Rook(row=7, column=7, color='b')
        self.position_dictionary[(7, 7)] = self.board[7][7]

        #white queen
        self.board[0][3] = Queen(row=0, column=3, color='w')
        self.position_dictionary[(0, 3)] = self.board[0][3]

        #black queen
        self.board[7][3] = Queen(row=7, column=3, color= 'b')
        self.position_dictionary[(7, 3)] = self.board[7][3]

        #white bishop
        self.board[0][2] = Bishop(row=0, column=2, color='w')
        self.position_dictionary[(0,2)] = self.board[0][2]

        self.board[0][5] = Bishop(row=0, column=5, color='w')
        self.position_dictionary[(0, 5)] = self.board[0][5]

        #black bishop
        self.board[7][2] = Bishop(row=7, column=2, color='b')
        self.position_dictionary[(7,2)] = self.board[7][2]

        self.board[7][5] = Bishop(row=7, column=5, color='b')
        self.position_dictionary[(7, 5)] = self.board[7][5]

        #white knight
        self.board[0][1] = Horse(row=0, column=1, color='w')
        self.position_dictionary[(0, 1)] = self.board[0][1]

        self.board[0][6] = Horse(row=0, column=6, color='w')
        self.position_dictionary[(0,6)] = self.board[0][6]

        #black knight
        self.board[7][1] = Horse(row=7, column=1, color='b')
        self.position_dictionary[(7, 1)] = self.board[7][1]

        self.board[7][6] = Horse(row=7, column=6, color='b')
        self.position_dictionary[(7,6)] = self.board[7][6]

        #white and black pawn
        for i in range(8):
            self.board[1][i] = Pawn(row=1, column=i, color='w')
            self.position_dictionary[(1, i)] = self.board[1][i]

            self.board[6][i] = Pawn(row=6, column=i, color='b')
            self.position_dictionary[(6, i)] = self.board[6][i]
        
        self.zorbist_table = self.zorbist_hashing()
        self.zorbist_key = self.build_zorbist_key()

    def zorbist_hashing(self):
        random.Random(42) #64 positions for 12 different pieces
        zorbist_dictionary = {}
        zorbist_dictionary["positions"] = {}
        for row in range(8):
            for column in range(8):
                chesspieces = [
                    "K", "Q", "H", "R", "B", "P",
                    "k", "q", "h", "r", "b", "p"
                               ]
                zorbist_dictionary["positions"][(row, column)] = {}
                for chesspiece in chesspieces:
                    zorbist_dictionary["positions"][(row, column)][chesspiece] = random.getrandbits(64)
        
        #for whos turn to move
        zorbist_dictionary["move"] = {}
        zorbist_dictionary["move"]["b"], zorbist_dictionary["move"]["w"] = random.getrandbits(64), 0

        #for enpessant, basically which colun the enpessant tracker points to will reutrn its zorbist hash
        zorbist_dictionary["enpessant"] = {}
        zorbist_dictionary["enpessant"][None] = 0
        for column in range(8):
            zorbist_dictionary["enpessant"][column] = random.getrandbits(64)

        #design option one per corner or 16 different combinations
        colors, sides, booleans = ['w', 'b'], ['kingside', 'queenside'], [True, False]
        zorbist_dictionary["castle"] = {}
        for color in colors:
            for side in sides:
                for boolean in booleans:
                    zorbist_dictionary["castle"][(color, side, boolean)] = 0 if boolean is False else random.getrandbits(64)
        
        return zorbist_dictionary

    def build_zorbist_key(self): #builds the zorbist key first

        #initiliase the dictionaries to call later
        zorbist_positions, zorbist_enpessant, zorbist_castle, zorbist_move, position_dict, zorbist_number = self.zorbist_table["positions"], self.zorbist_table["enpessant"], self.zorbist_table["castle"], self.zorbist_table["move"], self.position_dictionary, 0

        #for the positions
        for position in position_dict:
            chesspiece = position_dict.get(position)
            zorbist_number ^= zorbist_positions[position][chesspiece.zorbist_symbol]
        
        #enpessant
        enpessant_column = None if self.enpessant_tracker is None else self.enpessant_tracker[1]
        zorbist_number ^= zorbist_enpessant[enpessant_column]

        #castles
        colors, sides = ['w', 'b'], ['kingside', 'queenside']
        for color in colors:
            for side in sides:
                able_to_castle = False
                if self.check_castle_zorbist(color, side):
                    able_to_castle = True
                
                zorbist_number ^= zorbist_castle[(color, side, able_to_castle)]

        #move
        turn = self.whos_turn()
        zorbist_number ^= zorbist_move[turn]

        return zorbist_number
    
    def check_castle_zorbist(self, color, side):
        #check if the king piece has moved
        king_po = self.white_king_po if color =='w' else self.black_king_po
        king_piece = self.position_dictionary.get(king_po)
        if king_piece.has_moved is True:
            return False
        
        #check which side so whcih column
        row_to_check = 0 if color == 'w' else 7
        column_to_check = 0 if side == "queenside" else 7
        rook_to_check = self.board[row_to_check][column_to_check]
        if rook_to_check == " ":
            return False
        else:
            if not isinstance(rook_to_check, Rook) or rook_to_check.has_moved is True or rook_to_check.color != color:
                return False
        
        return True
    
    def check_castle_rights(self):
        #returna  dictionary on castle rights (not the legality of it)
        dictionary_return = {}
        colors, sides = ['w', 'b'], ['kingside', 'queenside']
        for color in colors:
            for side in sides:
                boolean = self.check_castle_zorbist(color, side)
                dictionary_return[(color, side)] = boolean
        
        return dictionary_return
    
    def get_phase(self):
        phase = 0
        for piece in self.position_dictionary.values():
            phase += piece.phase_number
        
        if phase > 24:
            phase = 24
        return phase

    def evaluate_pawn_king(self):
        total_pawn_bonus, phase = 0, self.get_phase()
    
        for piece in self.position_dictionary.values():
            if isinstance(piece, Pawn):
                pawn_bonus, pawn_row, pawn_column = 0, piece.row, piece.column 
                pawn_fronts = [i for i in range(pawn_row + 1, 8)] if piece.color =="w" else [i for i in range(0, pawn_row)]
                neighbour_left, neighbour_right, neighbour_columns = pawn_column -1, pawn_column + 1, []
                if neighbour_left >= 0:
                    neighbour_columns.append(neighbour_left)
                if neighbour_right < 8 :
                    neighbour_columns.append(neighbour_right)

                #check for doubled pawn, -12 for midgame, -25 endgame
                for pawn_front in pawn_fronts:
                    doubled_pawn = self.position_dictionary.get((pawn_front, pawn_column), None)

                    if doubled_pawn is not None:
                        if doubled_pawn.color == piece.color and isinstance(doubled_pawn, Pawn):
                            pawn_bonus -= ((phase/24) * 12 + ((24-phase)/24) * 25)
                            break #later count another one, each pawn count one time

                isolated_pawn = True
                for neighbour_column in neighbour_columns:
                    for pawn_isolate_row in range(8):
                        pawn_isolate_check = self.position_dictionary.get((pawn_isolate_row, neighbour_column), None)
                        if pawn_isolate_check is not None:
                            if pawn_isolate_check.color == piece.color and isinstance(pawn_isolate_check, Pawn):
                                isolated_pawn = False
                                break
                    if isolated_pawn is False:
                        break
                
                if isolated_pawn is True:
                    pawn_bonus -= ((phase/24) * 12 + ((24-phase)/24) * 18)

                #check for passed pawn based ont he rank itself left is midgame and right is endgame
                passed_column_check = neighbour_columns.copy()
                passed_column_check.append(pawn_column)

                passed = True
                for column in passed_column_check:
                    for row in pawn_fronts:
                        passed_pawn_check = self.position_dictionary.get((row, column), None)
                        if passed_pawn_check is not None:
                            if passed_pawn_check.color != piece.color and isinstance(passed_pawn_check, Pawn):
                                passed = False
                                break
                    if passed is False:
                        break
                
                if passed is True:
                    side = -1 if piece.color == 'w' else 8
                    rank = abs(pawn_row - side)
                    rank_bonus = {4: (5, 15), 5: (10, 30), 6:(20, 60), 7:(35, 100)}
                    get_rank_bonus = rank_bonus.get(rank, None)

                    if get_rank_bonus is not None:
                        pawn_bonus += ((phase/24) * get_rank_bonus[0] + ((24-phase)/24) * get_rank_bonus[1])

                if piece.color == "w":
                    total_pawn_bonus += pawn_bonus
                else:
                    total_pawn_bonus -= pawn_bonus
                
            #check king shield + 15 for each 
            if isinstance(piece, King):
                kings_column, kings_row = piece.column, piece.row
                row_to_check = kings_row + 1 if piece.color == 'w' else kings_row -1
                neighbour_left, neighbour_right, columns_to_check = kings_column -1, kings_column + 1, [kings_column]
                if neighbour_left >= 0:
                    columns_to_check.append(neighbour_left)
                if neighbour_right < 8 :
                    columns_to_check.append(neighbour_right)
                
                pawn_shield = 0
                for column in columns_to_check:
                    pawn_check = self.position_dictionary.get((row_to_check, column), None)
                    if pawn_check is not None:
                        if isinstance(pawn_check, Pawn) and pawn_check.color == piece.color:
                            pawn_shield += (phase/24) * 15 + (24-phase)/24 * 2
                
                if piece.color == 'w':
                    total_pawn_bonus += pawn_shield
                else:
                    total_pawn_bonus -= pawn_shield
        
        return total_pawn_bonus
    
    def evaluate_mobility(self): #get the net mobility of the pieces
        total_mobility = 0
        for piece in self.position_dictionary.values():
            if piece.average_moves is not None:
                legal_moves = len(piece.legal_moves(self))
                mobility_score = (legal_moves - piece.average_moves) * piece.mobility_weight

                if piece.color == 'w':
                    total_mobility += mobility_score
                else:
                    total_mobility -= mobility_score
        
        return total_mobility

    #calculate the weight, implementation of a tapered pst basicallyt includes which phase we are in
    def evaluate_pst(self): # THIS IS THE EVAULATE BOARD FUNCTION
        weight = 0
        phase = self.get_phase()
        
        for piece in self.position_dictionary.values():
            midgame_pst = (phase/24) * (piece.midgame_pst[piece.row][piece.column] + piece.midgame_value)
            endgame_pst = ((24-phase)/24) * (piece.endgame_pst[piece.row][piece.column] + piece.endgame_value)

            if piece.color == 'w':
                weight += (midgame_pst + endgame_pst)
            else:
                weight -= (midgame_pst + endgame_pst)
            
        return weight
    
    #return the evualtion of the baord
    def evaluate_board(self):
        return self.evaluate_mobility() + self.evaluate_pst() + self.evaluate_pawn_king()
    
    #a function to give all the threats of the inital state of the baord by a specific color set of tuples
    def all_threats(self):
        #first get the items inside the pos dictionary and put it into the list
        opp_color = 'b' if self.whos_turn() == 'w' else 'w'
        enemy_pieces = []
        for piece in self.position_dictionary.values():
            if piece.color == opp_color:
                enemy_pieces.append(piece)
        
        #once you have all the enemy pieces get the position of all the 
        list_of_threaten_tiles = []
        for enemy_piece in enemy_pieces:
            #call the threaten function and pass the active baord into the function which is self
            list_of_threaten_tiles += enemy_piece.threaten(self)
        
        #use a set 
        return set(list_of_threaten_tiles)
    
    #checks to see if its still on the board
    def still_on_board(self, position):
        if position[0] >=0 and position[0] <=7 and position[1] >= 0 and position[1] <= 7:
            return True
        return False
        
    #check if that part of the baord is empty
    def empty(self, position):
        if self.board[position[0]][position[1]] == " ":
            return True
        return False
    
    #promotion
    def pawn_promotion(self, chesspiece, piece_change):
        position = (chesspiece.row, chesspiece.column)
        end_of_board = 0 if chesspiece.color == 'b' else 7
        if isinstance(chesspiece, Pawn) and chesspiece.row == end_of_board:
            options = {"horse": Horse, "rook": Rook, "queen": Queen, "bishop": Bishop}
            new_piece = options.get(piece_change, Queen)(chesspiece.row, chesspiece.column, chesspiece.color)

            new_piece.has_moved = True
            self.board[chesspiece.row][chesspiece.column] = new_piece
            self.position_dictionary[position] = new_piece

    #checks to see if there is a check if you move to that position
    def is_check(self, chesspiece, end_position):
        #ghost move
        initial_row, initial_column = chesspiece.row, chesspiece.column
        end_row, end_column = end_position
        initial_state = self.board[end_row][end_column]
        self.board[end_row][end_column] = chesspiece
        self.board[initial_row][initial_column] = " "

        #check to see if got someting in that position, the dictionary and checkfor enpessant
        if isinstance(chesspiece, Pawn) and end_position == self.enpessant_tracker:
            # change position in the dictionary
            change_in_row = 1 if chesspiece.color == 'w' else -1
            enpessnat_captured_position = (end_position[0] - change_in_row, end_position[1])
            enpessant_piece_capture = self.position_dictionary.get(enpessnat_captured_position)
            save_piece_capture = None

            #delete it on the physical board, save it first and delete the positikon of the enpessant pawn
            del self.position_dictionary[(enpessnat_captured_position)]
            enpessant_pawn = self.board[enpessnat_captured_position[0]][enpessnat_captured_position[1]]
            self.board[enpessnat_captured_position[0]][enpessnat_captured_position[1]] = " "
        else:
            save_piece_capture = self.position_dictionary.get((end_row, end_column), None)
            enpessant_piece_capture = None
            

        #update the posiiotn dictionary and check if there is soemthing there
        del self.position_dictionary[(initial_row, initial_column)]
        self.position_dictionary[(end_row, end_column)] = chesspiece

        #checks to see the new all threats, calls the all threat function
        all_threats = self.all_threats()

        #get king position, if its the king moving direclty assign it to the end position else have to get throguht he tracker
        if not chesspiece.is_king:
            king_position = self.white_king_po if chesspiece.color == "w" else self.black_king_po
        else:
            king_position = end_position

        #return back to the intiial state, and the position dictionary
        self.board[initial_row][initial_column] = chesspiece
        self.board[end_row][end_column] = initial_state
        del self.position_dictionary[(end_row, end_column)]
        self.position_dictionary[(initial_row, initial_column)] = chesspiece

        #check to see if save peice capture was there basically if sdoemthign was captured, check if the enpessant
        if save_piece_capture:
            self.position_dictionary[(end_row, end_column)] = save_piece_capture

        #check to see if enpessant exists instead
        if enpessant_piece_capture:
            self.board[enpessnat_captured_position[0]][enpessnat_captured_position[1]] = enpessant_pawn
            self.position_dictionary[enpessnat_captured_position] = enpessant_piece_capture

        if king_position in all_threats:
            return True
        return False
    
    def check_castle(self, color ,castle_direction): #helper function, automatically checks whos turn is it 
        # get which color and see whether it moved and the direction, cant castle if they move before/is false
        king_row = 7 if color == 'b' else 0
        rook_column = 0 if castle_direction == 'queenside' else 7
        columns_in_between = [1, 2, 3] if rook_column == 0 else [5, 6]

        #check if empty in the first place 
        if self.empty((king_row, 4)) or self.empty((king_row, rook_column)):
            return False
        #check if its a rook
        if not isinstance(self.board[king_row][rook_column], Rook):
            return False
        #check if got move ebfore
        if self.board[king_row][4].has_moved or self.board[king_row][rook_column].has_moved or self.current_check():
            return False
        #check fi column in between are empty
        for column_in_between in columns_in_between:
            if not self.empty((king_row, column_in_between)):
                return False
        
        if castle_direction == 'queenside':
            change_in_column = [-1, -2]
        else:
            change_in_column = [1, 2]
            
        #rules state that the king moves firs tbefore the roook, so have to check every piece that the king is going throguh to see if its being check
        all_threats = self.all_threats()
        for change_column in change_in_column:
            column = 4 + change_column
            if (king_row, column) in all_threats:
                return False
        
        return True
    #SPEICAL MOVES
    def attempt_castle(self, castle_direction):
        # get which color and see whether it moved and the direction, cant castle if they move before/is false
        king_row = 7 if self.whos_turn() == 'b' else 0
        rook_column = 0 if castle_direction == 'queenside' else 7
        color = self.whos_turn()
        
        #check is placed into a helper function
        if self.check_castle(color ,castle_direction):
            #make the move if it doest return False yet
            new_column_king = 2 if castle_direction == 'queenside' else 6
            new_column_rook = 3 if castle_direction == 'queenside' else 5
            self.board[king_row][new_column_king] = self.board[king_row][4]
            self.board[king_row][4] = " "
            self.board[king_row][new_column_rook] = self.board[king_row][rook_column]
            self.board[king_row][rook_column] = " "

            #update the atributes
            self.board[king_row][new_column_king].column = new_column_king
            self.board[king_row][new_column_rook].column = new_column_rook

            #update king position and the dictionaries, we dont use the move
            self.update_king_po((king_row, new_column_king))
            del self.position_dictionary[(king_row, 4)], self.position_dictionary[(king_row, rook_column)]
            self.position_dictionary[(king_row, new_column_king)] = self.board[king_row][new_column_king]
            self.position_dictionary[(king_row, new_column_rook)] = self.board[king_row][new_column_rook]


            #update attributes of the king and rook and the enpessant tracker need set to false
            self.board[king_row][new_column_king].has_moved = True
            self.board[king_row][new_column_rook].has_moved = True
            self.enpessant_tracker = None

            return True
        
        return False

    #update king_position
    def update_king_po(self, end_position):
        if self.whos_turn() == 'w':
            self.white_king_po = end_position
        else:
            self.black_king_po = end_position
        
    def whos_turn(self):
        if self.turn_count % 2 == 0:
            your_color = 'b'
        else:
            your_color = 'w'
        return your_color
    
    #checks to see if tis at its endgame, can be used for win/draw/lose
    def is_end_game(self):
        turn = self.whos_turn()

        #list of all your possible moves first get list of all your 
        your_pieces = [piece for piece in self.position_dictionary.values() if piece.color == turn]
        possible_moves = {}

        #check to see if its the pawn piece
        for piece in your_pieces:
            if not isinstance(piece, Pawn):
                possible_moves[piece] = piece.threaten(self)
            else:
                possible_moves[piece] = piece.legal_moves(self)

        
        #loop throguh each and every piece and call the move to see if its valid
        for piece in possible_moves:
            for end_position in possible_moves[piece]:
                if not self.is_check(piece, end_position):
                    return False
        
        return True
    
    #see who wins, basically see if u are currently being checked if you are u lose
    def current_check(self):
        #check whos turn
        if self.whos_turn() == 'b':
            king_position = self.black_king_po
            opponent_color = 'w'
        else:
            king_position = self.white_king_po
            opponent_color = 'b'
        
        #get the list of all the threats and see if king inside
        allthreaten_tiles = self.all_threats()
        if king_position in allthreaten_tiles:
            return True
        return False
    
    #NOT IN USE
    """
    def redo_move(self):
        if self.turn_count in self.move_history:
            data = self.move_history[self.turn_count]
            return data["piece"].move(data["end"], self, type(data["promotion"]).__name__.lower() if data["promotion"] is not None else None)
        return False
    """
   
    def undo_move(self):
        if self.turn_count > 1:
            self.turn_count -= 1
            data = self.move_history[self.turn_count]
            initial_pos, end_pos = data["start"], data["end"]

            data["piece"].row, data["piece"].column = initial_pos[0], initial_pos[1] #change the data of the chesspiece
            data["piece"].has_moved = data["had_moved"]

            self.board[initial_pos[0]][initial_pos[1]] = data["piece"] #free up the end square first
            self.position_dictionary.pop(end_pos) # pop the dictionary thing and replace it 
            self.position_dictionary[initial_pos] = data["piece"]
    
            self.enpessant_tracker = data["enpessant"] #assign all the data
            self.white_king_po = data["white_king_po"]
            self.black_king_po = data["black_king_po"]

            if data["captured"] is not None:
                #check for capture
                captured_pos = data["captured_pos"]
                self.board[captured_pos[0]][captured_pos[1]] = data["captured"]
                #create the dictioanry
                self.position_dictionary[captured_pos] = data["captured"]
                #for enpessant
                if captured_pos != end_pos:
                    self.board[end_pos[0]][end_pos[1]] = " "
            else:
                self.board[end_pos[0]][end_pos[1]] = " "

            #check if got rook
            if data["rook"] is not None:
                rook_start, rook_end = data["rook_start"], data["rook_end"] #change the attriobnutes first
                data["rook"].has_moved = False
                data["rook"].row, data["rook"].column = rook_start[0], rook_start[1]
                
                self.board[rook_start[0]][rook_start[1]] = data["rook"] #change the board the position dictionary
                self.position_dictionary.pop(rook_end)
                self.position_dictionary[rook_start] = data["rook"]

                self.board[rook_end[0]][rook_end[1]] = " " #empty the square
            
            #change back the zorbist key
            self.zorbist_key = data["zorbist_key"]

            del self.move_history[self.turn_count]

            return True
        
        return False
    
    #increase the count
    def turn_increase(self):
        self.turn_count += 1
    
    #1 means white win, -1 means black wins and 0 means draw
    def winner(self):
        turn = self.whos_turn()
        if self.current_check():
            if turn == 'w':
                return -1
            else:
                return 1
        else:
            return 0

#objects and its importance, the default which its its end_position
class ChessPiece():
    #basically the end_position of the chesspiece, the color etc. 
    def __init__(self, row, column, color):
        self.row = row
        self.column = column
        self.color = color
        self.phase_number = 0
        self.is_king = False #sets all the default false except the king
        self.has_moved = False #used for rook and king
        self.average_moves = None
        self.mobility_weight = None
           
    #appends all the availabe diagonal move for queen and bishop and rook
    def direction_move(self, return_list, active_board, delta_row, delta_column):
        #initialise the stuff
        row, column = self.row, self.column
        while True:
            #the direction
            row, column = row + delta_row, column + delta_column
            threat_position = (row, column)

            #first check if its still ont he baord then check if its empty
            if active_board.still_on_board(threat_position):
                if active_board.empty(threat_position):
                    return_list.append(threat_position)
                    #if its not empty need to check if its ur color if it is opp color append else dont append then break 
                else:
                    if self.color != active_board.board[row][column].color:
                        return_list.append(threat_position)
                    break
            else:
                break

    """
    because XOR undo itself naturally and update zorbist gets the state now adn the state before if we ^= the state now
    and ^= the state before, we naturally can undo it
    """
    def update_zorbist(self, board, record):#to change the zorbist key based on the data, and the move

        #get the relevant data 
        current_key, zorbist_dict = board.zorbist_key, board.zorbist_table
        chesspiece, start_pos, end_pos, initial_enpessant, final_enpessant = record["piece"], record["start"], record["end"], record["enpessant"], board.enpessant_tracker
        movement_piece = record["piece"].zorbist_symbol

        #change the position first
        current_key ^= zorbist_dict["positions"][start_pos][movement_piece]
        current_key ^= zorbist_dict["positions"][end_pos][movement_piece]

        #change the enpessant
        initial_enpessant_column = None if initial_enpessant is None else initial_enpessant[1]
        final_enpessant_column = None if final_enpessant is None else final_enpessant[1]
        current_key ^= zorbist_dict["enpessant"][initial_enpessant_column]
        current_key ^= zorbist_dict["enpessant"][final_enpessant_column]

        #check if its king or rook then you gotta update it
        initial_castle_rights = record["castle_rights"]
        final_castle_rights = board.check_castle_rights()
        for key in initial_castle_rights.keys():
            initial_boolean = initial_castle_rights.get(key)
            final_boolean = final_castle_rights.get(key)
            if initial_castle_rights.get(key) != final_castle_rights.get(key):
                current_key ^= zorbist_dict["castle"][(key[0], key[1], initial_boolean)]
                current_key ^= zorbist_dict["castle"][(key[0], key[1], final_boolean)]
        
        #check the capture (if got capture remove it fromt he zorbist key)
        if record["captured"] is not None:
            current_key ^= zorbist_dict["positions"][record["captured_pos"]][record["captured"].zorbist_symbol]
        
        #check the promotion (remvoe the final position then change it to the queen or wtv)
        if record["promotion"] is not None:
            piece_promoted = record["promotion"].zorbist_symbol
            current_key ^= zorbist_dict["positions"][end_pos][movement_piece]
            current_key ^= zorbist_dict["positions"][end_pos][piece_promoted]

        #check for castle (remove the initial position of the rook then add the final position of the rook)
        if record["rook"] is not None:
            rook_piece = record["rook"].zorbist_symbol
            current_key ^= zorbist_dict["positions"][record["rook_start"]][rook_piece]
            current_key ^= zorbist_dict["positions"][record["rook_end"]][rook_piece]
        
        #move turn before and after using the chesspiece color
        side_that_moved = chesspiece.color
        side_to_move = 'w' if side_that_moved == 'b' else 'b'
        current_key ^= zorbist_dict["move"][side_that_moved]
        current_key ^= zorbist_dict["move"][side_to_move]

        board.zorbist_key = current_key
        
    def move(self, end_position, active_board, piece_change=None):
        record_to_add = self.make_record(active_board, end_position)
        initial_position = (self.row, self.column)
        initial_turn_count = active_board.turn_count

        #check for castle
        if self.is_king:
            current_row, current_col = self.row, self.column
            end_row, end_col = end_position
            if current_row == end_row and abs(end_col - current_col) == 2:
                direction = 'queenside' if end_col == 2 else 'kingside'
                if active_board.attempt_castle(direction):
                    active_board.turn_increase()

                    rook_initial_column = 7 if direction == 'kingside' else 0 
                    rook_final_column = 5 if direction == 'kingside' else 3
                    rooks_initial_position = (self.row, rook_initial_column)
                    rook_final_position = (self.row, rook_final_column)

                    record_to_add["rook"] = active_board.board[rook_final_position[0]][rook_final_position[1]] 
                    record_to_add["rook_start"] = rooks_initial_position 
                    record_to_add["rook_end"] = rook_final_position

                    self.update_zorbist(active_board, record_to_add)
                    active_board.move_history[initial_turn_count] = record_to_add
                    return True
                
                return False
        
        #create a validate function
        if self.validate_move(end_position, active_board):
            end_capture = active_board.board[end_position[0]][end_position[1]] #store the capture
            captured_position = end_position #see where it is captured at

            enpessant_tracker = active_board.enpessant_tracker
            #update enpessant first
            self.update_enpessant(end_position, active_board)

            #replace the inital posiion with space andc hange the posiiton, put ur object somewhere else
            self.row = end_position[0]
            self.column = end_position[1]
            active_board.board[end_position[0]][end_position[1]] = self

            #change the intial square to empty
            active_board.board[initial_position[0]][initial_position[1]] = " "

            #update the poisiton dictionary, since objects are completely unique in memory it would duplicate even if its the same class
            active_board.position_dictionary[end_position] = self
            active_board.position_dictionary.pop(initial_position)

            #check if its enpessant it will capture th peice if ure taking it with a pawn else nothign will happen
            if end_position == enpessant_tracker:
                if self.enpessant_capture():
                    enpessant_row_change = 1 if self.color == 'w' else -1 #create the data
                    new_row = self.row - enpessant_row_change

                    captured_position = (new_row, self.column) #store the data
                    end_capture = active_board.board[new_row][self.column]

                    active_board.board[new_row][self.column] = " " #make the changes
                    del active_board.position_dictionary[(new_row, self.column)]


            #check if its the KING and change the king position
            if self.is_king:
                active_board.update_king_po(end_position)

            #turn it to be true, update the enpessant tracker
            if self.has_moved is False:
                self.has_moved = True
            
            #increment the turn
            active_board.turn_increase()

            #check for pawn promotion
            if self.reached_promotion_row(end_position):
                if piece_change is None:
                    piece_change = "queen"
                active_board.pawn_promotion(self, piece_change)
                record_to_add["promotion"] = active_board.board[end_position[0]][end_position[1]]

            #put the move into a history
            captured = None if end_capture == " " else end_capture
            captured_pos = None if end_capture == " " else captured_position
            record_to_add["captured"] = captured
            record_to_add["captured_pos"] = captured_pos

            #put the enpessant into the history

            #crete the history
            self.update_zorbist(active_board, record_to_add)
            active_board.move_history[initial_turn_count] = record_to_add
            return True
        
        return False
    
    def validate_move(self, end_position, active_board):
        
        #get a list of all available move
        list_available = self.threaten(active_board)
        if end_position not in list_available:
            return False
        
        #does the movement result in a check, basically put ur own color into the parameter 
        if active_board.is_check(self, end_position):
            return False
        
        return True
    
    #get the list of legal moves, for easy use
    def legal_moves(self, active_board):
        legal_move_list = self.threaten(active_board)
        
        return legal_move_list
   
    def update_enpessant(self, end_position, active_board):
        active_board.enpessant_tracker = None

    def enpessant_capture(self):
        return False
    
    def make_record(self, active_board, end_position):
        #the state of the board before th emove is made and what the next move is made 
        return {
            "piece": self,
            "start": (self.row, self.column),
            "end": end_position,
            "had_moved": self.has_moved,
            "enpessant": active_board.enpessant_tracker,
            "white_king_po": active_board.white_king_po,
            "black_king_po": active_board.black_king_po,
            "captured": None, "captured_pos": None,
            "rook": None, "rook_start": None, "rook_end": None,
            "promotion": None,
            "castle_rights": active_board.check_castle_rights(),
            "zorbist_key": active_board.zorbist_key
        }  

    #for pawn promotion
    def reached_promotion_row(self, end_position):
        return False
              
class King(ChessPiece):
    def __init__(self, row, column, color):
        super().__init__(row, column, color)
        self.midgame_value = 0
        self.endgame_value = 0
        self.centipawn = 20000
        self.weight = 100
        self.is_king = True
        self.zorbist_symbol = "K" if self.color == "w" else "k"
        mg_table = [
            [-65,  23,  16, -15, -56, -34,   2,  13],
            [ 29,  -1, -20,  -7,  -8,  -4, -38, -29],
            [ -9,  24,   2, -16, -20,   6,  22, -22],
            [-17, -20, -12, -27, -30, -25, -14, -36],
            [-49,  -1, -27, -39, -46, -44, -33, -51],
            [-14, -14, -22, -46, -44, -30, -15, -27],
            [  1,   7,  -8, -64, -43, -16,   9,   8],
            [-15,  36,  12, -54,   8, -28,  24,  14]
        ]

        eg_table = [
            [-74, -35, -18, -18, -11,  15,   4, -17],
            [-12,  17,  14,  17,  17,  38,  23,  11],
            [ 10,  17,  23,  15,  20,  45,  44,  13],
            [ -8,  22,  24,  27,  26,  33,  26,   3],
            [-18,  -4,  21,  24,  27,  23,   9, -11],
            [-19,  -3,  11,  21,  23,  16,   7,  -9],
            [-27, -11,   4,  13,  14,   4,  -5, -17],
            [-53, -34, -21, -11, -28, -14, -24, -43]
        ]
        if self.color == 'w':
            mg_table.reverse()
            eg_table.reverse()
            self.midgame_pst = mg_table
            self.endgame_pst = eg_table
        else:
            self.midgame_pst = mg_table
            self.endgame_pst = eg_table
            
    #basically gives a list of all that is threaten by this piece
    def threaten(self, active_board):
        return_list = []

        #get the surrounding cells
        for i in range(3):
            row_threat = self.row - 1 + i
            for j in range(3):
                column_threat = self.column - 1 + j
                threat_position = (row_threat, column_threat)

                #check if its still on the baord
                if active_board.still_on_board(threat_position) and threat_position != (self.row, self.column):
                    #check to see if there is ur pieces inside that cell, and if its ur color or theirs
                    if active_board.empty(threat_position) or active_board.board[row_threat][column_threat].color != self.color:
                        return_list.append(threat_position)
        
        return return_list
    
    def legal_moves(self, active_board):
        legal_move_list = self.threaten(active_board)
        if not self.has_moved:
            legal_move_list.append((self.row, 2))
            legal_move_list.append((self.row, 6))
        
        return legal_move_list
    
    #prints what color it is
    def __repr__(self):
        return "♔" if self.color == "b" else "♚"

class Queen(ChessPiece):
    def __init__(self, row ,column, color):
        super().__init__(row, column, color)
        self.phase_number = 4
        self.midgame_value = 1025
        self.endgame_value = 936
        self.centipawn = 900
        self.weight = 9
        self.average_moves = 13
        self.mobility_weight = 1
        self.zorbist_symbol = "Q" if self.color == "w" else "q"
        mg_table = [
            [-28,   0,  29,  12,  59,  44,  43,  45],
            [-24, -39,  -5,   1, -16,  57,  28,  54],
            [-13, -17,   7,   8,  29,  56,  47,  57],
            [-27, -27, -16, -16,  -1,  17,  -2,   1],
            [ -9, -26,  -9, -10,  -2,  -4,   3,  -3],
            [-14,   2, -11,  -2,  -5,   2,  14,   5],
            [-35,  -8,  11,   2,   8,  15,  -3,   1],
            [ -1, -18,  -9,  10, -15, -25, -31, -50]
        ]

        eg_table = [
            [ -9,  22,  22,  27,  27,  19,  10,  20],
            [-17,  20,  32,  41,  58,  25,  30,   0],
            [-20,   6,   9,  49,  47,  35,  19,   9],
            [  3,  22,  24,  45,  57,  40,  57,  36],
            [-18,  28,  19,  47,  31,  34,  39,  23],
            [-16, -27,  15,   6,   9,  17,  10,   5],
            [-22, -23, -30, -16, -16, -23, -36, -32],
            [-33, -28, -22, -43,  -5, -32, -20, -41]
        ]
        if self.color == 'w':
            mg_table.reverse()
            eg_table.reverse()
            self.midgame_pst = mg_table
            self.endgame_pst = eg_table
        else:

            self.midgame_pst = mg_table
            self.endgame_pst = eg_table


    def threaten(self, active_board):
        return_list = []
        #get all 4 direction
        self.direction_move(return_list, active_board, 1, 1)
        self.direction_move(return_list, active_board, 1, -1)
        self.direction_move(return_list, active_board, -1, -1)
        self.direction_move(return_list, active_board, -1, 1)
        self.direction_move(return_list, active_board, 1, 0)
        self.direction_move(return_list, active_board, 0, 1)
        self.direction_move(return_list, active_board, -1, 0)
        self.direction_move(return_list, active_board, 0, -1)
        
        return return_list

    def __repr__(self):
        return "♕" if self.color == "b" else "♛"
    
class Rook(ChessPiece):
    def __init__(self, row, column, color):
        super().__init__(row, column, color)
        self.phase_number = 2
        self.midgame_value = 477
        self.endgame_value = 512
        self.centipawn = 500
        self.weight = 5
        self.average_moves = 7
        self.mobility_weight = 2
        self.zorbist_symbol = "R" if self.color == "w" else"r"
        mg_table = [
            [ 32,  42,  32,  51,  63,   9,  31,  43],
            [ 27,  32,  58,  62,  80,  67,  26,  44],
            [ -5,  19,  26,  36,  17,  45,  61,  16],
            [-24, -11,   7,  26,  24,  35,  -8, -20],
            [-36, -26, -12,  -1,   9,  -7,   6, -23],
            [-45, -25, -16, -17,   3,   0,  -5, -33],
            [-44, -16, -20,  -9,  -1,  11,  -6, -71],
            [-19, -13,   1,  17,  16,   7, -37, -26]
        ]

        eg_table = [
            [ 13,  10,  18,  15,  12,  12,   8,   5],
            [ 11,  13,  13,  11,  -3,   3,   8,   3],
            [  7,   7,   7,   5,   4,  -3,  -5,  -3],
            [  4,   3,  13,   1,   2,   1,  -1,   2],
            [  3,   5,  8,  4,  -5,  -6,  -8, -11],
            [ -4,   0,  -5,  -1,  -7, -12,  -8, -16],
            [ -6,  -6,   0,   2,  -9,  -9, -11,  -3],
            [ -9,   2,   3,  -1,  -5, -13,   4, -20]
        ]
        if self.color == 'w':
            mg_table.reverse()
            eg_table.reverse()
            self.midgame_pst = mg_table
            self.endgame_pst = eg_table
        else:
            self.midgame_pst = mg_table
            self.endgame_pst = eg_table

    def threaten(self, active_board):
        return_list = []

        self.direction_move(return_list, active_board, 1, 0)
        self.direction_move(return_list, active_board, 0, 1)
        self.direction_move(return_list, active_board, -1, 0)
        self.direction_move(return_list, active_board, 0, -1)

        return return_list

    def __repr__(self):
        return "♖" if self.color == "b" else "♜"

class Bishop(ChessPiece):
    def __init__(self, row, column, color):
        super().__init__(row, column, color)
        self.phase_number = 1
        self.midgame_value = 365
        self.endgame_value = 297
        self.centipawn = 320
        self.weight = 3
        self.average_moves = 7
        self.mobility_weight = 4
        self.zorbist_symbol = "B" if self.color == "w" else "b"

        mg_table = [
            [-29,   4, -82, -37, -25, -42,   7,  -8],
            [-26,  16, -18, -13,  30,  59,  18, -47],
            [-16,  37,  43,  40,  35,  50,  37,  -2],
            [ -4,   5,  19,  50,  37,  37,   7,  -2],
            [ -6,  13,  13,  26,  34,  12,  10,   4],
            [  0,  15,  15,  15,  14,  27,  18,  10],
            [  4,  15,  16,   0,   7,  21,  33,   1],
            [-33,  -3, -14, -21, -13, -12, -39, -21]
        ]

        eg_table = [
            [-14, -21, -11,  -8, -7,  -9, -17, -24],
            [ -8,  -4,   7, -12, -3, -13,  -4, -14],
            [  2,  -8,   0,  -1, -2,   6,   0,   4],
            [ -3,   9,  12,   9, 14,  10,   3,   2],
            [ -6,   3,  13,  19,  7,  10,  -3,  -9],
            [-12,  -3,   8,  10, 13,   3,  -7, -15],
            [-14, -18,  -7,  -1,   4,  -9, -15, -27],
            [-23,  -9, -23,  -5,  -9, -16,  -5, -17]
        ]
        if self.color == 'w':
            mg_table.reverse()
            eg_table.reverse()
            self.midgame_pst = mg_table
            self.endgame_pst = eg_table
        else:
            self.midgame_pst = mg_table
            self.endgame_pst = eg_table

    def threaten(self, active_board):
        return_list = []

        self.direction_move(return_list, active_board, 1, 1)
        self.direction_move(return_list, active_board, -1, -1)
        self.direction_move(return_list, active_board, -1, 1)
        self.direction_move(return_list, active_board, 1, -1)

        return return_list

    def __repr__(self):
        return "♗" if self.color == "b" else "♝"

class Horse(ChessPiece):
    def __init__(self, row, column, color):
        super().__init__(row, column, color)
        self.phase_number = 1
        self.midgame_value = 337
        self.endgame_value = 281
        self.centipawn = 320
        self.weight = 3
        self.average_moves = 4
        self.mobility_weight = 4
        self.zorbist_symbol = "H" if self.color == "w" else "h"
        mg_table = [
            [-167, -89, -34, -49,  61, -97, -15, -107],
            [ -73, -41,  72,  36,  23,  62,   7,  -17],
            [ -47,  60,  37,  65,  84, 129,  73,   44],
            [  -9,  17,  19,  53,  37,  69,  18,   22],
            [ -13,   4,  16,  13,  28,  19,  21,   -8],
            [ -23,  -9,  12,  10,  19,  17,  25,  -16],
            [ -29, -53, -12,  -3,  -1,  18, -14,  -19],
            [-105, -21, -58, -33, -17, -28, -19,  -23]
        ]

        eg_table = [
            [-58, -38, -13, -28, -31, -27, -63, -99],
            [-25,  -8, -25,  -2,  -9, -25, -24, -52],
            [-24, -20,  10,   9,  -1,  -9, -19, -41],
            [-17,   3,  22,  22,  22,  11,   8, -18],
            [-18,  -6,  16,  25,  16,  17,   4, -18],
            [-23,  -3,  -1,  15,  10,  -3, -20, -22],
            [-42, -20, -10,  -5,  -2, -20, -23, -44],
            [-29, -51, -23, -15, -22, -18, -50, -64]
        ]
        if self.color == 'w':
            mg_table.reverse()
            eg_table.reverse()
            self.midgame_pst = mg_table
            self.endgame_pst = eg_table
        else:
            self.midgame_pst = mg_table
            self.endgame_pst = eg_table

    
    def threaten(self, active_board):
        return_list = []
        row, column = self.row, self.column
        #get all the change in coordainte all the legal moves and loop throguh each
        coordinate_change = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
        for change in coordinate_change:
            #check if the new_position is empty and still on baord or if there is other of ur pieces
            new_position = (row + change[0], column + change[1])
            if active_board.still_on_board(new_position):
                if active_board.empty(new_position):
                    return_list.append(new_position)
                else:
                    if active_board.board[new_position[0]][new_position[1]].color != self.color:
                        return_list.append(new_position)
        
        return return_list

    def __repr__(self):
        return "♘" if self.color == "b" else "♞"

class Pawn(ChessPiece):
    def __init__(self, row, column, color):
        super().__init__(row, column, color)
        self.midgame_value = 82
        self.endgame_value = 94
        self.centipawn = 100
        self.weight = 1
        self.zorbist_symbol = "P" if self.color == "w" else"p"

        
        mg_table = [
            [  0,   0,   0,   0,   0,   0,   0,   0],
            [ 98, 134,  61,  95,  68, 126,  34, -11],
            [ -6,   7,  26,  31,  65,  56,  25, -20],
            [-14,  13,   6,  21,  23,  12,  17, -23],
            [-27,  -2,  -5,  12,  17,   6,  10, -25],
            [-26,  -4,  -4, -10,   3,   3,  33, -12],
            [-35,  -1, -20, -23, -15,  24,  38, -22],
            [  0,   0,   0,   0,   0,   0,   0,   0]
        ]

        eg_table = [
            [  0,   0,   0,   0,   0,   0,   0,   0],
            [178, 173, 158, 134, 147, 132, 165, 187],
            [ 94, 100,  85,  67,  56,  53,  82,  84],
            [ 32,  24,  13,   5,  -2,   4,  17,  17],
            [ 13,   9,  -3,  -7,  -7,  -8,   3,  -1],
            [  4,   7,  -6,   1,   0,  -5,  -1,  -8],
            [ 13,   8,   8,  10,  13,   0,   2,  -7],
            [  0,   0,   0,   0,   0,   0,   0,   0]
        ]

        if self.color == 'w':
            mg_table.reverse()
            eg_table.reverse()
            self.midgame_pst = mg_table
            self.endgame_pst = eg_table
        else:
            self.midgame_pst = mg_table
            self.endgame_pst = eg_table


            

    def threaten(self, active_board):
        return_list = []
        row, column = self.row, self.column

        if self.color == 'w':
            coordinate_change = [(1, 1), (1, -1)]
        else:
            coordinate_change = [(-1, 1), (-1, -1)]
        for change in coordinate_change:
            new_position = (row + change[0], column + change[1])
            if active_board.still_on_board(new_position):
                if active_board.empty(new_position):
                    return_list.append(new_position)
                else:
                    if active_board.board[new_position[0]][new_position[1]].color != self.color:
                        return_list.append(new_position)
        
        return return_list
    
    def validate_move(self, end_position, active_board):
        available_moves = self.legal_moves(active_board)
        
        if end_position not in available_moves:
            return False
        
        if active_board.is_check(self, end_position):
            return False
        return True
    
    def legal_moves(self, active_board):
        available_moves = []
        if self.color == 'w':
            current_row, current_column = self.row, self.column
            #check if the thing has moved if not it can mvoe 2 steps and check if its empty
            if current_row == 1 and active_board.empty((current_row + 2, current_column)) and active_board.empty((current_row +1, current_column)):
                available_moves.append((current_row + 2, current_column))

            #it can move one step down
            if active_board.still_on_board((current_row +1, current_column)):
                if active_board.empty((current_row +1, current_column)):
                    available_moves.append((current_row + 1, current_column))

            #check if can eat 
            if active_board.still_on_board((current_row +1, current_column + 1)):
                if not active_board.empty((current_row+1, current_column+1)) and active_board.board[current_row+1][current_column+1].color != self.color:
                    available_moves.append((current_row + 1, current_column+1))

            if active_board.still_on_board((current_row +1, current_column-1)):
                if not active_board.empty((current_row+1, current_column-1)) and active_board.board[current_row+1][current_column-1].color != self.color:
                    available_moves.append((current_row + 1, current_column-1))

        else:
            current_row, current_column = self.row, self.column
            #check if the thing has moved if not it can mvoe 2 steps and check if its empty
            if current_row == 6 and active_board.empty((current_row - 2, current_column)) and active_board.empty((current_row -1, current_column)):
                available_moves.append((current_row - 2, current_column))

            #it can move one step down
            if active_board.still_on_board((current_row -1, current_column)):
                if active_board.empty((current_row -1, current_column)):
                    available_moves.append((current_row - 1, current_column))

            #check if can eat 
            if active_board.still_on_board((current_row -1, current_column - 1)):
                if not active_board.empty((current_row-1, current_column-1)) and active_board.board[current_row-1][current_column-1].color != self.color:
                    available_moves.append((current_row - 1, current_column-1))

            if active_board.still_on_board((current_row -1, current_column+1)):
                if not active_board.empty((current_row-1, current_column+1)) and active_board.board[current_row-1][current_column+1].color != self.color:
                    available_moves.append((current_row-1, current_column+1))
        
        #check if enpessant and check if its diagonal
        if active_board.enpessant_tracker is not None:
            end_position = active_board.enpessant_tracker
            direction = 1 if self.color == 'b' else -1
            if self.row - end_position[0] == direction and abs(self.column - end_position[1]) == 1:
                available_moves.append(active_board.enpessant_tracker)

        return available_moves
    
    def update_enpessant(self, end_position, active_board):
        initial_row = self.row
        end_row = end_position[0]
        enpessant_row_change = 1 if self.color == 'w' else -1
        if abs(end_row - initial_row) == 2:
            active_board.enpessant_tracker = (initial_row + enpessant_row_change, end_position[1])
        else:
            active_board.enpessant_tracker = None

    def enpessant_capture(self):
        return True

    def __repr__(self):
        return "♙" if self.color == "b" else "♟"
    
    def reached_promotion_row(self, end_position):
        end_row = 7 if self.color == 'w' else 0
        if end_position[0] == end_row:
            return True
        
        return False
    
class Player():
    def __init__(self, color, weight):
        self.color = color
        self.weight = weight
        self.captured_pieces = []
    
    def __repr__(self):
        return f'Player {self.color}'
    



