#!/usr/bin/env python

"""
This utility allows for generating some data that can be used in tests.
The data include:
  * arguments and result for investigate() function
  * puzzle definitions and result of .is_complete() and .positions.ambiguous() methods for that puzzles
"""
import argparse
import json
import logging

import chess.engine
import chess.pgn

from modules.bcolors.bcolors import bcolors
from modules.utils.encoding import puzzle_to_dict, board_to_dict, score_to_dict
from modules.investigate.investigate import investigate
from modules.puzzle.puzzle import puzzle
from modules.utils.helpers import str2bool, get_stockfish_command, configure_logging, prepare_terminal


def prepare_settings():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument("--threads", metavar="THREADS", nargs="?", type=int, default=4,
                        help="number of engine threads")
    parser.add_argument("--memory", metavar="MEMORY", nargs="?", type=int, default=2048,
                        help="memory in MB to use for engine hashtables")
    parser.add_argument("--depth", metavar="DEPTH", nargs="?", type=int, default=8,
                        help="depth for stockfish analysis")
    parser.add_argument("--quiet", dest="loglevel",
                        default=logging.DEBUG, action="store_const", const=logging.INFO,
                        help="substantially reduce the number of logged messages")
    parser.add_argument("--games", metavar="GAMES", default="games.pgn",
                        help="A specific pgn with games")
    parser.add_argument("--strict", metavar="STRICT", default=True,
                        help="If False then it will be generate more tactics but maybe a little ambiguous")
    parser.add_argument("--includeBlunder", metavar="INCLUDE_BLUNDER", default=True,
                        type=str2bool, const=True, dest="include_blunder", nargs="?",
                        help="If False then generated puzzles won't include initial blunder move")
    parser.add_argument("--stockfish", metavar="STOCKFISH", default=None, help="Path to Stockfish binary")

    return parser.parse_args()


settings = prepare_settings()

prepare_terminal()

configure_logging(settings.loglevel)

stockfish_command = get_stockfish_command(settings.stockfish)
logging.debug(f'Using {stockfish_command} to run Stockfish.')
engine = chess.engine.SimpleEngine.popen_uci(stockfish_command)
engine.configure({'Threads': settings.threads, 'Hash': settings.memory})

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

    prev_score = chess.engine.Cp(0)
    puzzles = []

    logging.debug("Analysing Game..." + bcolors.ENDC)

    # find candidates (positions)
    while not node.is_end():
        next_node = node.variation(0)
        info = engine.analyse(next_node.board(), chess.engine.Limit(depth=settings.depth))

        cur_score = info["score"].relative
        logging.debug(bcolors.OKGREEN + node.board().san(next_node.move) + bcolors.ENDC)
        logging.debug(bcolors.OKBLUE + "   CP: " + str(cur_score.score()))
        logging.debug("   Mate: " + str(cur_score.mate()) + bcolors.ENDC)

        result = investigate(prev_score, cur_score, node.board())

        if result:
            logging.debug(bcolors.WARNING + "   Investigate!" + bcolors.ENDC)
            puzzles.append(
                puzzle(node.board(), next_node.move, str(game_id), engine, None, game, settings.strict))

            # save the data for investigate() testing
            investigate_test_data.append(
                {'score_a': score_to_dict(prev_score), 'score_b': score_to_dict(cur_score),
                 'board': board_to_dict(node.board(), True), 'result': result})

        prev_score = cur_score
        node = next_node

    # check puzzle completeness
    for i in puzzles:
        logging.info(bcolors.WARNING + "Generating new puzzle..." + bcolors.ENDC)
        i.generate(settings.depth)

        is_complete = i.is_complete()
        is_ambiguous = i.positions.ambiguous()
        logging.info(f'{i.last_pos.fen()} -- {is_complete}, {is_ambiguous}')
        if is_complete:
            complete_test_data.append({'puzzle': puzzle_to_dict(i), 'is_complete': is_complete})

# dump the test data to files
write_test_data('investigate.json', json.dumps(investigate_test_data, indent=2))
write_test_data('is_complete.json', json.dumps(complete_test_data, indent=2))

engine.quit()
