from pypokerengine.engine.pay_info import PayInfo
from pypokerengine.engine.card import Card
from pypokerengine.engine.poker_constants import PokerConstants as Const


class Player:

  ACTION_FOLD_STR = "FOLD"
  ACTION_CALL_STR = "CALL"
  ACTION_RAISE_STR = "RAISE"
  ACTION_SMALL_BLIND = "SMALLBLIND"
  ACTION_BIG_BLIND = "BIGBLIND"
  ACTION_ANTE = "ANTE"

  def __init__(self, uuid, initial_stack, name="No Name"):
    self.name = name
    self.uuid = uuid
    self.hole_card = []
    self.stack = initial_stack
    self.round_action_histories = self.__init_round_action_histories()
    self.action_histories = []
    self.pay_info = PayInfo()

  def add_holecard(self, cards):
    if len(self.hole_card) != 0:
      raise ValueError(self.__dup_hole_msg)
    if len(cards) != 2:
      raise ValueError(self.__wrong_num_hole_msg % (len(cards)))
    if not all([isinstance(card, Card) for card in cards]):
      raise ValueError(self.__wrong_type_hole_msg)
    self.hole_card = cards

  def clear_holecard(self):
    self.hole_card = []

  def append_chip(self, amount):
    self.stack += amount

  def collect_bet(self, amount):
    if self.stack < amount:
      raise ValueError(self.__collect_err_msg % (amount, self.stack))
    self.stack -= amount

  def is_active(self):
    return self.pay_info.status != PayInfo.FOLDED

  def is_waiting_ask(self):
    return self.pay_info.status == PayInfo.PAY_TILL_END

  def add_action_history(self, kind, chip_amount=None, add_amount=None, sb_amount=None):
    history = None
    if kind == Const.Action.FOLD:
      history = self.__fold_history()
    elif kind == Const.Action.CALL:
      history = self.__call_history(chip_amount)
    elif kind == Const.Action.RAISE:
      history = self.__raise_history(chip_amount, add_amount)
    elif kind == Const.Action.SMALL_BLIND:
      history = self.__blind_history(True, sb_amount)
    elif kind == Const.Action.BIG_BLIND:
      history = self.__blind_history(False, sb_amount)
    elif kind == Const.Action.ANTE:
      history = self.__ante_history(chip_amount)
    else:
      raise "UnKnown action history is added (kind = %s)" % kind
    history = self.__add_uuid_on_history(history)
    self.action_histories.append(history)

  def save_street_action_histories(self, street_flg):
    self.round_action_histories[street_flg] = self.action_histories
    self.action_histories = []

  def clear_action_histories(self):
    self.round_action_histories = self.__init_round_action_histories()
    self.action_histories = []

  def clear_pay_info(self):
    self.pay_info = PayInfo()

  def paid_sum(self):
    pay_history = [h for h in self.action_histories if h["action"] not in ["FOLD", "ANTE"]]
    last_pay_history = pay_history[-1] if len(pay_history)!=0 else None
    return last_pay_history["amount"] if last_pay_history else 0

  def serialize(self):
    hole = [card.to_id() for card in self.hole_card]
    return [
        self.name, self.uuid, self.stack, hole,\
            self.action_histories[::], self.pay_info.serialize(), self.round_action_histories[::]
    ]

  @classmethod
  def deserialize(self, serial):
    hole = [Card.from_id(cid) for cid in serial[3]]
    player = self(serial[1], serial[2], serial[0])
    if len(hole)!=0: player.add_holecard(hole)
    player.action_histories = serial[4]
    player.pay_info = PayInfo.deserialize(serial[5])
    player.round_action_histories = serial[6]
    return player

  """ private """

  __dup_hole_msg = "Hole card is already set"
  __wrong_num_hole_msg = "You passed  %d hole cards"
  __wrong_type_hole_msg = "You passed not Card object as hole card"
  __collect_err_msg = "Failed to collect %d chips. Because he has only %d chips"

  def __init_round_action_histories(self):
    return [None for _ in range(4)]  # 4 == len(["preflop", "flop", "turn", "river"])

  def __fold_history(self):
    return { "action" : self.ACTION_FOLD_STR }

  def __call_history(self, bet_amount):
    return {
        "action" : self.ACTION_CALL_STR,
        "amount" : bet_amount,
        "paid" : bet_amount - self.paid_sum()
    }

  def __raise_history(self, bet_amount, add_amount):
    return {
        "action" : self.ACTION_RAISE_STR,
        "amount" : bet_amount,
        "paid" : bet_amount - self.paid_sum(),
        "add_amount" : add_amount
        }

  def __blind_history(self, small_blind, sb_amount):
    assert(sb_amount is not None)
    action = self.ACTION_SMALL_BLIND if small_blind else self.ACTION_BIG_BLIND
    amount = sb_amount if small_blind else sb_amount*2
    add_amount = sb_amount
    return {
        "action" : action,
        "amount" : amount,
        "add_amount" : add_amount
        }

  def __ante_history(self, pay_amount):
    assert(pay_amount > 0)
    return {
        "action" : self.ACTION_ANTE,
        "amount" : pay_amount
        }

  def __add_uuid_on_history(self, history):
    history["uuid"] = self.uuid
    return history

