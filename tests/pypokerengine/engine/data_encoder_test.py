from tests.base_unittest import BaseUnitTest
from pypokerengine.engine.card import Card
from pypokerengine.engine.player import Player
from pypokerengine.engine.pay_info import PayInfo
from pypokerengine.engine.table import Table
from pypokerengine.engine.seats import Seats
from pypokerengine.engine.poker_constants import PokerConstants as Const
from pypokerengine.engine.data_encoder import DataEncoder
from pypokerengine.engine.round_manager import RoundManager

class DataEncoderTest(BaseUnitTest):

    def test_encode_player_without_holecard(self):
        player = setup_player()
        hsh = DataEncoder.encode_player(player)
        self.eq(player.name, hsh["name"])
        self.eq(player.uuid, hsh["uuid"])
        self.eq(player.stack, hsh["stack"])
        self.eq("folded", hsh["state"])
        self.false("hole_card" in hsh)

    def test_encode_player_with_holecard(self):
        player = setup_player()
        hsh = DataEncoder.encode_player(player, holecard=True)
        self.eq([str(card) for card in player.hole_card], hsh["hole_card"])

    def test_encode_seats(self):
        seats = setup_seats()
        hsh = DataEncoder.encode_seats(seats)
        self.eq(3, len(hsh["seats"]))
        self.eq(DataEncoder.encode_player(seats.players[0]), hsh["seats"][0])

    def test_encode_pot(self):
        players = setup_players_for_pot()
        hsh = DataEncoder.encode_pot(players)
        main_pot  = hsh["main"]
        side_pot1 = hsh["side"][0]
        side_pot2 = hsh["side"][1]
        self.eq(22, main_pot["amount"])
        self.eq(9, side_pot1["amount"])
        self.eq(3, len(side_pot1["eligibles"]))
        self.eq(['uuid1', 'uuid2', 'uuid3'], side_pot1['eligibles'])
        self.eq(4, side_pot2["amount"])
        self.eq(2, len(side_pot2["eligibles"]))
        self.eq(['uuid1', 'uuid3'], side_pot2['eligibles'])

    def test_encofe_game_information(self):
        config = { "initial_stack":100, "max_round":10, "small_blind_amount":5,\
                "ante":1, "blind_structure": {1: {"ante": 3, "small_blind": 10} } }
        seats = setup_seats()
        hsh = DataEncoder.encode_game_information(config, seats)
        self.eq(3, hsh["player_num"])
        self.eq(DataEncoder.encode_seats(seats)["seats"], hsh["seats"])
        self.eq(config["small_blind_amount"], hsh["rule"]["small_blind_amount"])
        self.eq(config["max_round"], hsh["rule"]["max_round"])
        self.eq(config["initial_stack"], hsh["rule"]["initial_stack"])
        self.eq(config["ante"], hsh["rule"]["ante"])
        self.eq(config["blind_structure"], hsh["rule"]["blind_structure"])

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
        player = setup_player()
        hsh = DataEncoder.encode_action(player, "raise", 20)
        self.eq(player.uuid, hsh["player_uuid"])
        self.eq("raise", hsh["action"])
        self.eq(20, hsh["amount"])

    def test_encode_street(self):
        def check(arg, expected):
            self.eq(expected, DataEncoder.encode_street(arg)["street"])
        check(Const.Street.PREFLOP, "preflop")
        check(Const.Street.FLOP, "flop")
        check(Const.Street.TURN, "turn")
        check(Const.Street.RIVER, "river")
        check(Const.Street.SHOWDOWN, "showdown")

    def test_encode_action_histories(self):
        table = setup_table()
        p1, p2, p3 = table.seats.players
        hsh = DataEncoder.encode_action_histories(table)
        hsty = hsh["action_histories"]
        self.eq(4, len(hsty["preflop"]))
        fetch_info = lambda info: (info["action"], info["amount"])
        self.eq(("RAISE", 10), fetch_info(hsty["preflop"][0]))
        self.eq("FOLD", hsty["preflop"][1]["action"])
        self.eq(("RAISE", 20), fetch_info(hsty["preflop"][2]))
        self.eq(("CALL", 20), fetch_info(hsty["preflop"][3]))
        self.eq(2, len(hsty["flop"]))
        self.eq(("CALL", 5), fetch_info(hsty["flop"][0]))
        self.eq(("RAISE", 5), fetch_info(hsty["flop"][1]))
        self.assertFalse("turn" in hsty)
        self.assertFalse("river" in hsty)

    def test_encode_winners(self):
        winners = [setup_player() for _ in range(2)]
        hsh = DataEncoder.encode_winners(winners)
        self.eq(2, len(hsh["winners"]))
        self.eq([DataEncoder.encode_player(p) for p in winners], hsh["winners"])

    def test_encode_round_state(self):
        state = setup_round_state()
        state["table"].set_blind_pos(1, 3)
        hsh = DataEncoder.encode_round_state(state)
        self.eq("flop", hsh["street"])
        self.eq(DataEncoder.encode_pot(state["table"].seats.players), hsh["pot"])
        self.eq(DataEncoder.encode_seats(state["table"].seats)["seats"], hsh["seats"])
        self.eq(["CA"], hsh["community_card"])
        self.eq(state["table"].dealer_btn, hsh["dealer_btn"])
        self.eq(state["next_player"], hsh["next_player"])
        self.eq(1, hsh["small_blind_pos"])
        self.eq(3, hsh["big_blind_pos"])
        self.eq(DataEncoder.encode_action_histories(state["table"])["action_histories"], hsh["action_histories"])
        self.eq(state["round_count"], hsh["round_count"])
        self.eq(state["small_blind_amount"], hsh["small_blind_amount"])

def setup_player():
    player = setup_player_with_payinfo(0, "hoge", 50, PayInfo.FOLDED)
    player.add_holecard([Card.from_id(1), Card.from_id(2)])
    player.add_action_history(Const.Action.CALL, 50)
    return player

def setup_player_with_payinfo(idx, name, amount, status):
    player = Player("uuid%d" % idx, 100, name)
    player.pay_info.amount = amount
    player.pay_info.status = status
    return player

def setup_players_for_pot():
    p1 = setup_player_with_payinfo(0, "A", 5, PayInfo.ALLIN)
    p2 = setup_player_with_payinfo(1, "B", 10, PayInfo.PAY_TILL_END)
    p3 = setup_player_with_payinfo(2, "C", 8, PayInfo.ALLIN)
    p4 = setup_player_with_payinfo(3, "D", 10, PayInfo.PAY_TILL_END)
    p5 = setup_player_with_payinfo(4, "E", 2, PayInfo.FOLDED)
    return [p1, p2, p3, p4, p5]

def setup_seats():
    seats = Seats()
    for _ in range(3):
      seats.sitdown(setup_player())
    return seats

def setup_table():
    table = Table()
    players = [Player("uuid%d"%i, 100, "hoge") for i in range(3)]
    table.seats.players = players
    table.add_community_card(Card.from_id(1))
    table.dealer_btn = 2
    table.set_blind_pos(2, 0)
    p1, p2, p3 = table.seats.players
    p3.add_action_history(Const.Action.RAISE, 10, 5)
    p1.add_action_history(Const.Action.FOLD)
    p2.add_action_history(Const.Action.RAISE, 20, 10)
    p3.add_action_history(Const.Action.CALL, 20)
    [p.save_street_action_histories(Const.Street.PREFLOP) for p in [p1, p2, p3]]
    p3.add_action_history(Const.Action.CALL, 5)
    p2.add_action_history(Const.Action.RAISE, 5, 5)
    return table

def setup_round_state():
    return {
        "street": 1,
        "next_player": 2,
        "round_count": 3,
        "small_blind_amount": 4,
        "table": setup_table()
    }

