from pypokerengine.engine.table import Table
from pypokerengine.engine.seats import Seats
from pypokerengine.engine.card import Card
from pypokerengine.engine.deck import Deck
from pypokerengine.engine.player import Player
from pypokerengine.engine.pay_info import PayInfo
from pypokerengine.engine.data_encoder import DataEncoder
from pypokerengine.engine.poker_constants import PokerConstants as Const
from pypokerengine.engine.round_manager import RoundManager
from pypokerengine.engine.message_builder import MessageBuilder
from pypokerengine.players import BasePokerPlayer
from pypokerengine.api.state_builder import deepcopy_game_state

class Emulator(object):

    def __init__(self):
        self.players_holder = {}

    def register_player(self, uuid, player):
        if not isinstance(player, BasePokerPlayer):
            raise TypeError("player must inherit %s class." % BasePokerPlayer.__class__)
        self.players_holder[uuid] = player

    def fetch_player(self, uuid):
        return self.players_holder[uuid]

    def run_until_next_event(self, game_state, apply_action, bet_amount=0):
        updated_state, messages = RoundManager.apply_action(game_state, apply_action, bet_amount)
        event = self.create_event(messages)
        return updated_state, event

    def start_new_round(self, round_count, sb_amount, ante, game_state):
        deepcopy_table = Table.deserialize(game_state["table"].serialize())
        deepcopy_table.shift_dealer_btn()
        new_state, messages = RoundManager.start_new_round(round_count, sb_amount, ante, deepcopy_table)
        event = self.create_event(messages)
        return new_state, event

    def create_event(self, raw_messages):
        messages = [m[1]["message"] for m in raw_messages]
        message_types = [m["message_type"] for m in messages]
        if MessageBuilder.STREET_START_MESSAGE in message_types:
            assert(messages[-2]["message_type"]==MessageBuilder.STREET_START_MESSAGE)
            assert(messages[-1]["message_type"]==MessageBuilder.ASK_MESSAGE)
            return Event.create_new_street_event(messages[-2], messages[-1])
        if MessageBuilder.ASK_MESSAGE in message_types:
            assert(messages[-1]["message_type"]==MessageBuilder.ASK_MESSAGE)
            return Event.create_ask_player_event(messages[-1])
        if MessageBuilder.GAME_RESULT_MESSAGE in message_types:
            assert(messages[-2]["message_type"]==MessageBuilder.ROUND_RESULT_MESSAGE)
            assert(messages[-1]["message_type"]==MessageBuilder.GAME_RESULT_MESSAGE)
            return Event.create_game_finish_event(messages[-2], messages[-1])
        if MessageBuilder.ROUND_RESULT_MESSAGE in message_types:
            assert(messages[-1]["message_type"]==MessageBuilder.ROUND_RESULT_MESSAGE)
            return Event.create_round_finish_event(messages[-1])
        raise Exception("Unexpected format of messages received => %s" % messages)

class Event:
    NEW_STREET = "event_new_street"
    ASK_PLAYER = "event_ask_player"
    ROUND_FINISH = "event_round_finish"
    GAME_FINISH = "event_game_finish"

    @classmethod
    def create_new_street_event(self, street_message, ask_message):
        ask_event = self.create_ask_player_event(ask_message)
        return {
                "type": self.NEW_STREET,
                "street": street_message["street"],
                "round_state": street_message["round_state"],
                "next_ask_info": {
                    "uuid": ask_event["uuid"],
                    "valid_actions": ask_event["valid_actions"],
                    "round_state": ask_event["round_state"]  # TODO maybe redundant
                    }
                }

    @classmethod
    def create_ask_player_event(self, message):
        players = message["round_state"]["seats"]
        next_player_pos = message["round_state"]["next_player"]
        asked_player_uuid = players[next_player_pos]["uuid"]
        return {
                "type": self.ASK_PLAYER,
                "uuid": asked_player_uuid,
                "valid_actions": message["valid_actions"],
                "round_state": message["round_state"]
                }

    @classmethod
    def create_round_finish_event(self, message):
        player_info = lambda info: { "uuid": info["uuid"], "stack": info["stack"] }
        return {
                "type": self.ROUND_FINISH,
                "round_state": message["round_state"],
                "winners": [player_info(info) for info in message["winners"]]
                }

    @classmethod
    def create_game_finish_event(self, round_fin_msg, game_fin_msg):
        player_info = lambda info: { "uuid": info["uuid"], "stack": info["stack"] }
        return {
                "type": self.GAME_FINISH,
                "round_state": round_fin_msg["round_state"],
                "players": [player_info(info) for info in game_fin_msg["game_information"]["seats"]]
                }


class Action:
    FOLD = "fold"
    CALL = "call"
    RAISE = "raise"


