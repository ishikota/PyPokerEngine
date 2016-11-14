from tests.base_unittest import BaseUnitTest
from pypokerengine.engine.player import Player
from pypokerengine.engine.seats import Seats

class SeatsTest(BaseUnitTest):

  def setUp(self):
    self.seats = Seats()
    self.p1 = Player("uuid1", 100)
    self.p2 = Player("uuid2", 100)
    self.p3 = Player("uuid3", 100)

  def test_sitdown(self):
    self.seats.sitdown(self.p1)
    self.true(self.p1 in self.seats.players)

  def test_size(self):
    self.__sitdown_players()
    self.eq(3, len(self.seats.players))

  def test_count_active_players(self):
    self.__setup_pay_status()
    self.__sitdown_players()
    self.eq(2, self.seats.count_active_players())

  def test_acount_ask_wait_players(self):
    self.__setup_pay_status()
    self.__sitdown_players()
    self.eq(1, self.seats.count_ask_wait_players())

  def test_serialization(self):
    self.__sitdown_players()
    serial = self.seats.serialize()
    restored = Seats.deserialize(serial)
    for i in range(len(self.seats.players)):
      self.eq(Player.serialize(self.seats.players[i]), Player.serialize(restored.players[i]))

  def __setup_pay_status(self):
    self.p1.pay_info.update_by_pay(10)
    self.p2.pay_info.update_to_fold()
    self.p3.pay_info.update_to_allin()

  def __sitdown_players(self):
    for player in [self.p1, self.p2, self.p3]:
      self.seats.sitdown(player)

