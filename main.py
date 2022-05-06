#!/usr/bin/env python

"""Creating chess puzzles for lichess.org"""

import argparse
import logging
import io
import sys

import chess.engine
import chess.pgn

from modules.api.api import post_puzzle
from modules.bcolors.bcolors import bcolors
from modules.investigate.investigate import investigate
from modules.investigate.investigate import filter_game
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

    parser.add_argument("--color", metavar="DESIRED_COLOR", type=str, default="EITHER",
                        help="desired color in puzzle- BLACK, WHITE, or EITHER(default)")

    parser.add_argument("--forcedMate", metavar="MATES_ONLY", type=bool, default=False,
                        help="only return forced checkmates")

    parser.add_argument("--minTurn", metavar="MIN_TURN", type=int, default=0,
                        help="only return tactics starting after inputted turn")

    parser.add_argument("--maxTurn", metavar="MAX_TURN", type=int, default=999,
                        help="only return tactics starting before inputted turn")

    parser.add_argument("--opening", metavar="ROOT_PGN", type=str, default="NONE",
                        help="to get tactics from a specific opening, input opening moves as pgn")

    return parser.parse_args()


settings = prepare_settings()

prepare_terminal()

configure_logging(settings.loglevel)

stockfish_command = get_stockfish_command(settings.stockfish)
logging.debug(f'Using {stockfish_command} to run Stockfish.')
engine = chess.engine.SimpleEngine.popen_uci(stockfish_command)
engine.configure({'Threads': settings.threads, 'Hash': settings.memory})

all_games = open(settings.games, "r")
tactics_file = open("tactics.pgn", "w")
game_id = 0

opening_str = settings.opening
checkmate_only = settings.forcedMate
min_turn = settings.minTurn
max_turn = settings.maxTurn
color_str = settings.color.upper()
preferred_color = 0 if (color_str == "BLACK" or color_str == 'B') else 1 if (
            color_str == "WHITE" or color_str == "W") else 2
opening_pgn = io.StringIO(settings.opening)
opening = chess.pgn.read_game(opening_pgn)

if len(opening.errors) > 0:
    logging.debug(bcolors.FAIL + "Error with opening: " + opening_str)
    tactics_file.close()
    engine.quit()
    sys.exit("INVALID/ILLEGAL OPENING")

puzzle_count = 0

while True:
    game = chess.pgn.read_game(all_games)
    if game is None:
        break
    if opening != "NONE":
        while not filter_game(opening, game):
            game = chess.pgn.read_game(all_games)
        if game is None:
            break

    node = game

    game_id = game_id + 1
    logging.debug(bcolors.WARNING + "Game ID: " + str(game_id) + bcolors.ENDC)
    logging.debug(bcolors.WARNING + "Game headers: " + str(game) + bcolors.ENDC)

    prev_score = chess.engine.Cp(0)
    puzzles = []

    logging.debug(bcolors.OKGREEN + "Game Length: " + str(game.end().board().fullmove_number))
    logging.debug("Analysing Game..." + bcolors.ENDC)

    # store last ply where black and white created a puzzle to avoid repeats
    last_black = -1
    last_white = -1

    while not node.is_end():
        next_node = node.variation(0)

        info = engine.analyse(next_node.board(), chess.engine.Limit(depth=settings.depth))

        cur_score = info["score"].relative
        logging.debug(bcolors.OKGREEN + node.board().san(next_node.move) + bcolors.ENDC)
        logging.debug(bcolors.OKBLUE + "   CP: " + str(cur_score.score()))
        logging.debug("   Mate: " + str(cur_score.mate()) + bcolors.ENDC)

        if min_turn * 2 - 1 <= node.ply() <= max_turn * 2 and (preferred_color == 2 or node.turn() == preferred_color):
            if investigate(prev_score, cur_score, node.board(), checkmate_only):
                last_colored_puzzle = last_white if node.ply()%2==1 else last_black
                if node.ply() > last_colored_puzzle + 2:
                    logging.debug(bcolors.WARNING + "   Investigate!" + bcolors.ENDC)
                    puzzles.append(puzzle(node.board(), next_node.move, str(game_id), engine, info, game, settings.strict))

        prev_score = cur_score
        node = next_node

    for i in puzzles:
        logging.debug(bcolors.WARNING + "Generating new puzzle..." + bcolors.ENDC)
        i.generate(settings.depth)
        if i.is_complete():
            puzzle_pgn = post_puzzle(i, settings.include_blunder)
            tactics_file.write(puzzle_pgn)
            tactics_file.write("\n\n")
            puzzle_count+=1

logging.debug(bcolors.OKGREEN + "Puzzles generated:  " + str(puzzle_count))

tactics_file.close()

engine.quit()
