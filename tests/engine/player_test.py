from tests.base_unittest import BaseUnitTest
from pypoker2.engine.card import Card
from pypoker2.engine.player import Player
from pypoker2.engine.action import Action
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

  def test_add_fold_action_history(self):
    self.player.add_action_history(Action.FOLD)
    self.eq("FOLD", self.player.action_histories[-1]["action"])

  def test_add_call_action_history(self):
    self.player.add_action_history(Action.CALL, 10)
    action = self.player.action_histories[-1]
    self.eq("CALL", action["action"])
    self.eq(10, action["amount"])
    self.eq(10, action["paid"])

  def test_add_call_action_history_after_paid(self):
    self.player.add_action_history(Action.CALL, 10)

    self.player.add_action_history(Action.CALL, 20)
    action = self.player.action_histories[-1]
    self.eq(20, action["amount"])
    self.eq(10, action["paid"])

  def test_add_raise_action_history(self):
    self.player.add_action_history(Action.RAISE, 10, 5)
    action = self.player.action_histories[-1]
    self.eq("RAISE", action["action"])
    self.eq(10, action["amount"])
    self.eq(10, action["paid"])
    self.eq(5, action["add_amount"])

  def test_add_raise_action_history_after_paid(self):
    self.player.add_action_history(Action.CALL, 10)

    self.player.add_action_history(Action.RAISE, 20, 10)
    action = self.player.action_histories[-1]
    self.eq(20, action["amount"])
    self.eq(10, action["paid"])

