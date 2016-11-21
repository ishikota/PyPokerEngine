from pypokerengine.engine.card import Card
from pypokerengine.engine.seats import Seats
from pypokerengine.engine.deck import Deck

class Table:

  def __init__(self, cheat_deck=None):
    self.dealer_btn = 0
    self._blind_pos = None
    self.seats = Seats()
    self.deck = cheat_deck if cheat_deck else Deck()
    self._community_card = []

  def set_blind_pos(self, sb_pos, bb_pos):
    self._blind_pos = [sb_pos, bb_pos]

  def sb_pos(self):
    if self._blind_pos is None: raise Exception("blind position is not yet set")
    return self._blind_pos[0]

  def bb_pos(self):
    if self._blind_pos is None: raise Exception("blind position is not yet set")
    return self._blind_pos[1]

  def get_community_card(self):
    return self._community_card[::]

  def add_community_card(self, card):
    if len(self._community_card) == 5:
      raise ValueError(self.__exceed_card_size_msg)
    self._community_card.append(card)

  def reset(self):
    self.deck.restore()
    self._community_card = []
    for player in self.seats.players:
      player.clear_holecard()
      player.clear_action_histories()
      player.clear_pay_info()

  def shift_dealer_btn(self):
    self.dealer_btn = self.next_active_player_pos(self.dealer_btn)

  def next_active_player_pos(self, start_pos):
    return self.__find_entitled_player_pos(start_pos, lambda player: player.is_active() and player.stack != 0)

  def next_ask_waiting_player_pos(self, start_pos):
    return self.__find_entitled_player_pos(start_pos, lambda player: player.is_waiting_ask())

  def serialize(self):
    community_card = [card.to_id() for card in self._community_card]
    return [
        self.dealer_btn, Seats.serialize(self.seats),
        Deck.serialize(self.deck), community_card, self._blind_pos
    ]

  @classmethod
  def deserialize(self, serial):
    deck = Deck.deserialize(serial[2])
    community_card = [Card.from_id(cid) for cid in serial[3]]
    table = self(cheat_deck=deck)
    table.dealer_btn = serial[0]
    table.seats = Seats.deserialize(serial[1])
    table._community_card = community_card
    table._blind_pos = serial[4]
    return table

  def __find_entitled_player_pos(self, start_pos, check_method):
    players = self.seats.players
    search_targets = players + players
    search_targets = search_targets[start_pos+1:start_pos+len(players)+1]
    assert(len(search_targets) == len(players))
    match_player = next((player for player in search_targets if check_method(player)), -1)
    return self._player_not_found if match_player == -1 else players.index(match_player)

  _player_not_found = "not_found"

  __exceed_card_size_msg = "Community card is already full"
