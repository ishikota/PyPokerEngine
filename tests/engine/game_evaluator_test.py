from tests.base_unittest import BaseUnitTest
from mock import patch
import pypoker2.engine.hand_evaluator
from pypoker2.engine.player import Player
from pypoker2.engine.pay_info import PayInfo
from pypoker2.engine.table import Table
from pypoker2.engine.game_evaluator import GameEvaluator
from nose.tools import *

class GameEvaluatorTest(BaseUnitTest):

  def test_judge_without_allin(self):
    gen_player = lambda acc, _: acc + [self.__create_player_with_pay_info("", 5, PayInfo.PAY_TILL_END)]
    players = reduce(gen_player, range(3), [])
    table = self.__setup_table(players)
    mock_eval_hand_return = [0,1,0]*2
    with patch('pypoker2.engine.hand_evaluator.HandEvaluator.eval_hand', side_effect=mock_eval_hand_return):
      winner, prize_map = GameEvaluator.judge(table)
      self.eq(1, len(winner))
      self.true(players[1] in winner)
      self.eq(15, prize_map[1])

  def test_judge_without_allin_but_winner_folded(self):
    gen_player = lambda acc, _: acc + [self.__create_player_with_pay_info("", 5, PayInfo.PAY_TILL_END)]
    players = reduce(gen_player, range(3), [])
    players[1].pay_info.update_to_fold()
    table = self.__setup_table(players)
    mock_eval_hand_return = [0,0]*2
    with patch('pypoker2.engine.hand_evaluator.HandEvaluator.eval_hand', side_effect=mock_eval_hand_return):
      winner, prize_map = GameEvaluator.judge(table)
      self.eq(2, len(winner))
      self.eq(7, prize_map[0])
      self.eq(0, prize_map[1])
      self.eq(7, prize_map[2])

  """ B win (hand rank = B > C > A) """
  def test_judge_with_allin_when_allin_wins_case1(self):
    players = self.__setup_players_for_judge()
    table = self.__setup_table(players)
    mock_eval_hand_return = [0,2,1]*3
    with patch('pypoker2.engine.hand_evaluator.HandEvaluator.eval_hand', side_effect=mock_eval_hand_return):
      winner, prize_map = GameEvaluator.judge(table)
      self.eq(20, prize_map[0])
      self.eq(60, prize_map[1])
      self.eq(20, prize_map[2])

  """ B win (hand rank = B > A > C) """
  def test_judge_with_allin_when_allin_wins_case2(self):
    players = self.__setup_players_for_judge()
    table = self.__setup_table(players)
    mock_eval_hand_return = [1,2,0]*2 + [1,0] + [0]
    with patch('pypoker2.engine.hand_evaluator.HandEvaluator.eval_hand', side_effect=mock_eval_hand_return):
      winner, prize_map = GameEvaluator.judge(table)
      self.eq(40, prize_map[0])
      self.eq(60, prize_map[1])
      self.eq(0, prize_map[2])

  def test_judge_with_allin_when_allin_does_not_win(self):
    players = self.__setup_players_for_judge()
    table = self.__setup_table(players)
    mock_eval_hand_return = [2,1,0]*2 + [2,0] + [2]
    with patch('pypoker2.engine.hand_evaluator.HandEvaluator.eval_hand', side_effect=mock_eval_hand_return):
      winner, prize_map = GameEvaluator.judge(table)
      self.eq(100, prize_map[0])
      self.eq(0, prize_map[1])
      self.eq(0, prize_map[2])


  def test_find_a_winner(self):
    mock_eval_hand_return = [0, 1, 0]
    dummy_players = self.__setup_players()
    dummy_community = []
    with patch('pypoker2.engine.hand_evaluator.HandEvaluator.eval_hand', side_effect=mock_eval_hand_return):
      winner = GameEvaluator._GameEvaluator__find_winners_from(dummy_community, dummy_players)
      self.eq(1, len(winner))
      self.true(dummy_players[1] in winner)

  def test_find_winners(self):
    mock_eval_hand_return = [0, 1, 1]
    dummy_players = self.__setup_players()
    dummy_community = []
    with patch('pypoker2.engine.hand_evaluator.HandEvaluator.eval_hand', side_effect=mock_eval_hand_return):
      winner = GameEvaluator._GameEvaluator__find_winners_from(dummy_community, dummy_players)
      self.eq(2, len(winner))
      self.true(dummy_players[1] in winner)
      self.true(dummy_players[2] in winner)


  def __setup_table(self, players):
    table = Table()
    for player in players:
      table.seats.sitdown(player)
    return table

  def __setup_players(self):
    return reduce(lambda acc, _: acc + [Player("uuid", 100)], range(3), [])

  def __setup_players_for_judge(self):
    return [
        self.__create_player_with_pay_info("A", 50, PayInfo.PAY_TILL_END),
        self.__create_player_with_pay_info("B", 20, PayInfo.ALLIN),
        self.__create_player_with_pay_info("C", 30, PayInfo.ALLIN)
    ]

  def __create_player_with_pay_info(self, name, amount, status):
    player = Player("uuid", 100, name)
    player.pay_info.amount = amount
    player.pay_info.status = status
    return player

