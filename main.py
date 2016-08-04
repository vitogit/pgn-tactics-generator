import chess
import chess.uci
import chess.pgn
import os
import requests
import sys
import re
from modules.fishnet.fishnet import stockfish_filename
from modules.puzzle.puzzle import puzzle
from modules.bcolors.bcolors import bcolors
from modules.investigate.investigate import investigate
from modules.api.api import get_pgn, post_puzzle

token = ''
name = ''
threads = 4

if len(sys.argv) > 3:
    threads = int(sys.argv[3])
if len(sys.argv) > 2:
    name = sys.argv[2]
if len(sys.argv) > 1:
    token = sys.argv[1]

slack_key = None
if os.path.isfile('slack_key.txt'):
    f = open('slack_key.txt', 'r')
    slack_key = f.read()

engine = chess.uci.popen_engine(os.path.join(os.getcwd(),stockfish_filename()))
engine.setoption({'Threads': threads, 'Hash': 2048})
engine.uci()
info_handler = chess.uci.InfoHandler()
engine.info_handlers.append(info_handler)

while True:
    pgn = get_pgn(token)
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
        if investigate(prev_score, cur_score, node.board()):
            print(bcolors.WARNING + "   Investigate!" + bcolors.ENDC)
            puzzles.append(puzzle(node.board(), next_node.move, game_id, engine, info_handler))

        prev_score = cur_score
        node = next_node

    for i in puzzles:
        print(bcolors.WARNING + "Generating new puzzle..." + bcolors.ENDC)
        i.generate()
        if i.is_complete():
            post_puzzle(token, i, name)
