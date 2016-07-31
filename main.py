import chess
import chess.uci
import chess.pgn
from modules.fishnet.fishnet import stockfish_filename
import os
import requests
import sys
from modules.puzzle.puzzle import puzzle
from modules.bcolors.bcolors import bcolors

token = ''
if len(sys.argv) > 1:
    token = sys.argv[1]

slack_key = None
if os.path.isfile('slack_key.txt'):
    f = open('slack_key.txt', 'r')
    slack_key = f.read()

engine = chess.uci.popen_engine(os.path.join(os.getcwd(),stockfish_filename()))
engine.setoption({'Threads': 4})
engine.uci()
info_handler = chess.uci.InfoHandler()
engine.info_handlers.append(info_handler)

def compare_scores(a, b):
    # determine if the difference between position A and B 
    # is worth investigating for a puzzle.
    if a.cp is not None and b.cp is not None:
        if abs(a.cp) < 110 and abs(b.cp) > 200 and abs(b.cp) < 850:
            return True
    elif a.cp is not None and b.mate is not None:
        if abs(a.cp) < 200:
            return True
    else:
        return False

while True:
    print(bcolors.WARNING + "Getting new game..." + bcolors.ENDC)
    response = requests.get('https://en.lichess.org/training/api/game.pgn?token=' + token)

    try:
        from StringIO import StringIO
    except ImportError:
        from io import StringIO

    pgn = StringIO(response.content)
    game = chess.pgn.read_game(pgn)
    pgn.close()

    node = game

    game_id = game.headers["Site"].split('/')[-1:][0]
    print(bcolors.WARNING + "Game ID: " + game_id + bcolors.ENDC)

    prev_score = chess.uci.Score(None, None, False, False)
    puzzles = []

    print(bcolors.OKGREEN + "Game Length: " + str(game.end().board().fullmove_number))
    print("Analysing Game..." + bcolors.ENDC)

    engine.ucinewgame()

    while not node.is_end():
        next_node = node.variation(0)
        engine.position(next_node.board())

        engine.go(nodes=3500000)
        cur_score = info_handler.info["score"][1]
        print(bcolors.OKGREEN + node.board().san(next_node.move) + bcolors.ENDC)
        print(bcolors.OKBLUE + "   CP: " + str(cur_score.cp))
        print("   Mate: " + str(cur_score.mate) + bcolors.ENDC)
        if compare_scores(prev_score, cur_score):
            print(bcolors.WARNING + "   Investigate!" + bcolors.ENDC)
            puzzles.append(puzzle(node.board(), next_node.move, game_id))

        prev_score = cur_score
        node = next_node

    for i in puzzles:
        print(bcolors.WARNING + "Generating new puzzle..." + bcolors.ENDC)
        i.generate()
        if i.is_complete():
            print(bcolors.OKBLUE + str(i.to_dict()) + bcolors.ENDC)
            r = requests.post("https://en.stage.lichess.org/training/api/puzzle?token=" + token, json=i.to_dict())
            urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', r.content)
            if len(urls) > 0:
                print(bcolors.WARNING + "Imported with ID " + urls[0] + bcolors.ENDC)
                if slack_key is not None:
                    message = {"channel": "#general",
                        "username": "webhookbot",
                        "text": "New puzzle added: " + urls[0],
                        "icon_emoji": ":star:"}
                    requests.post("https://hooks.slack.com/services/" + slack_key, json=message)
            else:
                print(bcolors.FAIL + "Failed to import with response: " + r.content + bcolors.ENDC)
