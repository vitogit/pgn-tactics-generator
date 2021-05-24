import logging

from modules.bcolors.bcolors import bcolors
from modules.exporters.pgn_exporter import PgnExporter


def post_puzzle(puzzle, include_blunder=True):
    logging.debug(bcolors.WARNING + "NEW PUZZLE GENERATED" + bcolors.ENDC)

    result = PgnExporter.export(puzzle, include_blunder)
    logging.info(bcolors.OKBLUE + result + bcolors.ENDC)

    return result
