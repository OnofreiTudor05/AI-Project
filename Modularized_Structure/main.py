import pygame
import random
import sys
from Chess import Chess
from Node import Node

pygame.display.set_caption("Chess")

count = 0

if __name__ == '__main__':
    command = sys.argv[1]
    see_me = sys.argv[2]
    selected = False
    moves = 0
    piece_to_move = []
    possible = []
    current_note_piece = 0

    chess = Chess()
    node = Node(1, 0, chess.board)
    chess.build_starting_board(chess.window_width / 16)
    chess.build_starting_board2(chess.window_width / 16)

    background = pygame.image.load(chess.PATH + 'board.jpg')
    background = pygame.transform.scale(background, (400, 400))

    if command == 'cc':
        node.mco_vs_random(chess.black, background, chess.screen, chess.window_width, 0)
    else:
        if command == 'rmc':
            chess.random_vs_mc = 1
            chess.random_vs_monteCarlo(chess.black, background, chess.screen, chess.window_width, 1)
        else:
            while (not chess.white_won) and (not chess.black_won) and (not chess.stalemate) and (not chess.draw):
                pygame.time.delay(50)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pos = pygame.mouse.get_pos()
                        if chess.check_clicked_on_arrows(pos, chess.window_width) != 0:
                            chess.update_display(chess.black, background, chess.screen, chess.window_width)
                            continue

                        position_on_note = chess.get_note_table_cell([0, 400, 50])
                        if 0 <= position_on_note[0] <= 8 and 0 <= position_on_note[1] <= 7:
                            if current_note_piece == 0:
                                if position_on_note[0] == 8:
                                    if position_on_note[0] != 0:
                                        if position_on_note[1] - 1 == 6:
                                            chess.current_note_piece = -1
                                        else:
                                            chess.current_note_piece = position_on_note[1] - 1 + 1
                            else:
                                if position_on_note[0] != 8:
                                    if chess.current_note_piece == -1:
                                        chess.note_table[position_on_note[0]][position_on_note[1]] = 0
                                        chess.current_note_piece = 0
                                    else:
                                        chess.note_table[position_on_note[0]][position_on_note[1]] = chess.current_note_piece
                                        chess.current_note_piece = 0

                        x, y = chess.get_pos(pos, chess.window_width / 16)
                        x, y = y, 7 - x
                        if x > 7 or y > 7:
                            continue
                        if not selected:
                            possible = chess.select_moves((x, y), moves)
                            chess.make_them_killable(possible)
                            piece_to_move = x, y
                            if len(possible) != 0:
                                selected = True
                        else:
                            if chess.board[x][y].info['killable']:
                                row, col = piece_to_move
                                if moves % 2 == 0 and chess.board[row][col].info['type'] == 'p' and col != y and (
                                        not chess.board[x][y].info['occupied']) and row == 3:
                                    chess.clear_square((x + 1, y))
                                if moves % 2 == 1 and chess.board[row][col].info['type'] == 'p' and col != y and (
                                        not chess.board[x][y].info['occupied']) and row == 4:
                                    chess.clear_square((x - 1, y))
                                if piece_to_move == (7, 3) and (x, y) == (7, 1):
                                    chess.move_piece((7, 0), (7, 2), moves)
                                    chess.move_counter -= 1
                                if piece_to_move == (0, 3) and (x, y) == (0, 1):
                                    chess.move_piece((0, 0), (0, 2), moves)
                                    chess.move_counter -= 1
                                if piece_to_move == (7, 3) and (x, y) == (7, 5):
                                    chess.move_piece((7, 7), (7, 4), moves)
                                    chess.move_counter -= 1
                                if piece_to_move == (0, 3) and (x, y) == (0, 5):
                                    chess.move_piece((0, 7), (0, 4), moves)
                                    chess.move_counter -= 1

                                if chess.board[x][y].info['type'] is None:
                                    chess.queue_message.append("player with white pieces moved")
                                    last_shown_message_index = len(chess.queue_message)
                                else:
                                    line = "12345678"
                                    column = "ABCDEFGH"
                                    msg = f"White captured a piece from {column[7 - piece_to_move[1]]}{line[7 - piece_to_move[0]]} to {column[7 - y]}{line[7 - x]}"
                                    chess.queue_message.append(msg)
                                    chess.last_shown_message_index = len(chess.queue_message)

                                chess.move_piece(piece_to_move, (x, y), moves)
                                moves += 1
                                if command == 'hc':
                                    no_iter = 2
                                    chess.make_them_not_killable(possible)
                                    if chess.is_black_checked(chess.get_black_king_position(), 1):
                                        chess.queue_message.append("Black king is checked")
                                        chess.last_shown_message_index = len(chess.queue_message)
                                    random_vs_mc = 0
                                    node.move_black_monte_carlo_optimized(chess.black, background, chess.screen, chess.window_width)
                                    moves += 1
                            else:
                                chess.queue_message.append("White tried an invalid move")
                                chess.last_shown_message_index = len(chess.queue_message)
                            chess.make_them_not_killable(possible)
                            possible = []
                            selected = False
                            pieces_ = []
                            for i in range(0, 8):
                                for j in range(0, 8):
                                    if (chess.board[i][j].info['color'] == 'w' and moves % 2 == 0) or (
                                            (chess.board[i][j].info['color'] == 'b' and moves % 2 == 1)):
                                        pieces_.append((i, j))
                            random.shuffle(pieces_)
                            player_ok = True
                            for sz in range(0, len(pieces_)):
                                possible_ = chess.select_moves(pieces_[sz], moves)
                                if len(possible_) == 0:
                                    continue
                                player_ok = False
                                break
                            if player_ok:
                                if moves % 2 == 1 and chess.is_black_checked(chess.get_black_king_position(), moves):
                                    chess.white_won = True
                                else:
                                    if moves % 2 == 0 and chess.is_white_checked(chess.get_white_king_position(), moves):
                                        chess.black_won = True
                                    else:
                                        chess.stalemate = True

                chess.update_display(chess.black, background, chess.screen, chess.window_width)

    if chess.draw:
        msg = "Draw"
        chess.queue_message.append(msg)
        chess.last_shown_message_index = len(chess.queue_message)
    if chess.stalemate:
        msg = "Stalemate"
        chess.queue_message.append(msg)
        chess.last_shown_message_index = len(chess.queue_message)
    if chess.black_won:
        msg = "Black won!"
        chess.queue_message.append(msg)
        chess.last_shown_message_index = len(chess.queue_message)
    if chess.white_won:
        msg = "White won!"
        chess.queue_message.append(msg)
        chess.last_shown_message_index = len(chess.queue_message)

    while True:

        chess.update_display(chess.black, background, chess.screen, chess.window_width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if chess.check_clicked_on_arrows(pos, chess.window_width) != 0:
                    chess.update_display(chess.black, background, chess.screen, chess.window_width)
                    continue
