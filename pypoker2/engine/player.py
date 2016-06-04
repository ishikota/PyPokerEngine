from pypoker2.engine.pay_info import PayInfo
from pypoker2.engine.card import Card

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


  """ private """

  __dup_hole_msg = "Hole card is already set"
  __wrong_num_hole_msg = "You passed  %d hole cards"
  __wrong_type_hole_msg = "You passed not Card object as hole card"
  __collect_err_msg = "Failed to collect %d chips. Because he has only %d chips"

