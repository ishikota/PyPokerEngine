from tests.base_unittest import BaseUnitTest
from pypokerengine.engine.player import Player
from pypokerengine.engine.card import Card
from pypokerengine.engine.seats import Seats
from pypokerengine.engine.table import Table
from pypokerengine.engine.data_encoder import DataEncoder
from pypokerengine.engine.message_builder import MessageBuilder

class MessageBuilderTest(BaseUnitTest):

  def test_game_start_message(self):
    config = self.__setup_config()
    seats = self.__setup_seats()
    message = MessageBuilder.build_game_start_message(config, seats)
    msg = message["message"]
    self.eq("notification", message["type"])
    self.eq(MessageBuilder.GAME_START_MESSAGE, msg["message_type"])
    self.eq(MessageBuilder.GAME_START_MESSAGE, msg["message_type"])
    self.eq(DataEncoder.encode_game_information(config, seats), msg["game_information"])

  def test_round_start_message(self):
    seats = self.__setup_seats()
    message = MessageBuilder.build_round_start_message(7, 1, seats)
    msg = message["message"]
    self.eq("notification", message["type"])
    self.eq(MessageBuilder.ROUND_START_MESSAGE, msg["message_type"])
    self.eq(7, msg["round_count"])
    self.eq(DataEncoder.encode_seats(seats)["seats"], msg["seats"])
    self.eq(["CA", "C2"], msg["hole_card"])

  def test_street_start_message(self):
    state = self.__setup_state()
    message = MessageBuilder.build_street_start_message(state)
    msg = message["message"]
    self.eq(MessageBuilder.STREET_START_MESSAGE, msg["message_type"])
    self.eq("notification", message["type"])
    self.eq("flop", msg["street"])
    self.eq(DataEncoder.encode_round_state(state), msg["round_state"])

  def test_ask_message(self):
    state = self.__setup_state()
    table = state["table"]
    message = MessageBuilder.build_ask_message(1, state)
    msg = message["message"]
    self.eq("ask", message["type"])
    self.eq(MessageBuilder.ASK_MESSAGE, msg["message_type"])
    self.eq(["CA", "C2"], msg["hole_card"])
    self.eq(3, len(msg["valid_actions"]))
    self.eq(DataEncoder.encode_round_state(state), msg["round_state"])
    self.eq(DataEncoder.encode_action_histories(table), msg["action_histories"])

  def test_game_update_message(self):
    state = self.__setup_state()
    table = state["table"]
    player = table.seats.players[1]
    message = MessageBuilder.build_game_update_message(1, "call", 10, state)
    msg = message["message"]
    self.eq("notification", message["type"])
    self.eq(MessageBuilder.GAME_UPDATE_MESSAGE, msg["message_type"])
    self.eq(DataEncoder.encode_action(player, "call", 10), msg["action"])
    self.eq(DataEncoder.encode_round_state(state), msg["round_state"])
    self.eq(DataEncoder.encode_action_histories(table), msg["action_histories"])

  def test_round_result_message(self):
    state = self.__setup_state()
    winners = state["table"].seats.players[1:2]
    hand_info = ["dummy", "info"]
    message = MessageBuilder.build_round_result_message(7, winners, hand_info, state)
    msg = message["message"]
    self.eq("notification", message["type"])
    self.eq(MessageBuilder.ROUND_RESULT_MESSAGE, msg["message_type"])
    self.eq(7, msg["round_count"])
    self.eq(hand_info, msg["hand_info"])
    self.eq(DataEncoder.encode_winners(winners)["winners"], msg["winners"])
    self.eq(DataEncoder.encode_round_state(state), msg["round_state"])

  def test_game_result_message(self):
    config = self.__setup_config()
    seats = self.__setup_seats()
    state = self.__setup_state()
    message = MessageBuilder.build_game_result_message(config, seats)
    msg = message["message"]
    self.eq("notification", message["type"])
    self.eq(MessageBuilder.GAME_RESULT_MESSAGE, msg["message_type"])
    self.eq(DataEncoder.encode_game_information(config, seats), msg["game_information"])


  def __setup_state(self):
    return {
        "street": 1,
        "next_player": 2,
        "round_count": 3,
        "small_blind_amount": 4,
        "table": self.__setup_table(),
    }

  def __setup_table(self):
    table = Table()
    table.seats = self.__setup_seats()
    table.add_community_card(Card.from_id(1))
    table.set_blind_pos(1, 2)
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
