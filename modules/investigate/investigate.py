import chess

def sign(a):
    if a > 0:
        return 1
    elif a < 0:
        return -1
    else:
        return 0

def material_value(board):
    total = 0
    for i in chess.SQUARES:
        square = board.piece_at(i)
        if square is not None:
            if square.piece_type == chess.KNIGHT:
                total += 3
            elif square.piece_type == chess.BISHOP:
                total += 3
            elif square.piece_type == chess.ROOK:
                total += 5.5
            elif square.piece_type == chess.QUEEN:
                total += 9
    return total

def investigate(a, b, board):
    # determine if the difference between position A and B 
    # is worth investigating for a puzzle.
    if a.cp is not None and b.cp is not None:
        if (((a.cp < 850 and a.cp > -110 and b.cp > 200 and b.cp < 850)
            or (a.cp > -850 and a.cp < 110 and b.cp < -200 and b.cp > -850))
            and material_value(board) > 3
            and sign(a.cp) == sign(b.cp)):
            return True
    elif (a.cp is not None
        and b.mate is not None
        and material_value(board) > 3):
        if ((a.cp < 110 and sign(b.mate) == -1)
            or (a.cp > -110 and sign(b.mate) == 1)):
            return True
    elif (a.mate is not None
        and b.mate is not None):
        if sign(a.mate) == sign(b.mate): #actually means that they're opposite
            return True
    return False