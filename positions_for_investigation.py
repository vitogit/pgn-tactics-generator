#!/usr/bin/env python

import argparse
import json
import logging
import sys

import chess.pgn
import chess.uci

from modules.bcolors.bcolors import bcolors
from modules.encoding import puzzle_to_dict, board_to_dict
from modules.fishnet.fishnet import stockfish_command
from modules.investigate.investigate import investigate
from modules.puzzle.puzzle import puzzle

# from position_list_to import PositionList

parser = argparse.ArgumentParser(description=__doc__)

parser.add_argument("--threads", metavar="THREADS", nargs="?", type=int, default=4, help="number of engine threads")
parser.add_argument("--memory", metavar="MEMORY", nargs="?", type=int, default=2048,
                    help="memory in MB to use for engine hashtables")
parser.add_argument("--depth", metavar="DEPTH", nargs="?", type=int, default=8, help="depth for stockfish analysis")
parser.add_argument("--quiet", dest="loglevel", default=logging.DEBUG, action="store_const", const=logging.INFO,
                    help="substantially reduce the number of logged messages")
parser.add_argument("--games", metavar="GAMES", default="games.pgn", help="A specific pgn with games")
parser.add_argument("--strict", metavar="STRICT", default=True,
                    help="If False then it will be generate more tactics but maybe a little ambiguous")
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
logging.getLogger("chess._engine").setLevel(logging.WARNING)

engine = chess.uci.popen_engine(stockfish_command())
engine.setoption({'Threads': settings.threads, 'Hash': settings.memory})
engine.uci()
info_handler = chess.uci.InfoHandler()
engine.info_handlers.append(info_handler)

all_games = open(settings.games, "r")


def write_test_data(filename: str, payload: str):
    with open(filename, "w") as f:
        f.write(payload)


# data collection for testing investigate function
investigate_test_data = []
complete_test_data = []

game_id = 0
while True:
    game = chess.pgn.read_game(all_games)
    if game is None:
        break
    node = game

    game_id = game_id + 1
    logging.debug(bcolors.WARNING + "Game ID: " + str(game_id) + bcolors.ENDC)
    logging.debug(bcolors.WARNING + "Game headers: " + str(game) + bcolors.ENDC)

    prev_score = chess.uci.Score(None, None)
    puzzles = []

    logging.debug("Analysing Game..." + bcolors.ENDC)

    engine.ucinewgame()

    # find candidates (positions)
    while not node.is_end():
        next_node = node.variation(0)
        engine.position(next_node.board())

        engine.go(depth=settings.depth)
        cur_score = info_handler.info["score"][1]
        logging.debug(bcolors.OKGREEN + node.board().san(next_node.move) + bcolors.ENDC)
        logging.debug(bcolors.OKBLUE + "   CP: " + str(cur_score.cp))
        logging.debug("   Mate: " + str(cur_score.mate) + bcolors.ENDC)

        result = investigate(prev_score, cur_score, node.board())

        if result:
            logging.debug(bcolors.WARNING + "   Investigate!" + bcolors.ENDC)
            puzzles.append(
                puzzle(node.board(), next_node.move, str(game_id), engine, info_handler, game, settings.strict))

            # save the data for investigate() testing
            investigate_test_data.append(
                {'score_a': prev_score, 'score_b': cur_score, 'board': board_to_dict(node.board(), True), 'result': result})

        prev_score = cur_score
        node = next_node

    # check puzzle completeness
    for i in puzzles:
        logging.info(bcolors.WARNING + "Generating new puzzle..." + bcolors.ENDC)
        i.generate(settings.depth)

        is_complete = i.is_complete()
        logging.info(f'{i.last_pos.fen()} -- {is_complete}')
        if is_complete:
            complete_test_data.append({'puzzle': puzzle_to_dict(i), 'is_complete': is_complete})

# dump the test data to files
write_test_data('investigate.json', json.dumps(investigate_test_data, indent=2))
write_test_data('is_complete.json', json.dumps(complete_test_data, indent=2))
