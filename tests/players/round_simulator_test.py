from tests.base_unittest import BaseUnitTest
from pypokerengine.players.round_simulator import RoundSimualtor
from pypokerengine.players.sample.fold_man import PokerPlayer as FoldMan
from pypokerengine.engine.round_manager import RoundManager
from pypokerengine.engine.player import Player
from pypokerengine.engine.deck import Deck
from pypokerengine.engine.table import Table

class RoundSimulatorTest(BaseUnitTest):

  def setUp(self):
    self.table = self.__setup_table()
    self.simualtor = RoundSimualtor()
    for player in self.table.seats.players:
      self.simualtor.register_algorithm(player.uuid, FoldMan())

  def test_simulation(self):
    round_count, small_blind = 1, 5
    initial_state, _ = RoundManager.start_new_round(round_count, small_blind, self.table)
    for i in range(2):
      action = self.simualtor.gen_action_info(RoundSimualtor.CALL, 10)
      round_result = self.simualtor.start_simulation(initial_state, action)
      players = round_result["seats"]
      self.eq(95, players[0]["stack"])
      self.eq(90, players[1]["stack"])
      self.eq(115, players[2]["stack"])


  def __setup_table(self):
    players = [Player("uuid%d" % i, 100) for i in range(3)]
    deck = Deck(cheat=True, cheat_card_ids=range(1,53))
    table = Table(cheat_deck=deck)
    for player in players: table.seats.sitdown(player)
    return table

