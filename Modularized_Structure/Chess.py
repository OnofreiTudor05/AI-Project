from Piece import Piece
import sys
import copy
import pygame
import random
import numpy as np


class Chess:
    def __init__(self):
        pygame.display.set_caption("Chess")
        pygame.font.init()
        self.white_king_has_moved = 0
        self.left_white_rook_has_moved = 0
        self.right_white_rook_has_moved = 0
        self.black_king_has_moved = 0
        self.left_black_rook_has_moved = 0
        self.right_black_rook_has_moved = 0
        self.black_en_passant = 0
        self.white_en_passant = 0
        self.draw = 0
        self.move_counter = 0
        self.see_me = 'n'
        self.PATH = 'resources\\'
        self.visited_vector = [0. for i in range(0, 500)]
        self.score_vector = [0. for i in range(0, 500)]
        self.nodes_counter_in_mcts = 0
        self.queue_message = []
        self.last_shown_message_index = 0
        self.draw = False
        self.black_won = False
        self.white_won = False
        self.stalemate = False
        self.white_king_has_moved = False
        self.left_white_rook_has_moved = False
        self.right_white_rook_has_moved = False
        self.black_king_has_moved = False
        self.left_black_rook_has_moved = False
        self.right_black_rook_has_moved = False
        self.game_states = {}
        self.black_en_passant, self.white_en_passant = [False for i in range(0, 8)], [False for i in range(0, 8)]
        self.count = 0
        self.black_color = (129, 73, 0)
        self.white_color = (255, 235, 156)
        self.window_width = 800
        self.window_height = 800
        self.down_arrow = pygame.image.load(self.PATH + "down.png")
        self.down_arrow = pygame.transform.scale(self.down_arrow, (45, 45))
        self.up_arrow = pygame.image.load(self.PATH + "up.png")
        self.up_arrow = pygame.transform.scale(self.up_arrow, (45, 45))
        self.black = pygame.image.load(self.PATH + "black.png")
        self.size = (self.window_height, self.window_width)
        self.screen = pygame.display.set_mode(self.size)
        self.width = 50
        self.board = [[Piece(None, None, None, False, False, 0, 0, 0) for i in range(0, 8)] for j in range(0, 8)]
        self.board_black = [[Piece(None, None, None, False, False, 0, 0, 0) for i in range(0, 8)] for j in range(0, 8)]
        self.build_starting_board(self.width)
        self.pieces = {'bP': pygame.image.load(self.PATH + 'bP.svg'), 'bR': pygame.image.load(self.PATH + 'bR.svg'),
                       'bN': pygame.image.load(self.PATH + 'bN.svg'),
                       'bB': pygame.image.load(self.PATH + 'bB.svg'),
                       'bQ': pygame.image.load(self.PATH + 'bQ.svg'), 'bK': pygame.image.load(self.PATH + 'bK.svg'),
                       'wP': pygame.image.load(self.PATH + 'wP.svg'), 'wR': pygame.image.load(self.PATH + 'wR.svg'),
                       'wN': pygame.image.load(self.PATH + 'wN.svg'),
                       'wB': pygame.image.load(self.PATH + 'wB.svg'),
                       'wQ': pygame.image.load(self.PATH + 'wQ.svg'), 'wK': pygame.image.load(self.PATH + 'wK.svg')}

        self.note_table = [[0, 0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0, 0],
                           [0, 1, 2, 3, 4, 5, 6, 7]]

        self.selected = False
        self.moves = 0
        self.piece_to_move = []
        self.possible = []
        self.current_note_piece = 0
        self.M_white = [[[[0 for i in range(0, 8)] for i in range(0, 8)] for i in range(0, 100)] for i in range(0, 3)]
        self.M_black = [[[[0 for i in range(0, 8)] for i in range(0, 8)] for i in range(0, 100)] for i in range(0, 3)]

    def create_random_matrix(self):
        self.M_white = np.random.uniform(size=np.shape(self.M_white))
        self.M_black = np.random.uniform(size=np.shape(self.M_black))

    def build_starting_board(self, width):
        """initialises the board"""

        self.board[0][0] = Piece('b', 'r', 'bR', False, True, 0, 0, width)
        self.board[0][1] = Piece('b', 'n', 'bN', False, True, 0, 1, width)
        self.board[0][2] = Piece('b', 'b', 'bB', False, True, 0, 2, width)
        self.board[0][3] = Piece('b', 'k', 'bK', False, True, 0, 3, width)
        self.board[0][4] = Piece('b', 'q', 'bQ', False, True, 0, 4, width)
        self.board[0][5] = Piece('b', 'b', 'bB', False, True, 0, 5, width)
        self.board[0][6] = Piece('b', 'n', 'bN', False, True, 0, 6, width)
        self.board[0][7] = Piece('b', 'r', 'bR', False, True, 0, 7, width)
        for i in range(0, 8):
            self.board[1][i] = Piece('b', 'p', 'bP', False, True, 1, i, width)
        for i in range(2, 6):
            for j in range(0, 8):
                self.board[i][j] = Piece(None, None, None, False, False, i, j, width)
        for i in range(0, 8):
            self.board[6][i] = Piece('w', 'p', 'wP', False, True, 6, i, width)
        self.board[7][0] = Piece('w', 'r', 'wR', False, True, 7, 0, width)
        self.board[7][1] = Piece('w', 'n', 'wN', False, True, 7, 1, width)
        self.board[7][2] = Piece('w', 'b', 'wB', False, True, 7, 2, width)
        self.board[7][3] = Piece('w', 'k', 'wK', False, True, 7, 3, width)
        self.board[7][4] = Piece('w', 'q', 'wQ', False, True, 7, 4, width)
        self.board[7][5] = Piece('w', 'b', 'wB', False, True, 7, 5, width)
        self.board[7][6] = Piece('w', 'n', 'wN', False, True, 7, 6, width)
        self.board[7][7] = Piece('w', 'r', 'wR', False, True, 7, 7, width)

    def get_white_king_position(self):
        """returns a pair of integers, coordinates of the white king"""
        for i in range(0, 8):
            for j in range(0, 8):
                if self.board[i][j].info['color'] == 'w' \
                        and self.board[i][j].info['type'] == 'k':
                    return i, j

    def get_black_king_position(self):
        """returns a pairs of integers, coordinates of the black king"""
        for i in range(0, 8):
            for j in range(0, 8):
                if self.board[i][j].info['color'] == 'b' \
                        and self.board[i][j].info['type'] == 'k':
                    return i, j
        sys.exit()

    def inside_board(self, x_, y_):
        """ check a pair of coordinates is within the borders """
        if 0 <= x_ <= 7 and 0 <= y_ <= 7:
            return True
        return False

    def is_white_checked(self, pos_, moves_):
        """returns True if the king's position is attacked by another piece"""
        possible_moves = []
        moves_ += 1
        for i in range(0, 8):
            for j in range(0, 8):
                if self.board[i][j].info['color'] == 'b':
                    if self.board[i][j].info['type'] == 'k':
                        possible_moves.extend(self.king_to_move((i, j), moves_))
                    if self.board[i][j].info['type'] == 'b':
                        possible_moves.extend(self.bishop_to_move((i, j), moves_))
                    if self.board[i][j].info['type'] == 'n':
                        possible_moves.extend(self.knight_to_move((i, j), moves_))
                    if self.board[i][j].info['type'] == 'q':
                        possible_moves.extend(self.queen_to_move((i, j), moves_))
                    if self.board[i][j].info['type'] == 'r':
                        possible_moves.extend(self.rook_to_move((i, j), moves_))
                    if self.board[i][j].info['type'] == 'p':
                        possible_moves.extend(self.black_pawn_to_move((i, j), moves_))

        for i in possible_moves:
            if i == pos_:
                return True
        return False

    def simulate_move(self, from_, to_, moves_):
        """return True if moving piece from from_ to to_ is a valid move, i.e it doesnt discover the king"""
        board2 = copy.deepcopy(self.board)
        self.board[to_[0]][to_[1]].update('type', self.board[from_[0]][from_[1]].info['type'])
        self.board[from_[0]][from_[1]].update('type', None)
        self.board[to_[0]][to_[1]].update('color', self.board[from_[0]][from_[1]].info['color'])
        self.board[from_[0]][from_[1]].update('color', None)
        self.board[to_[0]][to_[1]].update('image', self.board[from_[0]][from_[1]].info['image'])
        self.board[from_[0]][from_[1]].update('image', None)
        self.board[to_[0]][to_[1]].update('occupied', True)
        self.board[from_[0]][from_[1]].update('occupied', False)
        self.board[to_[0]][to_[1]].update('killable', False)
        self.board[from_[0]][from_[1]].update('killable', False)
        if moves_ % 2 == 0:
            if self.is_white_checked(self.get_white_king_position(), moves_):
                board = copy.deepcopy(board2)
                return False
        if moves_ % 2 == 1:
            if self.is_black_checked(self.get_black_king_position(), moves_):
                board = copy.deepcopy(board2)
                return False
        board = copy.deepcopy(board2)
        return True

    def king_to_move2(self, pos_, moves_):
        """ return valid positions available for the king located in pos_ """
        possible_ = []
        di = [-1, -1, -1, 0, 1, 1, 1, 0]
        dj = [-1, 0, 1, -1, -1, 0, 1, 1]
        for d in range(0, len(di)):
            new_x = pos_[0] + di[d]
            new_y = pos_[1] + dj[d]
            if moves_ % 2 == 1:
                if self.inside_board(new_x, new_y) and self.board[new_x][new_y].info['color'] != 'b':
                    if self.simulate_move(pos_, (new_x, new_y), moves_):
                        possible_.append((new_x, new_y))
            else:
                if self.inside_board(new_x, new_y) and self.board[new_x][new_y].info['color'] != 'w':
                    if self.simulate_move(pos_, (new_x, new_y), moves_):
                        possible_.append((new_x, new_y))
        return possible_

    def king_to_move(self, pos_, moves_):
        """ return threatened positions available for the king located in pos_ """
        possible_ = []
        di = [-1, -1, -1, 0, 1, 1, 1, 0]
        dj = [-1, 0, 1, -1, -1, 0, 1, 1]
        for d in range(0, len(di)):
            new_x = pos_[0] + di[d]
            new_y = pos_[1] + dj[d]
            if moves_ % 2 == 1:
                if self.inside_board(new_x, new_y) and self.board[new_x][new_y].info['color'] != 'b':
                    possible_.append((new_x, new_y))
            else:
                if self.inside_board(new_x, new_y) and self.board[new_x][new_y].info['color'] != 'w':
                    possible_.append((new_x, new_y))
        return possible_

    def is_black_checked2(self, pos_, moves_):
        """returns True if the king's position is attacked by another piece"""
        moves_ += 1
        possible_moves = []
        for i in range(0, 8):
            for j in range(0, 8):
                if self.board[i][j].info['color'] == 'w':
                    if self.board[i][j].info['type'] == 'k':
                        possible_moves.extend(self.king_to_move2((i, j), moves_))
                    if self.board[i][j].info['type'] == 'b':
                        possible_moves.extend(self.bishop_to_move2((i, j), moves_))
                    if self.board[i][j].info['type'] == 'n':
                        possible_moves.extend(self.knight_to_move2((i, j), moves_))
                    if self.board[i][j].info['type'] == 'q':
                        possible_moves.extend(self.queen_to_move2((i, j), moves_))
                    if self.board[i][j].info['type'] == 'r':
                        possible_moves.extend(self.rook_to_move2((i, j), moves_))
                    if self.board[i][j].info['type'] == 'p':
                        possible_moves.extend(self.white_pawn_to_move2((i, j), moves_))

        for i in possible_moves:
            if i == pos_:
                return True
        return False

    def is_black_checked(self, pos_, moves_):
        """returns True if the king's position is attacked by another piece"""
        moves_ += 1
        possible_moves = []
        for i in range(0, 8):
            for j in range(0, 8):
                if self.board[i][j].info['color'] == 'w':
                    if self.board[i][j].info['type'] == 'k':
                        possible_moves.extend(self.king_to_move((i, j), moves_))
                    if self.board[i][j].info['type'] == 'b':
                        possible_moves.extend(self.bishop_to_move((i, j), moves_))
                    if self.board[i][j].info['type'] == 'n':
                        possible_moves.extend(self.knight_to_move((i, j), moves_))
                    if self.board[i][j].info['type'] == 'q':
                        possible_moves.extend(self.queen_to_move((i, j), moves_))
                    if self.board[i][j].info['type'] == 'r':
                        possible_moves.extend(self.rook_to_move((i, j), moves_))
                    if self.board[i][j].info['type'] == 'p':
                        possible_moves.extend(self.white_pawn_to_move((i, j), moves_))

        for i in possible_moves:
            if i == pos_:
                return True
        return False

    def is_white_checked2(self, pos_, moves_):
        """returns True if the king's position is attacked by another piece"""
        possible_moves = []
        moves_ += 1
        for i in range(0, 8):
            for j in range(0, 8):
                if self.board[i][j].info['color'] == 'b':
                    if self.board[i][j].info['type'] == 'k':
                        possible_moves.extend(self.king_to_move2((i, j), moves_))
                    if self.board[i][j].info['type'] == 'b':
                        possible_moves.extend(self.bishop_to_move2((i, j), moves_))
                    if self.board[i][j].info['type'] == 'n':
                        possible_moves.extend(self.knight_to_move2((i, j), moves_))
                    if self.board[i][j].info['type'] == 'q':
                        possible_moves.extend(self.queen_to_move2((i, j), moves_))
                    if self.board[i][j].info['type'] == 'r':
                        possible_moves.extend(self.rook_to_move2((i, j), moves_))
                    if self.board[i][j].info['type'] == 'p':
                        possible_moves.extend(self.black_pawn_to_move2((i, j), moves_))

        for i in possible_moves:
            if i == pos_:
                return True
        return False

    def bishop_to_move(self, pos_, moves_):
        """ return threatened positions available for the bishop located in pos_ """
        possible_ = []
        x_, y_ = pos_
        for i in range(1, 8):
            new_x = x_ + i
            new_y = y_ + i
            if (not self.inside_board(new_x, new_y) or
                self.board[new_x][new_y].info['color'] == 'b' and moves_ % 2 == 1) \
                    or (self.board[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
                break
            possible_.append((new_x, new_y))
            if self.board[new_x][new_y].info['occupied']:
                break
        for i in range(1, 8):
            new_x = x_ - i
            new_y = y_ + i
            if (not self.inside_board(new_x, new_y) or self.board[new_x][new_y].info['color'] == 'b'
                and moves_ % 2 == 1) \
                    or (self.board[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
                break
            possible_.append((new_x, new_y))
            if self.board[new_x][new_y].info['occupied']:
                break
        for i in range(1, 8):
            new_x = x_ + i
            new_y = y_ - i
            if (not self.inside_board(new_x, new_y) or self.board[new_x][new_y].info['color'] == 'b'
                and moves_ % 2 == 1) \
                    or (self.board[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
                break
            possible_.append((new_x, new_y))
            if self.board[new_x][new_y].info['occupied']:
                break
        for i in range(1, 8):
            new_x = x_ - i
            new_y = y_ - i
            if (not self.inside_board(new_x, new_y) or self.board[new_x][new_y].info['color'] == 'b'
                and moves_ % 2 == 1) \
                    or (self.board[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
                break
            possible_.append((new_x, new_y))
            if self.board[new_x][new_y].info['occupied']:
                break
        return possible_

    def knight_to_move(self, pos_, moves_):
        """ return threatened positions available for the knight located in pos_ """
        possible_ = []
        di = [-1, -1, 1, 1, -2, -2, 2, 2]
        dj = [2, -2, -2, 2, -1, 1, -1, 1]
        for d in range(0, len(di)):
            new_x = pos_[0] + di[d]
            new_y = pos_[1] + dj[d]
            if moves_ % 2 == 1:
                if self.inside_board(new_x, new_y) and self.board[new_x][new_y].info['color'] != 'b':
                    possible_.append((new_x, new_y))
            else:
                if self.inside_board(new_x, new_y) and self.board[new_x][new_y].info['color'] != 'w':
                    possible_.append((new_x, new_y))
        return possible_

    def queen_to_move(self, pos_, moves_):
        """ return threatened positions available for the queen located in pos_ """
        possible_ = set()
        x_, y_ = pos_
        for i in range(1, 8):
            new_x = x_ + i
            new_y = y_ + i
            if (not self.inside_board(new_x, new_y) or self.board[new_x][new_y].info['color'] == 'b'
                and moves_ % 2 == 1) \
                    or (self.board[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
                break
            possible_.add((new_x, new_y))
            if self.board[new_x][new_y].info['occupied']:
                break
        for i in range(1, 8):
            new_x = x_ - i
            new_y = y_ + i
            if (not self.inside_board(new_x, new_y) or self.board[new_x][new_y].info['color'] == 'b'
                and moves_ % 2 == 1) \
                    or (self.board[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
                break
            possible_.add((new_x, new_y))
            if self.board[new_x][new_y].info['occupied']:
                break
        for i in range(1, 8):
            new_x = x_ + i
            new_y = y_ - i
            if (not self.inside_board(new_x, new_y) or self.board[new_x][new_y].info['color'] == 'b'
                and moves_ % 2 == 1) \
                    or (self.board[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
                break
            possible_.add((new_x, new_y))

            if self.board[new_x][new_y].info['occupied']:
                break
        for i in range(1, 8):
            new_x = x_ - i
            new_y = y_ - i
            if (not self.inside_board(new_x, new_y) or self.board[new_x][new_y].info['color'] == 'b'
                and moves_ % 2 == 1) \
                    or (self.board[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
                break
            possible_.add((new_x, new_y))
            if self.board[new_x][new_y].info['occupied']:
                break
        for x_2 in range(x_ + 1, 8, 1):
            if (self.board[x_2][y_].info['color'] == 'b' and moves_ % 2 == 1) or (
                    self.board[x_2][y_].info['color'] == 'w' and moves_ % 2 == 0):
                break
            possible_.add((x_2, y_))
            if self.board[x_2][y_].info['occupied']:
                break
        for x_2 in range(x_ - 1, -1, -1):
            if (self.board[x_2][y_].info['color'] == 'b' and moves_ % 2 == 1) or (
                    self.board[x_2][y_].info['color'] == 'w' and moves_ % 2 == 0):
                break
            possible_.add((x_2, y_))
            if self.board[x_2][y_].info['occupied']:
                break
        for y_2 in range(y_ + 1, 8, 1):
            if (self.board[x_][y_2].info['color'] == 'b' and moves_ % 2 == 1) or (
                    self.board[x_][y_2].info['color'] == 'w' and moves_ % 2 == 0):
                break
            possible_.add((x_, y_2))
            if self.board[x_][y_2].info['occupied']:
                break
        for y_2 in range(y_ - 1, -1, -1):
            if (self.board[x_][y_2].info['color'] == 'b' and moves_ % 2 == 1) \
                    or (self.board[x_][y_2].info['color'] == 'w' and moves_ % 2 == 0):
                break
            possible_.add((x_, y_2))
            if self.board[x_][y_2].info['occupied']:
                break

        return list(possible_)

    def rook_to_move(self, pos_, moves_):
        """ return threatened positions available for the rook located in pos_ """
        possible_ = []
        x_, y_ = pos_
        for x_2 in range(x_ + 1, 8, 1):
            if (self.board[x_2][y_].info['color'] == 'b' and moves_ % 2 == 1) or (
                    self.board[x_2][y_].info['color'] == 'w' and moves_ % 2 == 0):
                break
            possible_.append((x_2, y_))
            if self.board[x_2][y_].info['occupied']:
                break
        for x_2 in range(x_ - 1, -1, -1):
            if (self.board[x_2][y_].info['color'] == 'b' and moves_ % 2 == 1) or (
                    self.board[x_2][y_].info['color'] == 'w' and moves_ % 2 == 0):
                break
            possible_.append((x_2, y_))
            if self.board[x_2][y_].info['occupied']:
                break
        for y_2 in range(y_ + 1, 8, 1):
            if (self.board[x_][y_2].info['color'] == 'b' and moves_ % 2 == 1) or (
                    self.board[x_][y_2].info['color'] == 'w' and moves_ % 2 == 0):
                break
            possible_.append((x_, y_2))
            if self.board[x_][y_2].info['occupied']:
                break
        for y_2 in range(y_ - 1, -1, -1):
            if (self.board[x_][y_2].info['color'] == 'b' and moves_ % 2 == 1) or (
                    self.board[x_][y_2].info['color'] == 'w' and moves_ % 2 == 0):
                break
            possible_.append((x_, y_2))
            if self.board[x_][y_2].info['occupied']:
                break

        return possible_

    def black_pawn_to_move(self, pos_, moves_):
        """ return threatened positions available for the pawn located in pos_ """
        x_, y_ = pos_
        possible_ = []
        if self.inside_board(x_ + 1, y_) and not self.board[x_ + 1][y_].info['occupied']:
            possible_.append((x_ + 1, y_))
        if self.inside_board(x_ + 2, y_) and (not self.board[x_ + 1][y_].info['occupied']) \
                and (not self.board[x_ + 2][y_].info['occupied']) and (x_ == 1):
            possible_.append((x_ + 2, y_))

        if self.inside_board(x_ + 1, y_ + 1) and self.board[x_ + 1][y_ + 1].info['occupied'] \
                and (self.board[x_ + 1][y_ + 1].info['color'] == 'w'):
            possible_.append((x_ + 1, y_ + 1))
        if self.inside_board(x_ + 1, y_ - 1) and self.board[x_ + 1][y_ - 1].info['occupied'] \
                and (self.board[x_ + 1][y_ - 1].info['color'] == 'w'):
            possible_.append((x_ + 1, y_ - 1))
        return possible_

    def bishop_to_move2(self, pos_, moves_):
        """ return valid positions available for the bishop located in pos_ """
        possible_ = []
        x_, y_ = pos_
        for i in range(1, 8):
            new_x = x_ + i
            new_y = y_ + i
            if (not self.inside_board(new_x, new_y) or self.board[new_x][new_y].info['color'] == 'b'
                and moves_ % 2 == 1) or (self.board[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
                break
            if self.simulate_move(pos_, (new_x, new_y), moves_):
                possible_.append((new_x, new_y))
            if self.board[new_x][new_y].info['occupied']:
                break
        for i in range(1, 8):
            new_x = x_ - i
            new_y = y_ + i
            if (not self.inside_board(new_x, new_y) or self.board[new_x][new_y].info['color'] == 'b'
                and moves_ % 2 == 1) or (self.board[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
                break
            if self.simulate_move(pos_, (new_x, new_y), moves_):
                possible_.append((new_x, new_y))
            if self.board[new_x][new_y].info['occupied']:
                break
        for i in range(1, 8):
            new_x = x_ + i
            new_y = y_ - i
            if (not self.inside_board(new_x, new_y) or self.board[new_x][new_y].info['color'] == 'b'
                and moves_ % 2 == 1) or (self.board[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
                break
            if self.simulate_move(pos_, (new_x, new_y), moves_):
                possible_.append((new_x, new_y))
            if self.board[new_x][new_y].info['occupied']:
                break
        for i in range(1, 8):
            new_x = x_ - i
            new_y = y_ - i
            if (not self.inside_board(new_x, new_y) or self.board[new_x][new_y].info['color'] == 'b'
                and moves_ % 2 == 1) or (self.board[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
                break
            if self.simulate_move(pos_, (new_x, new_y), moves_):
                possible_.append((new_x, new_y))
            if self.board[new_x][new_y].info['occupied']:
                break
        return possible_

    def knight_to_move2(self, pos_, moves_):
        """ return valid positions available for the knight located in pos_ """
        possible_ = []
        di = [-1, -1, 1, 1, -2, -2, 2, 2]
        dj = [2, -2, -2, 2, -1, 1, -1, 1]
        for d in range(0, len(di)):
            new_x = pos_[0] + di[d]
            new_y = pos_[1] + dj[d]
            if moves_ % 2 == 1:
                if self.inside_board(new_x, new_y) and self.board[new_x][new_y].info['color'] != 'b':
                    if self.simulate_move(pos_, (new_x, new_y), moves_):
                        possible_.append((new_x, new_y))
            else:
                if self.inside_board(new_x, new_y) and self.board[new_x][new_y].info['color'] != 'w':
                    if self.simulate_move(pos_, (new_x, new_y), moves_):
                        possible_.append((new_x, new_y))
        return possible_

    def queen_to_move2(self, pos_, moves_):
        """ return valid positions available for the queen located in pos_ """
        possible_ = set()
        x_, y_ = pos_
        for i in range(1, 8):
            new_x = x_ + i
            new_y = y_ + i
            if (not self.inside_board(new_x, new_y) or self.board[new_x][new_y].info['color'] == 'b'
                and moves_ % 2 == 1) or (self.board[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
                break
            if self.simulate_move(pos_, (new_x, new_y), moves_):
                possible_.add((new_x, new_y))
            if self.board[new_x][new_y].info['occupied']:
                break
        for i in range(1, 8):
            new_x = x_ - i
            new_y = y_ + i
            if (not self.inside_board(new_x, new_y) or self.board[new_x][new_y].info['color'] == 'b'
                and moves_ % 2 == 1) or (self.board[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
                break
            if self.simulate_move(pos_, (new_x, new_y), moves_):
                possible_.add((new_x, new_y))
            if self.board[new_x][new_y].info['occupied']:
                break
        for i in range(1, 8):
            new_x = x_ + i
            new_y = y_ - i
            if (not self.inside_board(new_x, new_y) or self.board[new_x][new_y].info['color'] == 'b'
                and moves_ % 2 == 1) or (self.board[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
                break
            if self.simulate_move(pos_, (new_x, new_y), moves_):
                possible_.add((new_x, new_y))

            if self.board[new_x][new_y].info['occupied']:
                break
        for i in range(1, 8):
            new_x = x_ - i
            new_y = y_ - i
            if (not self.inside_board(new_x, new_y) or self.board[new_x][new_y].info['color'] == 'b'
                and moves_ % 2 == 1) or (self.board[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
                break
            if self.simulate_move(pos_, (new_x, new_y), moves_):
                possible_.add((new_x, new_y))
            if self.board[new_x][new_y].info['occupied']:
                break
        for x_2 in range(x_ + 1, 8, 1):
            if (self.board[x_2][y_].info['color'] == 'b' and moves_ % 2 == 1) or (
                    self.board[x_2][y_].info['color'] == 'w' and moves_ % 2 == 0):
                break
            if self.simulate_move(pos_, (x_2, y_), moves_):
                possible_.add((x_2, y_))
            if self.board[x_2][y_].info['occupied']:
                break
        for x_2 in range(x_ - 1, -1, -1):
            if (self.board[x_2][y_].info['color'] == 'b' and moves_ % 2 == 1) or (
                    self.board[x_2][y_].info['color'] == 'w' and moves_ % 2 == 0):
                break
            if self.simulate_move(pos_, (x_2, y_), moves_):
                possible_.add((x_2, y_))
            if self.board[x_2][y_].info['occupied']:
                break
        for y_2 in range(y_ + 1, 8, 1):
            if (self.board[x_][y_2].info['color'] == 'b' and moves_ % 2 == 1) or (
                    self.board[x_][y_2].info['color'] == 'w' and moves_ % 2 == 0):
                break
            if self.simulate_move(pos_, (x_, y_2), moves_):
                possible_.add((x_, y_2))
            if self.board[x_][y_2].info['occupied']:
                break
        for y_2 in range(y_ - 1, -1, -1):
            if (self.board[x_][y_2].info['color'] == 'b' and moves_ % 2 == 1) or (
                    self.board[x_][y_2].info['color'] == 'w' and moves_ % 2 == 0):
                break
            if self.simulate_move(pos_, (x_, y_2), moves_):
                possible_.add((x_, y_2))
            if self.board[x_][y_2].info['occupied']:
                break

        return list(possible_)

    def rook_to_move2(self, pos_, moves_):
        """ return valid positions available for the rook located in pos_ """
        possible_ = []
        x_, y_ = pos_
        for x_2 in range(x_ + 1, 8, 1):
            if (self.board[x_2][y_].info['color'] == 'b' and moves_ % 2 == 1) or (
                    self.board[x_2][y_].info['color'] == 'w' and moves_ % 2 == 0):
                break
            if self.simulate_move(pos_, (x_2, y_), moves_):
                possible_.append((x_2, y_))
            if self.board[x_2][y_].info['occupied']:
                break
        for x_2 in range(x_ - 1, -1, -1):
            if (self.board[x_2][y_].info['color'] == 'b' and moves_ % 2 == 1) \
                    or (self.board[x_2][y_].info['color'] == 'w' and moves_ % 2 == 0):
                break
            if self.simulate_move(pos_, (x_2, y_), moves_):
                possible_.append((x_2, y_))
            if self.board[x_2][y_].info['occupied']:
                break
        for y_2 in range(y_ + 1, 8, 1):
            if (self.board[x_][y_2].info['color'] == 'b' and moves_ % 2 == 1) \
                    or (self.board[x_][y_2].info['color'] == 'w' and moves_ % 2 == 0):
                break
            if self.simulate_move(pos_, (x_, y_2), moves_):
                possible_.append((x_, y_2))
            if self.board[x_][y_2].info['occupied']:
                break
        for y_2 in range(y_ - 1, -1, -1):
            if (self.board[x_][y_2].info['color'] == 'b' and moves_ % 2 == 1) \
                    or (self.board[x_][y_2].info['color'] == 'w' and moves_ % 2 == 0):
                break
            if self.simulate_move(pos_, (x_, y_2), moves_):
                possible_.append((x_, y_2))
            if self.board[x_][y_2].info['occupied']:
                break
        return possible_

    def white_pawn_to_move2(self, pos_, moves_):
        """ return valid positions available for the pawn located in pos_ """
        x_, y_ = pos_
        possible_ = []
        if self.inside_board(x_ - 1, y_) and not self.board[x_ - 1][y_].info['occupied']:
            if self.simulate_move(pos_, (x_ - 1, y_), moves_):
                possible_.append((x_ - 1, y_))
        if self.inside_board(x_ - 2, y_) and (not self.board[x_ - 1][y_].info['occupied']) \
                and (not self.board[x_ - 2][y_].info['occupied']) and (x_ == 6):
            if self.simulate_move(pos_, (x_ - 2, y_), moves_):
                possible_.append((x_ - 2, y_))
        if self.inside_board(x_ - 1, y_ + 1) and self.board[x_ - 1][y_ + 1].info['occupied'] \
                and (self.board[x_ - 1][y_ + 1].info['color'] == 'b'):
            if self.simulate_move(pos_, (x_ - 1, y_ + 1), moves_):
                possible_.append((x_ - 1, y_ + 1))

        if self.inside_board(x_ - 1, y_ - 1) and self.board[x_ - 1][y_ - 1].info['occupied'] \
                and (self.board[x_ - 1][y_ - 1].info['color'] == 'b'):
            if self.simulate_move(pos_, (x_ - 1, y_ - 1), moves_):
                possible_.append((x_ - 1, y_ - 1))
        return possible_

    def black_pawn_to_move2(self, pos_, moves_):
        """ return valid positions available for the pawn located in pos_ """
        x_, y_ = pos_
        possible_ = []
        if self.inside_board(x_ + 1, y_) and not self.board[x_ + 1][y_].info['occupied']:
            if self.simulate_move(pos_, (x_ + 1, y_), moves_):
                possible_.append((x_ + 1, y_))
        if self.inside_board(x_ + 2, y_) and (not self.board[x_ + 1][y_].info['occupied']) \
                and (not self.board[x_ + 2][y_].info['occupied']) and (x_ == 1):
            if self.simulate_move(pos_, (x_ + 2, y_), moves_):
                possible_.append((x_ + 2, y_))

        if self.inside_board(x_ + 1, y_ + 1) and self.board[x_ + 1][y_ + 1].info['occupied'] \
                and (self.board[x_ + 1][y_ + 1].info['color'] == 'w'):
            if self.simulate_move(pos_, (x_ + 1, y_ + 1), moves_):
                possible_.append((x_ + 1, y_ + 1))
        if self.inside_board(x_ + 1, y_ - 1) and self.board[x_ + 1][y_ - 1].info['occupied'] \
                and (self.board[x_ + 1][y_ - 1].info['color'] == 'w'):
            if self.simulate_move(pos_, (x_ + 1, y_ - 1), moves_):
                possible_.append((x_ + 1, y_ - 1))
        return possible_

    def white_pawn_to_move(self, pos_, moves_):
        """ return threatened positions available for the pawn located in pos_ """
        x_, y_ = pos_
        possible_ = []
        if self.inside_board(x_ - 1, y_) and not self.board[x_ - 1][y_].info['occupied']:
            possible_.append((x_ - 1, y_))
        if self.inside_board(x_ - 2, y_) and (not self.board[x_ - 1][y_].info['occupied']) \
                and (not self.board[x_ - 2][y_].info['occupied']) and (x_ == 6):
            possible_.append((x_ - 2, y_))
        if self.inside_board(x_ - 1, y_ + 1) and self.board[x_ - 1][y_ + 1].info['occupied'] \
                and (self.board[x_ - 1][y_ + 1].info['color'] == 'b'):
            possible_.append((x_ - 1, y_ + 1))
        if self.inside_board(x_ - 1, y_ - 1) and self.board[x_ - 1][y_ - 1].info['occupied'] and \
                (self.board[x_ - 1][y_ - 1].info['color'] == 'b'):
            possible_.append((x_ - 1, y_ - 1))
        return possible_

    def bishop_to_move2_black(self, pos_, moves_):
        """ return valid positions available for the bishop located in pos_ """
        possible_ = []
        x_, y_ = pos_
        for i in range(1, 8):
            new_x = x_ + i
            new_y = y_ + i
            if (not self.inside_board(new_x, new_y) or self.board_black[new_x][new_y].info['color'] == 'b' and
                moves_ % 2 == 1) or (self.board_black[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
                break
            possible_.append((new_x, new_y))
            if self.board_black[new_x][new_y].info['occupied']:
                break
        for i in range(1, 8):
            new_x = x_ - i
            new_y = y_ + i
            if (not self.inside_board(new_x, new_y) or self.board_black[new_x][new_y].info['color'] == 'b'
                and moves_ % 2 == 1) or (self.board_black[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
                break
            possible_.append((new_x, new_y))
            if self.board_black[new_x][new_y].info['occupied']:
                break
        for i in range(1, 8):
            new_x = x_ + i
            new_y = y_ - i
            if (not self.inside_board(new_x, new_y) or self.board_black[new_x][new_y].info['color'] == 'b'
                and moves_ % 2 == 1) or (self.board_black[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
                break
            possible_.append((new_x, new_y))
            if self.board_black[new_x][new_y].info['occupied']:
                break
        for i in range(1, 8):
            new_x = x_ - i
            new_y = y_ - i
            if (not self.inside_board(new_x, new_y) or self.board_black[new_x][new_y].info['color'] == 'b'
                and moves_ % 2 == 1) or (self.board_black[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
                break
            possible_.append((new_x, new_y))
            if self.board_black[new_x][new_y].info['occupied']:
                break
        return possible_

    def build_starting_board2(self, width):
        """initialises the board"""
        self.board_black[0][0] = Piece('b', 'r', 'bR', False, True, 0, 0, width)
        self.board_black[0][1] = Piece('b', 'n', 'bN', False, True, 0, 1, width)
        self.board_black[0][2] = Piece('b', 'b', 'bB', False, True, 0, 2, width)
        self.board_black[0][3] = Piece('b', 'k', 'bK', False, True, 0, 3, width)
        self.board_black[0][4] = Piece('b', 'q', 'bQ', False, True, 0, 4, width)
        self.board_black[0][5] = Piece('b', 'b', 'bB', False, True, 0, 5, width)
        self.board_black[0][6] = Piece('b', 'n', 'bN', False, True, 0, 6, width)
        self.board_black[0][7] = Piece('b', 'r', 'bR', False, True, 0, 7, width)
        for i in range(0, 8):
            self.board_black[1][i] = Piece('b', 'p', 'bP', False, True, 1, i, width)
        for i in range(2, 6):
            for j in range(0, 8):
                self.board_black[i][j] = Piece(None, None, None, False, False, i, j, width)
        for i in range(0, 8):
            self.board_black[6][i] = Piece(None, None, None, False, False, 6, i, width)
        self.board_black[7][0] = Piece(None, None, None, False, False, 7, 0, width)
        self.board_black[7][1] = Piece(None, None, None, False, False, 7, 1, width)
        self.board_black[7][2] = Piece(None, None, None, False, False, 7, 2, width)
        self.board_black[7][3] = Piece(None, None, None, False, False, 7, 3, width)
        self.board_black[7][4] = Piece(None, None, None, False, False, 7, 4, width)
        self.board_black[7][5] = Piece(None, None, None, False, False, 7, 5, width)
        self.board_black[7][6] = Piece(None, None, None, False, False, 7, 6, width)
        self.board_black[7][7] = Piece(None, None, None, False, False, 7, 7, width)

    def queen_to_move2_black(self, pos_, moves_):
        """ return valid positions available for the queen located in pos_ """
        possible_ = set()
        x_, y_ = pos_
        for i in range(1, 8):
            new_x = x_ + i
            new_y = y_ + i
            if (not self.inside_board(new_x, new_y) or self.board_black[new_x][new_y].info['color'] == 'b'
                and moves_ % 2 == 1) or (self.board_black[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
                break
            possible_.add((new_x, new_y))
            if self.board_black[new_x][new_y].info['occupied']:
                break
        for i in range(1, 8):
            new_x = x_ - i
            new_y = y_ + i
            if (not self.inside_board(new_x, new_y) or self.board_black[new_x][new_y].info['color'] == 'b'
                and moves_ % 2 == 1) or (self.board_black[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
                break
            possible_.add((new_x, new_y))
            if self.board_black[new_x][new_y].info['occupied']:
                break
        for i in range(1, 8):
            new_x = x_ + i
            new_y = y_ - i
            if (not self.inside_board(new_x, new_y) or self.board_black[new_x][new_y].info['color'] == 'b'
                and moves_ % 2 == 1) or (self.board_black[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
                break
            possible_.add((new_x, new_y))

            if self.board_black[new_x][new_y].info['occupied']:
                break
        for i in range(1, 8):
            new_x = x_ - i
            new_y = y_ - i
            if (not self.inside_board(new_x, new_y) or self.board_black[new_x][new_y].info['color'] == 'b'
                and moves_ % 2 == 1) or (self.board_black[new_x][new_y].info['color'] == 'w' and moves_ % 2 == 0):
                break
            possible_.add((new_x, new_y))
            if self.board_black[new_x][new_y].info['occupied']:
                break
        for x_2 in range(x_ + 1, 8, 1):
            if (self.board_black[x_2][y_].info['color'] == 'b' and moves_ % 2 == 1) \
                    or (self.board_black[x_2][y_].info['color'] == 'w' and moves_ % 2 == 0):
                break
            possible_.add((x_2, y_))
            if self.board_black[x_2][y_].info['occupied']:
                break
        for x_2 in range(x_ - 1, -1, -1):
            if (self.board_black[x_2][y_].info['color'] == 'b' and moves_ % 2 == 1) or \
                    (self.board_black[x_2][y_].info['color'] == 'w' and moves_ % 2 == 0):
                break
            possible_.add((x_2, y_))
            if self.board_black[x_2][y_].info['occupied']:
                break
        for y_2 in range(y_ + 1, 8, 1):
            if (self.board_black[x_][y_2].info['color'] == 'b' and moves_ % 2 == 1) or \
                    (self.board_black[x_][y_2].info['color'] == 'w' and moves_ % 2 == 0):
                break
            possible_.add((x_, y_2))
            if self.board_black[x_][y_2].info['occupied']:
                break
        for y_2 in range(y_ - 1, -1, -1):
            if (self.board_black[x_][y_2].info['color'] == 'b' and moves_ % 2 == 1) or \
                    (self.board_black[x_][y_2].info['color'] == 'w' and moves_ % 2 == 0):
                break
            possible_.add((x_, y_2))
            if self.board_black[x_][y_2].info['occupied']:
                break
        return list(possible_)

    def black_pawn_to_move2_black(self, pos_, moves_):
        """ return valid positions available for the pawn located in pos_ """
        x_, y_ = pos_
        possible_ = []
        if self.inside_board(x_ + 1, y_) and not self.board_black[x_ + 1][y_].info['occupied']:
            possible_.append((x_ + 1, y_))
        if self.inside_board(x_ + 2, y_) and (not self.board_black[x_ + 1][y_].info['occupied']) \
                and (not self.board_black[x_ + 2][y_].info['occupied']) and (x_ == 1):
            if self.simulate_move(pos_, (x_ + 2, y_), moves_):
                possible_.append((x_ + 2, y_))

        if self.inside_board(x_ + 1, y_ + 1) and self.board_black[x_ + 1][y_ + 1].info['occupied'] \
                and (self.board_black[x_ + 1][y_ + 1].info['color'] == 'w'):
            if self.simulate_move(pos_, (x_ + 1, y_ + 1), moves_):
                possible_.append((x_ + 1, y_ + 1))
        if self.inside_board(x_ + 1, y_ - 1) and self.board_black[x_ + 1][y_ - 1].info['occupied'] \
                and (self.board_black[x_ + 1][y_ - 1].info['color'] == 'w'):
            possible_.append((x_ + 1, y_ - 1))
        return possible_

    def king_to_move_simple(self, pos_, moves_):
        """ return threatened positions available for the king located in pos_ """
        possible_ = []
        di = [-1, -1, -1, 0, 1, 1, 1, 0]
        dj = [-1, 0, 1, -1, -1, 0, 1, 1]
        for d in range(0, len(di)):
            new_x = pos_[0] + di[d]
            new_y = pos_[1] + dj[d]
            if moves_ % 2 == 1:
                if self.inside_board(new_x, new_y) and self.board[new_x][new_y].info['color'] != 'b':
                    possible_.append((new_x, new_y))
            else:
                if self.inside_board(new_x, new_y) and self.board[new_x][new_y].info['color'] != 'w':
                    possible_.append((new_x, new_y))
        return possible_

    def king_to_move2_black(self, pos_, moves_):
        """ return valid positions available for the king located in pos_ """
        possible_ = []
        di = [-1, -1, -1, 0, 1, 1, 1, 0]
        dj = [-1, 0, 1, -1, -1, 0, 1, 1]
        for d in range(0, len(di)):
            new_x = pos_[0] + di[d]
            new_y = pos_[1] + dj[d]
            if moves_ % 2 == 1:
                if self.inside_board(new_x, new_y) and self.board_black[new_x][new_y].info['color'] != 'b':
                    possible_.append((new_x, new_y))
            else:
                if self.inside_board(new_x, new_y) and self.board_black[new_x][new_y].info['color'] != 'w':
                    possible_.append((new_x, new_y))
        return possible_

    def get_note_table_cell(self, position_to_draw):
        mouse_pos = pygame.mouse.get_pos()
        return [int((mouse_pos[1] - position_to_draw[0]) / position_to_draw[2]),
                int((mouse_pos[0] - position_to_draw[1]) / position_to_draw[2])]

    def pawn_to_move_simple(self, pos_, moves_):
        """ squares a pawn can attack """
        x_, y_ = pos_
        possible_ = []
        if self.inside_board(x_ - 1, y_ + 1) and (not self.board[x_ - 1][y_ + 1].info['occupied']) and moves_ % 2 == 0:
            possible_.append((x_ - 1, y_ + 1))
        if self.inside_board(x_ - 1, y_ - 1) and (not self.board[x_ - 1][y_ - 1].info['occupied']) and moves_ % 2 == 0:
            possible_.append((x_ - 1, y_ - 1))
        if self.inside_board(x_ + 1, y_ + 1) and (not self.board[x_ + 1][y_ + 1].info['occupied']) and moves_ % 2 == 1:
            possible_.append((x_ + 1, y_ + 1))
        if self.inside_board(x_ + 1, y_ - 1) and (not self.board[x_ + 1][y_ - 1].info['occupied']) and moves_ % 2 == 1:
            possible_.append((x_ + 1, y_ - 1))
        return possible_

    def knight_to_move2_black(self, pos_, moves_):
        """ return valid positions available for the knight located in pos_ """
        possible_ = []
        di = [-1, -1, 1, 1, -2, -2, 2, 2]
        dj = [2, -2, -2, 2, -1, 1, -1, 1]
        for d in range(0, len(di)):
            new_x = pos_[0] + di[d]
            new_y = pos_[1] + dj[d]
            if moves_ % 2 == 1:
                if self.inside_board(new_x, new_y) and self.board_black[new_x][new_y].info['color'] != 'b':
                    possible_.append((new_x, new_y))
            else:
                if self.inside_board(new_x, new_y) and self.board_black[new_x][new_y].info['color'] != 'w':
                    possible_.append((new_x, new_y))
        return possible_

    def rook_to_move2_black(self, pos_, moves_):
        """ return valid positions available for the rook located in pos_ """
        possible_ = []
        x_, y_ = pos_
        for x_2 in range(x_ + 1, 8, 1):
            if (self.board_black[x_2][y_].info['color'] == 'b' and moves_ % 2 == 1) or (
                    self.board_black[x_2][y_].info['color'] == 'w' and moves_ % 2 == 0):
                break
            possible_.append((x_2, y_))
            if self.board_black[x_2][y_].info['occupied']:
                break
        for x_2 in range(x_ - 1, -1, -1):
            if (self.board_black[x_2][y_].info['color'] == 'b' and moves_ % 2 == 1) or (
                    self.board_black[x_2][y_].info['color'] == 'w' and moves_ % 2 == 0):
                break
            possible_.append((x_2, y_))
            if self.board_black[x_2][y_].info['occupied']:
                break
        for y_2 in range(y_ + 1, 8, 1):
            if (self.board_black[x_][y_2].info['color'] == 'b' and moves_ % 2 == 1) or (
                    self.board_black[x_][y_2].info['color'] == 'w' and moves_ % 2 == 0):
                break
            possible_.append((x_, y_2))
            if self.board_black[x_][y_2].info['occupied']:
                break
        for y_2 in range(y_ - 1, -1, -1):
            if (self.board_black[x_][y_2].info['color'] == 'b' and moves_ % 2 == 1) or (
                    self.board_black[x_][y_2].info['color'] == 'w' and moves_ % 2 == 0):
                break
            possible_.append((x_, y_2))
            if self.board_black[x_][y_2].info['occupied']:
                break
        return possible_

    def get_pos(self, pos_, seg):
        """get a square coordinates"""
        x_, y_ = pos_
        row_ = x_ // seg
        col_ = y_ // seg
        return int(row_), int(col_)

    def draw_note_table(self, _background, position_to_draw):
        for i in range(0, 9):
            for j in range(0, 8):
                if (i + j) % 2 == 1:
                    color_to_draw = self.black_color
                else:
                    color_to_draw = self.white_color
                if i != 8:
                    pygame.draw.rect(_background, color_to_draw, (
                        position_to_draw[1] + position_to_draw[2] * j,
                        position_to_draw[0] + position_to_draw[2] * i,
                        position_to_draw[2], position_to_draw[2]))
                else:
                    if j == 0:
                        continue
                    pygame.draw.rect(_background, (255, 255, 255, 125), (
                        position_to_draw[1] + position_to_draw[2] * j,
                        position_to_draw[0] + position_to_draw[2] * i,
                        position_to_draw[2] - 1, position_to_draw[2] - 1))
                piece_to_draw = self.note_table[i][j] - 1
                if piece_to_draw != -1:
                    _background.blit(self.pieces[piece_to_draw],
                                     (position_to_draw[1] + position_to_draw[2] * j,
                                      position_to_draw[0] + position_to_draw[2] * i,))

    def update_display(self, black, background_, screen_, width):
        """display the console before the game is over"""
        screen_.blit(black, [0, 0])
        screen_.blit(background_, [0, 0])
        for i in range(0, 8):
            for j in range(0, 8):
                if self.board[i][j].info['occupied']:
                    if self.board[i][j].info['color'] == 'b' and self.see_me == 'n':
                        continue
                    screen_.blit(self.pieces[self.board[i][j].info['image']],
                                 (self.board[7 - j][i].info['x'], self.board[7 - j][i].info['y']))
        self.screen.blit(self.up_arrow, (width - width / 15, width - width / 2 + 50))
        self.screen.blit(self.down_arrow, (width - width / 15, width - width / 15))
        self.draw_note_table(self.screen, [0, 400, 50])
        self.draw_log_messages()
        pygame.display.update()

    def update_display2(self, black, background_, screen_, width, text):
        """display the console after the game is over"""
        screen_.blit(black, [0, 0])
        screen_.blit(background_, [0, 0])
        for i in range(0, 8):
            for j in range(0, 8):
                if self.board[i][j].info['occupied']:
                    screen_.blit(self.pieces[self.board[i][j].info['image']],
                                 (self.board[7 - j][i].info['x'], self.board[7 - j][i].info['y']))
                if self.board[i][j].info['killable']:
                    if not self.board[i][j].info['occupied']:
                        pygame.draw.circle(screen_, (220, 20, 60),
                                           (self.board[7 - j][i].info['x'] + width / 16,
                                            self.board[7 - j][i].info['y'] + width / 16),
                                           width / 40)
                    else:
                        pygame.draw.polygon(screen_, (220, 20, 60),
                                            [(self.board[7 - j][i].info['x'],
                                              self.board[7 - j][i].info['y']),
                                             (self.board[7 - j][i].info['x'],
                                              self.board[7 - j][i].info['y'] + width / 30),
                                             (self.board[7 - j][i].info['x'] + width / 30,
                                              self.board[7 - j][i].info['y'])],
                                            0)
                        pygame.draw.polygon(screen_, (220, 20, 60),
                                            [(self.board[7 - j][i].info['x'] + width / 8,
                                              self.board[7 - j][i].info['y']),
                                             (self.board[7 - j][i].info['x'] + width / 8,
                                              self.board[7 - j][i].info['y'] + width / 30),
                                             (self.board[7 - j][i].info['x'] + width / 8 - width / 30,
                                              self.board[7 - j][i].info['y'])],
                                            0)
                        pygame.draw.polygon(screen_, (220, 20, 60),
                                            [(self.board[7 - j][i].info['x'] + width / 8,
                                              self.board[7 - j][i].info['y'] + width / 8),
                                             (self.board[7 - j][i].info['x'] + width / 8,
                                              self.board[7 - j][i].info['y'] + + width / 8 - width / 30),
                                             (self.board[7 - j][i].info['x'] + width / 8 - width / 30,
                                              self.board[7 - j][i].info['y'] + width / 8)], 0)
                        pygame.draw.polygon(screen_, (220, 20, 60),
                                            [(self.board[7 - j][i].info['x'],
                                              self.board[7 - j][i].info['y'] + width / 8),
                                             (self.board[7 - j][i].info['x'],
                                              self.board[7 - j][i].info['y'] + + width / 8 - width / 30),
                                             (self.board[7 - j][i].info['x'] + width / 30,
                                              self.board[7 - j][i].info['y'] + width / 8)],
                                            0)
        my_font = pygame.font.SysFont('Times New Roman', 32)
        text_surface = my_font.render(text, False, (255, 255, 255))
        self.screen.blit(text_surface, (width / 2 + width / 50, 0))
        self.draw_note_table(self.screen, [0, 400, 50])
        self.draw_log_messages()
        pygame.display.update()

    def draw_log_messages(self):
        pygame.draw.rect(self.screen, self.black_color, (753, 600, 44, 40))
        font = pygame.font.SysFont("Comic Sans MS", 20)
        count = 1 + self.count
        log_length = 40
        for i in range(9):
            pygame.draw.rect(self.screen, (255, 235, 156), (0, 435 + log_length * (i + 1), 750, 1))
        no_of_messages_to_display = min(9, self.last_shown_message_index)
        for i in range(no_of_messages_to_display):
            text_to_display = str(self.last_shown_message_index - i) + ' : ' \
                              + self.queue_message[self.last_shown_message_index - i - 1]
            text_to_display = font.render(text_to_display, True, (255, 235, 156))
            self.screen.blit(text_to_display, (50, 440 + log_length * i))
        question_text = 'Any?'
        question_text = font.render(question_text, True, self.white_color)
        self.screen.blit(question_text, (754, 600))

    def check_clicked_on_arrows(self, mouse_pos, width):
        if len(self.queue_message) > 9 and width - width / 15 <= mouse_pos[0] <= width - width / 15 + 45:
            if width - width / 2 + 45 <= mouse_pos[1] <= width - width / 2 + 90:
                last_shown_message_index = min(self.last_shown_message_index + 1, len(self.queue_message))
                return 1
            if width - width / 15 <= mouse_pos[1] <= width:
                last_shown_message_index = max(9, self.last_shown_message_index - 1)
                return 2
        if 753 <= mouse_pos[0] <= 797 and 600 <= mouse_pos[1] <= 640:
            self.check_if_pawn_can_take_piece()
            return 3
        return 0

    def check_if_pawn_can_take_piece(self):
        pawn = False
        for i in range(8):
            for j in range(8):
                if self.board[i][j].info['type'] == 'p' and self.board[i][j].info['color'] == 'w':
                    if (self.inside_board(i - 1, j - 1) and self.board[i - 1][j - 1].info['color'] == 'b') \
                            or (self.inside_board(i - 1, j + 1) and self.board[i - 1][j + 1].info['color'] == 'b'):
                        pawn = True

        if pawn is True:
            message = "Try"
        else:
            message = "No chance"
        self.queue_message.append(message)
        self.last_shown_message_index = len(self.queue_message)

    def clear_square(self, pos_):
        """ set a square to empty """
        self.board[pos_[0]][pos_[1]].update('type', None)
        self.board[pos_[0]][pos_[1]].update('color', None)
        self.board[pos_[0]][pos_[1]].update('image', None)
        self.board[pos_[0]][pos_[1]].update('occupied', False)
        self.board[pos_[0]][pos_[1]].update('killable', False)



    def move_white_ai(self, moves_, black, background_, screen_, window_width_):
        self.queue_message.append("loading..")
        self.last_shown_message_index = len(self.queue_message)
        self.update_display(black, background_, screen_, window_width_)
        self.queue_message.pop()
        white_pieces = []
        possible__ = []
        for i in range(0, 8):
            for j in range(0, 8):
                if self.board[i][j].info['color'] == 'w':
                    white_pieces.append((i, j))
        random.shuffle(white_pieces)
        player_ok = True
        for sz in range(0, len(white_pieces)):
            possible__ = self.select_moves(white_pieces[sz], moves_)
            if len(possible__) == 0:
                continue
            new_position = random.randint(0, len(possible__) - 1)
            child_index = (white_pieces[sz], possible__[new_position])
            if self.board[child_index[1][0]][child_index[1][1]].info['type'] is None:
                self.queue_message.append("player with white pieces moved")
                last_shown_message_index = len(self.queue_message)
            else:
                line = "12345678"
                column = "ABCDEFGH"
                msg = f"White captured a piece from {column[7 - child_index[0][1]]}{line[7 - child_index[0][0]]} to " \
                      f"{column[7 - child_index[1][1]]}{line[7 - child_index[1][0]]}"
                self.queue_message.append(msg)
                last_shown_message_index = len(self.queue_message)
            self.move_piece(white_pieces[sz], possible__[new_position], moves_)
            self.update_display(black, background_, screen_, window_width_)
            player_ok = False
            break

        if self.is_black_checked2(self.get_black_king_position(), 1):
            msg = "Black king is checked!"
            self.queue_message.append(msg)
            self.last_shown_message_index = len(self.queue_message)

        if player_ok:
            if self.is_white_checked(self.get_white_king_position(), moves_):
                self.black_won = True
            else:
                self.stalemate = True

    def generate_possible_moves(self):
        black_pieces = []
        possible__ = []
        ret = []
        for i in range(0, 8):
            for j in range(0, 8):
                if self.board[i][j].info['color'] == 'b':
                    black_pieces.append((i, j))
        random.shuffle(black_pieces)
        for sz in range(0, len(black_pieces)):
            possible__ = self.select_moves(black_pieces[sz], 1)
            random.shuffle(possible__)
            for i in range(0, len(possible__)):
                ret.append([black_pieces[sz], possible__[i], 1])
        return ret

    def simulate_game(self, act_board, black, background_, screen_, window_width_):
        board_copy = copy.deepcopy(self.board)
        board = copy.deepcopy(act_board)
        moves__ = 1
        self.white_won, self.black_won, self.stalemate, self.draw = 0, 0, 0, 0
        while (not self.white_won) and (not self.black_won) and (not self.stalemate) and (not self.draw):
            if moves__ % 2 == 0:
                self.move_white_ai(moves__, black, background_, screen_, window_width_)
                moves__ += 1
            else:
                self.move_black_ai(moves__)
                moves__ += 1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            if self.see_me == 'y':
                self.update_display(black, background_, screen_, window_width_)

        board = copy.deepcopy(board_copy)

        if self.white_won:
            print("white won!")
            self.white_won = 0
            return 0
        if self.stalemate or self.draw:
            print("draw|stalemate!")
            self.stalemate = 0
            self.draw = 0
            return 1
        if self.black_won:
            print("black won!")
            self.black_won = 0
            return 2

    def select_moves(self, pos_, moves_):
        """ returns list of available moves for the piece located in pos_"""
        x_, y_ = pos_
        if (self.board[x_][y_].info['color'] == 'w' and moves_ % 2 == 1) or (
                self.board[x_][y_].info['color'] == 'b' and moves_ % 2 == 0):
            return []
        ret = []
        if self.board[x_][y_].info['type'] == 'p':
            if self.board[x_][y_].info['color'] == 'b':
                ret = self.black_pawn_to_move2(pos_, moves_)
                if self.inside_board(x_ + 1, y_ + 1) and self.white_en_passant[y_ + 1] and x_ == 4:
                    ret.extend([(x_ + 1, y_ + 1)])
                if self.inside_board(x_ + 1, y_ - 1) and self.white_en_passant[y_ - 1] and x_ == 4:
                    ret.extend([(x_ + 1, y_ - 1)])
            else:
                ret = self.white_pawn_to_move2(pos_, moves_)
                if self.inside_board(x_ - 1, y_ + 1) and self.black_en_passant[y_ + 1] and x_ == 3:
                    ret.extend([(x_ - 1, y_ + 1)])
                if self.inside_board(x_ - 1, y_ - 1) and self.black_en_passant[y_ - 1] and x_ == 3:
                    ret.extend([(x_ - 1, y_ - 1)])
        if self.board[x_][y_].info['type'] == 'n':
            ret = self.knight_to_move2(pos_, moves_)
        if self.board[x_][y_].info['type'] == 'r':
            ret = self.rook_to_move2(pos_, moves_)
        if self.board[x_][y_].info['type'] == 'b':
            ret = self.bishop_to_move2(pos_, moves_)
        if self.board[x_][y_].info['type'] == 'q':
            ret = self.queen_to_move2(pos_, moves_)
        if self.board[x_][y_].info['type'] == 'k':
            ret = self.king_to_move2(pos_, moves_)
            if (moves_ % 2 == 0) and (not self.is_white_checked((7, 1), moves_)) and \
                    (not self.is_white_checked((7, 2), moves_)) and (not self.is_white_checked((7, 3), moves_)) and \
                    (not self.right_white_rook_has_moved) and (not self.white_king_has_moved) \
                    and (not self.board[7][1].info['occupied']) \
                    and (not self.board[7][2].info['occupied']):
                ret.extend([(-1, -1)])
            if (moves_ % 2 == 1) and (not self.is_black_checked((0, 1), moves_)) and \
                    (not self.is_black_checked((0, 2), moves_)) \
                    and (not self.is_black_checked((0, 3), moves_)) and (not self.right_black_rook_has_moved) \
                    and (not self.black_king_has_moved) and (not self.board[0][1].info['occupied']) and \
                    (not self.board[0][2].info['occupied']):
                ret.extend([(-2, -2)])
            if (moves_ % 2 == 0) and (not self.is_white_checked((7, 3), moves_)) \
                    and (not self.is_white_checked((7, 4), moves_)) \
                    and (not self.is_white_checked((7, 5), moves_)) \
                    and (not self.left_white_rook_has_moved) \
                    and (not self.white_king_has_moved) \
                    and (not self.board[7][4].info['occupied']) and (not self.board[7][5].info['occupied']):
                ret.extend([(-3, -3)])
            if (moves_ % 2 == 1) and (not self.is_black_checked((0, 3), moves_)) and \
                    (not self.is_black_checked((0, 4), moves_)) \
                    and (not self.is_black_checked((0, 5), moves_)) \
                    and (not self.left_black_rook_has_moved) \
                    and (not self.black_king_has_moved) \
                    and (not self.board[0][4].info['occupied']) \
                    and (not self.board[0][5].info['occupied']):
                ret.extend([(-4, -4)])
        return ret

    def simulate_move2(self, from_, to_, moves_, check):
        """return True if moving piece from from_ to to_ is a valid move, i.e it doesnt discover the king"""
        board2 = copy.deepcopy(self.board)
        self.board[to_[0]][to_[1]].update('type', self.board[from_[0]][from_[1]].info['type'])
        self.board[from_[0]][from_[1]].update('type', None)
        self.board[to_[0]][to_[1]].update('color', self.board[from_[0]][from_[1]].info['color'])
        self.board[from_[0]][from_[1]].update('color', None)
        self.board[to_[0]][to_[1]].update('image', self.board[from_[0]][from_[1]].info['image'])
        self.board[from_[0]][from_[1]].update('image', None)
        self.board[to_[0]][to_[1]].update('occupied', True)
        self.board[from_[0]][from_[1]].update('occupied', False)
        self.board[to_[0]][to_[1]].update('killable', False)
        self.board[from_[0]][from_[1]].update('killable', False)
        if moves_ % 2 == 0:
            if self.is_white_checked2(self.get_white_king_position(), moves_):
                self.board = copy.deepcopy(board2)
                return False
        if moves_ % 2 == 1:
            if self.is_black_checked2(self.get_black_king_position(), moves_):
                self.board = copy.deepcopy(board2)
                return False
        self.board = copy.deepcopy(board2)
        return True

    def select_moves_black(self, pos_, moves_):
        """ returns list of available moves for the piece located in pos_"""
        x_, y_ = pos_
        if (self.board_black[x_][y_].info['color'] == 'w' and moves_ % 2 == 1) or (
                self.board_black[x_][y_].info['color'] == 'b' and moves_ % 2 == 0):
            return []
        ret = []
        if self.board_black[x_][y_].info['type'] == 'p':
            if self.board_black[x_][y_].info['color'] == 'b':
                ret = self.black_pawn_to_move2_black(pos_, moves_)
                if self.inside_board(x_ + 1, y_ + 1) and self.white_en_passant[y_ + 1] and x_ == 4:
                    ret.extend([(x_ + 1, y_ + 1)])
                if self.inside_board(x_ + 1, y_ - 1) and self.white_en_passant[y_ - 1] and x_ == 4:
                    ret.extend([(x_ + 1, y_ - 1)])
        if self.board[x_][y_].info['type'] == 'n':
            ret = self.knight_to_move2_black(pos_, moves_)
        if self.board[x_][y_].info['type'] == 'r':
            ret = self.rook_to_move2_black(pos_, moves_)
        if self.board[x_][y_].info['type'] == 'b':
            ret = self.bishop_to_move2_black(pos_, moves_)
        if self.board[x_][y_].info['type'] == 'q':
            ret = self.queen_to_move2_black(pos_, moves_)
        if self.board[x_][y_].info['type'] == 'k':
            ret = self.king_to_move2_black(pos_, moves_)
            if (not self.right_black_rook_has_moved) and (not self.black_king_has_moved) and (
                    not self.board[0][1].info['occupied']) and (
                    not self.board[0][2].info['occupied']):
                ret.extend([(-2, -2)])
            if (not self.left_black_rook_has_moved) and (not self.black_king_has_moved) and (
                    not self.board[0][4].info['occupied']) and (
                    not self.board[0][5].info['occupied']):
                ret.extend([(-4, -4)])
        return ret

    def move_black_ai(self, moves_):
        """computer moves black pieces"""
        black_pieces = []
        possible__ = []
        for i in range(0, 8):
            for j in range(0, 8):
                if self.board[i][j].info['color'] == 'b':
                    black_pieces.append((i, j))
        random.shuffle(black_pieces)
        player_ok = True
        for sz in range(0, len(black_pieces)):
            possible__ = self.select_moves(black_pieces[sz], moves_)
            if len(possible__) == 0:
                continue
            new_position = random.randint(0, len(possible__) - 1)
            self.move_piece(black_pieces[sz], possible__[new_position], moves_)
            player_ok = False
            break
        if player_ok:
            if self.is_black_checked(self.get_black_king_position(), moves_):
                white_won = True
            else:
                stalemate = True

    def move_piece(self, from_, to_, moves_):
        """piece from position from_ is moved to position to_ and position from_ is cleared with respect to special moves like castles and en passant"""
        if self.board[from_[0]][from_[1]].info['type'] == 'k' and moves_ % 2 == 0:
            self.white_king_has_moved = True
        if self.board[from_[0]][from_[1]].info['type'] == 'k' and moves_ % 2 == 1:
            self.black_king_has_moved = True
        if self.board[from_[0]][from_[1]].info['type'] == 'r' and moves_ % 2 == 0 and from_ == (7, 0):
            self.right_white_rook_has_moved = True
        if self.board[from_[0]][from_[1]].info['type'] == 'r' and moves_ % 2 == 0 and from_ == (7, 7):
            self.left_white_rook_has_moved = True
        if self.board[from_[0]][from_[1]].info['type'] == 'r' and moves_ % 2 == 1 and from_ == (0, 0):
            self.right_black_rook_has_moved = True
        if self.board[from_[0]][from_[1]].info['type'] == 'r' and moves_ % 2 == 1 and from_ == (0, 7):
            self.left_black_rook_has_moved = True

        if self.board[to_[0]][to_[1]].info['occupied'] or self.board[from_[0]][from_[1]].info['type'] == 'p':
            self.move_counter = 0
        else:
            self.move_counter += 1
        self.black_en_passant, self.white_en_passant = [False for i in range(0, 8)], [False for i in range(0, 8)]
        if moves_ % 2 == 0 and self.board[from_[0]][from_[1]].info['type'] == 'p' and from_[0] - to_[0] == 2:
            self.white_en_passant[from_[1]] = True
        if moves_ % 2 == 1 and self.board[from_[0]][from_[1]].info['type'] == 'p' and to_[0] - from_[0] == 2:
            self.black_en_passant[from_[1]] = True

        self.board[to_[0]][to_[1]].update('type', self.board[from_[0]][from_[1]].info['type'])
        self.board[from_[0]][from_[1]].update('type', None)
        self.board[to_[0]][to_[1]].update('color', self.board[from_[0]][from_[1]].info['color'])
        self.board[from_[0]][from_[1]].update('color', None)
        self.board[to_[0]][to_[1]].update('image', self.board[from_[0]][from_[1]].info['image'])
        self.board[from_[0]][from_[1]].update('image', None)
        self.board[to_[0]][to_[1]].update('occupied', True)
        self.board[from_[0]][from_[1]].update('occupied', False)
        self.board[to_[0]][to_[1]].update('killable', False)
        self.board[from_[0]][from_[1]].update('killable', False)

        self.board_black[to_[0]][to_[1]].update('type', self.board_black[from_[0]][from_[1]].info['type'])
        self.board_black[from_[0]][from_[1]].update('type', None)
        self.board_black[to_[0]][to_[1]].update('color', self.board_black[from_[0]][from_[1]].info['color'])
        self.board_black[from_[0]][from_[1]].update('color', None)
        self.board_black[to_[0]][to_[1]].update('image', self.board_black[from_[0]][from_[1]].info['image'])
        self.board_black[from_[0]][from_[1]].update('image', None)
        self.board_black[to_[0]][to_[1]].update('occupied', True)
        self.board_black[from_[0]][from_[1]].update('occupied', False)
        self.board_black[to_[0]][to_[1]].update('killable', False)
        self.board_black[from_[0]][from_[1]].update('killable', False)

        if moves_ % 2 == 0 and to_[0] == 0 and self.board[to_[0]][to_[1]].info['type'] == 'p':
            self.board[to_[0]][to_[1]].update('type', 'q')
            self.board[to_[0]][to_[1]].update('image', 'wQ')
        if moves_ % 2 == 1 and to_[0] == 7 and self.board[to_[0]][to_[1]].info['type'] == 'p':
            self.board[to_[0]][to_[1]].update('type', 'q')
            self.board[to_[0]][to_[1]].update('image', 'bQ')
            self.board_black[to_[0]][to_[1]].update('type', 'q')
            self.board_black[to_[0]][to_[1]].update('image', 'bQ')

        current_state = ""
        for i in range(0, 8):
            for j in range(0, 8):
                current_state += str(self.board[i][j].info['type'])
        self.game_states[current_state] = self.game_states.get(current_state, 0) + 1
        if self.game_states[current_state] == 3 or self.move_counter == 100:
            self.draw = True

    def make_them_killable(self, possible_):
        """ mark available squares """
        for i in possible_:
            if i == (-1, -1):
                self.board[7][1].update('killable', True)
                continue
            if i == (-2, -2):
                self.board[0][1].update('killable', True)
                continue
            if i == (-3, -3):
                self.board[7][5].update('killable', True)
                continue
            if i == (-4, -4):
                self.board[0][5].update('killable', True)
                continue
            self.board[i[0]][i[1]].update('killable', True)

    def make_them_not_killable(self, possible_):
        """ unmark available squares """
        for i in possible_:
            if i == (-1, -1):
                self.board[7][1].update('killable', False)
                continue
            if i == (-2, -2):
                self.board[0][1].update('killable', False)
                continue
            if i == (-3, -3):
                self.board[7][5].update('killable', False)
                continue
            if i == (-4, -4):
                self.board[0][5].update('killable', False)
                continue
            self.board[i[0]][i[1]].update('killable', False)

    def random_vs_random(self, black, background_, screen_, window_width_, moves__):
        """ computer plays black and whites pieces """
        while (not self.white_won) and (not self.black_won) and (not self.stalemate) and (
        not self.draw):
            if moves__ % 2 == 0:
                self.move_white_ai(moves__, black, background_, screen_, window_width_)
                moves__ += 1
            else:
                self.move_black_ai(moves__)
                moves__ += 1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.update_display(black, background_, screen_, window_width_)
