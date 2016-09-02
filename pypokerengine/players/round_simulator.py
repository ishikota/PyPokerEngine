from pypokerengine.engine.round_manager import RoundManager
from pypokerengine.engine.message_builder import MessageBuilder
from pypokerengine.engine.table import Table

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


