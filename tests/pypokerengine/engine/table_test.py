from tests.base_unittest import BaseUnitTest
from nose.tools import *

from pypokerengine.engine.card import Card
from pypokerengine.engine.pay_info import PayInfo
from pypokerengine.engine.poker_constants import PokerConstants as Const
from pypokerengine.engine.player import Player
from pypokerengine.engine.table import Table
from pypokerengine.engine.seats import Seats
from pypokerengine.engine.deck import Deck

class TableTest(BaseUnitTest):

  def setUp(self):
    self.__setup_table()
    self.__setup_player()
    self.table.seats.sitdown(self.player)

  def test_set_blind(self):
    self.assertIsNone(self.table._blind_pos)
    self.table.set_blind_pos(1, 2)
    self.assertIsNotNone(self.table._blind_pos)
    self.eq(1, self.table.sb_pos())
    self.eq(2, self.table.bb_pos())

  def test_set_blind_error(self):
    with self.assertRaises(Exception) as e1: self.table.sb_pos()
    with self.assertRaises(Exception) as e2: self.table.bb_pos()
    for e in [e1, e2]: self.eq("blind position is not yet set", str(e.exception))

  def test_reset_deck(self):
    self.table.reset()
    self.eq(52, self.table.deck.size())

  def test_reset_commynity_card(self):
    self.table.reset()
    for card in self.table.deck.draw_cards(5):
      self.table.add_community_card(card)

  def test_reset_player_status(self):
    self.table.reset()
    self.eq(0, len(self.player.hole_card))
    self.eq(0, len(self.player.action_histories))
    self.eq(PayInfo.PAY_TILL_END, self.player.pay_info.status)

  @raises(ValueError)
  def test_community_card_exceed_size(self):
    self.table.add_community_card(Card.from_id(1))

  def test_shift_dealer_btn_skip(self):
    table = self.__setup_players_with_table()
    table.shift_dealer_btn()
    self.eq(2, table.dealer_btn)
    table.shift_dealer_btn()
    self.eq(0, table.dealer_btn)

  def test_next_ask_waiting_player_pos(self):
    table = self.__setup_players_with_table()
    self.eq(0, table.next_ask_waiting_player_pos(0))
    self.eq(0, table.next_ask_waiting_player_pos(1))
    self.eq(0, table.next_ask_waiting_player_pos(2))

  def test_next_ask_waitint_player_pos_when_no_one_waiting(self):
    table = self.__setup_players_with_table()
    table.seats.players[0].pay_info.update_to_allin()
    self.eq(table._player_not_found, table.next_ask_waiting_player_pos(0))
    self.eq(table._player_not_found, table.next_ask_waiting_player_pos(1))
    self.eq(table._player_not_found, table.next_ask_waiting_player_pos(2))

  def test_serialization(self):
    table = self.__setup_players_with_table()
    for card in table.deck.draw_cards(3):
      table.add_community_card(card)
    table.shift_dealer_btn()
    table.set_blind_pos(1, 2)
    serial = table.serialize()
    restored = Table.deserialize(serial)
    self.eq(table.dealer_btn, restored.dealer_btn)
    self.eq(Seats.serialize(table.seats), Seats.serialize(restored.seats))
    self.eq(Deck.serialize(table.deck), Deck.serialize(restored.deck))
    self.eq(table.get_community_card(), restored.get_community_card())
    self.eq(1, restored.sb_pos())
    self.eq(2, restored.bb_pos())

  def __setup_table(self):
    self.table = Table()
    for card in self.table.deck.draw_cards(5):
      self.table.add_community_card(card)

  def __setup_player(self):
    self.player = Player("uuid", 100)
    self.player.add_holecard([Card.from_id(cid+1) for cid in range(2)])
    self.player.add_action_history(Const.Action.CALL, 10)
    self.player.pay_info.update_to_fold()

  def __setup_players_with_table(self):
    p1 = Player("uuid1", 100)
    p2 = Player("uuid2", 100)
    p3 = Player("uuid3", 100)
    p2.pay_info.update_to_fold()
    p3.pay_info.update_to_allin()
    table = Table()
    for player in [p1, p2, p3]:
      table.seats.sitdown(player)
    return table

