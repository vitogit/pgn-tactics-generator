import chess
import chess.uci
import chess.pgn
from modules.puzzle.puzzle import puzzle

engine = chess.uci.popen_engine("Stockfish/stockfish-7-linux/Linux/stockfish 7 x64")
engine.uci()
info_handler = chess.uci.InfoHandler()
engine.info_handlers.append(info_handler)

pgn = open("Sample Data/Game 7.pgn")
game = chess.pgn.read_game(pgn)
pgn.close()

node = game
prev_score = chess.uci.Score(None, None, False, False)

puzzles = []

def compare_scores(a, b):
    # determine if the difference between position A and B 
    # is worth investigating for a puzzle.
    if a.cp is not None and b.cp is not None:
        if abs(a.cp) < 200 and abs(b.cp) > 200 and a.cp + b.cp > 200:
            return True
    elif a.cp is not None and b.mate is not None:
        if abs(a.cp) < 200:
            return True
    else:
        return False

print("Game Length: " + str(game.end().board().fullmove_number))
print("Analysing Game...")

while not node.is_end():
    next_node = node.variation(0)
    engine.position(next_node.board())

    engine.go(nodes=1500000)
    cur_score = info_handler.info["score"][1]
    print(node.board().san(next_node.move))
    print("   CP " + str(cur_score.cp))
    print("   Mate: " + str(cur_score.mate))
    if compare_scores(prev_score, cur_score):
        print("   Investigate")
        puzzles.append(puzzle(node.board(), next_node.move))

    prev_score = cur_score
    node = next_node

successful_puzzles = []
for i in puzzles:
    i.generate()
    if i.is_complete():
        successful_puzzles.append(i)
        print(i.to_json())