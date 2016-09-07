from pypokerengine.players.base_poker_player import BasePokerPlayer
from pypokerengine.players.console_writer import ConsoleWriter

class PokerPlayer(BasePokerPlayer):

  def __init__(self, input_receiver=None):
    self.input_receiver = input_receiver if input_receiver else self.__gen_raw_input_wrapper()
    self.writer = ConsoleWriter(self)

  def declare_action(self, hole_card, valid_actions, round_state, action_histories):
    self.writer.write_declare_action(hole_card, valid_actions, round_state, action_histories)
    action, amount = self.__receive_action_from_console(valid_actions)
    return action, amount

  def receive_game_start_message(self, game_info):
    self.writer.write_game_start_message(game_info)
    self.__wait_until_input()

  def receive_round_start_message(self, round_count, hole_card, seats):
    self.writer.write_round_start_message(round_count, hole_card, seats)
    self.__wait_until_input()

  def receive_street_start_message(self, street, round_state):
    self.writer.write_street_start_message(street, round_state)
    self.__wait_until_input()

  def receive_game_update_message(self, action, round_state, action_histories):
    self.writer.write_game_update_message(action, round_state, action_histories)
    self.__wait_until_input()

  def receive_round_result_message(self, winners, hand_info, round_state):
    self.writer.write_round_result_message(winners, hand_info, round_state)
    self.__wait_until_input()

  def receive_game_result_message(self, seats):
    pass

  def __wait_until_input(self):
    raw_input("Enter some key to continue ...")

  def __gen_raw_input_wrapper(self):
    return lambda msg: raw_input(msg)

  def __receive_action_from_console(self, valid_actions):
    flg = self.input_receiver('Enter f(fold), c(call), r(raise).\n >> ')
    if flg in self.__gen_valid_flg(valid_actions):
      if flg == 'f':
        return valid_actions[0]['action'], valid_actions[0]['amount']
      elif flg == 'c':
        return valid_actions[1]['action'], valid_actions[1]['amount']
      elif flg == 'r':
        valid_amounts = valid_actions[2]['amount']
        raise_amount = self.__receive_raise_amount_from_console(valid_amounts['min'], valid_amounts['max'])
        return valid_actions[2]['action'], raise_amount
    else:
      return self.__receive_action_from_console(valid_actions)

  def __gen_valid_flg(self, valid_actions):
    flgs = ['f', 'c']
    is_raise_possible = valid_actions[2]['amount']['min'] != -1
    if is_raise_possible:
      flgs.append('r')
    return flgs

  def __receive_raise_amount_from_console(self, min_amount, max_amount):
    raw_amount = self.input_receiver("valid raise range = [%d, %d]" % (min_amount, max_amount))
    try:
      amount = int(raw_amount)
      if min_amount <= amount and amount <= max_amount:
        return amount
      else:
        print "Invalid raise amount %d. Try again."
        return self.__receive_raise_amount_from_console(min_amount, max_amount)
    except:
      print "Invalid input received. Try again."
      return self.__receive_raise_amount_from_console(min_amount, max_amount)

