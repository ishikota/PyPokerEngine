from pypokerengine.engine.table import Table
from pypokerengine.engine.seats import Seats
from pypokerengine.engine.card import Card
from pypokerengine.engine.deck import Deck
from pypokerengine.engine.player import Player
from pypokerengine.engine.pay_info import PayInfo
from pypokerengine.engine.data_encoder import DataEncoder
from pypokerengine.engine.poker_constants import PokerConstants as Const
from pypokerengine.players import BasePokerPlayer

class Emulator(object):

    def __init__(self):
        self.players_holder = {}

    def register_player(self, uuid, player):
        if not isinstance(player, BasePokerPlayer):
            raise TypeError("player must inherit %s class." % BasePokerPlayer.__class__)
        self.players_holder[uuid] = player

    def fetch_player(self, uuid):
        return self.players_holder[uuid]


def restore_game_state(round_state):
    return {
            "round_count": round_state["round_count"],
            "small_blind_amount": round_state["small_blind_amount"],
            "street": _street_flg_translator[round_state["street"]],
            "next_player": round_state["next_player"],
            "table": _restore_table(round_state)
            }

def attach_hole_card(game_state, uuid, hole_card):
    target = [player for player in game_state["table"].seats.players if uuid==player.uuid]
    if len(target)==0: raise Exception('The player whose uuid is "%s" is not found in passed game_state.' % uuid)
    if len(target)!=1: raise Exception('Multiple players have uuid "%s". So we cannot attach hole card.' % uuid)
    target[0].hole_card = hole_card
    return game_state

def replace_community_card(game_state, community_card):
    game_state["table"]._community_card = community_card
    return game_state


_street_flg_translator = {
        "preflop": Const.Street.PREFLOP,
        "flop": Const.Street.FLOP,
        "turn": Const.Street.TURN,
        "river": Const.Street.RIVER,
        "showdown": Const.Street.SHOWDOWN
        }

def _restore_table(round_state):
    table = Table()
    table.dealer_btn = round_state["dealer_btn"]
    _restore_community_card_on_table(table, round_state["community_card"])
    table.deck = _restore_deck(round_state["community_card"])
    table.seats = _restore_seats(round_state["seats"], round_state["action_histories"])
    return table

def _restore_community_card_on_table(table, card_data):
    for str_card in card_data:
        table.add_community_card(Card.from_str(str_card))

def _restore_deck(str_exclude_cards):
    deck = Deck()
    exclude_ids = [Card.to_id(Card.from_str(s)) for s in str_exclude_cards]
    deck_cards = [Card.from_id(cid) for cid in range(1, 53) if cid not in exclude_ids]
    deck.deck = deck_cards
    return deck

def _restore_seats(seats_info, action_histories):
    players = [Player(info["uuid"], info["stack"], info["name"]) for info in seats_info]
    players_state = [info["state"] for info in seats_info]
    _restore_action_histories_on_players(players, action_histories)
    _restore_pay_info_on_players(players, players_state, action_histories)
    seats = Seats()
    seats.players = players
    return seats

def _restore_action_histories_on_players(players, round_action_histories):
    ordered_street_names = sorted(round_action_histories.keys(), key=lambda x:_street_flg_translator[x])
    current_street_name = ordered_street_names[-1]
    past_street_names = ordered_street_names[:-1]

    # restore round_action_histories
    for street_name in past_street_names:
        street_flg = _street_flg_translator[street_name]
        action_histories = round_action_histories[street_name]
        for player in players: player.round_action_histories[street_flg] = []
        for action_history in action_histories:
            player = _find_user_by_uuid(players, action_history["uuid"])
            player.round_action_histories[street_flg].append(action_history)

    # resotre action_histories
    for action_history in round_action_histories[current_street_name]:
        player = _find_user_by_uuid(players, action_history["uuid"])
        player.action_histories.append(action_history)

def _restore_pay_info_on_players(players, players_state, round_action_histories):
    _restore_pay_info_status_on_players(players, players_state)
    _restore_pay_info_amount_on_players(players, round_action_histories)

def _restore_pay_info_amount_on_players(players, round_action_histories):
    ordered_street_names = sorted(round_action_histories.keys(), key=lambda x:_street_flg_translator[x])
    all_histories = reduce(lambda ary, key: ary + round_action_histories[key], ordered_street_names, [])
    for action_history in all_histories:
        player = _find_user_by_uuid(players, action_history["uuid"])
        player.pay_info.amount += _fetch_pay_amount(action_history)

def _find_user_by_uuid(players, uuid):
    return [player for player in players if player.uuid==uuid][0]

def _fetch_pay_amount(action_history):
    action = action_history["action"]
    if action == Player.ACTION_FOLD_STR: return 0
    if action == Player.ACTION_CALL_STR: return action_history["paid"]
    if action == Player.ACTION_RAISE_STR: return action_history["paid"]
    if action == Player.ACTION_SMALL_BLIND: return action_history["amount"]
    if action == Player.ACTION_BIG_BLIND: return action_history["amount"]
    raise Exception("Unexpected type of action_history is passed => %s" % action_history)


def _restore_pay_info_status_on_players(players, players_state):
    for player, state_str in zip(players, players_state):
        player.pay_info.status = _pay_info_state_translator[state_str]

_pay_info_state_translator = {
        DataEncoder.PAY_INFO_PAY_TILL_END_STR: PayInfo.PAY_TILL_END,
        DataEncoder.PAY_INFO_ALLIN_STR: PayInfo.ALLIN,
        DataEncoder.PAY_INFO_FOLDED_STR: PayInfo.FOLDED
        }


