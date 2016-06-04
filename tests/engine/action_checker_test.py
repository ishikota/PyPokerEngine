from tests.base_unittest import BaseUnitTest
from pypoker2.engine.player import Player
from pypoker2.engine.action import Action
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

  def test_too_small_raise(self):
    players = self.__setup_clean_players()
    self.true(self.checker.is_illegal(players, 0, 'raise', 4))

  def test_legal_raise(self):
    players = self.__setup_clean_players()
    self.false(self.checker.is_illegal(players, 0, 'raise', 5))

  """ the case when agree amount = $10, minimum bet = $15"""
  def test__fold(self):
    players = self.__setup_blind_players()
    self.false(self.checker.is_illegal(players, 0, 'fold'))

  def test__call(self):
    players = self.__setup_blind_players()
    self.true(self.checker.is_illegal(players, 0, 'call', 9))
    self.false(self.checker.is_illegal(players, 0, 'call', 10))
    self.true(self.checker.is_illegal(players, 0, 'call', 11))
    self.eq(5, self.checker.need_amount_for_action(players[0], 10))
    self.eq(0, self.checker.need_amount_for_action(players[1], 10))

  def test__raise(self):
    players = self.__setup_blind_players()
    self.true(self.checker.is_illegal(players, 0, 'raise', 14))
    self.false(self.checker.is_illegal(players, 0, 'raise', 15))
    self.false(self.checker.is_illegal(players, 0, 'raise', 16))
    self.eq(10, self.checker.need_amount_for_action(players[0], 15))
    self.eq(5, self.checker.need_amount_for_action(players[1], 15))


  def __setup_clean_players(self):
    return [Player("uuid", 100) for  _ in range(2)]

  def __setup_blind_players(self):
    return [self.__create_blind_player(flg) for flg in [True, False]]

  def __create_blind_player(self, small_blind=True):
    name = "sb" if small_blind else "bb"
    blind = 5 if small_blind else 10
    player = Player("uuid", 100, name=name)
    player.add_action_history(Action.RAISE, blind, 5)
    player.collect_bet(blind)
    player.pay_info.update_by_pay(blind)
    return player

