import copy
import numpy as np
import pygame
import random
import math
import sys
import time
from Piece import Piece
from Node import Node

pygame.display.set_caption("Chess")


start = time.time()

PERIOD_OF_TIME = 30  # 5min

random_vs_mc = 0
no_iter = 0
time_stamp_ = 1

def create_child_nodes(nod):
    global board, nodes_counter_in_mcts
    moves_to_do = generate_possible_moves()
    for i in range(0, len(moves_to_do)):
        curr_board = copy.deepcopy(board)
        move_piece(moves_to_do[i][0], moves_to_do[i][1], moves_to_do[i][2])
        nodes_counter_in_mcts += 1
        curr_node = Node(nodes_counter_in_mcts, nod.get_index(), board)
        nod.add_child(curr_node)
        board = copy.deepcopy(curr_board)


def dfs_check_tree_structure(nod):
    for ch in range(0, nod.get_child_size()):
        # print(str(nod.get_index()) + "  " + str(nod.v[ch].get_index()))
        dfs_check_tree_structure(nod.v[ch])


def mc_dfs(nod, black, background_, screen_, window_width_):
    if nod.get_child_size() == 0:
        if nod.get_visited() == 0.00001:
            reward = simulate_game(nod.config, black, background_, screen_, window_width_)
            nod.update_score(reward)
            nod.update_visit()
            visited_vector[nod.get_index()] = nod.get_visited()
            score_vector[nod.get_index()] = nod.get_score()
            return reward
        else:
            create_child_nodes(nod)
    if nod.get_child_size() == 0:
        if is_black_checked(get_black_king_position(), 1):
            return 0
        else:
            return 1
    curr_val = 0
    next_node = -1
    for ch in range(0, nod.get_child_size()):
        val = nod.v[ch].get_formula_value(nod.get_visited())
        if val > curr_val:
            curr_val = val
            next_node = ch
    nod.update_score(mc_dfs(nod.v[next_node], black, background_, screen_, window_width_))
    nod.update_visit()
    visited_vector[nod.get_index()] = nod.get_visited()
    score_vector[nod.get_index()] = nod.get_score()


def create_random_matrix():
    global M_white, M_black
    M_white = np.random.uniform(size=np.shape(M_white))
    M_black = np.random.uniform(size=np.shape(M_black))

def probability_control(pos_, prob_table, tip):
    global time_stamp_
    ret = 0.
    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            if i == 0 and j == 0:
                continue
            if inside_board(i, j):
                if tip == 1:
                    ret += prob_table[0][time_stamp_][i][j]
                else:
                    ret += prob_table[0][i][j]
    if inside_board(pos_[0] - 1, pos_[1] - 1):
        if tip == 1:
            ret += prob_table[0][time_stamp_][pos_[0] - 1][pos_[1] - 1]
        else:
            ret += prob_table[0][pos_[0] - 1][pos_[1] - 1]
    if inside_board(pos_[0] - 1, pos_[1] + 1):
        if tip == 1:
            ret += prob_table[0][time_stamp_][pos_[0] - 1][pos_[1] + 1]
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
            while inside_board(curr_pos0, curr_pos1):
                c2 = 1. / (seq_len - 1.)
                ret += c1 * probability_free_range((curr_pos0, curr_pos1), (pos_[0], pos_[1])) * c2
                curr_pos0 = curr_pos0 + i
                curr_pos1 = curr_pos1 + j
                seq_len += 1
    return ret


def probability_free_range(from_, to_):
    global board
    global time_stamp_
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
        if not inside_board(from_0, from_1):
            break
        from_0 += i_ratio
        from_1 += j_ratio
        probability_ *= 1 - M_white[0][time_stamp_][from_0][from_1] - M_white[1][time_stamp_][from_0][
            from_1] - M_white[2][time_stamp_][from_0][from_1]
    return probability_


def probability_pin(from_, to_):
    global board
    global time_stamp_
    if board[from_[0]][from_[1]].info['type'] == 'k':
        return probability_control(to_, M_white, 1)
    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            if i == 0 and j == 0:
                continue
            curr_pos = list(from_)
            curr_pos[0] += i
            curr_pos[1] += j
            while inside_board(curr_pos[0], curr_pos[1]):
                if board[curr_pos[0]][curr_pos[1]].info['type'] == 'k':
                    return probability_control(from_, M_white, 1)
                if board[curr_pos[0]][curr_pos[1]].info['type'] is not None:
                    break
                curr_pos[0] += i
                curr_pos[1] += j
    return 0


def move_black_monte_carlo_optimized(black, background_, screen_, window_width_):
    global board_black, queue_message, last_shown_message_index
    global time_stamp_, white_won, stalemate, black_won
    create_random_matrix()
    queue_message.append("loading...")
    last_shown_message_index = len(queue_message)
    update_display(black, background_, screen_, window_width_)
    child_list = []
    for i in range(0, 8):
        for j in range(0, 8):
            if board_black[i][j].info['color'] == 'b':
                my_list = select_moves_black((i, j), 1)
                for it in my_list:
                    child_list.append(((i, j), it))
    child_score = [[0., 0] for i in range(len(child_list))]
    for son in range(0, len(child_list)):
        child_score[son][1] = son
        from_ = (child_list[son][0])
        to_ = (child_list[son][1])
        probability_legal = 1.
        if board_black[from_[0]][from_[1]].info['type'] != 'n' and board_black[from_[0]][from_[1]].info['type'] != 'p':
            probability_legal *= probability_free_range(from_, to_)
        probability_legal -= probability_pin(from_, to_)
        probability_illegal = 1. - probability_legal
        probability_capture = (M_white[1][time_stamp_][to_[0]][to_[1]] + M_white[2][time_stamp_][to_[0]][to_[1]]) / 2.
        probability_silent = 1. - probability_capture
        probability_sum = probability_illegal + probability_silent + probability_capture
        probability_silent /= probability_sum
        probability_capture /= probability_sum
        probability_illegal /= probability_sum
        pieces_can_attack = 0
        for i in range(0, 8):
            for j in range(0, 8):
                if board_black[i][j].info['color'] == 'b':
                    pos_ = i, j
                    possible_squares = select_moves(pos_, 1)
                    pieces_can_attack += possible_squares.count(to_)
        probability_matrix_white = [[[0 for i in range(0, 8)] for i in range(0, 8)] for i in range(0, 3)]
        probability_matrix_black = [[[0 for i in range(0, 8)] for i in range(0, 8)] for i in range(0, 3)]
        for i in range(0, 3):
            for j in range(0, 8):
                for l in range(0, 8):
                    probability_matrix_white[i][j][l] = M_white[i][time_stamp_][j][l]
                    probability_matrix_black[i][j][l] = M_black[i][time_stamp_][j][l]

        product = probability_capture
        for i in range(1, pieces_can_attack):
            max_prob = 0.
            for ii in range(0, 8):
                for jj in range(0, 8):
                    max_prob = max(max_prob, probability_control((ii, jj), probability_matrix_white, 0))
            probability_to_capture_back = probability_control(to_, probability_matrix_white, 0) / max_prob
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
                max_prob = max(max_prob, probability_control((ii, jj), probability_matrix_white, 0))
        probability_to_capture_back = probability_control(to_, probability_matrix_white, 0) / max_prob
        child_score[son][0] -= probability_to_capture_back * probability_silent

    child_score.sort(key=lambda x: x[0], reverse=True)
    has_moved = 0
    is_capture = 0
    queue_message.pop()
    last_shown_message_index = min(last_shown_message_index, len(queue_message))
    for i in range(0, len(child_score)):
        child_index = child_list[child_score[i][1]]
        legal_moves = select_moves(child_index[0], 1)
        if legal_moves.count(child_index[1]) > 0:
            if board[child_index[1][0]][child_index[1][1]].info['type'] is None:
                queue_message.append("player with black pieces moved")
                last_shown_message_index = len(queue_message)
            else:
                line = "12345678"
                column = "ABCDEFGH"
                msg = f"Black captured a piece from {column[7 - child_index[0][1]]}{line[7 - child_index[0][0]]} to {column[7 - child_index[1][1]]}{line[7 - child_index[1][0]]}"
                queue_message.append(msg)
                last_shown_message_index = len(queue_message)
            has_moved = 1
            move_piece(child_index[0], child_index[1], 1)
            update_display(black, background_, screen_, window_width_)
            break
        else:
            if is_black_checked2(get_black_king_position(), 1) and \
                    board_black[child_index[0][0]][child_index[0][1]].info[
                        'type'] != 'k':
                continue
            queue_message.append("Black tried an invalid move")
            last_shown_message_index = len(queue_message)
            update_display(black, background_, screen_, window_width_)

    if is_white_checked2(get_white_king_position(), 0):
        msg = "White king is checked!"
        queue_message.append(msg)
        last_shown_message_index = len(queue_message)

    if has_moved == 0:
        if is_black_checked(get_black_king_position(), 1):
            white_won = True
        else:
            stalemate = True
        return
    global random_vs_mc


def move_black_monte_carlo(black, background_, screen_, window_width_):
    global board, nodes_counter_in_mcts, white_won, stalemate, queue_message, last_shown_message_index, no_iter
    nodes_counter_in_mcts = 0
    curr_board = copy.deepcopy(board)
    root = Node(1, 0, curr_board)
    for i in range(0, no_iter):
        mc_dfs(root, black, background_, screen_, window_width_)
        global start, PERIOD_OF_TIME
        print(time.time() - start)
        if time.time() > start + PERIOD_OF_TIME: break
    start = time.time()

    dfs_check_tree_structure(root)
    #  for i in range(1, nodes_counter_in_mcts + 1):
    #      print(f" node {i} --> {visited_vector[i]} and  {score_vector[i]}", end='\n')
    curr_val = 0
    best_node = -1
    nod = root
    for ch in range(0, nod.get_child_size()):
        val = nod.v[ch].get_score()
        if val > curr_val:
            curr_val = val
            best_node = ch
    if nod.get_child_size() == 0:
        if is_black_checked(get_black_king_position(), 1):
            white_won = True
        else:
            stalemate = True
    else:
        #    print(best_node)
        board = copy.deepcopy(nod.v[best_node].get_config())
    global random_vs_mc
    if random_vs_mc == 0:
        queue_message.pop()
    queue_message.append("player with black pieces moved")
    last_shown_message_index = len(queue_message)

def select_moves_black(pos_, moves_):
    """ returns list of available moves for the piece located in pos_"""
    x_, y_ = pos_
    if (board_black[x_][y_].info['color'] == 'w' and moves_ % 2 == 1) or (
            board_black[x_][y_].info['color'] == 'b' and moves_ % 2 == 0):
        return []
    ret = []
    if board_black[x_][y_].info['type'] == 'p':
        if board_black[x_][y_].info['color'] == 'b':
            ret = black_pawn_to_move2_black(pos_, moves_)
            if inside_board(x_ + 1, y_ + 1) and white_en_passant[y_ + 1] and x_ == 4:
                ret.extend([(x_ + 1, y_ + 1)])
            if inside_board(x_ + 1, y_ - 1) and white_en_passant[y_ - 1] and x_ == 4:
                ret.extend([(x_ + 1, y_ - 1)])
    if board[x_][y_].info['type'] == 'n':
        ret = knight_to_move2_black(pos_, moves_)
    if board[x_][y_].info['type'] == 'r':
        ret = rook_to_move2_black(pos_, moves_)
    if board[x_][y_].info['type'] == 'b':
        ret = bishop_to_move2_black(pos_, moves_)
    if board[x_][y_].info['type'] == 'q':
        ret = queen_to_move2_black(pos_, moves_)
    if board[x_][y_].info['type'] == 'k':
        ret = king_to_move2_black(pos_, moves_)
        if (not right_black_rook_has_moved) and (not black_king_has_moved) and (not board[0][1].info['occupied']) and (
                not board[0][2].info['occupied']):
            ret.extend([(-2, -2)])
        if (not left_black_rook_has_moved) and (not black_king_has_moved) and (not board[0][4].info['occupied']) and (
                not board[0][5].info['occupied']):
            ret.extend([(-4, -4)])
    return ret

def make_them_killable(possible_):
    """ mark available squares """
    for i in possible_:
        if i == (-1, -1):
            board[7][1].update('killable', True)
            continue
        if i == (-2, -2):
            board[0][1].update('killable', True)
            continue
        if i == (-3, -3):
            board[7][5].update('killable', True)
            continue
        if i == (-4, -4):
            board[0][5].update('killable', True)
            continue
        board[i[0]][i[1]].update('killable', True)


def make_them_not_killable(possible_):
    """ unmark available squares """
    for i in possible_:
        if i == (-1, -1):
            board[7][1].update('killable', False)
            continue
        if i == (-2, -2):
            board[0][1].update('killable', False)
            continue
        if i == (-3, -3):
            board[7][5].update('killable', False)
            continue
        if i == (-4, -4):
            board[0][5].update('killable', False)
            continue
        board[i[0]][i[1]].update('killable', False)


def simulate_move2(from_, to_, moves_, check):
    """return True if moving piece from from_ to to_ is a valid move, i.e it doesnt discover the king"""
    global board
    board2 = copy.deepcopy(board)
    board[to_[0]][to_[1]].update('type', board[from_[0]][from_[1]].info['type'])
    board[from_[0]][from_[1]].update('type', None)
    board[to_[0]][to_[1]].update('color', board[from_[0]][from_[1]].info['color'])
    board[from_[0]][from_[1]].update('color', None)
    board[to_[0]][to_[1]].update('image', board[from_[0]][from_[1]].info['image'])
    board[from_[0]][from_[1]].update('image', None)
    board[to_[0]][to_[1]].update('occupied', True)
    board[from_[0]][from_[1]].update('occupied', False)
    board[to_[0]][to_[1]].update('killable', False)
    board[from_[0]][from_[1]].update('killable', False)
    if moves_ % 2 == 0:
        if is_white_checked2(get_white_king_position(), moves_):
            board = copy.deepcopy(board2)
            return False
    if moves_ % 2 == 1:
        if is_black_checked2(get_black_king_position(), moves_):
            board = copy.deepcopy(board2)
            return False
    board = copy.deepcopy(board2)
    return True


def mco_vs_random(black, background_, screen_, window_width_, moves__):
    global white_won, black_won, stalemate, draw, random_vs_mc, time_stamp_, queue_message, last_shown_message_index
    random_vs_mc = 1
    while (not white_won) and (not black_won) and (not stalemate) and (not draw):
        if moves__ % 2 == 0:
            move_white_ai(moves__, black, background_, screen_, window_width_)
            moves__ += 1
            update_display(black, background_, screen_, window_width_)
        else:
            if time_stamp_ < 100:
                move_black_monte_carlo_optimized(black, background_, screen_, window_width_)
            else:
                move_black_ai(moves__)
            moves__ += 1
            time_stamp_ += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        update_display(black, background_, screen_, window_width_)


def random_vs_random(black, background_, screen_, window_width_, moves__):
    """ computer plays black and whites pieces """
    global white_won, black_won, stalemate, draw
    while (not white_won) and (not black_won) and (not stalemate) and (not draw):
        if moves__ % 2 == 0:
            move_white_ai(moves__, black, background_, screen_, window_width_)
            moves__ += 1
        else:
            move_black_ai(moves__)
            moves__ += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        update_display(black, background_, screen_, window_width_)


def random_vs_monteCarlo(black, background_, screen_, window_width_, moves__):
    """ computer plays black and whites pieces """
    global white_won, black_won, stalemate, draw
    while (not white_won) and (not black_won) and (not stalemate) and (not draw):
        if moves__ % 2 == 0:
            move_white_ai(moves__, black, background_, screen_, window_width_)
            moves__ += 1
        else:
            move_black_monte_carlo(black, background_, screen_, window_width_)
            moves__ += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        update_display(black, background_, screen_, window_width_)


count = 0


if __name__ == '__main__':
    command = sys.argv[1]
    see_me = sys.argv[2]
    selected = False
    moves = 0
    piece_to_move = []
    possible = []
    current_note_piece = 0

build_starting_board(window_width / 16)
build_starting_board2(window_width / 16)

if command == 'cc':
    mco_vs_random(black, background, screen, window_width, 0)
else:
    if command == 'rmc':
        random_vs_mc = 1
        random_vs_monteCarlo(black, background, screen, window_width, 1)
    else:
        while (not white_won) and (not black_won) and (not stalemate) and (not draw):
            pygame.time.delay(50)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if check_clicked_on_arrows(pos, window_width) != 0:
                        update_display(black, background, screen, window_width)
                        continue

                    position_on_note = get_note_table_cell([0, 400, 50])
                    if 0 <= position_on_note[0] <= 8 and 0 <= position_on_note[1] <= 7:
                        if current_note_piece == 0:
                            if position_on_note[0] == 8:
                                if position_on_note[0] != 0:
                                    if position_on_note[1] - 1 == 6:
                                        current_note_piece = -1
                                    else:
                                        current_note_piece = position_on_note[1] - 1 + 1
                        else:
                            if position_on_note[0] != 8:
                                if current_note_piece == -1:
                                    note_table[position_on_note[0]][position_on_note[1]] = 0
                                    current_note_piece = 0
                                else:
                                    note_table[position_on_note[0]][position_on_note[1]] = current_note_piece
                                    current_note_piece = 0

                    x, y = get_pos(pos, window_width / 16)
                    x, y = y, 7 - x
                    if x > 7 or y > 7:
                        continue
                    if not selected:
                        possible = select_moves((x, y), moves)
                        make_them_killable(possible)
                        piece_to_move = x, y
                        if len(possible) != 0:
                            selected = True
                    else:
                        if board[x][y].info['killable']:
                            row, col = piece_to_move
                            if moves % 2 == 0 and board[row][col].info['type'] == 'p' and col != y and (
                                    not board[x][y].info['occupied']) and row == 3:
                                clear_square((x + 1, y))
                            if moves % 2 == 1 and board[row][col].info['type'] == 'p' and col != y and (
                                    not board[x][y].info['occupied']) and row == 4:
                                clear_square((x - 1, y))
                            if piece_to_move == (7, 3) and (x, y) == (7, 1):
                                move_piece((7, 0), (7, 2), moves)
                                move_counter -= 1
                            if piece_to_move == (0, 3) and (x, y) == (0, 1):
                                move_piece((0, 0), (0, 2), moves)
                                move_counter -= 1
                            if piece_to_move == (7, 3) and (x, y) == (7, 5):
                                move_piece((7, 7), (7, 4), moves)
                                move_counter -= 1
                            if piece_to_move == (0, 3) and (x, y) == (0, 5):
                                move_piece((0, 7), (0, 4), moves)
                                move_counter -= 1

                            if board[x][y].info['type'] is None:
                                queue_message.append("player with white pieces moved")
                                last_shown_message_index = len(queue_message)
                            else:
                                line = "12345678"
                                column = "ABCDEFGH"
                                msg = f"White captured a piece from {column[7 - piece_to_move[1]]}{line[7 - piece_to_move[0]]} to {column[7 - y]}{line[7 - x]}"
                                queue_message.append(msg)
                                last_shown_message_index = len(queue_message)

                            move_piece(piece_to_move, (x, y), moves)
                            moves += 1
                            if command == 'hc':
                                no_iter = 2
                                make_them_not_killable(possible)
                                if is_black_checked(get_black_king_position(), 1):
                                    queue_message.append("Black king is checked")
                                    last_shown_message_index = len(queue_message)
                                random_vs_mc = 0
                                move_black_monte_carlo_optimized(black, background, screen, window_width)
                                moves += 1
                        else:
                            queue_message.append("White tried an invalid move")
                            last_shown_message_index = len(queue_message)
                        make_them_not_killable(possible)
                        possible = []
                        selected = False
                        pieces_ = []
                        for i in range(0, 8):
                            for j in range(0, 8):
                                if (board[i][j].info['color'] == 'w' and moves % 2 == 0) or (
                                        (board[i][j].info['color'] == 'b' and moves % 2 == 1)):
                                    pieces_.append((i, j))
                        random.shuffle(pieces_)
                        player_ok = True
                        for sz in range(0, len(pieces_)):
                            possible_ = select_moves(pieces_[sz], moves)
                            if len(possible_) == 0:
                                continue
                            player_ok = False
                            break
                        if player_ok:
                            if moves % 2 == 1 and is_black_checked(get_black_king_position(), moves):
                                white_won = True
                            else:
                                if moves % 2 == 0 and is_white_checked(get_white_king_position(), moves):
                                    black_won = True
                                else:
                                    stalemate = True

            update_display(black, background, screen, window_width)

if draw:
    msg = "Draw"
    queue_message.append(msg)
    last_shown_message_index = len(queue_message)
if stalemate:
    msg = "Stalemate"
    queue_message.append(msg)
    last_shown_message_index = len(queue_message)
if black_won:
    msg = "Black won!"
    queue_message.append(msg)
    last_shown_message_index = len(queue_message)
if white_won:
    msg = "White won!"
    queue_message.append(msg)
    last_shown_message_index = len(queue_message)

while True:

    update_display(black, background, screen, window_width)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if check_clicked_on_arrows(pos, window_width) != 0:
                update_display(black, background, screen, window_width)
                continue
