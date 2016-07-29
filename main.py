import chess
import chess.uci
import chess.pgn
from modules.puzzle.fishnet import stockfish_filename
import os
import requests
import sys
from modules.puzzle.puzzle import puzzle, bcolors

token = ''
if len(sys.argv) > 1:
	token = sys.argv[1]

engine = chess.uci.popen_engine(os.path.join(".",stockfish_filename()))
engine.uci()
info_handler = chess.uci.InfoHandler()
engine.info_handlers.append(info_handler)

response = requests.get('https://en.stage.lichess.org/training/api/game.pgn?token=' + token)

try:
	from StringIO import StringIO
except ImportError:
	from io import StringIO

print(response.content)

pgn = StringIO(response.content)
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

print(bcolors.OKGREEN + "Game Length: " + str(game.end().board().fullmove_number))
print("Analysing Game..." + bcolors.ENDC)

game_id = game.headers["Site"].split('/')[-1:][0]

while not node.is_end():
    next_node = node.variation(0)
    engine.position(next_node.board())

    engine.go(nodes=1500000)
    cur_score = info_handler.info["score"][1]
    print(bcolors.OKGREEN + node.board().san(next_node.move) + bcolors.ENDC)
    print(bcolors.OKBLUE + "   CP: " + str(cur_score.cp))
    print("   Mate: " + str(cur_score.mate) + bcolors.ENDC)
    if compare_scores(prev_score, cur_score):
        print(bcolors.WARNING + "   Investigate!" + bcolors.ENDC)
        puzzles.append(puzzle(node.board(), next_node.move, game_id))

    prev_score = cur_score
    node = next_node

successful_puzzles = []
for i in puzzles:
    i.generate()
    if i.is_complete():
        successful_puzzles.append(i)
        print(bcolors.OKBLUE + str(i.to_dict()) + bcolors.ENDC)
        r = requests.post("https://en.stage.lichess.org/training/api/puzzle?token=" + token, json=i.to_dict())
        print(bcolors.WARNING + "Imported with ID " + r.content + bcolors.ENDC)
