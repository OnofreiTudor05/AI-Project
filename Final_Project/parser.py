import chess.pgn
import numpy as np

f = open("lichess_db_standard_rated_2014-10.pgn", encoding="utf-8")
file_white = open("white_results.txt", "w")
file_black = open("black_results.txt", "w")
# pawn, rook, bishop, queen, knight, king
M_black = [[[[0. for i in range(0, 8)] for i in range(0, 8)] for i in range(0, 100)] for i in range(0, 3)]
M_white = [[[[0. for i in range(0, 8)] for i in range(0, 8)] for i in range(0, 100)] for i in range(0, 3)]

print(np.shape(M_black))
my_list = []
# lowercase is black
# uppercase is white
number_of_total_games = 1000000
for i in range(0, number_of_total_games):
    if i % 1000 == 0:
        print(i)
    game = chess.pgn.read_game(f)
    if game is None:
        break
    board = game.board()
    moves_counter = 0
    for move in game.mainline_moves():
        for ii in range(0, 8):
            for j in range(0, 8):
                if moves_counter > 99:
                    continue
                position = (7 - ii) * 8 + j
                new_i = 7 - ii
                new_j = j
                if str(board.piece_at(position)) == "k":
                    M_black[0][moves_counter][new_i][new_j] += 1
                if str(board.piece_at(position)) == 'p':
                    M_black[1][moves_counter][new_i][new_j] += 1
                if str(board.piece_at(position)) == 'q' or str(board.piece_at(position)) == 'r' or str(
                        board.piece_at(position)) == 'b':
                    M_black[2][moves_counter][new_i][new_j] += 1

                if str(board.piece_at(position)) == 'K':
                    M_white[0][moves_counter][new_i][new_j] += 1
                if str(board.piece_at(position)) == 'P':
                    M_white[1][moves_counter][new_i][new_j] += 1
                if str(board.piece_at(position)) == 'Q' or str(board.piece_at(position)) == 'R' or str(
                        board.piece_at(position)) == 'B':
                    M_white[2][moves_counter][new_i][new_j] += 1
        board.push(move)
        moves_counter = moves_counter + 1
    if i % 100 == 0:
        print(i)
for i in range(0, 3):
    for j in range(0, 100):
        for l in range(0, 8):
            for k in range(0, 8):
                M_white[i][j][l][k] /= number_of_total_games
                M_black[i][j][l][k] /= number_of_total_games
                if i == 2:
                    M_white[i][j][l][k] /= 3.
                    M_black[i][j][l][k] /= 3.

for piece in range(3):
    for moves in range(100):
        for line in range(8):
            for column in range(8):
                file_white.write(str(M_white[piece][moves][line][column]) + " ")
            file_white.write("\n")
        file_white.write("\n")

for piece in range(3):
    for moves in range(100):
        for line in range(8):
            for column in range(8):
                file_black.write(str(M_black[piece][moves][line][column]) + " ")
            file_black.write("\n")
        file_black.write("\n")
