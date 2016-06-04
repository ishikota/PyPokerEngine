from tests.base_unittest import BaseUnitTest
from pypoker2.engine.player import Player
from pypoker2.engine.action_checker import ActionChecker

class ActionCheckerTest(BaseUnitTest):

  def setUp(self):
    self.checker = ActionChecker()

  """ the case when no action is done before """
  def test_check(self):
    players = self.__setup_clean_players()
    self.false(self.checker.is_illegal(players, 0, 'call', 0))
    self.eq(0, self.checker.need_amount_for_action(players[0], 0))
    self.eq(0, self.checker.need_amount_for_action(players[1], 0))

  def test_call(self):
    players = self.__setup_clean_players()
    self.true(self.checker.is_illegal(players, 0, 'call', 10))

  def __setup_clean_players(self):
    return [Player("uuid", 100) for  _ in range(2)]

