from functools import reduce

from pypokerengine.engine.table import Table
from pypokerengine.engine.player import Player
from pypokerengine.engine.pay_info import PayInfo
from pypokerengine.engine.poker_constants import PokerConstants as Const
from pypokerengine.engine.action_checker import ActionChecker
from pypokerengine.engine.game_evaluator import GameEvaluator
from pypokerengine.engine.message_builder import MessageBuilder

class RoundManager:

  @classmethod
  def start_new_round(self, round_count, small_blind_amount, ante_amount, table):
    _state = self.__gen_initial_state(round_count, small_blind_amount, table)
    state = self.__deep_copy_state(_state)
    table = state["table"]

    table.deck.shuffle()
    self.__correct_ante(ante_amount, table.seats.players)
    self.__correct_blind(small_blind_amount, table)
    self.__deal_holecard(table.deck, table.seats.players)
    start_msg = self.__round_start_message(round_count, table)
    state, street_msgs = self.__start_street(state)
    return state, start_msg + street_msgs

  @classmethod
  def apply_action(self, original_state, action, bet_amount):
    state = self.__deep_copy_state(original_state)
    state = self.__update_state_by_action(state, action, bet_amount)
    update_msg = self.__update_message(state, action, bet_amount)
    if self.__is_everyone_agreed(state):
      [player.save_street_action_histories(state["street"]) for player in state["table"].seats.players]
      state["street"] += 1
      state, street_msgs = self.__start_street(state)
      return state, [update_msg] + street_msgs
    else:
      state["next_player"] = state["table"].next_ask_waiting_player_pos(state["next_player"])
      next_player_pos = state["next_player"]
      next_player = state["table"].seats.players[next_player_pos]
      ask_message = (next_player.uuid, MessageBuilder.build_ask_message(next_player_pos, state))
      return state, [update_msg, ask_message]

  @classmethod
  def __correct_ante(self, ante_amount, players):
    if ante_amount == 0: return
    active_players = [player for player in players if player.is_active()]
    for player in active_players:
      player.collect_bet(ante_amount)
      player.pay_info.update_by_pay(ante_amount)
      player.add_action_history(Const.Action.ANTE, ante_amount)

  @classmethod
  def __correct_blind(self, sb_amount, table):
    self.__blind_transaction(table.seats.players[table.sb_pos()], True, sb_amount)
    self.__blind_transaction(table.seats.players[table.bb_pos()], False, sb_amount)

  @classmethod
  def __blind_transaction(self, player, small_blind, sb_amount):
    action = Const.Action.SMALL_BLIND if small_blind else Const.Action.BIG_BLIND
    blind_amount = sb_amount if small_blind else sb_amount*2
    player.collect_bet(blind_amount)
    player.add_action_history(action, sb_amount=sb_amount)
    player.pay_info.update_by_pay(blind_amount)

  @classmethod
  def __deal_holecard(self, deck, players):
    for player in players:
      player.add_holecard(deck.draw_cards(2))

  @classmethod
  def __start_street(self, state):
    next_player_pos = state["table"].next_ask_waiting_player_pos(state["table"].sb_pos()-1)
    state["next_player"] = next_player_pos
    street = state["street"]
    if street == Const.Street.PREFLOP:
      return self.__preflop(state)
    elif street == Const.Street.FLOP:
      return self.__flop(state)
    elif street == Const.Street.TURN:
      return self.__turn(state)
    elif street == Const.Street.RIVER:
      return self.__river(state)
    elif street == Const.Street.SHOWDOWN:
      return self.__showdown(state)
    else:
      raise ValueError("Street is already finished [street = %d]" % street)

  @classmethod
  def __preflop(self, state):
    for i in range(2):
      state["next_player"] = state["table"].next_ask_waiting_player_pos(state["next_player"])
    return self.__forward_street(state)

  @classmethod
  def __flop(self, state):
    for card in state["table"].deck.draw_cards(3):
      state["table"].add_community_card(card)
    return self.__forward_street(state)

  @classmethod
  def __turn(self, state):
    state["table"].add_community_card(state["table"].deck.draw_card())
    return self.__forward_street(state)

  @classmethod
  def __river(self, state):
    state["table"].add_community_card(state["table"].deck.draw_card())
    return self.__forward_street(state)

  @classmethod
  def __showdown(self, state):
    winners, hand_info, prize_map = GameEvaluator.judge(state["table"])
    self.__prize_to_winners(state["table"].seats.players, prize_map)
    result_message = MessageBuilder.build_round_result_message(state["round_count"], winners, hand_info, state)
    state["table"].reset()
    state["street"] += 1
    return state, [(-1, result_message)]

  @classmethod
  def __prize_to_winners(self, players, prize_map):
    for idx, prize in prize_map.items():
      players[idx].append_chip(prize)

  @classmethod
  def __round_start_message(self, round_count, table):
    players = table.seats.players
    gen_msg = lambda idx: (players[idx].uuid, MessageBuilder.build_round_start_message(round_count, idx, table.seats))
    return reduce(lambda acc, idx: acc + [gen_msg(idx)], range(len(players)), [])

  @classmethod
  def __forward_street(self, state):
    table = state["table"]
    street_start_msg = [(-1, MessageBuilder.build_street_start_message(state))]
    if table.seats.count_active_players() == 1: street_start_msg = []
    if table.seats.count_ask_wait_players() <= 1:
      state["street"] += 1
      state, messages = self.__start_street(state)
      return state, street_start_msg + messages
    else:
      next_player_pos = state["next_player"]
      next_player = table.seats.players[next_player_pos]
      ask_message = [(next_player.uuid, MessageBuilder.build_ask_message(next_player_pos, state))]
      return state, street_start_msg + ask_message

  @classmethod
  def __update_state_by_action(self, state, action, bet_amount):
    table = state["table"]
    action, bet_amount = ActionChecker.correct_action(\
        table.seats.players, state["next_player"], state["small_blind_amount"], action, bet_amount)
    next_player = table.seats.players[state["next_player"]]
    if ActionChecker.is_allin(next_player, action, bet_amount):
      next_player.pay_info.update_to_allin()
    return self.__accept_action(state, action, bet_amount)

  @classmethod
  def __accept_action(self, state, action, bet_amount):
    player = state["table"].seats.players[state["next_player"]]
    if action == 'call':
      self.__chip_transaction(player, bet_amount)
      player.add_action_history(Const.Action.CALL, bet_amount)
    elif action == 'raise':
      self.__chip_transaction(player, bet_amount)
      add_amount = bet_amount - ActionChecker.agree_amount(state["table"].seats.players)
      player.add_action_history(Const.Action.RAISE, bet_amount, add_amount)
    elif action == 'fold':
      player.add_action_history(Const.Action.FOLD)
      player.pay_info.update_to_fold()
    else:
      raise ValueError("Unexpected action %s received" % action)
    return state

  @classmethod
  def __chip_transaction(self, player, bet_amount):
    need_amount = ActionChecker.need_amount_for_action(player, bet_amount)
    player.collect_bet(need_amount)
    player.pay_info.update_by_pay(need_amount)

  @classmethod
  def __update_message(self, state, action, bet_amount):
    return (-1, MessageBuilder.build_game_update_message(
      state["next_player"], action, bet_amount, state))

  @classmethod
  def __is_everyone_agreed(self, state):
    self.__agree_logic_bug_catch(state)
    players = state["table"].seats.players
    next_player_pos = state["table"].next_ask_waiting_player_pos(state["next_player"])
    next_player = players[next_player_pos] if next_player_pos != "not_found" else None
    max_pay = max([p.paid_sum() for p in players])
    everyone_agreed = len(players) == len([p for p in players if self.__is_agreed(max_pay, p)])
    lonely_player = state["table"].seats.count_active_players() == 1
    no_need_to_ask = state["table"].seats.count_ask_wait_players() == 1 and\
            next_player and next_player.is_waiting_ask() and next_player.paid_sum() == max_pay
    return everyone_agreed or lonely_player or no_need_to_ask

  @classmethod
  def __agree_logic_bug_catch(self, state):
    if state["table"].seats.count_active_players() == 0:
      raise "[__is_everyone_agreed] no-active-players!!"

  @classmethod
  def __is_agreed(self, max_pay, player):
    # BigBlind should be asked action at least once
    is_preflop = player.round_action_histories[0] == None
    bb_ask_once = len(player.action_histories)==1 \
            and player.action_histories[0]["action"] == Player.ACTION_BIG_BLIND
    bb_ask_check = not is_preflop or not bb_ask_once
    return (bb_ask_check and player.paid_sum() == max_pay and len(player.action_histories) != 0)\
        or player.pay_info.status in [PayInfo.FOLDED, PayInfo.ALLIN]

  @classmethod
  def __gen_initial_state(self, round_count, small_blind_amount, table):
    return {
        "round_count": round_count,
        "small_blind_amount": small_blind_amount,
        "street": Const.Street.PREFLOP,
        "next_player": table.next_ask_waiting_player_pos(table.bb_pos()),
        "table": table
    }

  @classmethod
  def __deep_copy_state(self, state):
    table_deepcopy = Table.deserialize(state["table"].serialize())
    return {
        "round_count": state["round_count"],
        "small_blind_amount": state["small_blind_amount"],
        "street": state["street"],
        "next_player": state["next_player"],
        "table": table_deepcopy
        }
