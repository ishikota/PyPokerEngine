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
        exclude_short_of_money_players(deepcopy_table, ante, sb_amount)
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

def exclude_short_of_money_players(table, ante, sb_amount):
    updated_dealer_btn_pos = _steal_money_from_poor_player(table, ante, sb_amount)
    _disable_no_money_player(table.seats.players)
    table.dealer_btn = updated_dealer_btn_pos
    return table

def _steal_money_from_poor_player(table, ante, sb_amount):
    players = table.seats.players
    search_targets = players + players
    search_targets = search_targets[table.dealer_btn:table.dealer_btn+len(players)]
    # exclude player who cannot pay small blind
    sb_player = _find_first_elligible_player(search_targets, sb_amount + ante)
    sb_relative_pos = search_targets.index(sb_player)
    for player in search_targets[:sb_relative_pos]: player.stack = 0
    # exclude player who cannot pay big blind
    search_targets = search_targets[sb_relative_pos+1:sb_relative_pos+len(players)]
    bb_player = _find_first_elligible_player(search_targets, sb_amount*2 + ante, sb_player)
    if sb_player == bb_player:  # no one can pay big blind. So steal money from all players except small blind
        for player in [p for p in players if p!=bb_player]: player.stack = 0
    else:
        bb_relative_pos = search_targets.index(bb_player)
        for player in search_targets[:bb_relative_pos]: player.stack = 0
    return players.index(sb_player)


def _find_first_elligible_player(players, need_amount, default=None):
    if default: return next((player for player in players if player.stack >= need_amount), default)
    return next((player for player in players if player.stack >= need_amount))

def _disable_no_money_player(players):
    no_money_players = [player for player in players if player.stack == 0]
    for player in no_money_players:
        player.pay_info.update_to_fold()


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


