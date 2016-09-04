from pypokerengine.engine.pay_info import PayInfo
from pypokerengine.engine.card import Card
from pypokerengine.engine.poker_constants import PokerConstants as Const


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
    history = None
    if kind == Const.Action.FOLD:
      history = self.__fold_history()
    elif kind == Const.Action.CALL:
      history = self.__call_history(chip_amount)
    elif kind == Const.Action.RAISE:
      history = self.__raise_history(chip_amount, add_amount)
    elif kind == Const.Action.SMALL_BLIND:
      history = self.__blind_history(small_blind=True)
    elif kind == Const.Action.BIG_BLIND:
      history = self.__blind_history(small_blind=False)
    else:
      raise "UnKnown action history is added (kind = %s)" % kind
    history = self.__add_uuid_on_history(history)
    self.action_histories.append(history)

  def clear_action_histories(self):
    self.action_histories = []

  def clear_pay_info(self):
    self.pay_info = PayInfo()

  def paid_sum(self):
    pay_history = [h for h in self.action_histories if h["action"] != "FOLD"]
    last_pay_history = pay_history[-1] if len(pay_history)!=0 else None
    return last_pay_history["amount"] if last_pay_history else 0

  def serialize(self):
    hole = [card.to_id() for card in self.hole_card]
    return [
        self.name, self.uuid, self.stack, hole,\
            self.action_histories[::], self.pay_info.serialize()
    ]

  @classmethod
  def deserialize(self, serial):
    hole = [Card.from_id(cid) for cid in serial[3]]
    player = self(serial[1], serial[2], serial[0])
    if len(hole)!=0: player.add_holecard(hole)
    player.action_histories = serial[4]
    player.pay_info = PayInfo.deserialize(serial[5])
    return player

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
        "paid" : bet_amount - self.paid_sum()
    }

  def __raise_history(self, bet_amount, add_amount):
    return {
        "action" : "RAISE",
        "amount" : bet_amount,
        "paid" : bet_amount - self.paid_sum(),
        "add_amount" : add_amount
        }

  # TODO read blind amount from config
  def __blind_history(self, small_blind):
    action = "SMALLBLIND" if small_blind else "BIGBLIND"
    amount = 5 if small_blind else 10
    add_amount = 5
    return {
        "action" : action,
        "amount" : amount,
        "add_amount" : add_amount
        }

  def __add_uuid_on_history(self, history):
    history["uuid"] = self.uuid
    return history

