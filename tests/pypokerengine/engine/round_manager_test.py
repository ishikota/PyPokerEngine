from tests.base_unittest import BaseUnitTest
from mock import patch
from pypokerengine.engine.round_manager import RoundManager
from pypokerengine.engine.poker_constants import PokerConstants as Const
from pypokerengine.engine.player import Player
from pypokerengine.engine.pay_info import PayInfo
from pypokerengine.engine.card import Card
from pypokerengine.engine.deck import Deck
from pypokerengine.engine.table import Table

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
    with patch('pypokerengine.engine.message_builder.MessageBuilder.build_round_start_message', return_value="hoge"),\
         patch('pypokerengine.engine.message_builder.MessageBuilder.build_street_start_message', return_value="fuga"),\
         patch('pypokerengine.engine.message_builder.MessageBuilder.build_ask_message', return_value="bar"):
      _, msgs = self.__start_round()
      self.eq(("uuid0", "hoge"), msgs[0])
      self.eq(("uuid1", "hoge"), msgs[1])
      self.eq(("uuid2", "hoge"),  msgs[2])
      self.eq((-1, "fuga"), msgs[3])
      self.eq(("uuid2", "bar"), msgs[4])

  def test_state_after_start_round(self):
    state, msgs = self.__start_round()
    self.eq(2, state["next_player"])
    self.eq("SMALLBLIND", state["table"].seats.players[0].action_histories[0]["action"])
    self.eq("BIGBLIND", state["table"].seats.players[1].action_histories[0]["action"])

  def test_message_after_apply_action(self):
    with patch('pypokerengine.engine.message_builder.MessageBuilder.build_round_start_message', return_value="hoge"),\
         patch('pypokerengine.engine.message_builder.MessageBuilder.build_street_start_message', return_value="fuga"),\
         patch('pypokerengine.engine.message_builder.MessageBuilder.build_ask_message', return_value="bar"),\
         patch('pypokerengine.engine.message_builder.MessageBuilder.build_game_update_message', return_value="boo"):
      state, _ = self.__start_round()
      _, msgs  = RoundManager.apply_action(state, "call", 10)
      self.eq((-1, "boo"), msgs[0])
      self.eq(("uuid0", "bar"), msgs[1])

  def test_state_after_apply_call(self):
    state, _ = self.__start_round()
    state, _ = RoundManager.apply_action(state, "call", 10)
    self.eq(0, state["next_player"])
    self.eq("CALL", state["table"].seats.players[2].action_histories[0]["action"])

  def test_state_after_apply_raise(self):
    state, _ = self.__start_round()
    state, _ = RoundManager.apply_action(state, "raise", 15)
    self.eq(0, state["next_player"])
    self.eq("RAISE", state["table"].seats.players[2].action_histories[0]["action"])

  def test_message_after_forward_to_flop(self):
    with patch('pypokerengine.engine.message_builder.MessageBuilder.build_street_start_message', return_value="fuga"),\
         patch('pypokerengine.engine.message_builder.MessageBuilder.build_ask_message', return_value="bar"),\
         patch('pypokerengine.engine.message_builder.MessageBuilder.build_game_update_message', return_value="boo"):
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
    self.eq([Card.from_id(cid) for cid in range(7,10)], state["table"].get_community_card())

    fetch_player = lambda uuid: [p for p in state["table"].seats.players if p.uuid==uuid][0]
    self.true(all(map(lambda p: len(p.action_histories)==0, state["table"].seats.players)))
    self.eq(2, len(fetch_player("uuid0").round_action_histories[Const.Street.PREFLOP]))
    self.eq(1, len(fetch_player("uuid1").round_action_histories[Const.Street.PREFLOP]))
    self.eq(1, len(fetch_player("uuid2").round_action_histories[Const.Street.PREFLOP]))
    self.assertIsNone(fetch_player("uuid0").round_action_histories[Const.Street.TURN])


  def test_state_after_forward_to_turn(self):
    state, _ = self.__start_round()
    state, _ = RoundManager.apply_action(state, "fold", 0)
    state, _ = RoundManager.apply_action(state, "call", 10)
    state, _ = RoundManager.apply_action(state, "call", 0)
    state, msgs = RoundManager.apply_action(state, "call", 0)

    self.eq(Const.Street.TURN, state["street"])
    self.eq([Card.from_id(cid) for cid in range(7,11)], state["table"].get_community_card())
    self.eq(3, len(msgs))

    fetch_player = lambda uuid: [p for p in state["table"].seats.players if p.uuid==uuid][0]
    self.true(all(map(lambda p: len(p.action_histories)==0, state["table"].seats.players)))
    self.eq(2, len(fetch_player("uuid0").round_action_histories[Const.Street.PREFLOP]))
    self.eq(1, len(fetch_player("uuid1").round_action_histories[Const.Street.PREFLOP]))
    self.eq(1, len(fetch_player("uuid2").round_action_histories[Const.Street.PREFLOP]))
    self.eq(1, len(fetch_player("uuid0").round_action_histories[Const.Street.FLOP]))
    self.eq(1, len(fetch_player("uuid1").round_action_histories[Const.Street.FLOP]))
    self.eq(0, len(fetch_player("uuid2").round_action_histories[Const.Street.FLOP]))
    self.assertIsNone(fetch_player("uuid0").round_action_histories[Const.Street.TURN])

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

    fetch_player = lambda uuid: [p for p in state["table"].seats.players if p.uuid==uuid][0]
    self.true(all(map(lambda p: len(p.action_histories)==0, state["table"].seats.players)))
    self.eq(2, len(fetch_player("uuid0").round_action_histories[Const.Street.PREFLOP]))
    self.eq(1, len(fetch_player("uuid1").round_action_histories[Const.Street.PREFLOP]))
    self.eq(1, len(fetch_player("uuid2").round_action_histories[Const.Street.PREFLOP]))
    self.eq(1, len(fetch_player("uuid0").round_action_histories[Const.Street.FLOP]))
    self.eq(1, len(fetch_player("uuid1").round_action_histories[Const.Street.FLOP]))
    self.eq(0, len(fetch_player("uuid2").round_action_histories[Const.Street.FLOP]))
    self.eq(1, len(fetch_player("uuid0").round_action_histories[Const.Street.TURN]))
    self.eq(1, len(fetch_player("uuid1").round_action_histories[Const.Street.TURN]))
    self.eq(0, len(fetch_player("uuid2").round_action_histories[Const.Street.TURN]))
    self.assertIsNone(fetch_player("uuid0").round_action_histories[Const.Street.RIVER])

  def test_state_after_showdown(self):
    mock_return = [1,0]*3
    with patch('pypokerengine.engine.hand_evaluator.HandEvaluator.eval_hand', side_effect=mock_return),\
         patch('pypokerengine.engine.message_builder.MessageBuilder.build_round_result_message', return_value="bogo"):
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

      self.true(all(map(lambda p: len(p.action_histories)==0, state["table"].seats.players)))
      self.true(all(map(lambda p: p.round_action_histories==[None]*4, state["table"].seats.players)))

  def test_message_after_showdown(self):
    mock_return = [1,0]*3
    with patch('pypokerengine.engine.hand_evaluator.HandEvaluator.eval_hand', side_effect=mock_return),\
         patch('pypokerengine.engine.message_builder.MessageBuilder.build_game_update_message', return_value="boo"),\
         patch('pypokerengine.engine.message_builder.MessageBuilder.build_round_result_message', return_value="foo"):
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

  def test_table_reset_after_showdown(self):
    mock_return = [1,0]*3
    with patch('pypokerengine.engine.hand_evaluator.HandEvaluator.eval_hand', side_effect=mock_return),\
         patch('pypokerengine.engine.message_builder.MessageBuilder.build_game_update_message', return_value="boo"),\
         patch('pypokerengine.engine.message_builder.MessageBuilder.build_round_result_message', return_value="foo"):
      state, _ = self.__start_round()
      state, _ = RoundManager.apply_action(state, "fold", 0)
      state, _ = RoundManager.apply_action(state, "call", 10)
      state, _ = RoundManager.apply_action(state, "call", 0)
      state, _ = RoundManager.apply_action(state, "call", 0)
      state, _ = RoundManager.apply_action(state, "call", 0)
      state, _ = RoundManager.apply_action(state, "call", 0)
      state, _ = RoundManager.apply_action(state, "call", 0)
      state, _ = RoundManager.apply_action(state, "call", 0)
      table = state["table"]
      player = state["table"].seats.players[0]
      self.eq(52, table.deck.size())
      self.eq([], table.get_community_card())
      self.eq([], player.hole_card)
      self.eq([], player.action_histories)
      self.eq(PayInfo.PAY_TILL_END, player.pay_info.status)

  def test_message_skip_when_only_one_player_is_active(self):
    state, _ = self.__start_round()
    state, _ = RoundManager.apply_action(state, "fold", 0)
    state, msgs = RoundManager.apply_action(state, "fold", 0)
    self.eq(Const.Street.FINISHED, state["street"])
    self.false("street_start_message" in [msg["message"]["message_type"] for _, msg in msgs])

  def test_ask_player_target_when_dealer_btn_player_is_folded(self):
    state, _ = self.__start_round()
    state, _ = RoundManager.apply_action(state, "call", 10)
    state, _ = RoundManager.apply_action(state, "call", 10)
    state, _ = RoundManager.apply_action(state, "fold", 10)
    state, _ = RoundManager.apply_action(state, "call", 0)
    state, msgs = RoundManager.apply_action(state, "call", 0)
    self.eq("uuid1", msgs[-1][0])

  def __start_round(self):
    table = self.__setup_table()
    round_count = 1
    small_blind_amount = 5
    return RoundManager.start_new_round(round_count, small_blind_amount, table)

  def __setup_table(self):
    players = [Player("uuid%d" % i, 100) for i in range(3)]
    deck = Deck(cheat=True, cheat_card_ids=range(1,53))
    table = Table(cheat_deck=deck)
    for player in players: table.seats.sitdown(player)
    return table

