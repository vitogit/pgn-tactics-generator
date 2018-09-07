# pgn-tactics-generator

## About

This is a python application dedicated to creating chess puzzles/tactics from a pgn file.
Also it can download your games from lichess.org and use that file. 

It's based on the great  (https://github.com/clarkerubber/Python-Puzzle-Creator)[https://github.com/clarkerubber/Python-Puzzle-Creator] by @clarkerubber

Things that I changed:
- Use a local pgn file 
- Write results to a file called tactics.json
- Engine depth to 6 (from nodes=3500000), because it took a lot of time to analyze. (probably this could be a param)
- chess.pop_count to chess.popcount because it was failing

## Installation

This script requires the *Requests* and *Python-Chess* libraries to run, as well as a copy of *Stockfish*

### Install Requests

`pip install requests`

### Install Python Chess

`pip install python-chess`

### Setup

MacOS / Linux : `sh build-stockfish.sh` to obtain the current lichess Stockfish instance.

## Launching Application
First you can download your games from lichess with

`python download_games.py <lichess username>`

This will download the last 60 games. You can add some params like max number of games and the lichess api token that make downloading faster. https://lichess.org/api#operation/apiGamesUser

`python download_games.py <lichess username> --max 100 --token 123456789`


Then execute the generator (it will look for a file called lichess_games.pgn) the params are optional

`python main.py <#Threads = 4> <Hash (MBytes) = 2048>`

## Python 3

If you have problems with pip maybe it's because your system use a separate version like pip3.
Or maybe you should execute the scripts with python3 instead of python if you have that installed. 
Like:

`python3 download_games.py <lichess username> <Secret API Token>`

`python3 main.py <Secret API Token> <#Threads = 4> <Hash (MBytes) = 2048>`
