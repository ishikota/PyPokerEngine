from tests.base_unittest import BaseUnitTest
from mock import patch
from pypokerengine.engine.dealer import Dealer
from examples.players.fold_man import FoldMan
from pypokerengine.engine.pay_info import PayInfo
from pypokerengine.engine.table import Table

class DealerTest(BaseUnitTest):

  def setUp(self):
    self.dealer = Dealer(5, 100)
    self.mh = self.dealer.message_handler

  def test_register_poker_player(self):
    algo = FoldMan()
    with patch.object(self.dealer, '_Dealer__fetch_uuid', return_value="a"):
      self.dealer.register_player("hoge", algo)
      player = self.dealer.table.seats.players[0]
      self.eq("hoge", player.name)
      self.eq(100, player.stack)
      self.eq(algo, self.mh.algo_owner_map["a"])

  def test_publish_msg(self):
    self.dealer = Dealer(1, 100)
    self.dealer.table.dealer_btn = 1
    self.mh = self.dealer.message_handler
    algos = [RecordMan() for _ in range(2)]
    [self.dealer.register_player(name, algo) for name, algo in zip(["hoge", "fuga"], algos)]
    players = self.dealer.table.seats.players
    _ = self.dealer.start_game(1)

    first_player_expected = [
        "receive_game_start_message",
        "receive_round_start_message",
        "receive_street_start_message",
        "declare_action",
        "receive_game_update_message",
        "receive_round_result_message"
        ]
    second_player_expected = [
        "receive_game_start_message",
        "receive_round_start_message",
        "receive_street_start_message",
        "receive_game_update_message",
        "receive_round_result_message"
        ]

    for i, expected in enumerate(first_player_expected):
      self.eq(expected, algos[0].received_msgs[i])
    for i, expected in enumerate(second_player_expected):
      self.eq(expected, algos[1].received_msgs[i])

  def test_play_a_round(self):
    algos = [FoldMan() for _ in range(2)]
    [self.dealer.register_player(name, algo) for name, algo in zip(["hoge", "fuga"], algos)]
    players = self.dealer.table.seats.players
    self.dealer.table.dealer_btn = 1
    summary = self.dealer.start_game(1)
    player_state = summary["message"]["game_information"]["seats"]
    self.eq(95, player_state[0]["stack"])
    self.eq(105, player_state[1]["stack"])

  def test_play_two_round(self):
    algos = [FoldMan() for _ in range(2)]
    [self.dealer.register_player(name, algo) for name, algo in zip(["hoge", "fuga"], algos)]
    players = self.dealer.table.seats.players
    summary = self.dealer.start_game(2)
    player_state = summary["message"]["game_information"]["seats"]
    self.eq(100, player_state[0]["stack"])
    self.eq(100, player_state[1]["stack"])

  def test_exclude_short_of_money_player(self):
    algos = [FoldMan() for _ in range(7)]
    [self.dealer.register_player("algo-%d" % idx, algo) for idx, algo in enumerate(algos)]
    self.dealer.table.dealer_btn = 5
    # initialize stack
    for idx, stack in enumerate([11, 7, 9, 11, 9, 7, 100]):
      self.dealer.table.seats.players[idx].stack = stack
    fetch_stacks = lambda res: [p["stack"] for p in res["message"]["game_information"]["seats"]]

    # -- NOTICE --
    # dealer.start_game does not change the internal table.
    # So running dealer.start_game twice returns same result
    # dealer_btn progress
    # round-1 => sb:player6, bb:player0
    # round-2 => sb:player0, bb:player3
    # round-3 => sb:player3, bb:player6
    # round-3 => sb:player6, bb:player0
    result = self.dealer.start_game(1)
    self.eq(fetch_stacks(result), [16, 7, 9, 11, 9, 7, 95])
    result = self.dealer.start_game(2)
    self.eq(fetch_stacks(result), [11, 0, 0, 16, 9, 7, 95])
    result = self.dealer.start_game(3)
    self.eq(fetch_stacks(result), [11, 0, 0, 11, 0, 0, 100])
    result = self.dealer.start_game(4)
    self.eq(fetch_stacks(result), [16, 0, 0, 11, 0, 0, 95])

  def test_exclude_short_of_money_player_when_ante_on(self):
    dealer = Dealer(5, 100, 20)
    blind_structure = { 3:{"ante":30, "small_blind": 10}}
    dealer.set_blind_structure(blind_structure)
    algos = [FoldMan() for _ in range(5)]
    [dealer.register_player("algo-%d" % idx, algo) for idx, algo in enumerate(algos)]
    dealer.table.dealer_btn = 3
    # initialize stack
    for idx, stack in enumerate([1000, 30, 46, 1000, 85]):
      dealer.table.seats.players[idx].stack = stack
    fetch_stacks = lambda res: [p["stack"] for p in res["message"]["game_information"]["seats"]]

    result = dealer.start_game(1)
    self.eq(fetch_stacks(result), [1085, 10, 26, 980, 60])
    result = dealer.start_game(2)
    self.eq(fetch_stacks(result), [1060, 0, 0, 1025, 40])
    result = dealer.start_game(3)
    self.eq(fetch_stacks(result), [1100, 0, 0, 985, 0])
    result = dealer.start_game(4)
    self.eq(fetch_stacks(result), [1060, 0, 0, 1025, 0])

  def test_exclude_short_of_money_player_when_ante_on2(self):
    dealer = Dealer(5, 100, 20)
    algos = [FoldMan() for _ in range(3)]
    [dealer.register_player("algo-%d" % idx, algo) for idx, algo in enumerate(algos)]
    dealer.table.dealer_btn = 2
    # initialize stack
    for idx, stack in enumerate([30, 25, 19]):
      dealer.table.seats.players[idx].stack = stack
    fetch_stacks = lambda res: [p["stack"] for p in res["message"]["game_information"]["seats"]]

    result = dealer.start_game(1)
    self.eq([55, 0, 0], fetch_stacks(result))


  def test_only_one_player_is_left(self):
    algos = [FoldMan() for _ in range(2)]
    [self.dealer.register_player(name, algo) for name, algo in zip(["hoge", "fuga"], algos)]
    players = self.dealer.table.seats.players
    players[0].stack = 14
    summary = self.dealer.start_game(2)

  def test_set_blind_structure(self):
    dealer = Dealer(5, 100, 3)
    dealer.table.dealer_btn = 2
    blind_structure = { 3:{"ante":7, "small_blind": 11}, 4:{"ante":13, "small_blind":30} }
    dealer.set_blind_structure(blind_structure)
    algos = [FoldMan() for _ in range(3)]
    [dealer.register_player("algo-%d" % idx, algo) for idx, algo in enumerate(algos)]
    fetch_stacks = lambda res: [p["stack"] for p in res["message"]["game_information"]["seats"]]
    result = dealer.start_game(1)
    self.eq(fetch_stacks(result), [92, 111, 97])
    result = dealer.start_game(2)
    self.eq(fetch_stacks(result), [89, 103, 108])
    result = dealer.start_game(3)
    self.eq(fetch_stacks(result), [114, 96, 90])
    result = dealer.start_game(4)
    self.eq(fetch_stacks(result), [71, 152, 77])
    result = dealer.start_game(5)
    self.eq(fetch_stacks(result), [58, 109, 133])

class RecordMan(FoldMan):

  def __init__(self):
    self.received_msgs = []

  def declare_action(self, valid_actions, hole_card, round_state):
    self.received_msgs.append("declare_action")
    return 'fold', 0

  def receive_game_start_message(self, game_info):
    self.received_msgs.append("receive_game_start_message")

  def receive_round_start_message(self, round_count, hole_card, seats):
    self.received_msgs.append("receive_round_start_message")

  def receive_street_start_message(self, street, round_state):
    self.received_msgs.append("receive_street_start_message")

  def receive_game_update_message(self, new_action, round_state):
    self.received_msgs.append("receive_game_update_message")

  def receive_round_result_message(self, winners, hand_info, round_state):
    self.received_msgs.append("receive_round_result_message")

