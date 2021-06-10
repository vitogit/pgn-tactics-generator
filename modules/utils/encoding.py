from typing import Optional

from chess import Move, Board
from chess.engine import BestMove, Score

from modules.puzzle import position_list, puzzle


def move_to_dict(m: Move) -> Optional[str]:
    return m.uci() if m else None


def bestmove_to_dict(bm: BestMove) -> dict:
    return {
        'move': move_to_dict(bm.move),
        'ponder': move_to_dict(bm.ponder)
    } if bm else None


def board_to_dict(b: Board, position_only: bool = False) -> Optional[dict]:
    if not b:
        return None
    else:
        result = {
            'fen': b.fen()
        }
        if not position_only:
            result.update({
                'aliases': b.aliases,
                'fullmove_number': b.fullmove_number,
                'move_stack': [m.uci() for m in b.move_stack],
                'uci_variant': b.uci_variant,
                'piece_map': piecemap_to_dict(b.piece_map())
            })
        return result


def piecemap_to_dict(pm) -> dict:
    return {key: val.symbol() for key, val in pm.items()}


def score_to_dict(score: Score):
    return [score.score(), score.mate()] if score else None


def positionlist_to_dict(pl: position_list) -> dict:
    return {
        'position': board_to_dict(pl.position),
        'player_turn': pl.player_turn,
        'best_move': bestmove_to_dict(pl.best_move),
        'evaluation': score_to_dict(pl.evaluation),
        'next_position': positionlist_to_dict(pl.next_position) if pl.next_position else None,
        'analysed_legals': [analyzed_to_dict(al) for al in pl.analysed_legals],
        'strict': pl.strict,
        'is_ambiguous': pl.ambiguous()
    } if pl else None


def analyzed_to_dict(a):
    return {
        'move': move_to_dict(a.move),
        'evaluation': score_to_dict(a.evaluation)
    }


def puzzle_to_dict(p: puzzle):
    return {
        'game_id': p.game_id,
        'category': p.positions.category(),
        'last_pos': board_to_dict(p.last_pos),
        'last_move': move_to_dict(p.last_move),
        'move_list': p.positions.move_list(),
        'positions': positionlist_to_dict(p.positions)
        # , 'game': p.game
    } if p else None
