#!/usr/bin/env python

"""Downloading chess puzzles for lichess.org"""

import argparse
import logging
import sys

import requests

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--token", metavar="TOKEN", default="",
                    help="secret token for the lichess api")
parser.add_argument("username", metavar="USERNAME",
                    help="Username in lichess")
parser.add_argument("--quiet", dest="loglevel",
                    default=logging.DEBUG, action="store_const", const=logging.INFO,
                    help="substantially reduce the number of logged messages")
parser.add_argument("--max", metavar="MAX", default="60",
                    help="max number of games")
parser.add_argument("--perfType", metavar="PERFTYPE", default="blitz,rapid,classical",
                    help="Game type in lichess : blitz, rapid or classical. Comma separated eg. 'classical " or "rapid,classical")

settings = parser.parse_args()
logging.basicConfig(format="%(message)s", level=settings.loglevel, stream=sys.stdout)

logging.debug("Downloading games from: " + settings.username)

response = requests.get(
    'https://lichess.org/api/games/user/' + settings.username + '?max=' + settings.max + '&token=' + settings.token + '&perfType=blitz,rapid,classical&opening=true')
pgn = str(response.text)
all_games = open("games.pgn", "w")
all_games.write(pgn)
all_games.close()
logging.debug("Finished. Pgn is in games.pgn ")
