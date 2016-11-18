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
        events = [self.create_event(message[1]["message"]) for message in messages]
        events = [e for e in events if e]
        return updated_state, events

    def start_new_round(self, round_count, sb_amount, ante, game_state):
        deepcopy_table = Table.deserialize(game_state["table"].serialize())
        deepcopy_table.shift_dealer_btn()
        new_state, messages = RoundManager.start_new_round(round_count, sb_amount, ante, deepcopy_table)
        events = [self.create_event(message[1]["message"]) for message in messages]
        events = [e for e in events if e]
        return new_state, events

    def create_event(self, message):
        message_type = message["message_type"]
        if MessageBuilder.STREET_START_MESSAGE == message_type:
            return Event.create_new_street_event(message)
        if MessageBuilder.ASK_MESSAGE == message_type:
            return Event.create_ask_player_event(message)
        if MessageBuilder.GAME_RESULT_MESSAGE == message_type:
            return Event.create_game_finish_event(message)
        if MessageBuilder.ROUND_RESULT_MESSAGE == message_type:
            return Event.create_round_finish_event(message)

class Event:
    NEW_STREET = "event_new_street"
    ASK_PLAYER = "event_ask_player"
    ROUND_FINISH = "event_round_finish"
    GAME_FINISH = "event_game_finish"

    @classmethod
    def create_new_street_event(self, message):
        return {
                "type": self.NEW_STREET,
                "street": message["street"],
                "round_state": message["round_state"],
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
    def create_game_finish_event(self, message):
        player_info = lambda info: { "uuid": info["uuid"], "stack": info["stack"] }
        return {
                "type": self.GAME_FINISH,
                "players": [player_info(info) for info in message["game_information"]["seats"]]
                }


class Action:
    FOLD = "fold"
    CALL = "call"
    RAISE = "raise"


