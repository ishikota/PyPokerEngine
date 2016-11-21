from pypokerengine.engine.data_encoder import DataEncoder
from pypokerengine.engine.action_checker import ActionChecker

class MessageBuilder:

  GAME_START_MESSAGE = "game_start_message"
  ROUND_START_MESSAGE = "round_start_message"
  STREET_START_MESSAGE = "street_start_message"
  ASK_MESSAGE = "ask_message"
  GAME_UPDATE_MESSAGE = "game_update_message"
  ROUND_RESULT_MESSAGE = "round_result_message"
  GAME_RESULT_MESSAGE = "game_result_message"

  @classmethod
  def build_game_start_message(self, config, seats):
    message = {
        "message_type": self.GAME_START_MESSAGE,
        "game_information": DataEncoder.encode_game_information(config, seats)
    }
    return self.__build_notification_message(message)

  @classmethod
  def build_round_start_message(self, round_count, player_pos, seats):
    player = seats.players[player_pos]
    hole_card = DataEncoder.encode_player(player, holecard=True)["hole_card"]
    message = {
        "message_type": self.ROUND_START_MESSAGE,
        "round_count": round_count,
        "hole_card": hole_card
    }
    message.update(DataEncoder.encode_seats(seats))
    return self.__build_notification_message(message)

  @classmethod
  def build_street_start_message(self, state):
    message = {
        "message_type": self.STREET_START_MESSAGE,
        "round_state": DataEncoder.encode_round_state(state)
        }
    message.update(DataEncoder.encode_street(state["street"]))
    return self.__build_notification_message(message)

  @classmethod
  def build_ask_message(self, player_pos, state):
    players = state["table"].seats.players
    player = players[player_pos]
    hole_card = DataEncoder.encode_player(player, holecard=True)["hole_card"]
    valid_actions = ActionChecker.legal_actions(players, player_pos, state["small_blind_amount"])
    message = {
        "message_type" : self.ASK_MESSAGE,
        "hole_card": hole_card,
        "valid_actions": valid_actions,
        "round_state": DataEncoder.encode_round_state(state),
        "action_histories": DataEncoder.encode_action_histories(state["table"])
    }
    return self.__build_ask_message(message)

  @classmethod
  def build_game_update_message(self, player_pos, action, amount, state):
    player = state["table"].seats.players[player_pos]
    message = {
        "message_type": self.GAME_UPDATE_MESSAGE,
        "action": DataEncoder.encode_action(player, action, amount),
        "round_state": DataEncoder.encode_round_state(state),
        "action_histories": DataEncoder.encode_action_histories(state["table"])
    }
    return self.__build_notification_message(message)

  @classmethod
  def build_round_result_message(self, round_count, winners, hand_info, state):
    message = {
        "message_type": self.ROUND_RESULT_MESSAGE,
        "round_count": round_count,
        "hand_info"  : hand_info,
        "round_state": DataEncoder.encode_round_state(state)
    }
    message.update(DataEncoder.encode_winners(winners))
    return self.__build_notification_message(message)

  @classmethod
  def build_game_result_message(self, config, seats):
    message = {
      "message_type": self.GAME_RESULT_MESSAGE,
      "game_information": DataEncoder.encode_game_information(config, seats)
    }
    return self.__build_notification_message(message)


  @classmethod
  def __build_ask_message(self, message):
    return {
        "type": "ask",
        "message": message
    }

  @classmethod
  def __build_notification_message(self, message):
    return {
        "type": "notification",
        "message": message
    }

