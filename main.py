#!/usr/bin/env python

"""Creating chess puzzles for lichess.org"""

import argparse
import logging
import sys

import chess.pgn
import chess.uci

from modules.api.api import post_puzzle
from modules.bcolors.bcolors import bcolors
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
                        type=str2bool, const=True, nargs="?",
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
engine = chess.uci.popen_engine(stockfish_command)
engine.setoption({'Threads': settings.threads, 'Hash': settings.memory})
engine.uci()
info_handler = chess.uci.InfoHandler()
engine.info_handlers.append(info_handler)

all_games = open(settings.games, "r")
tactics_file = open("tactics.pgn", "w")
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

    logging.debug(bcolors.OKGREEN + "Game Length: " + str(game.end().board().fullmove_number))
    logging.debug("Analysing Game..." + bcolors.ENDC)

    engine.ucinewgame()

    while not node.is_end():
        next_node = node.variation(0)
        engine.position(next_node.board())

        engine.go(depth=settings.depth)
        cur_score = info_handler.info["score"][1]
        logging.debug(bcolors.OKGREEN + node.board().san(next_node.move) + bcolors.ENDC)
        logging.debug(bcolors.OKBLUE + "   CP: " + str(cur_score.cp))
        logging.debug("   Mate: " + str(cur_score.mate) + bcolors.ENDC)
        if investigate(prev_score, cur_score, node.board()):
            logging.debug(bcolors.WARNING + "   Investigate!" + bcolors.ENDC)
            puzzles.append(
                puzzle(node.board(), next_node.move, str(game_id), engine, info_handler, game, settings.strict))

        prev_score = cur_score
        node = next_node

    for i in puzzles:
        logging.debug(bcolors.WARNING + "Generating new puzzle..." + bcolors.ENDC)
        i.generate(settings.depth)
        if i.is_complete():
            puzzle_pgn = post_puzzle(i, settings.include_blunder)
            tactics_file.write(puzzle_pgn)
            tactics_file.write("\n\n")

tactics_file.close()
