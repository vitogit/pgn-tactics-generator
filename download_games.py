#!/usr/bin/env python

"""Downloading chess puzzles for Lichess.org"""

import argparse
import logging
import sys
import urllib

import requests
import lichess

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
parser.add_argument("--site", metavar="SITE", default="lichess", help="Website to query user game data")

settings = parser.parse_args()

logging.basicConfig(format="%(message)s", level=settings.loglevel, stream=sys.stdout)
logging.debug("Downloading games from: " + settings.username)


if settings.site == "lichess":
    with open("games.pgn", "w") as new_file:
        myclient = lichess.Client()
        new_file.write(myclient.export_by_user(settings.username, max_games=settings.max))
    new_file.close()
    logging.debug("Finished. Pgn is in games.pgn ")
elif settings.site == "chessdotcom":
    url_chessdotcom = "https://api.chess.com/pub/player/" + \
                      settings.username.lower() + "/games"
    url_archive = url_chessdotcom + "/archives"
    http_response = urllib.request.urlopen(url_archive)

    archives = http_response.read().decode("utf-8")
    archives = archives.replace("{\"archives\":[\"", "\",\"")
    archive_dates = archives.split("\",\"" + url_chessdotcom)
    archive_dates[len(archive_dates) - 1] = archive_dates[
        len(archive_dates) - 1].rstrip("\"]}")

    with open("games.pgn", "w") as new_file:
        for i in range(len(archive_dates) - 1):
            cur_url = url_chessdotcom + archive_dates[i + 1] + "/pgn"
            cur_filename = archive_dates[i + 1].replace("/", "-")
            response = requests.get(cur_url, "./" + cur_filename + ".pgn")
            new_file.write(response.text)
    new_file.close()
    logging.debug("Finished. Pgn is in games.pgn ")
else:
    logging.debug("Invalid argument for site: only arguments allowed are lichess and chessdotcom")


