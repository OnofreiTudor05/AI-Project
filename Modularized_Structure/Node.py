import sys

import pygame

from Chess import Chess
import copy
import math
import numpy as np
import time


class Node:
    def __init__(self, no, father, config):
        self.index = no
        self.father = father
        self.config = copy.deepcopy(config)
        self.score = 0.00001
        self.visited = 0.00001
        self.v = []
        self.chess = Chess()
        self.time_stamp_ = 1
        self.no_iter = 0
        self.random_vs_mc = 0
        self.start = time.time()
        self.PERIOD_OF_TIME = 30  # 5min

    def get_config(self):
        return self.config

    def get_index(self):
        return self.index

    def update_score(self, score):
        self.score += score

    def update_visit(self):
        self.visited += 1

    def add_child(self, nod):
        self.v.append(nod)

    def get_child_size(self):
        return len(self.v)

    def get_child(self, id_number):
        return self.v[id_number]

    def get_score(self):
        return self.score

    def get_visited(self):
        return self.visited

    def get_info_square(self, i, j, field):
        return self.config[i][j].info[field]

    def get_formula_value(self, n):
        return self.score / self.visited + 3. / 7. * math.sqrt(np.log(n) / self.visited)

    def create_child_nodes(self):
        moves_to_do = self.chess.generate_possible_moves()
        for i in range(0, len(moves_to_do)):
            curr_board = copy.deepcopy(self.chess.board)
            self.chess.move_piece(moves_to_do[i][0], moves_to_do[i][1], moves_to_do[i][2])
            self.chess.nodes_counter_in_mcts += 1
            curr_node = Node(self.chess.nodes_counter_in_mcts, self.get_index(), self.chess.board)
            self.add_child(curr_node)
            self.chess.board = copy.deepcopy(curr_board)

    def dfs_check_tree_structure(self, id_number):
        for ch in range(0, self.get_child_size()):
            self.dfs_check_tree_structure(self.v[ch])

    def mc_dfs(self, id_number, black, background_, screen_, window_width_):
        if self.get_child_size() == 0:
            if self.get_visited() == 0.00001:
                reward = self.chess.simulate_game(self.config, black, background_, screen_, window_width_)
                self.update_score(reward)
                self.update_visit()
                self.chess.visited_vector[self.get_index()] = self.get_visited()
                self.chess.score_vector[self.get_index()] = self.get_score()
                return reward
            else:
                self.create_child_nodes()
        if self.get_child_size() == 0:
            if self.chess.is_black_checked(self.chess.get_black_king_position(), 1):
                return 0
            else:
                return 1
        curr_val = 0
        next_node = -1
        for ch in range(0, self.get_child_size()):
            val = self.v[ch].get_formula_value(self.get_visited())
            if val > curr_val:
                curr_val = val
                next_node = ch
        self.update_score(self.mc_dfs(self.v[next_node], black, background_, screen_, window_width_))
        self.update_visit()
        self.chess.visited_vector[self.get_index()] = self.get_visited()
        self.chess.score_vector[self.get_index()] = self.get_score()

    def probability_free_range(self, from_, to_):
        global board
        i_ratio = 0
        to_0 = to_[0]
        to_1 = to_[1]
        from_0 = from_[0]
        from_1 = from_[1]
        if to_0 < from_0:
            i_ratio = -1
        if to_0 > from_0:
            i_ratio = 1
        j_ratio = 0
        if to_1 < from_1:
            j_ratio = -1
        if to_1 > from_1:
            j_ratio = 1
        probability_ = 1.
        while from_0 != to_0 or from_1 != to_1:
            if not self.chess.inside_board(from_0, from_1):
                break
            from_0 += i_ratio
            from_1 += j_ratio
            probability_ *= 1 - self.chess.M_white[0][self.time_stamp_][from_0][from_1] - \
                            self.chess.M_white[1][self.time_stamp_][from_0][
                                from_1] - self.chess.M_white[2][self.time_stamp_][from_0][from_1]
        return probability_

    def probability_control(self, pos_, prob_table, tip):
        ret = 0.
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                if i == 0 and j == 0:
                    continue
                if self.chess.inside_board(i, j):
                    if tip == 1:
                        ret += prob_table[0][self.time_stamp_][i][j]
                    else:
                        ret += prob_table[0][i][j]
        if self.chess.inside_board(pos_[0] - 1, pos_[1] - 1):
            if tip == 1:
                ret += prob_table[0][self.time_stamp_][pos_[0] - 1][pos_[1] - 1]
            else:
                ret += prob_table[0][pos_[0] - 1][pos_[1] - 1]
        if self.chess.inside_board(pos_[0] - 1, pos_[1] + 1):
            if tip == 1:
                ret += prob_table[0][self.time_stamp_][pos_[0] - 1][pos_[1] + 1]
            else:
                ret += prob_table[0][pos_[0] - 1][pos_[1] + 1]
        c1 = 3. / 7.
        c2 = 1.
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                if i == 0 and j == 0:
                    continue
                curr_pos0, curr_pos1 = pos_[0], pos_[1]
                curr_pos0 += i
                curr_pos1 += j
                seq_len = 2.
                while self.chess.inside_board(curr_pos0, curr_pos1):
                    c2 = 1. / (seq_len - 1.)
                    ret += c1 * self.probability_free_range((curr_pos0, curr_pos1), (pos_[0], pos_[1])) * c2
                    curr_pos0 = curr_pos0 + i
                    curr_pos1 = curr_pos1 + j
                    seq_len += 1
        return ret

    def probability_pin(self, from_, to_):
        if self.chess.board[from_[0]][from_[1]].info['type'] == 'k':
            return self.probability_control(to_, self.chess.M_white, 1)
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                if i == 0 and j == 0:
                    continue
                curr_pos = list(from_)
                curr_pos[0] += i
                curr_pos[1] += j
                while self.chess.inside_board(curr_pos[0], curr_pos[1]):
                    if self.chess.board[curr_pos[0]][curr_pos[1]].info['type'] == 'k':
                        return self.probability_control(from_, self.chess.M_white, 1)
                    if self.chess.board[curr_pos[0]][curr_pos[1]].info['type'] is not None:
                        break
                    curr_pos[0] += i
                    curr_pos[1] += j
        return 0

    def move_black_monte_carlo_optimized(self, black, background_, screen_, window_width_):
        self.chess.create_random_matrix()
        self.chess.queue_message.append("loading...")
        self.chess.last_shown_message_index = len(self.chess.queue_message)
        self.chess.update_display(black, background_, screen_, window_width_)
        child_list = []
        for i in range(0, 8):
            for j in range(0, 8):
                if self.chess.board_black[i][j].info['color'] == 'b':
                    my_list = self.chess.select_moves_black((i, j), 1)
                    for it in my_list:
                        child_list.append(((i, j), it))
        child_score = [[0., 0] for i in range(len(child_list))]
        for son in range(0, len(child_list)):
            child_score[son][1] = son
            from_ = (child_list[son][0])
            to_ = (child_list[son][1])
            probability_legal = 1.
            if self.chess.board_black[from_[0]][from_[1]].info['type'] != 'n' and \
                    self.chess.board_black[from_[0]][from_[1]].info[
                        'type'] != 'p':
                probability_legal *= self.probability_free_range(from_, to_)
            probability_legal -= self.probability_pin(from_, to_)
            probability_illegal = 1. - probability_legal
            probability_capture = (self.chess.M_white[1][self.time_stamp_][to_[0]][to_[1]] +
                                   self.chess.M_white[2][self.time_stamp_][to_[0]][
                                       to_[1]]) / 2.
            probability_silent = 1. - probability_capture
            probability_sum = probability_illegal + probability_silent + probability_capture
            probability_silent /= probability_sum
            probability_capture /= probability_sum
            probability_illegal /= probability_sum
            pieces_can_attack = 0
            for i in range(0, 8):
                for j in range(0, 8):
                    if self.chess.board_black[i][j].info['color'] == 'b':
                        pos_ = i, j
                        possible_squares = self.chess.select_moves(pos_, 1)
                        pieces_can_attack += possible_squares.count(to_)
            probability_matrix_white = [[[0 for i in range(0, 8)] for i in range(0, 8)] for i in range(0, 3)]
            probability_matrix_black = [[[0 for i in range(0, 8)] for i in range(0, 8)] for i in range(0, 3)]
            for i in range(0, 3):
                for j in range(0, 8):
                    for l in range(0, 8):
                        probability_matrix_white[i][j][l] = self.chess.M_white[i][self.time_stamp_][j][l]
                        probability_matrix_black[i][j][l] = self.chess.M_black[i][self.time_stamp_][j][l]

            product = probability_capture
            for i in range(1, pieces_can_attack):
                max_prob = 0.
                for ii in range(0, 8):
                    for jj in range(0, 8):
                        max_prob = max(max_prob, self.probability_control((ii, jj), probability_matrix_white, 0))
                probability_to_capture_back = self.probability_control(to_, probability_matrix_white, 0) / max_prob
                probability_to_play_silent_move = 1 - probability_to_capture_back
                child_score[son][0] += product * probability_to_play_silent_move
                product *= probability_to_capture_back
                for piece in range(0, 3):
                    for i1 in range(0, 8):
                        for j1 in range(0, 8):
                            if abs(to_[0] - i1) == abs(to_[1] - j1) or to_[0] - i1 == 0 or to_[1] - j1 == 0:
                                probability_matrix_white[piece][i1][j1] *= 0.5

            max_prob = 0.
            for ii in range(0, 8):
                for jj in range(0, 8):
                    max_prob = max(max_prob, self.probability_control((ii, jj), probability_matrix_white, 0))
            probability_to_capture_back = self.probability_control(to_, probability_matrix_white, 0) / max_prob
            child_score[son][0] -= probability_to_capture_back * probability_silent

        child_score.sort(key=lambda x: x[0], reverse=True)
        has_moved = 0
        self.chess.queue_message.pop()
        self.chess.last_shown_message_index = min(self.chess.last_shown_message_index, len(self.chess.queue_message))
        for i in range(0, len(child_score)):
            child_index = child_list[child_score[i][1]]
            legal_moves = self.chess.select_moves(child_index[0], 1)
            if legal_moves.count(child_index[1]) > 0:
                if self.chess.board[child_index[1][0]][child_index[1][1]].info['type'] is None:
                    self.chess.queue_message.append("player with black pieces moved")
                    self.chess.last_shown_message_index = len(self.chess.queue_message)
                else:
                    line = "12345678"
                    column = "ABCDEFGH"
                    msg = f"Black captured a piece from {column[7 - child_index[0][1]]}{line[7 - child_index[0][0]]} to {column[7 - child_index[1][1]]}{line[7 - child_index[1][0]]}"
                    self.chess.queue_message.append(msg)
                    self.chess.last_shown_message_index = len(self.chess.queue_message)
                has_moved = 1
                self.chess.move_piece(child_index[0], child_index[1], 1)
                self.chess.update_display(black, background_, screen_, window_width_)
                break
            else:
                if self.chess.is_black_checked2(self.chess.get_black_king_position(), 1) and \
                        self.chess.board_black[child_index[0][0]][child_index[0][1]].info[
                            'type'] != 'k':
                    continue
                self.chess.queue_message.append("Black tried an invalid move")
                self.chess.last_shown_message_index = len(self.chess.queue_message)
                self.chess.update_display(black, background_, screen_, window_width_)

        if self.chess.is_white_checked2(self.chess.get_white_king_position(), 0):
            msg = "White king is checked!"
            self.chess.queue_message.append(msg)
            self.chess.last_shown_message_index = len(self.chess.queue_message)

        if has_moved == 0:
            if self.chess.is_black_checked(self.chess.get_black_king_position(), 1):
                self.chess.white_won = True
            else:
                self.chess.stalemate = True
            return

    def move_black_monte_carlo(self, black, background_, screen_, window_width_):
        self.chess.nodes_counter_in_mcts = 0
        curr_board = copy.deepcopy(self.chess.board)
        root = Node(1, 0, curr_board)
        for i in range(0, self.no_iter):
            self.mc_dfs(root, black, background_, screen_, window_width_)
            print(time.time() - self.start)
            if time.time() > self.start + self.PERIOD_OF_TIME: break
        self.start = time.time()

        self.dfs_check_tree_structure(root)
        #  for i in range(1, nodes_counter_in_mcts + 1):
        #      print(f" node {i} --> {visited_vector[i]} and  {score_vector[i]}", end='\n')
        curr_val = 0
        best_node = -1
        nod = root
        for ch in range(0, self.get_child_size()):
            val = self.v[ch].get_score()
            if val > curr_val:
                curr_val = val
                best_node = ch
        if nod.get_child_size() == 0:
            if self.chess.is_black_checked(self.chess.get_black_king_position(), 1):
                self.chess.white_won = True
            else:
                self.chess.stalemate = True
        else:
            #    print(best_node)
            self.chess.board = copy.deepcopy(nod.v[best_node].get_config())
        if self.random_vs_mc == 0:
            self.chess.queue_message.pop()
        self.chess.queue_message.append("player with black pieces moved")
        self.chess.last_shown_message_index = len(self.chess.queue_message)

    def mco_vs_random(self, black, background_, screen_, window_width_, moves__):
        self.random_vs_mc = 1
        while (not self.chess.white_won) and (not self.chess.black_won) and (not self.chess.stalemate) and (not self.chess.draw):
            if moves__ % 2 == 0:
                self.chess.move_white_ai(moves__, black, background_, screen_, window_width_)
                moves__ += 1
                self.chess.update_display(black, background_, screen_, window_width_)
            else:
                if self.time_stamp_ < 100:
                    self.move_black_monte_carlo_optimized(black, background_, screen_, window_width_)
                else:
                    self.chess.move_black_ai(moves__)
                moves__ += 1
                self.time_stamp_ += 1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.chess.update_display(black, background_, screen_, window_width_)

    def random_vs_monteCarlo(self, black, background_, screen_, window_width_, moves__):
        """ computer plays black and whites pieces """
        while (not self.chess.white_won) and (not self.chess.black_won) and (not self.chess.stalemate) and (not self.chess.draw):
            if moves__ % 2 == 0:
                self.chess.move_white_ai(moves__, black, background_, screen_, window_width_)
                moves__ += 1
            else:
                self.move_black_monte_carlo(black, background_, screen_, window_width_)
                moves__ += 1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.chess.update_display(black, background_, screen_, window_width_)

