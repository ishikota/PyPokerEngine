from tests.base_unittest import BaseUnitTest
from pypokerengine.players.sample.simulation_player import PokerPlayer as SimulationPlayer
from pypokerengine.engine.card import Card

class SimulationPlayerTest(BaseUnitTest):

  def setUp(self):
    self.player = SimulationPlayer()

  def test_restore_round_state(self):
    hole_card, round_info, action_histories, restored_state = self.__setup_standard_round_state()

    hole_card = [Card(Card.HEART, 11), Card(Card.SPADE, 4)]
    community_card = []
    table = restored_state["table"]

    #self.eq(1, restored_state["round_count"])
    self.eq(0, restored_state["street"])
    self.eq(0, restored_state["next_player"])
    self.eq(round_info["dealer_btn"], table.dealer_btn)
    self.eq(community_card, table.get_community_card())
    # table.deck check
    self.eq(52-len(hole_card)-len(community_card), table.deck.size())
    for card in hole_card:
      self.false(card in table.deck.deck)
    # table.seats check
    serialized_players = [
        [u'player1', 'qziripusxnecumztkyfgot', 95, [19, 51], [{'action': 'SMALLBLIND', 'amount': 5, 'add_amount': 5, 'uuid': 'qziripusxnecumztkyfgot'}], [5, 0]],
        [u'player2', 'zjfvtucwhgjifzqpuhpghd', 90, [41, 14], [{'action': 'BIGBLIND', 'amount': 10, 'add_amount': 5, 'uuid': 'zjfvtucwhgjifzqpuhpghd'}], [10, 0]]
    ]
    restored_players = [player.serialize() for player in restored_state["table"].seats.players]
    for i in range(2):
      for col in [0,1,2,4,5]:
        self.eq(serialized_players[i][col], restored_players[i][col])

  def test_attach_hole_card_at_random(self):
    hole_card, _, _, restored_state = self.__setup_standard_round_state()
    table = restored_state["table"]
    self.player._PokerPlayer__attach_holecard_at_random(table.seats.players, hole_card, table.deck)

    hole_card = [Card(Card.HEART, 11), Card(Card.SPADE, 4)]
    for player in table.seats.players:
      if player.uuid == self.player.uuid:
        self.eq(hole_card, player.hole_card)
      else:
        self.eq(2, len(player.hole_card))
        for card in player.hole_card:
          self.false(card in table.deck.deck)
          self.false(card in hole_card)

  def test_attach_different_hole_card(self):
    hole_card, _, _, original_state = self.__setup_standard_round_state()
    # first time
    copy_state = self.player._PokerPlayer__deep_copy_state(original_state)
    table = copy_state["table"]
    self.player._PokerPlayer__attach_holecard_at_random(table.seats.players, hole_card, table.deck)
    first_time = [[str(c) for c in player.hole_card] for player in table.seats.players if player.uuid != self.player.uuid]
    # second time
    copy_state = self.player._PokerPlayer__deep_copy_state(original_state)
    table = copy_state["table"]
    self.player._PokerPlayer__attach_holecard_at_random(table.seats.players, hole_card, table.deck)
    second_time = [[str(c) for c in player.hole_card] for player in table.seats.players if player.uuid != self.player.uuid]
    self.neq(first_time, second_time)

  def __setup_standard_round_state(self):
    hole_card = ['HJ', 'S4']
    round_info = {
        'dealer_btn': 0,
        'street': 'preflop',
        'seats': [
          {'stack': 95, 'state': 'participating', 'name': u'player1', 'uuid': 'qziripusxnecumztkyfgot'},
          {'stack': 90, 'state': 'participating', 'name': u'player2', 'uuid': 'zjfvtucwhgjifzqpuhpghd'}
          ],
        'next_player': 0,
        'community_card': [],
        'pot': {'main': {'amount': 15}, 'side': []}
    }
    action_histories = {
        'action_histories': [
          {'action': 'SMALLBLIND', 'amount': 5, 'add_amount': 5, 'uuid': 'qziripusxnecumztkyfgot'},
          {'action': 'BIGBLIND', 'amount': 10, 'add_amount': 5, 'uuid': 'zjfvtucwhgjifzqpuhpghd'}]
        }

    self.player.set_uuid("qziripusxnecumztkyfgot")
    round_state = self.player._PokerPlayer__restore_round_state(hole_card, round_info, action_histories)
    return hole_card, round_info, action_histories, round_state

