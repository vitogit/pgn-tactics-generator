import requests
import chess
import re
import time
from modules.bcolors.bcolors import bcolors

def get_pgn(token):
    print(bcolors.WARNING + "Getting new game..." + bcolors.ENDC)
    success = False
    while not success:
        try:
            response = requests.get('https://en.lichess.org/training/api/game.pgn?token=' + token)
            success = True
        except ConnectionError:
            print(bcolors.WARNING + "CONNECTION ERROR: Failed to get new game.")
            print("Trying again in 30 sec" + bcolors.ENDC)
            time.sleep(30)
        except SSLError:
            print(bcolors.WARNING + "SSL ERROR: Failed to get new game.")
            print("Trying again in 30 sec" + bcolors.ENDC)
            time.sleep(30)


    try:
        from StringIO import StringIO
    except ImportError:
        from io import StringIO

    return StringIO(response.content)

def post_puzzle(token, puzzle, name):
    print(bcolors.OKBLUE + str(i.to_dict()) + bcolors.ENDC)
    success = False
    while not success:
        try:
            r = requests.post("https://en.lichess.org/training/api/puzzle?token=" + token, json=i.to_dict())
            success = True
        except ConnectionError:
            print(bcolors.WARNING + "CONNECTION ERROR: Failed to post puzzle.")
            print("Trying again in 30 sec" + bcolors.ENDC)
            time.sleep(30)
        except SSLError:
            print(bcolors.WARNING + "SSL ERROR: Failed to post puzzle.")
            print("Trying again in 30 sec" + bcolors.ENDC)
            time.sleep(30)

    
    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', r.content)
    if len(urls) > 0:
        print(bcolors.WARNING + "Imported with ID " + puzzle_id + bcolors.ENDC)
        if slack_key is not None:
            message = {"channel": "#puzzles",
                "username": "Puzzle Generator",
                "text": name + " added puzzle " + urls[0],
                "icon_emoji": ":star:"}
            requests.post("https://hooks.slack.com/services/" + slack_key, json=message)
    else:
        print(bcolors.FAIL + "Failed to import with response: " + r.content + bcolors.ENDC)