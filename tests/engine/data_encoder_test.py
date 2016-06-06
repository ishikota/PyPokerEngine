from tests.base_unittest import BaseUnitTest
from pypoker2.engine.card import Card
from pypoker2.engine.player import Player
from pypoker2.engine.pay_info import PayInfo
from pypoker2.engine.table import Table
from pypoker2.engine.seats import Seats
from pypoker2.engine.action import Action
from pypoker2.engine.data_encoder import DataEncoder
from pypoker2.engine.round_manager import RoundManager

class DataEncoderTest(BaseUnitTest):

  def test_encode_player_without_holecard(self):
    player = self.__setup_player()
    hsh = DataEncoder.encode_player(player)
    self.eq(player.name, hsh["name"])
    self.eq(player.uuid, hsh["uuid"])
    self.eq(player.stack, hsh["stack"])
    self.eq("folded", hsh["state"])
    self.false("hole_card" in hsh)

  def test_encode_player_with_holecard(self):
    player = self.__setup_player()
    hsh = DataEncoder.encode_player(player, holecard=True)
    self.eq([str(card) for card in player.hole_card], hsh["hole_card"])

  def test_encode_seats(self):
    seats = self.__setup_seats()
    hsh = DataEncoder.encode_seats(seats)
    self.eq(3, len(hsh["seats"]))
    self.eq(DataEncoder.encode_player(seats.players[0]), hsh["seats"][0])

  def test_encode_pot(self):
    players = self.__setup_players_for_pot()
    hsh = DataEncoder.encode_pot(players)
    main_pot  = hsh["main"]
    side_pot1 = hsh["side"][0]
    side_pot2 = hsh["side"][1]
    self.eq(22, main_pot["amount"])
    self.eq(9, side_pot1["amount"])
    self.eq(3, len(side_pot1["eligibles"]))
    self.eq(4, side_pot2["amount"])
    self.eq(2, len(side_pot2["eligibles"]))

  def test_encofe_game_information(self):
    config = { "initial_stack":100, "max_round":10, "small_blind_amount":5 }
    seats = self.__setup_seats()
    hsh = DataEncoder.encode_game_information(config, seats)
    self.eq(3, hsh["player_num"])
    self.eq(DataEncoder.encode_seats(seats)["seats"], hsh["seats"])
    self.eq(config["small_blind_amount"], hsh["rule"]["small_blind_amount"])
    self.eq(config["max_round"], hsh["rule"]["max_round"])
    self.eq(config["initial_stack"], hsh["rule"]["initial_stack"])

  def test_encode_valid_actions(self):
    hsh = DataEncoder.encode_valid_actions(10, 20, 100)
    acts = hsh["valid_actions"]
    self.eq("fold", acts[0]["action"])
    self.eq(0, acts[0]["amount"])
    self.eq("call", acts[1]["action"])
    self.eq(10, acts[1]["amount"])
    self.eq("raise", acts[2]["action"])
    self.eq(20, acts[2]["amount"]["min"])
    self.eq(100, acts[2]["amount"]["max"])

  def test_encode_action(self):
    player = self.__setup_player()
    hsh = DataEncoder.encode_action(player, "raise", 20)
    self.eq(player.uuid, hsh["player_uuid"])
    self.eq("raise", hsh["action"])
    self.eq(20, hsh["amount"])

  def test_encode_street(self):
    def check(arg, expected):
      self.eq(expected, DataEncoder.encode_street(arg)["street"])
    check(RoundManager.PREFLOP, "preflop")
    check(RoundManager.FLOP, "flop")
    check(RoundManager.TURN, "turn")
    check(RoundManager.RIVER, "river")
    check(RoundManager.SHOWDOWN, "showdown")

  def test_encode_action_histories(self):
    table = self.__setup_table()
    table.dealer_btn = 2
    p1, p2, p3 = table.seats.players
    p3.add_action_history(Action.RAISE, 10, 5)
    p1.add_action_history(Action.FOLD)
    p2.add_action_history(Action.RAISE, 20, 10)
    p3.add_action_history(Action.CALL, 20)
    hsh = DataEncoder.encode_action_histories(table)
    hsty = hsh["action_histories"]
    self.eq(4, len(hsty))
    self.eq(p3.action_histories[0], hsty[0])
    self.eq(p1.action_histories[0], hsty[1])
    self.eq(p2.action_histories[0], hsty[2])
    self.eq(p3.action_histories[1], hsty[3])

  def test_encode_winners(self):
    winners = [self.__setup_player() for _ in range(2)]
    hsh = DataEncoder.encode_winners(winners)
    self.eq(2, len(hsh["winners"]))
    self.eq([DataEncoder.encode_player(p) for p in winners], hsh["winners"])

  def test_encode_round_state(self):
    state = self.__setup_round_state()
    hsh = DataEncoder.encode_round_state(state)
    self.eq("flop", hsh["street"])
    self.eq(DataEncoder.encode_pot(state["table"].seats.players), hsh["pot"])
    self.eq(DataEncoder.encode_seats(state["table"].seats)["seats"], hsh["seats"])
    self.eq(["CA"], hsh["community_card"])
    self.eq(state["table"].dealer_btn, hsh["dealer_btn"])
    self.eq(state["next_player"], hsh["next_player"])

  def __setup_round_state(self):
    return {
        "street": 1,
        "agree_num": 0,
        "next_player": 2,
        "table": self.__setup_table()
    }

  def __setup_table(self):
    table = Table()
    players = [self.__setup_clean_player() for _ in range(3)]
    table.seats.players = players
    table.add_community_card(Card.from_id(1))
    return table

  def __setup_seats(self):
    seats = Seats()
    for _ in range(3):
      seats.sitdown(self.__setup_player())
    return seats

  def __setup_players_for_pot(self):
    p1 = self.__setup_player_with_payinfo("A", 5, PayInfo.ALLIN)
    p2 = self.__setup_player_with_payinfo("B", 10, PayInfo.PAY_TILL_END)
    p3 = self.__setup_player_with_payinfo("C", 8, PayInfo.ALLIN)
    p4 = self.__setup_player_with_payinfo("D", 10, PayInfo.PAY_TILL_END)
    p5 = self.__setup_player_with_payinfo("E", 2, PayInfo.FOLDED)
    return [p1, p2, p3, p4, p5]

  def __setup_player(self):
    player = self.__setup_player_with_payinfo("hoge", 50, PayInfo.FOLDED)
    player.add_holecard([Card.from_id(1), Card.from_id(2)])
    player.add_action_history(Action.CALL, 50)
    return player

  def __setup_player_with_payinfo(self, name, amount, status):
    player = Player("uuid", 100, name)
    player.pay_info.amount = amount
    player.pay_info.status = status
    return player

  def __setup_clean_player(self):
    return Player("uuid", 100, "hoge")

