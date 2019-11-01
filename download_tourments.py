#!/usr/bin/env python

"""Downloading chess puzzles for lichess.org"""

import argparse
import chess
import chess.pgn
import logging
import os
import sys
import requests
import chess
import re
import time


# tourments
tourment_ids = ['25MtoToy',
'E14kHVwX',
'tdntXNhy',
'sj5GoEdS',
'C4zdQLax',
'wobqi6QP',
'T4RW1ux2',
'nzw7OKBq']

all_games = open("games.pgn", "w")
pgn = ""
for id in tourment_ids:
    print ('https://lichess.org/api/tournament/'+id+'/games')
    response = requests.get('https://lichess.org/api/tournament/'+id+'/games')
    pgn = pgn +'\n'+ str(response.text)

all_games.write(pgn)
all_games.close()
logging.debug("Finished. Pgn is in games.pgn ")
