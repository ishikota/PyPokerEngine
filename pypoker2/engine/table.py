from pypoker2.engine.card import Card
from pypoker2.engine.seats import Seats
from pypoker2.engine.deck import Deck

class Table:

  def __init__(self, cheat_deck=None):
    self.dealer_btn = 0
    self.seats = Seats()
    self.deck = cheat_deck if cheat_deck else Deck()
    self.__community_card = []

  def get_community_card(self):
    return self.__community_card[::]

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

  def shift_dealer_btn(self, exec_shit=True):
    dealer_pos = self.dealer_btn
    while True:
      dealer_pos = (dealer_pos + 1) % self.seats.size()
      if self.seats.players[dealer_pos].is_active(): break
    if exec_shit: self.dealer_btn = dealer_pos
    return dealer_pos

  def serialize(self):
    community_card = [card.to_id() for card in self.__community_card]
    return [
        self.dealer_btn, Seats.serialize(self.seats),
        Deck.serialize(self.deck), community_card
    ]

  @classmethod
  def deserialize(self, serial):
    deck = Deck.deserialize(serial[2])
    community_card = [Card.from_id(cid) for cid in serial[3]]
    table = self(cheat_deck=deck)
    table.dealer_btn = serial[0]
    table.seats = Seats.deserialize(serial[1])
    table.__community_card = community_card
    return table


  __exceed_card_size_msg = "Community card is already full"
