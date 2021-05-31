import json
import logging
import sys
import unittest

from modules.decoding import score_from_dict, board_from_dict
from modules.investigate.investigate import investigate

INVESTIGATE_FILE = '../data/investigate.json'
IS_COMPLETE_FILE = '../data/is_complete.json'


def configure_logger():
    logging.basicConfig(format="%(message)s", level="DEBUG", stream=sys.stdout)
    logging.getLogger("chess.uci").setLevel(logging.WARNING)
    logging.getLogger("chess._engine").setLevel(logging.WARNING)


configure_logger()


class TestRegression(unittest.TestCase):
    engine = None
    investigate_test_data = []
    complete_test_data = []

    @classmethod
    def setUpClass(cls):
        with open(INVESTIGATE_FILE, 'r') as f:
            content = f.read()
            TestRegression.investigate_test_data = json.loads(content)

        with open(IS_COMPLETE_FILE, 'r') as f:
            content = f.read()
            TestRegression.complete_test_data = json.loads(content)

    def test_investigate(self):
        """
        Go through known investigate arguments and results and see if the actual result is the same.
        :return:
        """
        for definition in TestRegression.investigate_test_data:
            score_a, score_b = score_from_dict(definition["score_a"]), score_from_dict(definition["score_b"])
            expected_result = definition["result"]
            board = board_from_dict(definition["board"])
            logging.debug(f"Testing position {board.fen()} with scores {score_a} and {score_b}")

            result = investigate(score_a, score_b, board)

            self.assertEqual(expected_result, result)
