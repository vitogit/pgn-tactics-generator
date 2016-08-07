#!/usr/bin/env python

"""Creating chess puzzles for lichess.org"""

import argparse
import chess
import chess.uci
import chess.pgn
import logging
import os
import sys
from modules.fishnet.fishnet import stockfish_command
from modules.puzzle.puzzle import puzzle
from modules.bcolors.bcolors import bcolors
from modules.investigate.investigate import investigate
from modules.api.api import get_pgn, post_puzzle

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("token", metavar="TOKEN",
                    help="secret token for the lichess api")
parser.add_argument("name", metavar="NAME",
                    help="pick a name for the generator instance")
parser.add_argument("threads", metavar="THREADS", nargs="?", type=int, default=4,
                    help="number of engine threads")
parser.add_argument("memory", metavar="MEMORY", nargs="?", type=int, default=2048,
                    help="memory in MB to use for engine hashtables")
parser.add_argument("--quiet", dest="loglevel",
                    default=logging.DEBUG, action="store_const", const=logging.INFO,
                    help="substantially reduce the number of logged messages")
settings = parser.parse_args()

try:
    # Optionally fix colors on Windows and in journals if the colorama module
    # is available.
    import colorama
    wrapper = colorama.AnsiToWin32(sys.stdout)
    if wrapper.should_wrap():
        sys.stdout = wrapper.stream
except ImportError:
    pass

logging.basicConfig(format="%(message)s", level=settings.loglevel, stream=sys.stdout)
logging.getLogger("requests.packages.urllib3").setLevel(logging.WARNING)
logging.getLogger("chess.uci").setLevel(logging.WARNING)

slack_key = None
if os.path.isfile('slack_key.txt'):
    f = open('slack_key.txt', 'r')
    slack_key = f.read()

engine = chess.uci.popen_engine(stockfish_command())
engine.setoption({'Threads': settings.threads, 'Hash': settings.memory})
engine.uci()
info_handler = chess.uci.InfoHandler()
engine.info_handlers.append(info_handler)

while True:
    pgn = get_pgn(settings.token)
    game = chess.pgn.read_game(pgn)
    pgn.close()

    node = game

    game_id = game.headers["Site"].split('/')[-1:][0]
    logging.debug(bcolors.WARNING + "Game ID: " + game_id + bcolors.ENDC)

    prev_score = chess.uci.Score(None, None, False, False)
    puzzles = []

    logging.debug(bcolors.OKGREEN + "Game Length: " + str(game.end().board().fullmove_number))
    logging.debug("Analysing Game..." + bcolors.ENDC)

    engine.ucinewgame()

    while not node.is_end():
        next_node = node.variation(0)
        engine.position(next_node.board())

        engine.go(nodes=3500000)
        cur_score = info_handler.info["score"][1]
        logging.debug(bcolors.OKGREEN + node.board().san(next_node.move) + bcolors.ENDC)
        logging.debug(bcolors.OKBLUE + "   CP: " + str(cur_score.cp))
        logging.debug("   Mate: " + str(cur_score.mate) + bcolors.ENDC)
        if investigate(prev_score, cur_score, node.board()):
            logging.debug(bcolors.WARNING + "   Investigate!" + bcolors.ENDC)
            puzzles.append(puzzle(node.board(), next_node.move, game_id, engine, info_handler))

        prev_score = cur_score
        node = next_node

    for i in puzzles:
        logging.debug(bcolors.WARNING + "Generating new puzzle..." + bcolors.ENDC)
        i.generate()
        if i.is_complete():
            post_puzzle(settings.token, i, slack_key, settings.name)
