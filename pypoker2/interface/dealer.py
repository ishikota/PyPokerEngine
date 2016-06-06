from pypoker2.engine.table import Table
from pypoker2.engine.round_manager import RoundManager

class Dealer:

  def __init__(self, small_blind_amount=None, initial_stack=None):
    self.small_blind_amount = small_blind_amount
    self.initial_stack = initial_stack

  def register_player(self, player_name, algorithm):
    self.__config_check()
    self.__register_algorithm_to_message_handler(algorithm)
    self.__escort_player_to_table(player_name)

  def start_game(self, round_num):
    for round_count in range(1, round_num+1):
      self.__play_round()

  def summary_game_result(self):
    pass

  def set_small_blind_amount(self, amount):
    self.small_blind_amount = amount

  def set_initial_stack(self, amount):
    self.initial_stack = amount


  def __register_algorithm_to_message_handler(self, algorithm):
    pass

  def __escort_player_to_table(self, player_name):
    pass

  def __play_round(self):
    pass

  def __config_check(self):
    if self.small_blind_amount is None:
      raise Exception("small_blind_amount is not set!!\
          You need to call 'dealer.set_small_blind_amount' before.")
    if self.initial_stack is None:
      raise Exception("initial_stack is not set!!\
          You need to call 'dealer.set_initial_stack' before.")

