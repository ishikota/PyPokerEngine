from pypokerengine.engine.poker_constants import PokerConstants as Const
from pypokerengine.engine.table import Table
from pypokerengine.engine.player import Player
from pypokerengine.engine.round_manager import RoundManager
from pypokerengine.engine.message_builder import MessageBuilder
from pypokerengine.interface.message_handler import MessageHandler
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
    algorithm.set_uuid(uuid)
    self.__register_algorithm_to_message_handler(uuid, algorithm)

  def start_game(self, max_round):
    table = self.table
    self.__notify_game_start(max_round)
    for round_count in range(1, max_round+1):
      if self.__is_game_finished(table):
        break
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

  def __notify_game_start(self, max_round):
    config = self.__gen_config(max_round)
    start_msg = MessageBuilder.build_game_start_message(config, self.table.seats)
    self.message_handler.process_message(-1, start_msg)

  def __is_game_finished(self, table):
    return len([player for player in  table.seats.players if player.is_active()]) == 1

  def __play_round(self, round_count, blind_amount, table):
    state, msgs = RoundManager.start_new_round(round_count, blind_amount, table)
    while True:
      self.__message_check(msgs, state["street"])
      if state["street"] != Const.Street.FINISHED:  # continue the round
        action, bet_amount = self.__publish_messages(msgs)
        state, msgs = RoundManager.apply_action(state, action, bet_amount)
      else:  # finish the round after publish round result
        self.__publish_messages(msgs)
        break
    return self.__prepare_for_next_round(state["table"])

  def __message_check(self, msgs, street):
    address, msg = msgs[-1]
    invalid = msg["type"] != 'ask'
    invalid &= street != Const.Street.FINISHED or msg["message"]["message_type"] == 'round_result'
    if invalid:
      raise Exception("Last message is not ask type. : %s" % msgs)

  def __publish_messages(self, msgs):
    for address, msg in msgs[:-1]:
      self.message_handler.process_message(address, msg)
    return self.message_handler.process_message(*msgs[-1])

  def __prepare_for_next_round(self, table):
    table.shift_dealer_btn()
    small_blind_pos = table.dealer_btn
    big_blind_pos = table.next_active_player_pos(small_blind_pos)
    self.__exclude_cannot_pay_blind_player(small_blind_pos, big_blind_pos, table.seats.players)
    self.__exclude_no_money_player(table.seats.players)
    return table

  def __exclude_cannot_pay_blind_player(self, sb_pos, bb_pos, players):
    if players[sb_pos].stack < self.small_blind_amount:
      players[sb_pos].stack = 0
    if players[bb_pos].stack < self.small_blind_amount * 2:
      players[bb_pos].stack = 0

  def __exclude_no_money_player(self, players):
    no_money_players = [player for player in players if player.stack == 0]
    for player in no_money_players:
      player.pay_info.update_to_fold()

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

