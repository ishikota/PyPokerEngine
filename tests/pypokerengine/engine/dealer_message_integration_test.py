from tests.base_unittest import BaseUnitTest
from mock import Mock
from mock import patch
from pypokerengine.engine.player import Player
from pypokerengine.engine.seats import Seats
from pypokerengine.engine.table import Table
from pypokerengine.engine.card import Card
from pypokerengine.engine.message_builder import MessageBuilder
from pypokerengine.engine.dealer import MessageHandler
from pypokerengine.players import BasePokerPlayer
from nose.tools import *

class MessageIntegrationTest(BaseUnitTest):

  def setUp(self):
    self.player = BasePokerPlayer()
    self.MH = MessageHandler()
    self.MH.register_algorithm("U", self.player)

  def test_game_start_message(self):
    with patch.object(self.player, 'receive_game_start_message') as monkey:
      msg = self.__game_start_message()
      self.MH.process_message(-1, msg)
      monkey.assert_called_with(msg["message"]["game_information"])

  def test_round_start_message(self):
    with patch.object(self.player, 'receive_round_start_message') as monkey:
      msg = self.__round_start_message()
      self.MH.process_message("U", msg)
      round_count = msg["message"]["round_count"]
      hole = msg["message"]["hole_card"]
      seats = msg["message"]["seats"]
      monkey.assert_called_with(round_count, hole, seats)

  def test_street_start_message(self):
    with patch.object(self.player, 'receive_street_start_message') as monkey:
      msg = self.__street_start_message()
      self.MH.process_message(-1, msg)
      street = "flop"
      round_state = msg["message"]["round_state"]
      monkey.assert_called_with(street, round_state)

  def test_ask_message(self):
    with patch.object(self.player, 'declare_action') as monkey:
      msg = self.__ask_message()
      self.MH.process_message("U", msg)
      hole = msg["message"]["hole_card"]
      valid_actions = msg["message"]["valid_actions"]
      round_state = msg["message"]["round_state"]
      monkey.assert_called_with(valid_actions, hole, round_state)

  def test_game_update_message(self):
    with patch.object(self.player, 'receive_game_update_message') as monkey:
      msg = self.__game_update_message()
      self.MH.process_message(-1, msg)
      action = msg["message"]["action"]
      round_state = msg["message"]["round_state"]
      monkey.assert_called_with(action, round_state)

  def test_round_result_message(self):
    with patch.object(self.player, 'receive_round_result_message') as monkey:
      msg = self.__round_result_message()
      self.MH.process_message(-1, msg)
      winners = msg["message"]["winners"]
      hand_info = msg["message"]["hand_info"]
      round_state = msg["message"]["round_state"]
      monkey.assert_called_with(winners, hand_info, round_state)

  def __game_start_message(self):
    config = self.__setup_config()
    seats = self.__setup_seats()
    return MessageBuilder.build_game_start_message(config, seats)

  def __round_start_message(self):
    seats = self.__setup_seats()
    return MessageBuilder.build_round_start_message(7, 1, seats)

  def __street_start_message(self):
    state = self.__setup_state()
    return MessageBuilder.build_street_start_message(state)

  def __ask_message(self):
    state = self.__setup_state()
    return MessageBuilder.build_ask_message(1, state)

  def __game_update_message(self):
    state = self.__setup_state()
    return MessageBuilder.build_game_update_message(1, "call", 10, state)

  def __round_result_message(self):
    hand_info = ["dummy", "info"]
    state = self.__setup_state()
    winners = state["table"].seats.players[1:2]
    return MessageBuilder.build_round_result_message(7, winners, hand_info, state)

  def __game_result_message(self):
    config = self.__setup_config()
    seats = self.__setup_seats()
    return MessageBuilder.build_game_result_message(config, seats)

  def __setup_state(self):
    return {
        "street": 1,
        "next_player": 2,
        "round_count": 3,
        "small_blind_amount": 4,
        "table": self.__setup_table()
    }

  def __setup_table(self):
    table = Table()
    table.set_blind_pos(0, 1)
    table.seats = self.__setup_seats()
    table.add_community_card(Card.from_id(1))
    return table

  def __setup_config(self):
    return { "initial_stack":100, "max_round": 10, "small_blind_amount": 5,\
            "ante": 3, "blind_structure": {}}

  def __setup_seats(self):
    seats = Seats()
    for player in self.__setup_players():
      seats.sitdown(player)
    return seats

  def __setup_players(self):
    hole = [Card.from_id(1), Card.from_id(2)]
    players = [self.__setup_player() for _ in range(3)]
    players[1].add_holecard(hole)
    return players

  def __setup_player(self):
    return Player("uuid", 100, "hoge")

