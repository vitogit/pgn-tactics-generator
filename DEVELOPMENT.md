## About 
This document describes development-related topics of pgn-tactics-generator. 
pgn-tactics-generator is a python application dedicated to creating chess puzzles/tactics from a pgn file.
See [readme](./README.md) file for more details.


# Dependencies

This script requires the [Requests](https://docs.python-requests.org/) and [python-chess](https://python-chess.readthedocs.io/)
libraries to run, as well as a copy of *Stockfish*.
Is recommended that you use Python 3 and pip3. 
It should work with Python 2.7 and pip (probably you will need to install futures `pip install futures` )

To install the requirements use something, like:
`pip3 install -r requirements.txt --user`

It's recommended that the dependencies are isolated in a [virtual environment](https://docs.python.org/3/tutorial/venv.html)

# Testing
The project comes with a simple set of basic tests.

## Running the tests
The test can be run with:
```bash
python -m unittest
```

The recommended way to run the test is using `pytest`:
```bash
pytest
```

ATTOW, the tests cover:
  * investigate() function (running investigate with know arguments and expected result)
  * puzzle.is_complete
  * .ambiguous() and .move_list() methods of position_list class

The idea is that after introducing some changes to the app, you are able to check
if puzzle generation logic stayed untouched (produces the same results as the previous version).

## Test data
The tests are using [example data](./test/data) obtained with [positions_for_investigation.py](./positions_for_investigation.py).

The script works in similar fashion as `main.py`: It reads PGN file, goes through
the games, finds "interesting" positions and generates tactics puzzles.  
Some intermediate data (for example the puzzle definitions) are recorded and
writen to json files.

You don't need to re-run the script (as the project already includes required data), unless you want to
modify/extend the tests.