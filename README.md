# pgn-tactics-generator

## About

This is a python application dedicated to creating chess puzzles/tactics from a pgn file.
Also it can download your games from lichess.org and use that file. 

It's based on the great  [https://github.com/clarkerubber/Python-Puzzle-Creator](https://github.com/clarkerubber/Python-Puzzle-Creator) by @clarkerubber

Things that I changed:
- Use a local pgn file with games as a source.
- Write results to a file called tactics.pgn
- Default engine depth to 8 so it's faster. Before it was nodes=3500000 this is a depth around 20. So it took several minutes to analyze a game. With depth 8 it takes seconds.
- You can use a param to change the depth if you want more precision.
- chess.pop_count to chess.popcount because it was failing

### This is too complex, give something easy.
There is another option if you don't want to install and manage python scripts
I created a more user friendly tactics generator and it's online http://chesstacticsgenerator.vitomd.com
It uses a different approach to create tactics, so probably it will generate a different set of tactics.


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

This will download the last 60 games from blitz,rapid and classical. You can add some params like max number of games and the lichess api token that make the download faster. https://lichess.org/api#operation/apiGamesUser

`python download_games.py <lichess username> --max 100 --token 123456789`


Then execute the generator (it will look for a file called games.pgn)
`python main.py --quiet`

You can also use parameters

- --quiet to reduce the screen output.
- --depth=8 param to select the stockfish depth analysis. Default is `8` and will take some seconds to analyze a game, with `--depth=18` will take around 6 minutes.
- --games=ruy_lopez.pgn to select a specific pgn file. Default is `games.pgn`
- strict=False . False to generate more tactics but a little more ambiguous. Default is `True`
- Threads and Hash defaults to 4 and 2048
`python main.py --quiet --depth=18 --games=ruy_lopez.pgn --strict=True <#Threads = 4> <Hash (MBytes) = 2048>`


## Tactics output

The resulting file will be a pgn file called tactics.pgn. Each tactic contains the headers from the source game. The result header it's the tactic result and not the game result. It can be loaded to a lichess study or to an app like ichess to practice tactics.

## Problems?

#### Python 2.7
- For Python 2.7 install futures `pip install futures`

#### Python 3
If you have problems with pip maybe it's because your system use a separate version like pip3.
Or maybe you should execute the scripts with python3 instead of python if you have that installed. 
Like:

`python3 download_games.py <lichess username> <Secret API Token>`

`python3 main.py <Secret API Token> <#Threads = 4> <Hash (MBytes) = 2048>`

#### Stockfish errors
- If you have problems building stockfish try downloading stockfish directly https://stockfishchess.org/download/


## Want to see all my chess related projects? 
Check [My projects](http://vitomd.com/blog/projects/) for a full detailed list.

