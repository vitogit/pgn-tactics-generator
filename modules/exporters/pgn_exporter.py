import chess
from chess import Move
from chess.pgn import Game

from modules.exporters import BaseExporter


class PgnExporter(BaseExporter):
    @staticmethod
    def determine_result_tag(board):
        # In the generated tactics puzzle, the first to move is the one who lost
        return '0-1' if board.turn else '1-0'

    @staticmethod
    def export(puzzle, include_first_move=True):
        fen = puzzle.last_pos.fen()
        board = chess.Board(fen)
        game = Game().from_board(board)

        result = PgnExporter.determine_result_tag(board)
        moves = puzzle.positions.move_list()

        if include_first_move:
            first_move = puzzle.last_move
        else:
            # simulate the move (blunder)
            board.push(puzzle.last_move)
            board.clear_stack()
            # take resulting board and create new game
            game = Game().from_board(board)

            first_move = Move.from_uci(moves.pop(0))

        # start the line
        node = game.add_main_variation(first_move)

        # add the rest of the moves
        for m in moves:
            node = node.add_variation(Move.from_uci(m))

        # copy headers from the original game and override result tag
        for h in puzzle.game.headers:
            game.headers[h] = puzzle.game.headers[h]
        game.headers['Result'] = result
        return str(game)
