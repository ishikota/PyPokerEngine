from pypokerengine.players.base_poker_player import BasePokerPlayer
from pypokerengine.players.sample.random_player import PokerPlayer as RandomPlayer
import pypokerengine.players.round_simulator
from pypokerengine.engine.table import Table
from pypokerengine.engine.card import Card
from pypokerengine.engine.deck import Deck
from pypokerengine.engine.poker_constants import PokerConstants as Const
from pypokerengine.engine.player import Player
from pypokerengine.engine.action_checker import ActionChecker

class PokerPlayer(BasePokerPlayer):

  def __init__(self):
    self.simulator = pypokerengine.players.round_simulator.RoundSimualtor()
    self.small_blind_amount = 5

  def set_small_blind_amount(self, amount):
    self.small_blind_amount = amount

  def declare_action(self, hole_card, valid_actions, round_info, action_histories):
    # TODO execute simulation here
    return 'fold', 0

  def receive_game_start_message(self, game_info):
    self.__setup_algorithm_for_each_player(game_info["seats"])

  def receive_round_start_message(self, round_count, hole_card, seats):
    pass

  def receive_street_start_message(self, street, round_state):
    pass

  def receive_game_update_message(self, action, round_state, action_histories):
    pass

  def receive_round_result_message(self, winners, hand_info, round_state):
    pass

  def receive_game_result_message(self, seats):
    pass


  def __setup_algorithm_for_each_player(self, seats):
    for player in seats:
      self.simulator.register_algorithm(player["uuid"], RandomPlayer())

  def __restore_round_state(self, hole_card, round_info, action_histories):
    return {
        "round_count" : 0, #TODO
        "street" : self.__restore_street(round_info["street"]),
        "next_player" : round_info["next_player"],
        "table" : self.__restore_table(hole_card, round_info, action_histories)
    }

  def __attach_holecard_at_random(self, players, my_hole_info, deck):
    for player in players:
      if self.uuid == player.uuid:
        player.add_holecard([self.__restore_card(card) for card in my_hole_info])
      else:
        player.add_holecard(deck.draw_cards(2))

  def __restore_table(self, hole_card, round_info, action_histories):
    table = Table()
    table.dealer_btn = round_info["dealer_btn"]
    for card in self.__restore_community_card(round_info["community_card"]):
      table.add_community_card(card)
    table.deck = self.__restore_deck(hole_card)
    players = [self.__restore_player(info, hole_card, table.deck) for info in round_info["seats"]]
    players = self.__restore_action_histories_on_players(players, action_histories)
    for player in players:
      table.seats.sitdown(player)
    return table

  def __restore_deck(self, exclude_cards):
    deck = Deck()
    for card in exclude_cards:
      deck.deck.remove(self.__restore_card(card))
    deck.shuffle()
    return deck

  def __restore_street(self, info):
    if info == "preflop":
      return Const.Street.PREFLOP
    if info == "flop":
      return Const.Street.FLOP
    if info == "turn":
      return Const.Street.TURN
    if info == "river":
      return Const.Street.RIVER
    if info == "showdown":
      return Const.Street.SHOWDOWN

  def __restore_community_card(self, info):
    return [self.__restore_card(card) for card in info]

  def __restore_card(self, info):
    suit_map = { "H": Card.HEART, "C": Card.CLUB, "S":Card.SPADE, "D": Card.DIAMOND }
    rank_map = { v:k for k,v in Card.RANK_MAP.iteritems() }
    suit, rank = info[0], info[1]
    return Card(suit_map[suit], int(rank_map[rank]))

  def __restore_player(self, info, hole_info, deck):
    return Player(info["uuid"], info["stack"], info["name"])

  def __restore_action_histories_on_players(self, players, action_histories):
    player_map = { player.uuid:player for player in players }
    for history in action_histories["action_histories"]:
      player = player_map[history["uuid"]]
      player = self.__add_action_history(player, history)
    return players

  def __add_action_history(self, player, history):
    if "FOLD" == history["action"]:
      player.add_action_history(Const.Action.FOLD)
    elif "CALL" == history["action"]:
      player.add_action_history(Const.Action.CALL, history["amount"])
      need_amount = ActionChecker.need_amount_for_action(player, history["amount"])
      player.pay_info.update_by_pay(need_amount)
    elif "RAISE" == history["action"]:
      player.add_action_history(Const.Action.RAISE, history["amount"], history["add_amount"])
      need_amount = ActionChecker.need_amount_for_action(player, history["amount"])
      player.pay_info.update_by_pay(need_amount)
    elif "SMALLBLIND" == history["action"]:
      player.add_action_history(Const.Action.SMALL_BLIND)
      player.pay_info.update_by_pay(self.small_blind_amount)
    elif "BIGBLIND" == history["action"]:
      player.add_action_history(Const.Action.BIG_BLIND)
      player.pay_info.update_by_pay(self.small_blind_amount * 2)
    else:
      raise "Unknown type of history is passed => %s" % history
    return player

