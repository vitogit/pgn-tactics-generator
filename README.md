# Python-Puzzle-Creator

## About

This is a python library dedicated to creating chess puzzles for lichess.org. However it can easily be adapted to create puzzles from personal games.

## Installation

This script requires the *Requests* and *Python-Chess* libraries to run, as well as a copy of *Stockfish*

### Install Requests

`pip install requests`

### Install Python Chess

`pip install python-chess`

### Setup

Change line `17` of `main.py` and line `6` of `modules/puzzle/puzzle.py` to point to your local stockfish application.

## Launching application

`python main.py <Secret API Token>`