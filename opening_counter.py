#!/usr/bin/env python

"""Creating chess puzzles for lichess.org"""
import argparse
import collections
import logging

import chess.pgn

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--games", metavar="GAMES", default="games.pgn",
                    help="A specific pgn with games")
settings = parser.parse_args()

all_games = open(settings.games, "r")
ecos_white = []
ecos_black = []
game_id = 0
while True:
    game = chess.pgn.read_game(all_games)
    if game is None:
        break
    if game.headers["White"] == "engendrio":
        ecos_white.append(game.headers["ECO"] + '-' + game.headers["Opening"])
    else:
        ecos_black.append(game.headers["ECO"] + '-' + game.headers["Opening"])

print("WHITE_____")
print(collections.Counter(ecos_white))

print()
print("BLACK_____")
print(collections.Counter(ecos_black))
