from pypokerengine.engine.dealer import Dealer
from pypokerengine.players import BasePokerPlayer

def setup_config(max_round, initial_stack, small_blind_amount):
    return Config(max_round, initial_stack, small_blind_amount)

def start_poker(config, verbose=2):
    config.validation()
    dealer = Dealer(config.sb_amount, config.initial_stack)
    for info in config.players_info:
        dealer.register_player(info["name"], info["algorithm"])
    return dealer.start_game(config.max_round)

class Config(object):

    def __init__(self, max_round, initial_stack, sb_amount):
        self.players_info = []
        self.max_round = max_round
        self.initial_stack = initial_stack
        self.sb_amount = sb_amount

    def register_player(self, name, algorithm):
        if not isinstance(algorithm, BasePokerPlayer):
            base_msg = 'Poker player must be child class of "BasePokerPlayer". But its parent was "%s"'
            raise TypeError(base_msg % algorithm.__class__.__bases__)

        info = { "name" : name, "algorithm" : algorithm }
        self.players_info.append(info)

    def validation(self):
        player_num = len(self.players_info)
        if player_num < 2:
            detail_msg = "no player is registered yet" if player_num==0 else "you registered only 1 player"
            base_msg = "At least 2 players are needed to start the game"
            raise Exception("%s (but %s.)" % (base_msg, detail_msg))

