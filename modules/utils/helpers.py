import argparse
import logging
import sys

from modules.fishnet.fishnet import stockfish_command


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def get_stockfish_command(path: str):
    return path if path else stockfish_command()


def configure_logging(loglevel):
    logging.basicConfig(format="%(message)s", level=loglevel, stream=sys.stdout)
    logging.getLogger("requests.packages.urllib3").setLevel(logging.WARNING)
    logging.getLogger("chess.uci").setLevel(logging.WARNING)
    logging.getLogger("chess.engine").setLevel(logging.WARNING)
    logging.getLogger("chess._engine").setLevel(logging.WARNING)


def prepare_terminal():
    try:
        # Optionally fix colors on Windows and in journals if the colorama module
        # is available.
        import colorama

        wrapper = colorama.AnsiToWin32(sys.stdout)
        if wrapper.should_wrap():
            sys.stdout = wrapper.stream
    except ImportError:
        pass
