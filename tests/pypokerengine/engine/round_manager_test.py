from tests.base_unittest import BaseUnitTest
from mock import patch
from pypokerengine.engine.round_manager import RoundManager
from pypokerengine.engine.game_evaluator import GameEvaluator
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

  def test_collect_ante(self):
    ante = 10
    sb_amount = 5
    table = self.__setup_table()
    state, _ = RoundManager.start_new_round(1, sb_amount, ante, table)
    players = state["table"].seats.players
    self.eq(100-sb_amount-ante, players[0].stack)
    self.eq(100-sb_amount*2-ante, players[1].stack)
    self.eq(100-ante, players[2].stack)
    self.eq("ANTE", players[0].action_histories[0]["action"])
    self.eq("ANTE", players[1].action_histories[0]["action"])
    self.eq("ANTE", players[2].action_histories[0]["action"])
    self.eq(sb_amount+ante, players[0].pay_info.amount)
    self.eq(sb_amount*2+ante, players[1].pay_info.amount)
    self.eq(ante, players[2].pay_info.amount)
    self.eq(sb_amount+sb_amount*2+ante*3, GameEvaluator.create_pot(players)[0]["amount"])

  def test_collect_ante_skip_loser(self):
    ante = 10
    sb_amount = 5
    table = self.__setup_table()
    table.seats.players[2].stack = 0
    table.seats.players[2].pay_info.status = PayInfo.FOLDED
    state, _ = RoundManager.start_new_round(1, sb_amount, ante, table)
    players = state["table"].seats.players
    self.eq(sb_amount+sb_amount*2+ante*2, GameEvaluator.create_pot(players)[0]["amount"])

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
      state, _ = RoundManager.apply_action(state, "call", 10)
      _, msgs  = RoundManager.apply_action(state, "call", 10)

      self.eq((-1, "boo"), msgs[0])
      self.eq((-1, "fuga"), msgs[1])
      self.eq(("uuid0", "bar"), msgs[2])

  def test_state_after_forward_to_flop(self):
    state, _ = self.__start_round()
    state, _ = RoundManager.apply_action(state, "fold", 0)
    state, _ = RoundManager.apply_action(state, "call", 10)
    state, _ = RoundManager.apply_action(state, "call", 10)

    self.eq(Const.Street.FLOP, state["street"])
    self.eq(0, state["next_player"])
    self.eq([Card.from_id(cid) for cid in range(7,10)], state["table"].get_community_card())

    fetch_player = lambda uuid: [p for p in state["table"].seats.players if p.uuid==uuid][0]
    self.true(all(map(lambda p: len(p.action_histories)==0, state["table"].seats.players)))
    self.eq(2, len(fetch_player("uuid0").round_action_histories[Const.Street.PREFLOP]))
    self.eq(2, len(fetch_player("uuid1").round_action_histories[Const.Street.PREFLOP]))
    self.eq(1, len(fetch_player("uuid2").round_action_histories[Const.Street.PREFLOP]))
    self.assertIsNone(fetch_player("uuid0").round_action_histories[Const.Street.TURN])


  def test_state_after_forward_to_turn(self):
    state, _ = self.__start_round()
    state, _ = RoundManager.apply_action(state, "fold", 0)
    state, _ = RoundManager.apply_action(state, "call", 10)
    state, _ = RoundManager.apply_action(state, "call", 10)
    state, _ = RoundManager.apply_action(state, "call", 0)
    state, msgs = RoundManager.apply_action(state, "call", 0)

    self.eq(Const.Street.TURN, state["street"])
    self.eq([Card.from_id(cid) for cid in range(7,11)], state["table"].get_community_card())
    self.eq(3, len(msgs))

    fetch_player = lambda uuid: [p for p in state["table"].seats.players if p.uuid==uuid][0]
    self.true(all(map(lambda p: len(p.action_histories)==0, state["table"].seats.players)))
    self.eq(2, len(fetch_player("uuid0").round_action_histories[Const.Street.PREFLOP]))
    self.eq(2, len(fetch_player("uuid1").round_action_histories[Const.Street.PREFLOP]))
    self.eq(1, len(fetch_player("uuid2").round_action_histories[Const.Street.PREFLOP]))
    self.eq(1, len(fetch_player("uuid0").round_action_histories[Const.Street.FLOP]))
    self.eq(1, len(fetch_player("uuid1").round_action_histories[Const.Street.FLOP]))
    self.eq(0, len(fetch_player("uuid2").round_action_histories[Const.Street.FLOP]))
    self.assertIsNone(fetch_player("uuid0").round_action_histories[Const.Street.TURN])

  def test_state_after_forward_to_river(self):
    state, _ = self.__start_round()
    state, _ = RoundManager.apply_action(state, "fold", 0)
    state, _ = RoundManager.apply_action(state, "call", 10)
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
    self.eq(2, len(fetch_player("uuid1").round_action_histories[Const.Street.PREFLOP]))
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
    state, _ = RoundManager.apply_action(state, "call", 10)
    state, _ = RoundManager.apply_action(state, "fold", 10)
    state, _ = RoundManager.apply_action(state, "call", 0)
    state, msgs = RoundManager.apply_action(state, "call", 0)
    self.eq("uuid1", msgs[-1][0])

  def test_skip_asking_to_allin_player(self):
    state, _ = self.__start_round()
    # Round 1
    state, _ = RoundManager.apply_action(state, "call", 10)
    state, _ = RoundManager.apply_action(state, "fold", 0)
    state, _ = RoundManager.apply_action(state, "call", 10)
    state, _ = RoundManager.apply_action(state, "raise", 50)
    state, _ = RoundManager.apply_action(state, "call", 50)
    state, _ = RoundManager.apply_action(state, "fold", 0)
    self.eq([95, 40, 165], [p.stack for p in state["table"].seats.players])
    # Round 2
    state["table"].shift_dealer_btn()
    state["table"].set_blind_pos(1, 2)
    state, _ = RoundManager.start_new_round(2, 5, 0, state["table"])
    state, _ = RoundManager.apply_action(state, "raise", 40)
    state, _ = RoundManager.apply_action(state, "call", 40)
    state, _ = RoundManager.apply_action(state, "raise", 70)
    state, msgs = RoundManager.apply_action(state, "call", 70)
    self.eq([25, 0, 95], [p.stack for p in state["table"].seats.players])
    self.eq(1, state["street"])
    self.eq("uuid2", msgs[-1][0])

  def test_when_only_one_player_is_waiting_ask(self):
    state, _ = self.__start_round()
    # Round 1
    state, _ = RoundManager.apply_action(state, "call", 10)
    state, _ = RoundManager.apply_action(state, "fold", 0)
    state, _ = RoundManager.apply_action(state, "call", 10)
    state, _ = RoundManager.apply_action(state, "call", 0)
    state, _ = RoundManager.apply_action(state, "raise", 50)
    state, _ = RoundManager.apply_action(state, "call", 50)
    state, _ = RoundManager.apply_action(state, "fold", 0)
    self.eq([95, 40, 165], [p.stack for p in state["table"].seats.players])
    # Round 2
    state["table"].shift_dealer_btn()
    state, _ = RoundManager.start_new_round(2, 5, 0, state["table"])
    state, _ = RoundManager.apply_action(state, "raise", 40)
    state, _ = RoundManager.apply_action(state, "call", 40)
    state, _ = RoundManager.apply_action(state, "raise", 70)
    state, _ = RoundManager.apply_action(state, "call", 70)
    state, _ = RoundManager.apply_action(state, "call", 0)
    state, _ = RoundManager.apply_action(state, "raise", 10)
    state, _ = RoundManager.apply_action(state, "call", 10)
    state, _ = RoundManager.apply_action(state, "raise", 85)
    state, _ = RoundManager.apply_action(state, "call", 85)

  def test_ask_big_blind_in_preflop(self):
    state, _ = self.__start_round()
    state, _ = RoundManager.apply_action(state, "call", 10)
    state, msg = RoundManager.apply_action(state, "call", 10)
    self.eq("uuid1", msg[-1][0])
    self.eq(Const.Street.PREFLOP, state["street"])

  def test_everyone_agree_logic_regression(self):
    players = [Player("uuid%d" % i, 100) for i in range(4)]
    players[0].stack = 150
    players[1].stack = 150
    players[2].stack = 50
    players[3].stack = 50
    deck = Deck(cheat=True, cheat_card_ids=range(1,53))
    table = Table(cheat_deck=deck)
    for player in players: table.seats.sitdown(player)
    table.dealer_btn = 3
    table.set_blind_pos(0, 1)

    state, _ = RoundManager.start_new_round(1, 5, 0, table)
    state, _ = RoundManager.apply_action(state, "raise", 15)
    state, _ = RoundManager.apply_action(state, "raise", 20)
    state, _ = RoundManager.apply_action(state, "raise", 25)
    state, _ = RoundManager.apply_action(state, "raise", 30)
    state, _ = RoundManager.apply_action(state, "raise", 50)
    state, _ = RoundManager.apply_action(state, "call", 50)
    state, _ = RoundManager.apply_action(state, "raise", 125)
    state, _ = RoundManager.apply_action(state, "call", 125)
    state, _ = RoundManager.apply_action(state, "fold", 0)
    state, _ = RoundManager.apply_action(state, "fold", 0)
    self.eq(Const.Street.FINISHED, state["street"])

  def test_add_amount_calculationl_when_raise_on_ante(self):
    table = self.__setup_table()
    pot_amount = lambda state: GameEvaluator.create_pot(state["table"].seats.players)[0]["amount"]
    stack_check = lambda expected, state: self.eq(expected, [p.stack for p in state["table"].seats.players])
    start_state, _ = RoundManager.start_new_round(1, 10, 5, table)
    self.eq(45, pot_amount(start_state))
    stack_check([85, 75, 95], start_state)
    folded_state, _ = RoundManager.apply_action(start_state, "fold", 0)
    called_state, _ = RoundManager.apply_action(folded_state, "call", 20)
    self.eq(55, pot_amount(called_state))
    stack_check([85, 75, 95], start_state)
    called_state, _ = RoundManager.apply_action(start_state, "call", 20)
    self.eq(20, called_state["table"].seats.players[2].action_histories[-1]["paid"])
    self.eq(65, pot_amount(called_state))
    raised_state, _ = RoundManager.apply_action(start_state, "raise", 30)
    self.eq(30, raised_state["table"].seats.players[2].action_histories[-1]["paid"])
    self.eq(75, pot_amount(raised_state))


  def test_deepcopy_state(self):
    table = self.__setup_table()
    original = RoundManager._RoundManager__gen_initial_state(2, 5, table)
    copied = RoundManager._RoundManager__deep_copy_state(original)
    check = lambda key: self.eq(original[key], copied[key])
    [check(key) for key in ["round_count", "small_blind_amount", "street", "next_player"]]


  def __start_round(self):
    table = self.__setup_table()
    round_count = 1
    small_blind_amount = 5
    ante = 0
    return RoundManager.start_new_round(round_count, small_blind_amount, ante, table)

  def __setup_table(self):
    players = [Player("uuid%d" % i, 100) for i in range(3)]
    deck = Deck(cheat=True, cheat_card_ids=range(1,53))
    table = Table(cheat_deck=deck)
    for player in players: table.seats.sitdown(player)
    table.dealer_btn = 2
    table.set_blind_pos(0, 1)
    return table

