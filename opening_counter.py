#!/usr/bin/env python

"""Creating chess puzzles for lichess.org"""
import collections
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
from modules.api.api import post_puzzle

parser = argparse.ArgumentParser(description=__doc__)

parser.add_argument("threads", metavar="THREADS", nargs="?", type=int, default=4,
                    help="number of engine threads")
parser.add_argument("memory", metavar="MEMORY", nargs="?", type=int, default=2048,
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
settings = parser.parse_args()

all_games = open(settings.games, "r")
ecos_white = []
ecos_black = []
game_id = 0
while True:
    game = chess.pgn.read_game(all_games)
    if game == None:
        break
    if (game.headers["White"] == "engendrio"):
        ecos_white.append(game.headers["ECO"]+'-'+game.headers["Opening"])
    else:
        ecos_black.append(game.headers["ECO"]+'-'+game.headers["Opening"])

print("WHITE_____")
print(collections.Counter(ecos_white))

print()
print("BLACK_____")
print(collections.Counter(ecos_black))
