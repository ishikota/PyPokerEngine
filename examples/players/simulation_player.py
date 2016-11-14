from pypokerengine.players.base_poker_player import BasePokerPlayer
from pypokerengine.engine.table import Table
from pypokerengine.engine.card import Card
from pypokerengine.engine.deck import Deck
from pypokerengine.engine.poker_constants import PokerConstants as Const
from pypokerengine.engine.player import Player
from pypokerengine.engine.action_checker import ActionChecker
from pypokerengine.engine.round_manager import RoundManager
from pypokerengine.engine.message_builder import MessageBuilder
from examples.players.random_player import PokerPlayer as RandomPlayer

class PokerPlayer(BasePokerPlayer):

  def __init__(self):
    self.simulator = RoundSimualtor()
    self.small_blind_amount = 5
    self.simulation_times = 100

  def set_small_blind_amount(self, amount):
    self.small_blind_amount = amount

  def declare_action(self, hole_card, valid_actions, round_info, action_histories):
    round_state = self.__restore_round_state(hole_card, round_info, action_histories)
    simulation_results = self.__simulate_all_actions(self.simulation_times, hole_card, valid_actions, round_state)
    return self.__decide_action(valid_actions, simulation_results)

  def __decide_action(self, valid_actions, simulation_results):
    rewards = [self.__research_reward(action, simulation_results[action]) \
        for action in simulation_results.iterkeys()]
    best_action_idx = rewards.index(max(rewards))
    best_action = valid_actions[best_action_idx]
    action, amount = best_action["action"], best_action["amount"]
    if action == "raise":
      amount = best_action["amount"]["min"]
    print "Best action = %s:%d (rewards = %s)" % (action, amount, rewards)
    return action, amount

  def __research_reward(self, action, simulation_results):
    seats_results = [result["seats"]  for result in simulation_results]
    my_results = [[seat for seat in seats if seat["uuid"] == self.uuid][0] for seats in seats_results]
    stack_info = [result["stack"] for result in my_results]
    print "Simulation result of %s => min:%d, max:%d, average:%d" %\
      (action, min(stack_info), max(stack_info), sum(stack_info)*1.0/len(stack_info))
    return sum(stack_info) * 1.0 / len(stack_info)

  def __simulate_all_actions(self, simulation_times, hole_info, valid_actions, original_state):
    simulation_results = {}
    for valid_action in valid_actions:
      apply_action_info = self.__gen_apply_action(valid_action)
      simulation_results[valid_action["action"]] = \
          [self.__simulate_action(hole_info, original_state, apply_action_info) for _ in range(simulation_times)]
    return simulation_results

  def __simulate_action(self, hole_info, original_state, apply_action_info):
    copy_state = self.__deep_copy_state(original_state)
    table = copy_state["table"]
    self.__attach_holecard_at_random(table.seats.players, hole_info, table.deck)
    return self.simulator.start_simulation(copy_state, apply_action_info)

  def __gen_apply_action(self, action_info):
    action = action_info["action"]
    amount = action_info["amount"]["min"] if action == "raise" else action_info["amount"]
    return self.simulator.gen_action_info(action, amount)

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
    deck.shuffle()
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
      player.pay_info.update_to_fold()
    elif "CALL" == history["action"]:
      need_amount = ActionChecker.need_amount_for_action(player, history["amount"])
      player.pay_info.update_by_pay(need_amount)
      player.add_action_history(Const.Action.CALL, history["amount"])
    elif "RAISE" == history["action"]:
      need_amount = ActionChecker.need_amount_for_action(player, history["amount"])
      player.pay_info.update_by_pay(need_amount)
      player.add_action_history(Const.Action.RAISE, history["amount"], history["add_amount"])
    elif "SMALLBLIND" == history["action"]:
      player.add_action_history(Const.Action.SMALL_BLIND)
      player.pay_info.update_by_pay(self.small_blind_amount)
    elif "BIGBLIND" == history["action"]:
      player.add_action_history(Const.Action.BIG_BLIND)
      player.pay_info.update_by_pay(self.small_blind_amount * 2)
    else:
      raise "Unknown type of history is passed => %s" % history
    return player

  def __deep_copy_state(self, state):
    table_deepcopy = Table.deserialize(state["table"].serialize())
    return {
        "round_count": state["round_count"],
        "street": state["street"],
        "next_player": state["next_player"],
        "table": table_deepcopy
        }

class RoundSimualtor:

  CALL = "call"
  RAISE = "raise"
  FOLD = "fold"

  def __init__(self):
    self.algo_owner_map = {}

  def register_algorithm(self, uuid, algorithm):
    self.algo_owner_map[uuid] = algorithm

  def start_simulation(self, round_state, apply_action_info):
    state, action_info, msgs = self.__deep_copy_state(round_state), apply_action_info, None
    while True:
      action, bet_amount = self.__read_action_info(action_info)
      state, msgs = RoundManager.apply_action(state, action, bet_amount)
      if self.__round_result_found(msgs):
        return self.__format_round_result(self.__find_round_result(msgs)[0]["message"])
      action_info = self.__fetch_next_action_info(msgs)

  def gen_action_info(self, action, bet_amount=None):
    valid_actions = [self.CALL, self.RAISE, self.FOLD]
    if action not in valid_actions:
      raise "passed action [%s] is illegal. Choose from here => %s" % (action, valid_actions)
    return (action, bet_amount if bet_amount else 0)


  def __read_action_info(self, action_info):
    return action_info[0], action_info[1]

  def __round_result_found(self, msgs):
    return len(self.__find_round_result(msgs)) != 0

  def __find_round_result(self, msgs):
    return [msg[1] for msg in msgs if msg[1]["message"]["message_type"] == MessageBuilder.ROUND_RESULT_MESSAGE]

  def __fetch_next_action_info(self, msgs):
    uuid, ask_message = self.__find_ask_message(msgs)
    next_player_algo = self.algo_owner_map[uuid]
    action, bet_amount = next_player_algo.respond_to_ask(ask_message["message"])
    return self.gen_action_info(action, bet_amount)

  def __find_ask_message(self, msgs):
    return [msg for msg in msgs if msg[1]["message"]["message_type"] == MessageBuilder.ASK_MESSAGE][0]


  def __format_round_result(self, result_message):
    return result_message["round_state"]

  def __deep_copy_state(self, state):
    table_deepcopy = Table.deserialize(state["table"].serialize())
    return {
        "round_count": state["round_count"],
        "street": state["street"],
        "next_player": state["next_player"],
        "table": table_deepcopy
        }

