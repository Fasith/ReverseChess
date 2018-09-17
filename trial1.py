import time
import chess.variant
from random import randint

board = chess.variant.SuicideBoard()
Flag = True


while (True):
    legal_moves = board.legal_moves
    k = []
    for move in legal_moves:
        k.append(move)

    l = len(k)
    if l == 0 or board.is_variant_draw() == True:
        break
    rand = randint(0,l-1)
    move = k[rand]
    board.push(move)
    print(move)
    if Flag == True:
        Flag = False
    else:
        Flag = True
    
    
    print(board)
    input()

print("GAME_OVER")
print(board.result())
