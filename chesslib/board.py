from itertools import groupby
from copy import deepcopy

import pieces
import re
import time

class ChessError(Exception): pass
class InvalidCoord(ChessError): pass
class InvalidColor(ChessError): pass
class InvalidMove(ChessError): pass
class Check(ChessError): pass
class CheckMate(ChessError): pass
class Draw(ChessError): pass
class NotYourTurn(ChessError): pass

FEN_STARTING = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
RANK_REGEX = re.compile(r"^[A-Z][1-8]$")
total_time=0
count_moves=0
class Board(dict):
    '''
       Board

       A simple chessboard class

       TODO:

        * PGN export
        * En passant
        * Castling
        * Promoting pawns
        * Fifty-move rule
    '''

    axis_y = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H')
    axis_x = tuple(range(1,9)) # (1,2,3,...8)

    captured_pieces = { 'white': [], 'black': [] }
    player_turn = None
    castling = '-'
    en_passant = '-'
    halfmove_clock = 0
    fullmove_number = 1
    history = []

    def __init__(self, fen = None):
        if fen is None: self.load(FEN_STARTING)
        else: self.load(fen)

    def __getitem__(self, coord):
        if isinstance(coord, str):
            coord = coord.upper()
            if not re.match(RANK_REGEX, coord.upper()): raise KeyError
        elif isinstance(coord, tuple):
            coord = self.letter_notation(coord)
        try:
            return super(Board, self).__getitem__(coord)
        except KeyError:
            return None

    def save_to_file(self): pass

    def is_in_check_after_move(self, p1, p2):
        # Create a temporary board
        tmp = deepcopy(self)
        tmp._do_move(p1,p2)
        return tmp.is_in_check(self[p1].color)

    def move(self, p1, p2):
        p1, p2 = p1.upper(), p2.upper()
        piece = self[p1]
        dest  = self[p2]

        if self.player_turn != piece.color:
            raise NotYourTurn("Not " + piece.color + "'s turn!")

        enemy = self.get_enemy(piece.color)
        possible_moves = piece.possible_moves(p1)
        # 0. Check if p2 is in the possible moves
        if p2 not in possible_moves:
            raise InvalidMove

      
        if not possible_moves and self.is_in_check(piece.color):
            raise CheckMate
        elif not possible_moves:
            raise Draw
        else:
            self._do_move(p1, p2)
            self._finish_move(piece, dest, p1,p2)

    def get_enemy(self, color):
        if color == "white": return "black"
        else: return "white"

    def _do_move(self, p1, p2):
        '''
            Move a piece without validation
        '''
        piece = self[p1]
        dest  = self[p2]
        del self[p1]
        self[p2] = piece

    def set_next_turn(self,piece):
        enemy = self.get_enemy(piece.color)
        if piece.color == 'black':
            self.fullmove_number += 1
        self.halfmove_clock +=1
        self.player_turn = enemy

    def _finish_move(self, piece, dest, p1, p2):
        '''
            Set next player turn, count moves, log moves, etc.
        '''
        self.set_next_turn(piece)
        abbr = piece.abbriviation
        if abbr == 'P':
            # Pawn has no letter
            abbr = ''
            # Pawn resets halfmove_clock
            self.halfmove_clock = 0
        if dest is None:
            # No capturing
            movetext = abbr +  p2.lower()
        else:
            # Capturing
            movetext = abbr + 'x' + p2.lower()
            # Capturing resets halfmove_clock
            self.halfmove_clock = 0

        self.history.append(movetext)


    def all_possible_moves(self, color):
        '''
            Return a list of `color`'s possible moves.
            Does not check for check.
        '''
        if(color not in ("black", "white")): raise InvalidColor
        result = []
        for coord in self.keys():
            if (self[coord] is not None) and self[coord].color == color:
                moves = self[coord].possible_moves(coord)
                if moves: result += moves
        return result

    #minmax algo
    def minmax(self, count_turns, p1, p2, alpha ,beta):
        #tmp = deepcopy(self)  
       # print p1,p2
        global total_time
        st=time.time()
        self._do_move(p1,p2)
        if count_turns==4:
            value=self.state_value()
            return value
        if count_turns%2==0:
            self.player_turn="white"
            valid_move=self.check()
            for i in range(0,len(valid_move)):
                p3,p4=valid_move[i].split("+")
                piece2=self[p4]
                k=self.minmax(count_turns+1,p3,p4,alpha,beta)
                self.player_turn="white"
                self._do_move(p4, p3)
                if piece2 is not None:
                    self[p4]=piece2
                if k<beta:
                        beta=k
                if alpha>=beta:
                    break;
            return beta
                
        else:
            self.player_turn="black"
            valid_move=self.check()
            for i in range(0,len(valid_move)):
                p3,p4=valid_move[i].split("+")
                piece2=self[p4]
                k=self.minmax(count_turns+1,p3,p4,alpha,beta)
                self.player_turn="black"
                self._do_move(p4, p3)
                if piece2 is not None:
                    self[p4]=piece2
                if k > alpha:
                    alpha=k
                if alpha>=beta:
                    break
            return alpha

    def check(self):
        global total_time
        valid_moves=[]
        v_m=[]
        for i in range (0,8):
            for j in range (0,8):
                pos = self.letter_notation((i,j))
                piece = self[pos]
                if piece is not None and (piece.color == self.player_turn):
                    all_moves=piece.possible_moves(pos)
                    start=time.time()
                    for k in range(0,len(all_moves)):
                        pos1=all_moves[k]
                        valid_moves.append(pos+'+'+pos1)
                        piece2=self[pos1]
                        if piece2 is not None:
                            v_m.append(pos+'+'+pos1) 
                    end = time.time()   
        #print(total_time)
        if len(v_m)>0:
            return v_m
        else:
            return valid_moves
    #state of board
    def state_value(self):
        sum=0
        for i in range (0,8):
            for j in range (0,8):
                pos = self.letter_notation((i,j))
                piece = self[pos]
                if piece is not None:
                    sum+=self.assign_val(piece.abbriviation)
        return sum

    #assign value to piece
    def assign_val(self, piecename):
        value = {
        'R':5,
        'N':3,
        'B':3,
        'Q':9,
        'K':2,
        'P':1,
        'r':-5,
        'n':-3,
        'b':-3,
        'q':-9,
        'k':-2,
        'p':-1
        }
        return value.get(piecename, 0)

    def occupied(self, color):
        '''
            Return a list of coordinates occupied by `color`
        '''
        result = []
        if(color not in ("black", "white")): raise InvalidColor

        for coord in self:
            if self[coord].color == color:
                result.append(coord)
        return result

    def is_king(self, piece):
        return isinstance(piece, pieces.King)


    def get_king_position(self, color):
        for pos in self.keys():
            if self.is_king(self[pos]) and self[pos].color == color:
                return pos

    def get_king(self, color):
        if(color not in ("black", "white")): raise InvalidColor
        return self[self.get_king_position(color)]

    def is_in_check(self, color):
        if(color not in ("black", "white")): raise InvalidColor
        king = self.get_king(color)
        enemy = self.get_enemy(color)
        return king in map(self.__getitem__, self.all_possible_moves(enemy))

    def letter_notation(self,coord):
        if not self.is_in_bounds(coord): return
        try:
            return self.axis_y[coord[1]] + str(self.axis_x[coord[0]])
        except IndexError:
            raise InvalidCoord

    def number_notation(self, coord):
        return int(coord[1])-1, self.axis_y.index(coord[0])

    def is_in_bounds(self, coord):
        if coord[1] < 0 or coord[1] > 7 or\
           coord[0] < 0 or coord[0] > 7:
            return False
        else: return True

    def load(self, fen):
        '''
            Import state from FEN notation
        '''
        self.clear()
        # Split data
        fen = fen.split(' ')
        # Expand blanks
        def expand(match): return ' ' * int(match.group(0))

        fen[0] = re.compile(r'\d').sub(expand, fen[0])

        for x, row in enumerate(fen[0].split('/')):
            for y, letter in enumerate(row):
                if letter == ' ': continue
                coord = self.letter_notation((7-x,y))
                self[coord] = pieces.piece(letter)
                self[coord].place(self)

        if fen[1] == 'w': self.player_turn = 'white'
        else: self.player_turn = 'black'

        self.castling = fen[2]
        self.en_passant = fen[3]
        self.halfmove_clock = int(fen[4])
        self.fullmove_number = int(fen[5])

    def export(self):
        '''
            Export state to FEN notation
        '''
        def join(k, g):
            if k == ' ': return str(len(g))
            else: return "".join(g)

        def replace_spaces(row):
            # replace spaces with their count
            result = [join(k, list(g)) for k,g in groupby(row)]
            return "".join(result)


        result = ''
        for number in self.axis_x[::-1]:
            for letter in self.axis_y:
                piece = self[letter+str(number)]
                if piece is not None:
                    result += piece.abbriviation
                else: result += ' '
            result += '/'

        result = result[:-1] # remove trailing "/"
        result = replace_spaces(result)
        result += " " + (" ".join([self.player_turn[0],
                         self.castling,
                         self.en_passant,
                         str(self.halfmove_clock),
                         str(self.fullmove_number)]))
        return result
