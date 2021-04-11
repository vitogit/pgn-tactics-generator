#!/usr/bin/env python

"""Downloading chess puzzles for lichess.org"""

# import sys to handle command line arguments
import sys

import logging

import requests

# tournaments
tournament_ids = sys.argv[1:]

with open('games.pgn','w') as file:
    for id_number in tournament_ids:  # using id_number instead of id as a name cause id is a built-in python function
        url = f'https://lichess.org/api/tournament/{id_number}/games'
        print('\r' + f'Downloading tournament for {id_number}...',end = '')
        response = requests.get(url)
        if(response.status_code != 404):
            file.write(str(response.text) + '\n')
            print('\r' + f'Downloading complete for {id_number}......')
        else:
            print('\r' + f'Failed..! Tournament for {id_number} not found...')

logging.debug("Finished... Pgn is in games.pgn")