# pgn-tactics-generator

## About

This is a python application dedicated to creating chess puzzles/tactics from a pgn file.
Also it can download your games from lichess.org and use that file.

It's based on the great  [https://github.com/clarkerubber/Python-Puzzle-Creator](https://github.com/clarkerubber/Python-Puzzle-Creator) by @clarkerubber

Things that I changed:
- Use a local pgn file with games as a source.
- Write results to a file called tactics.pgn
- Default engine depth to 8 so it's faster. Before it was nodes=3500000 this is a depth around 20. So it took several minutes to analyze a game. With depth 8 it takes seconds.
- You can use the `depth` argument to change the depth if you want more precision.
- chess.pop_count to chess.popcount because it was failing

### This is too complex, give something easy.
There is another option if you don't want to install and manage python scripts
I created a more user friendly tactics generator and it's online http://chesstacticsgenerator.vitomd.com
It uses a different approach to create tactics, so probably it will generate a different set of tactics.

## Installation

This script requires the *Requests* and *Python-Chess* libraries to run, as well as a copy of *Stockfish*
Is recommended that you use Python 3 and pip3. But it could work with Python 2.7 and pip (probably you will need to install futures `pip install futures` )

### Install requirements

`pip3 install -r requirements.txt --user`

### Setup

MacOS / Linux : `sh build-stockfish.sh` to obtain the current lichess Stockfish instance.

## Launching Application

### Downloading games for a specific user
You can download games from a specific user using this command:
`python3 download_games.py <lichess username>`


By default it will download the last 60 games from blitz, rapid and classical.

**Arguments**

You can use the `max` argument to get more games and use the lichess api token with the `token` argument to make the download faster. https://lichess.org/api#operation/apiGamesUser

It will save the games in the `games.pgn` file


**Example to get 100 games using the token**

`python3 download_games.py <lichess username> --max 100 --token 123456789`

### Downloading games from tournaments
You can download games from multiple tournaments using this command:

`python3 download_tournaments.py E14kHVwX tdntXNhy`

**The arguments are the tournaments ids separate by a space**

It will save the games in the `games.pgn` file


### Generate tactics


To execute the generator execute this command. By default it will look for the `games.pgn` file:

`python3 main.py`


**Arguments**

- `--quiet` to reduce the screen output.
- `--depth=8` select the stockfish depth analysis. Default is `8` and will take some seconds to analyze a game, with `--depth=18` will take around 6 minutes.
- `--games=ruy_lopez.pgn` to select a specific pgn file. Default is `games.pgn`
- `strict=False` Use `False` to generate more tactics but a little more ambiguous. Default is `True`
- `--threads=4` Stockfish argument, number of engine threads, default `4`
- `--memory=2048` Stockfish argument, memory in MB to use for engine hashtables, default `2048`

Example:
`python3 main.py --quiet --depth=12 --games=ruy_lopez.pgn --strict=True --threads=2 --memory=1024`

## Tactics output

The resulting file will be a pgn file called `tactics.pgn`. Each tactic contains the headers from the source game.
The `result header` is the tactic result and not the game result. It can be loaded to a Lichess study or to an app like iChess to practice tactics.

## Problems?

#### Stockfish errors
- If you have problems building stockfish try downloading stockfish directly https://stockfishchess.org/download/

## Want to see all my chess related projects?
Check [My projects](http://vitomd.com/blog/projects/) for a full detailed list.
