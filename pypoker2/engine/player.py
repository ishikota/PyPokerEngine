from pypoker2.engine.pay_info import PayInfo
from pypoker2.engine.card import Card
from pypoker2.engine.action import Action


class Player:

  def __init__(self, uuid, initial_stack, name="No Name"):
    self.name = name
    self.uuid = uuid
    self.hole_card = []
    self.stack = initial_stack
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

  def add_action_history(self, kind, chip_amount=None, add_amount=None):
    if kind == Action.FOLD:
      self.action_histories.append(self.__fold_history())
    elif kind == Action.CALL:
      self.action_histories.append(self.__call_history(chip_amount))
    elif kind == Action.RAISE:
      self.action_histories.append(self.__raise_history(chip_amount, add_amount))

  def clear_action_histories(self):
    self.action_histories = []

  def clear_pay_info(self):
    self.pay_info = PayInfo()

  """ private """

  __dup_hole_msg = "Hole card is already set"
  __wrong_num_hole_msg = "You passed  %d hole cards"
  __wrong_type_hole_msg = "You passed not Card object as hole card"
  __collect_err_msg = "Failed to collect %d chips. Because he has only %d chips"

  def __fold_history(self):
    return { "action" : "FOLD" }

  def __call_history(self, bet_amount):
    return {
        "action" : "CALL",
        "amount" : bet_amount,
        "paid" : bet_amount - self.__paid_sum()
    }

  def __raise_history(self, bet_amount, add_amount):
    return {
        "action" : "RAISE",
        "amount" : bet_amount,
        "paid" : bet_amount - self.__paid_sum(),
        "add_amount" : add_amount
        }

  def __paid_sum(self):
    pay_history = [h for h in self.action_histories if h["action"] != "FOLD"]
    last_pay_history = pay_history[-1] if len(pay_history)!=0 else None
    return last_pay_history["amount"] if last_pay_history else 0

