from pypokerengine.players.sample.fold_man import PokerPlayer as FoldMan

class PokerPlayer(FoldMan):

  def __init__(self):
    self.received_msgs = []

  def declare_action(self, hole_card, valid_actions, round_state, action_histories):
    self.received_msgs.append("declare_action")
    return 'fold', 0

  def receive_game_start_message(self, game_info):
    self.received_msgs.append("receive_game_start_message")

  def receive_round_start_message(self, round_count, hole_card, seats):
    self.received_msgs.append("receive_round_start_message")

  def receive_street_start_message(self, street, round_state):
    self.received_msgs.append("receive_street_start_message")

  def receive_game_update_message(self, action, round_state, action_histories):
    self.received_msgs.append("receive_game_update_message")

  def receive_round_result_message(self, winners, hand_info, round_state):
    self.received_msgs.append("receive_round_result_message")

  def receive_game_result_message(self, seats):
    self.received_msgs.append("receive_game_result_message")

