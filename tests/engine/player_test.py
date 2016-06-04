from tests.base_unittest import BaseUnitTest
from pypoker2.engine.card import Card
from pypoker2.engine.player import Player
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

