from tests.base_unittest import BaseUnitTest
from mock import patch
from pypoker2.engine.round_manager import RoundManager
from pypoker2.engine.poker_constants import PokerConstants as Const
from pypoker2.engine.player import Player
from pypoker2.engine.card import Card
from pypoker2.engine.deck import Deck
from pypoker2.engine.table import Table

class RoundManagerTest(BaseUnitTest):

  def setUp(self):
    pass

  def test_collect_blind(self):
    state, _ = self.__start_round()
    players = state["table"].seats.players
    sb_amount = 5
    self.eq(100-sb_amount, players[0].stack)
    self.eq(100-sb_amount*2, players[1].stack)
    self.eq("SMALLBLIND", players[0].action_histories[-1]["action"])
    self.eq("BIGBLIND", players[1].action_histories[-1]["action"])
    self.eq(sb_amount, players[0].pay_info.amount)
    self.eq(sb_amount*2, players[1].pay_info.amount)

  def test_deal_holecard(self):
    state, _ = self.__start_round()
    players = state["table"].seats.players
    self.eq([Card.from_id(1), Card.from_id(2)], players[0].hole_card)
    self.eq([Card.from_id(3), Card.from_id(4)], players[1].hole_card)

  def test_message_after_start_round(self):
    with patch('pypoker2.engine.message_builder.MessageBuilder.build_round_start_message', return_value="hoge"),\
         patch('pypoker2.engine.message_builder.MessageBuilder.build_street_start_message', return_value="fuga"),\
         patch('pypoker2.engine.message_builder.MessageBuilder.build_ask_message', return_value="bar"):
      _, msgs = self.__start_round()
      self.eq(("uuid0", "hoge"), msgs[0])
      self.eq(("uuid1", "hoge"), msgs[1])
      self.eq(("uuid2", "hoge"),  msgs[2])
      self.eq((-1, "fuga"), msgs[3])
      self.eq(("uuid2", "bar"), msgs[4])

  def test_state_after_start_round(self):
    state, msgs = self.__start_round()
    self.eq(2, state["next_player"])
    self.eq(1, state["agree_num"])

  def test_message_after_apply_action(self):
    with patch('pypoker2.engine.message_builder.MessageBuilder.build_round_start_message', return_value="hoge"),\
         patch('pypoker2.engine.message_builder.MessageBuilder.build_street_start_message', return_value="fuga"),\
         patch('pypoker2.engine.message_builder.MessageBuilder.build_ask_message', return_value="bar"),\
         patch('pypoker2.engine.message_builder.MessageBuilder.build_game_update_message', return_value="boo"):
      state, _ = self.__start_round()
      _, msgs  = RoundManager.apply_action(state, "call", 10)
      self.eq((-1, "boo"), msgs[0])
      self.eq(("uuid0", "bar"), msgs[1])

  def test_state_after_apply_call(self):
    state, _ = self.__start_round()
    state, _ = RoundManager.apply_action(state, "call", 10)
    self.eq(0, state["next_player"])
    self.eq(2, state["agree_num"])

  def test_state_after_apply_raise(self):
    state, _ = self.__start_round()
    state, _ = RoundManager.apply_action(state, "raise", 15)
    self.eq(0, state["next_player"])
    self.eq(1, state["agree_num"])

  def test_message_after_forward_to_flop(self):
    with patch('pypoker2.engine.message_builder.MessageBuilder.build_street_start_message', return_value="fuga"),\
         patch('pypoker2.engine.message_builder.MessageBuilder.build_ask_message', return_value="bar"),\
         patch('pypoker2.engine.message_builder.MessageBuilder.build_game_update_message', return_value="boo"):
      state, _ = self.__start_round()
      state, _ = RoundManager.apply_action(state, "fold", 0)
      _, msgs  = RoundManager.apply_action(state, "call", 10)

      self.eq((-1, "boo"), msgs[0])
      self.eq((-1, "fuga"), msgs[1])
      self.eq(("uuid0", "bar"), msgs[2])

  def test_state_after_forward_to_flop(self):
    state, _ = self.__start_round()
    state, _ = RoundManager.apply_action(state, "fold", 0)
    state, _ = RoundManager.apply_action(state, "call", 10)

    self.eq(Const.Street.FLOP, state["street"])
    self.eq(0, state["next_player"])
    self.eq(0, state["agree_num"])
    self.eq([Card.from_id(cid) for cid in range(7,10)], state["table"].get_community_card())

  def test_state_after_forward_to_turn(self):
    state, _ = self.__start_round()
    state, _ = RoundManager.apply_action(state, "fold", 0)
    state, _ = RoundManager.apply_action(state, "call", 10)
    state, _ = RoundManager.apply_action(state, "call", 0)
    state, msgs = RoundManager.apply_action(state, "call", 0)

    self.eq(Const.Street.TURN, state["street"])
    self.eq([Card.from_id(cid) for cid in range(7,11)], state["table"].get_community_card())
    self.eq(3, len(msgs))

  def test_state_after_forward_to_river(self):
    state, _ = self.__start_round()
    state, _ = RoundManager.apply_action(state, "fold", 0)
    state, _ = RoundManager.apply_action(state, "call", 10)
    state, _ = RoundManager.apply_action(state, "call", 0)
    state, _ = RoundManager.apply_action(state, "call", 0)
    state, _ = RoundManager.apply_action(state, "call", 0)
    state, msgs = RoundManager.apply_action(state, "call", 0)

    self.eq(Const.Street.RIVER, state["street"])
    self.eq([Card.from_id(cid) for cid in range(7,12)], state["table"].get_community_card())
    self.eq(3, len(msgs))

  def test_state_after_showdown(self):
    mock_return = [1,0]*2
    with patch('pypoker2.engine.hand_evaluator.HandEvaluator.eval_hand', side_effect=mock_return),\
         patch('pypoker2.engine.message_builder.MessageBuilder.build_round_result_message', return_value="bogo"):
      state, _ = self.__start_round()
      state, _ = RoundManager.apply_action(state, "fold", 0)
      state, _ = RoundManager.apply_action(state, "call", 10)
      state, _ = RoundManager.apply_action(state, "call", 0)
      state, _ = RoundManager.apply_action(state, "call", 0)
      state, _ = RoundManager.apply_action(state, "call", 0)
      state, _ = RoundManager.apply_action(state, "call", 0)
      state, _ = RoundManager.apply_action(state, "call", 0)
      state, _ = RoundManager.apply_action(state, "call", 0)

      self.eq(Const.Street.FINISHED, state["street"])
      self.eq(110, state["table"].seats.players[0].stack)
      self.eq( 90, state["table"].seats.players[1].stack)
      self.eq(100, state["table"].seats.players[2].stack)

  def test_message_after_showdown(self):
    mock_return = [1,0]*2
    with patch('pypoker2.engine.hand_evaluator.HandEvaluator.eval_hand', side_effect=mock_return),\
         patch('pypoker2.engine.message_builder.MessageBuilder.build_game_update_message', return_value="boo"),\
         patch('pypoker2.engine.message_builder.MessageBuilder.build_round_result_message', return_value="foo"):
      state, _ = self.__start_round()
      state, _ = RoundManager.apply_action(state, "fold", 0)
      state, _ = RoundManager.apply_action(state, "call", 10)
      state, _ = RoundManager.apply_action(state, "call", 0)
      state, _ = RoundManager.apply_action(state, "call", 0)
      state, _ = RoundManager.apply_action(state, "call", 0)
      state, _ = RoundManager.apply_action(state, "call", 0)
      state, _ = RoundManager.apply_action(state, "call", 0)
      _, msgs = RoundManager.apply_action(state, "call", 0)
      self.eq((-1, "boo"), msgs[0])
      self.eq((-1, "foo"), msgs[1])

  def test_message_skip_when_only_one_player_is_active(self):
    state, _ = self.__start_round()
    state, _ = RoundManager.apply_action(state, "fold", 0)
    state, msgs = RoundManager.apply_action(state, "fold", 0)
    self.eq(Const.Street.FINISHED, state["street"])

  def __start_round(self):
    table = self.__setup_table()
    round_count = 0
    return RoundManager.start_new_round(round_count, table)

  def __setup_table(self):
    players = [Player("uuid%d" % i, 100) for i in range(3)]
    deck = Deck(cheat=True, cheat_card_ids=range(1,53))
    table = Table(cheat_deck=deck)
    for player in players: table.seats.sitdown(player)
    return table

