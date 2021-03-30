#!/usr/bin/env python

"""Downloading chess puzzles for lichess.org"""

import logging
import sys

import requests

# tourments
tourment_ids = sys.argv[1:]

all_games = open("games.pgn", "w")
pgn = ""
for id in tourment_ids:
    url = 'https://lichess.org/api/tournament/' + id + '/games'
    print(url)
    response = requests.get(url)
    if response.status_code == requests.codes.ok:
        pgn = pgn + '\n' + str(response.text)
    elif response.status_code==404:
        print(id + ' not found')

all_games.write(pgn)
all_games.close()
logging.debug("Finished. Pgn is in games.pgn ")
