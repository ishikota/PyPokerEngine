from pypoker2.engine.poker_constants import PokerConstants as Const
from pypoker2.engine.table import Table
from pypoker2.engine.player import Player
from pypoker2.engine.round_manager import RoundManager
from pypoker2.engine.message_builder import MessageBuilder
from pypoker2.interface.message_handler import MessageHandler
import random

class Dealer:

  def __init__(self, small_blind_amount=None, initial_stack=None):
    self.small_blind_amount = small_blind_amount
    self.initial_stack = initial_stack
    self.uuid_list = self.__generate_uuid_list()
    self.message_handler = MessageHandler()
    self.table = Table()

  def register_player(self, player_name, algorithm):
    self.__config_check()
    uuid = self.__escort_player_to_table(player_name)
    self.__register_algorithm_to_message_handler(uuid, algorithm)

  def start_game(self, max_round):
    table = self.table
    for round_count in range(1, max_round+1):
      table = self.__play_round(round_count, self.small_blind_amount, table)
    return self.__generate_game_result(max_round, table.seats)

  def set_small_blind_amount(self, amount):
    self.small_blind_amount = amount

  def set_initial_stack(self, amount):
    self.initial_stack = amount


  def __register_algorithm_to_message_handler(self, uuid, algorithm):
    self.message_handler.register_algorithm(uuid, algorithm)

  def __escort_player_to_table(self, player_name):
    uuid = self.__fetch_uuid()
    player = Player(uuid, self.initial_stack, player_name)
    self.table.seats.sitdown(player)
    return uuid

  def __play_round(self, round_count, blind_amount, table):
    state, msgs = RoundManager.start_new_round(round_count, blind_amount, table)
    while state["street"] != Const.Street.FINISHED:
      self.__message_check(msgs)
      action, bet_amount = self.__publish_messages(msgs)
      state, msgs = RoundManager.apply_action(state, action, bet_amount)
    return state["table"]

  def __message_check(self, msgs):
    address, msg = msgs[-1]
    if address == -1 or msg["type"] != 'ask':
      raise Exception("Last message is not ask type. : %s" % msgs)

  def __publish_messages(self, msgs):
    for address, msg in msgs[:-1]:
      self.message_handler.process_message(address, msg)
    return self.message_handler.process_message(*msgs[-1])

  def __generate_game_result(self, max_round, seats):
    config = self.__gen_config(max_round)
    return MessageBuilder.build_game_result_message(config, seats)["message"]

  def __gen_config(self, max_round):
    return {
        "initial_stack": self.initial_stack,
        "max_round": max_round,
        "small_blind_amount": self.small_blind_amount
    }


  def __config_check(self):
    if self.small_blind_amount is None:
      raise Exception("small_blind_amount is not set!!\
          You need to call 'dealer.set_small_blind_amount' before.")
    if self.initial_stack is None:
      raise Exception("initial_stack is not set!!\
          You need to call 'dealer.set_initial_stack' before.")

  def __fetch_uuid(self):
    return self.uuid_list.pop()

  def __generate_uuid_list(self):
    return [self.__generate_uuid() for _ in range(100)]

  def __generate_uuid(self):
    uuid_size = 22
    chars = [chr(code) for code in range(97,123)]
    return "".join([random.choice(chars) for _ in range(uuid_size)])

