from tests.base_unittest import BaseUnitTest

import pypokerengine.utils.action_utils as U
from pypokerengine.engine.player import Player
from pypokerengine.engine.poker_constants import PokerConstants as Const

class ActionUtilsTest(BaseUnitTest):

    def test_generate_legal_actions(self):
        players = _setup_blind_players()
        legal_actions = U.generate_legal_actions(players, 0, "dummy_sb_amount")
        self.eq(
                [
                    { "action": "fold", "amount": 0 },
                    { "action": "call", "amount": 10 },
                    { "action": "raise", "amount": { "min": 15, "max": 100 } }
                ], legal_actions)

    def test_is_legal_action(self):
        players = _setup_blind_players()
        self.false(U.is_legal_action(players, 0, "dummy_sb_amount", "call", 9))
        self.true(U.is_legal_action(players, 0, "dummy_sb_amount", "call", 10))
        self.false(U.is_legal_action(players, 0, "dummy_sb_amount", "call", 11))


_SB_AMOUNT = 5

def _setup_blind_players():
    return [_create_blind_player(flg) for flg in [True, False]]

def _create_blind_player(small_blind=True):
    name = "sb" if small_blind else "bb"
    blind = _SB_AMOUNT if small_blind else _SB_AMOUNT*2
    player = Player("uuid", 100, name=name)
    player.add_action_history(Const.Action.RAISE, blind, 5)
    player.collect_bet(blind)
    player.pay_info.update_by_pay(blind)
    return player

