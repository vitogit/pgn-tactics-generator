import logging

from modules.bcolors.bcolors import bcolors


def post_puzzle(puzzle):
    logging.debug(bcolors.WARNING + "NEW PUZZLE GENERATED" + bcolors.ENDC)
    logging.info(bcolors.OKBLUE + str(puzzle.to_pgn()) + bcolors.ENDC)
    return str(puzzle.to_pgn())
