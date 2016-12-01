from tests.base_unittest import BaseUnitTest
from pypokerengine.engine.card import Card
from pypokerengine.engine.player import Player
from pypokerengine.engine.poker_constants import PokerConstants as Const
from nose.tools import *

class PlayerTest(BaseUnitTest):

  def setUp(self):
    self.player = Player("uuid", 100)

  def test_add_holecard(self):
    cards = [Card.from_id(cid) for cid in range(1,3)]
    self.player.add_holecard(cards)
    self.true(cards[0] in self.player.hole_card)
    self.true(cards[1] in self.player.hole_card)

  @raises(ValueError)
  def test_add_single_hole_card(self):
    self.player.add_holecard([Card.from_id(1)])

  @raises(ValueError)
  def test_add_too_many_hole_card(self):
    self.player.add_holecard([Card.from_id(cid) for cid in range(1,4)])

  @raises(ValueError)
  def test_add_hole_card_twice(self):
    self.player.add_holecard([Card.from_id(cid) for cid in range(1,3)])
    self.player.add_holecard([Card.from_id(cid) for cid in range(1,3)])

  def test_clear_holecard(self):
    self.player.add_holecard([Card.from_id(cid) for cid in range(1,3)])
    self.player.clear_holecard()
    self.eq(0, len(self.player.hole_card))

  def test_append_chip(self):
    self.player.append_chip(10)
    self.eq(110, self.player.stack)

  def test_collect_bet(self):
    self.player.collect_bet(10)
    self.eq(90, self.player.stack)

  @raises(ValueError)
  def test_collect_too_much_bet(self):
    self.player.collect_bet(200)

  def test_is_active(self):
    self.player.pay_info.update_by_pay(10)
    self.true(self.player.is_active())

  def test_if_allin_player_is_active(self):
    self.player.pay_info.update_to_allin()
    self.true(self.player.is_active())

  def test_if_folded_player_is_not_active(self):
    self.player.pay_info.update_to_fold()
    self.false(self.player.is_active())

  def test_if_no_money_player_is_active(self):
    self.player.collect_bet(100)
    self.true(self.player.is_active())

  def test_is_waiting_ask(self):
    self.player.pay_info.update_by_pay(10)
    self.true(self.player.is_waiting_ask())

  def test_if_allin_player_is_not_waiting_ask(self):
    self.player.pay_info.update_to_allin()
    self.false(self.player.is_waiting_ask())

  def test_if_folded_player_is_not_waiting_ask(self):
    self.player.pay_info.update_to_fold()
    self.false(self.player.is_waiting_ask())

  def test_add_fold_action_history(self):
    self.player.add_action_history(Const.Action.FOLD)
    self.eq("FOLD", self.player.action_histories[-1]["action"])

  def test_add_call_action_history(self):
    self.player.add_action_history(Const.Action.CALL, 10)
    action = self.player.action_histories[-1]
    self.eq("CALL", action["action"])
    self.eq(10, action["amount"])
    self.eq(10, action["paid"])

  def test_add_call_action_history_after_paid(self):
    self.player.add_action_history(Const.Action.CALL, 10)

    self.player.add_action_history(Const.Action.CALL, 20)
    action = self.player.action_histories[-1]
    self.eq(20, action["amount"])
    self.eq(10, action["paid"])

  def test_add_raise_action_history(self):
    self.player.add_action_history(Const.Action.RAISE, 10, 5)
    action = self.player.action_histories[-1]
    self.eq("RAISE", action["action"])
    self.eq(10, action["amount"])
    self.eq(10, action["paid"])
    self.eq(5, action["add_amount"])

  def test_add_raise_action_history_after_paid(self):
    self.player.add_action_history(Const.Action.CALL, 10)

    self.player.add_action_history(Const.Action.RAISE, 20, 10)
    action = self.player.action_histories[-1]
    self.eq(20, action["amount"])
    self.eq(10, action["paid"])

  def test_add_small_blind_history(self):
    self.player.add_action_history(Const.Action.SMALL_BLIND, sb_amount=5)
    action = self.player.action_histories[-1]
    self.eq("SMALLBLIND", action["action"])
    self.eq(5, action["amount"])
    self.eq(5, action["add_amount"])

  def test_add_big_blind_history(self):
    self.player.add_action_history(Const.Action.BIG_BLIND, sb_amount=5)
    action = self.player.action_histories[-1]
    self.eq("BIGBLIND", action["action"])
    self.eq(10, action["amount"])
    self.eq(5, action["add_amount"])

  def test_add_ante_history(self):
    self.player.add_action_history(Const.Action.ANTE, 10)
    action = self.player.action_histories[-1]
    self.eq("ANTE", action["action"])
    self.eq(10, action["amount"])

  @raises(AssertionError)
  def test_add_empty_ante_history(self):
    self.player.add_action_history(Const.Action.ANTE, 0)

  def test_save_street_action_histories(self):
    self.assertIsNone(self.player.round_action_histories[Const.Street.PREFLOP])
    self.player.add_action_history(Const.Action.BIG_BLIND, sb_amount=5)
    self.player.save_street_action_histories(Const.Street.PREFLOP)
    self.eq(1, len(self.player.round_action_histories[Const.Street.PREFLOP]))
    self.eq("BIGBLIND", self.player.round_action_histories[Const.Street.PREFLOP][0]["action"])
    self.eq(0, len(self.player.action_histories))

  def test_clear_action_histories(self):
    self.player.add_action_history(Const.Action.BIG_BLIND, sb_amount=5)
    self.player.save_street_action_histories(Const.Street.PREFLOP)
    self.player.add_action_history(Const.Action.CALL, 10)
    self.assertIsNotNone(0, len(self.player.round_action_histories[Const.Street.PREFLOP]))
    self.neq(0, len(self.player.action_histories))
    self.player.clear_action_histories()
    self.assertIsNone(self.player.round_action_histories[Const.Street.PREFLOP])
    self.eq(0, len(self.player.action_histories))

  def test_paid_sum(self):
    self.eq(0, self.player.paid_sum())
    self.player.add_action_history(Const.Action.BIG_BLIND, sb_amount=5)
    self.eq(10, self.player.paid_sum())
    self.player.clear_action_histories()
    self.eq(0, self.player.paid_sum())
    self.player.add_action_history(Const.Action.ANTE, 3)
    self.eq(0, self.player.paid_sum())
    self.player.add_action_history(Const.Action.BIG_BLIND, sb_amount=5)
    self.eq(10, self.player.paid_sum())


  def test_serialization(self):
    player = self.__setup_player_for_serialization()
    serial = player.serialize()
    restored = Player.deserialize(serial)
    self.eq(player.name, restored.name)
    self.eq(player.uuid, restored.uuid)
    self.eq(player.stack, restored.stack)
    self.eq(player.hole_card, restored.hole_card)
    self.eq(player.action_histories, restored.action_histories)
    self.eq(player.round_action_histories, restored.round_action_histories)
    self.eq(player.pay_info.amount, restored.pay_info.amount)
    self.eq(player.pay_info.status, restored.pay_info.status)

  def __setup_player_for_serialization(self):
    player = Player("uuid", 50, "hoge")
    player.add_holecard([Card.from_id(cid) for cid in range(1,3)])
    player.add_action_history(Const.Action.SMALL_BLIND, sb_amount=5)
    player.save_street_action_histories(Const.Street.PREFLOP)
    player.add_action_history(Const.Action.CALL, 10)
    player.add_action_history(Const.Action.RAISE, 10, 5)
    player.add_action_history(Const.Action.FOLD)
    player.pay_info.update_by_pay(15)
    player.pay_info.update_to_fold()
    return player

