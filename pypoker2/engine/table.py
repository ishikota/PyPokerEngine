from pypoker2.engine.seats import Seats
from pypoker2.engine.deck import Deck

class Table:

  def __init__(self, cheat_deck=None):
    self.dealer_btn = 0
    self.seats = Seats()
    self.deck = cheat_deck if cheat_deck else Deck()
    self.__community_card = []

  def add_community_card(self, card):
    if len(self.__community_card) == 5:
      raise ValueError(self.__exceed_card_size_msg)
    self.__community_card.append(card)

  def reset(self):
    self.deck.restore()
    self.__community_card = []
    for player in self.seats.players:
      player.clear_holecard()
      player.clear_action_histories()
      player.clear_pay_info()

  def shift_dealer_btn(self):
    while True:
      self.dealer_btn = (self.dealer_btn + 1) % self.seats.size()
      if self.seats.players[self.dealer_btn].is_active(): break


  __exceed_card_size_msg = "Community card is already full"
