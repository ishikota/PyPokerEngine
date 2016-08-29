from tests.base_unittest import BaseUnitTest
from tests.record_player import PokerPlayer as RecordMan
from mock import patch
from pypokerengine.interface.dealer import Dealer
from pypokerengine.players.sample.fold_man import PokerPlayer as FoldMan
from pypokerengine.engine.pay_info import PayInfo

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
    self.mh = self.dealer.message_handler
    algos = [RecordMan() for _ in range(2)]
    [self.dealer.register_player(name, algo) for name, algo in zip(["hoge", "fuga"], algos)]
    players = self.dealer.table.seats.players
    _ = self.dealer.start_game(1)

    first_player_expected = [
        "receive_round_start_message",
        "receive_street_start_message",
        "declare_action",
        "receive_game_update_message",
        "receive_round_result_message"
        ]
    second_player_expected = [
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
    summary = self.dealer.start_game(1)
    player_state = summary["game_information"]["seats"]
    self.eq(95, player_state[0]["stack"])
    self.eq(105, player_state[1]["stack"])

  def test_play_two_round(self):
    algos = [FoldMan() for _ in range(2)]
    [self.dealer.register_player(name, algo) for name, algo in zip(["hoge", "fuga"], algos)]
    players = self.dealer.table.seats.players
    summary = self.dealer.start_game(2)
    player_state = summary["game_information"]["seats"]
    self.eq(100, player_state[0]["stack"])
    self.eq(100, player_state[1]["stack"])

  def test_exclude_no_money_playe(self):
    algos = [FoldMan() for _ in range(3)]
    [self.dealer.register_player(name, algo) for name, algo in zip(["hoge", "fuga", "bar"], algos)]
    players = self.dealer.table.seats.players
    players[2].stack = 0
    summary = self.dealer.start_game(1)
    player_state = summary["game_information"]["seats"]
    self.eq("folded", player_state[2]["state"])

