import json
import logging
import os
import unittest

from modules.utils.decoding import score_from_dict, board_from_dict, puzzle_from_dict
from modules.investigate.investigate import investigate
from modules.utils.helpers import configure_logging

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
INVESTIGATE_FILE = f'{TEST_DIR}/../data/investigate.json'
IS_COMPLETE_FILE = f'{TEST_DIR}/../data/is_complete.json'

configure_logging(logging.DEBUG)


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
            print(score_a)
            print(score_b)
            logging.debug(f"Testing position {board.fen()} with scores {score_a} and {score_b}")

            result = investigate(score_a, score_b, board)

            self.assertEqual(expected_result, result)

    def test_ambiguous(self):
        """
        Go through known ambiguous() arguments (position_list class)
        and results and see if the actual result is the same.
        :return:
        """
        for definition in TestRegression.complete_test_data:
            logging.debug(f"Testing puzzle {definition}")

            pd = definition['puzzle']
            expected_result = pd['positions']['is_ambiguous']
            puzzle = puzzle_from_dict(pd)
            result = puzzle.positions.ambiguous()

            logging.debug(f'{expected_result} vs {result}')
            self.assertEqual(expected_result, result)

    def test_positions_move_list(self):
        """
        Go through known move_list() results (position_list class)
        if the actual result is the same.
        :return:
        """
        for definition in TestRegression.complete_test_data:
            logging.debug(f"Testing puzzle {definition}")

            pd = definition['puzzle']
            puzzle = puzzle_from_dict(pd)
            result = puzzle.positions.move_list()

            expected_result = pd['move_list']

            logging.debug(f'{expected_result} vs {result}')
            self.assertEqual(expected_result, result)

    def test_is_complete(self):
        """
        :return:
        """
        for definition in TestRegression.complete_test_data:
            logging.debug(f"Testing puzzle {definition}")

            expected_result = definition['is_complete']

            pd = definition['puzzle']
            puzzle = puzzle_from_dict(pd)
            result = puzzle.is_complete()

            logging.debug(f'{expected_result} vs {result}')
            self.assertEqual(expected_result, result)


if __name__ == '__main__':
    unittest.main()
