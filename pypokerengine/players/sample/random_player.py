from pypokerengine.players.base_poker_player import BasePokerPlayer
import random as rand

class PokerPlayer(BasePokerPlayer):

  def declare_action(self, hole_card, valid_actions, round_state, action_histories):
    choice = rand.choice(valid_actions)
    action = choice["action"]
    amount = choice["amount"]
    if action == "raise":
      amount = rand.randrange(amount["min"], amount["max"] + 1)
    return action, amount

  def receive_game_start_message(self, game_info):
    pass

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

