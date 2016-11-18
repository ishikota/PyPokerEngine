from nose.tools import raises
from tests.base_unittest import BaseUnitTest
from pypokerengine.api.emulator import Emulator, Event
from pypokerengine.api.state_builder import restore_game_state,\
        attach_hole_card_from_deck, replace_community_card_from_deck
from pypokerengine.engine.card import Card
from pypokerengine.engine.pay_info import PayInfo
from pypokerengine.engine.game_evaluator import GameEvaluator
from pypokerengine.engine.poker_constants import PokerConstants as Const
from examples.players.fold_man import PokerPlayer as FoldMan

class EmulatorTest(BaseUnitTest):

    def setUp(self):
        self.emu = Emulator()

    def test_register_and_fetch_player(self):
        p1, p2 = FoldMan(), FoldMan()
        self.emu.register_player("uuid-1", p1)
        self.emu.register_player("uuid-2", p2)
        self.eq(p1, self.emu.fetch_player("uuid-1"))
        self.eq(p2, self.emu.fetch_player("uuid-2"))

    @raises(TypeError)
    def test_register_invalid_player(self):
        self.emu.register_player("uuid", "hoge")

    def test_run_until_next_event(self):
        game_state = restore_game_state(TwoPlayerSample.round_state)
        game_state = attach_hole_card_from_deck(game_state, "tojrbxmkuzrarnniosuhct")
        game_state = attach_hole_card_from_deck(game_state, "pwtwlmfciymjdoljkhagxa")
        p1, p2 = FoldMan(), FoldMan()
        self.emu.register_player("tojrbxmkuzrarnniosuhct", FoldMan())
        self.emu.register_player("pwtwlmfciymjdoljkhagxa", FoldMan())

        game_state, events = self.emu.run_until_next_event(game_state, "call", 15)
        self.eq(Const.Street.RIVER, game_state["street"])
        self.eq(TwoPlayerSample.p1_action_histories, \
                game_state["table"].seats.players[0].round_action_histories[Const.Street.TURN])
        self.eq(2, len(events))
        self.eq("event_new_street", events[0]["type"])
        self.eq("event_ask_player", events[1]["type"])

        game_state, events = self.emu.run_until_next_event(game_state, "call", 0)
        self.eq(1, len(events))
        self.eq("event_ask_player", events[0]["type"])

        game_state, events = self.emu.run_until_next_event(game_state, "call", 0)
        self.eq(1, len(events))
        self.eq("event_round_finish", events[0]["type"])

    def test_start_new_round(self):
        game_state = restore_game_state(TwoPlayerSample.round_state)
        game_state = attach_hole_card_from_deck(game_state, "tojrbxmkuzrarnniosuhct")
        game_state = attach_hole_card_from_deck(game_state, "pwtwlmfciymjdoljkhagxa")
        p1, p2 = FoldMan(), FoldMan()
        self.emu.register_player("tojrbxmkuzrarnniosuhct", FoldMan())
        self.emu.register_player("pwtwlmfciymjdoljkhagxa", FoldMan())

        # run until round finish
        game_state, event = self.emu.run_until_next_event(game_state, "call", 15)
        game_state, event = self.emu.run_until_next_event(game_state, "call", 0)
        game_state, event = self.emu.run_until_next_event(game_state, "call", 0)

        game_state, events = self.emu.start_new_round(2, 5, 0, game_state)
        self.eq(1, game_state["table"].dealer_btn)
        self.eq(0, game_state["street"])
        self.eq(1, game_state["next_player"])
        self.eq("event_new_street", events[0]["type"])
        self.eq("event_ask_player", events[1]["type"])
        self.eq("preflop", events[0]["street"])
        self.eq("pwtwlmfciymjdoljkhagxa", events[1]["uuid"])

    def test_start_new_round_exclude_no_money_players(self):
        uuids = ["ruypwwoqwuwdnauiwpefsw", "sqmfwdkpcoagzqxpxnmxwm", "uxrdiwvctvilasinweqven"]
        game_state = restore_game_state(ThreePlayerGameStateSample.round_state)
        original = reduce(lambda state, uuid: attach_hole_card_from_deck(state, uuid), uuids, game_state)
        [self.emu.register_player(uuid, FoldMan()) for uuid in uuids]

        sb_amount, ante = 5, 7
        # case1: second player cannot pay small blind
        finish_state, events = self.emu.run_until_next_event(original, "fold")
        finish_state["table"].seats.players[2].stack = 11
        stacks = [p.stack for p in finish_state["table"].seats.players]
        game_state, events = self.emu.start_new_round(2, sb_amount, ante, finish_state)
        self.eq(0, game_state["table"].dealer_btn)
        self.eq(0, game_state["next_player"])
        self.eq(stacks[0]-sb_amount-ante, game_state["table"].seats.players[0].stack)
        self.eq(stacks[1]-sb_amount*2-ante, game_state["table"].seats.players[1].stack)
        self.eq(PayInfo.FOLDED, game_state["table"].seats.players[2].pay_info.status)
        self.eq(sb_amount*3 + ante*2, GameEvaluator.create_pot(game_state["table"].seats.players)[0]["amount"])

        # case2: third player cannot pay big blind
        finish_state, events = self.emu.run_until_next_event(original, "fold")
        finish_state["table"].seats.players[0].stack = 16
        stacks = [p.stack for p in finish_state["table"].seats.players]
        game_state, events = self.emu.start_new_round(2, 5, 7, finish_state)
        self.eq(2, game_state["table"].dealer_btn)
        self.eq(2, game_state["next_player"])
        self.eq(stacks[2]-sb_amount-ante, game_state["table"].seats.players[2].stack)
        self.eq(stacks[1]-sb_amount*2-ante, game_state["table"].seats.players[1].stack)
        self.eq(PayInfo.FOLDED, game_state["table"].seats.players[0].pay_info.status)
        self.eq(PayInfo.PAY_TILL_END, game_state["table"].seats.players[2].pay_info.status)
        self.eq(sb_amount*3 + ante*2, GameEvaluator.create_pot(game_state["table"].seats.players)[0]["amount"])

class EventTest(BaseUnitTest):

    def setUp(self):
        self.emu = Emulator()

    def test_create_new_street_event(self):
        message = {
                "message_type": "street_start_message",
                "street": "preflop",
                "round_state": 1
                }
        event = self.emu.create_event(message)
        self.eq("event_new_street", event["type"])
        self.eq("preflop", event["street"])
        self.eq(1, event["round_state"])

    def test_create_ask_player_event(self):
        message = { 
                "message_type": "ask_message",
                "hole_card": 1,
                "valid_actions": 2,
                "round_state": TwoPlayerSample.round_state,
                "action_histories": [4,5]
                }
        event = self.emu.create_event(message)
        self.eq("event_ask_player", event["type"])
        self.eq(2, event["valid_actions"])
        self.eq(TwoPlayerSample.round_state, event["round_state"])
        self.eq("pwtwlmfciymjdoljkhagxa", event["uuid"])

    def test_create_round_finish_event(self):
        message = {
                "message_type": "round_result_message",
                "round_count": 2,
                "round_state": TwoPlayerSample.round_state,
                "hand_info": [],
                "winners": [{'stack': 105, 'state': 'participating', 'name': 'p2', 'uuid': 'pwtwlmfciymjdoljkhagxa'}]
                }
        event = self.emu.create_event(message)
        self.eq("event_round_finish", event["type"])
        self.eq(TwoPlayerSample.round_state, event["round_state"])
        self.eq("pwtwlmfciymjdoljkhagxa", event["winners"][0]["uuid"])
        self.eq(105, event["winners"][0]["stack"])

    def test_create_game_finish_event(self):
        message = {
                'message_type': 'game_result_message',
                'game_information': {
                    'player_num': 2,
                    'rule': {'max_round': 10, 'initial_stack': 100, 'small_blind_amount': 5},
                    "seats": [
                        {'stack': 0, 'state': 'folded', 'name': 'p1', 'uuid': 'tojrbxmkuzrarnniosuhct'},
                        {'stack': 200, 'state': 'participating', 'name': 'p2', 'uuid': 'pwtwlmfciymjdoljkhagxa'}
                    ]
                }
                }
        event = self.emu.create_event(message)
        self.eq("event_game_finish", event["type"])
        self.eq("tojrbxmkuzrarnniosuhct", event["players"][0]["uuid"])
        self.eq(0, event["players"][0]["stack"])
        self.eq("pwtwlmfciymjdoljkhagxa", event["players"][1]["uuid"])
        self.eq(200, event["players"][1]["stack"])

class TwoPlayerSample:
    valid_actions = [{'action': 'fold', 'amount': 0}, {'action': 'call', 'amount': 15}, {'action': 'raise', 'amount': {'max': 80, 'min': 30}}]
    hole_card = ['CA', 'S3']
    round_state = {
            'dealer_btn': 0,
            'round_count': 3,
            'small_blind_amount': 5,
            'next_player': 1,
            'street': 'turn',
            'community_card': ['D5', 'D9', 'H6', 'CK'],
            'pot': {'main': {'amount': 55}, 'side': []},
            'seats': [
                {'stack': 65, 'state': 'participating', 'name': 'p1', 'uuid': 'tojrbxmkuzrarnniosuhct'},
                {'stack': 80, 'state': 'participating', 'name': 'p2', 'uuid': 'pwtwlmfciymjdoljkhagxa'}
                ],
            'action_histories': {
                'preflop': [
                    {'action': 'SMALLBLIND', 'amount': 5, 'add_amount': 5, 'uuid': 'tojrbxmkuzrarnniosuhct'},
                    {'action': 'BIGBLIND', 'amount': 10, 'add_amount': 5, 'uuid': 'pwtwlmfciymjdoljkhagxa'},
                    {'action': 'CALL', 'amount': 10, 'uuid': 'tojrbxmkuzrarnniosuhct', 'paid': 5}
                    ],
                'flop': [
                    {'action': 'RAISE', 'amount': 5, 'add_amount': 5, 'paid': 5, 'uuid': 'tojrbxmkuzrarnniosuhct'},
                    {'action': 'RAISE', 'amount': 10, 'add_amount': 5, 'paid': 10, 'uuid': 'pwtwlmfciymjdoljkhagxa'},
                    {'action': 'CALL', 'amount': 10, 'uuid': 'tojrbxmkuzrarnniosuhct', 'paid': 5}
                    ],
                'turn': [
                    {'action': 'RAISE', 'amount': 15, 'add_amount': 15, 'paid': 15, 'uuid': 'tojrbxmkuzrarnniosuhct'}
                    ]
                }
            }

    p1_action_histories = [
            {'action': 'RAISE', 'amount': 15, 'add_amount': 15, 'paid': 15, 'uuid': 'tojrbxmkuzrarnniosuhct'}
            ]
    p2_action_histories = []
    p1_round_action_histories = [
            [
                {'action': 'SMALLBLIND', 'amount': 5, 'add_amount': 5, 'uuid': 'tojrbxmkuzrarnniosuhct'},
                {'action': 'CALL', 'amount': 10, 'uuid': 'tojrbxmkuzrarnniosuhct', 'paid': 5}
                ],
            [
                {'action': 'RAISE', 'amount': 5, 'add_amount': 5, 'paid': 5, 'uuid': 'tojrbxmkuzrarnniosuhct'},
                {'action': 'CALL', 'amount': 10, 'uuid': 'tojrbxmkuzrarnniosuhct', 'paid': 5}
                ],
            None,
            None
            ]
    p2_round_action_histories = [
            [
                {'action': 'BIGBLIND', 'amount': 10, 'add_amount': 5, 'uuid': 'pwtwlmfciymjdoljkhagxa'}
                ],
            [
                {'action': 'RAISE', 'amount': 10, 'add_amount': 5, 'paid': 10, 'uuid': 'pwtwlmfciymjdoljkhagxa'}
                ],
            None,
            None
            ]
    # player_pay_info = [pay_info.status, pay_info.amount]
    p1_pay_info = [0, 35]
    p2_pay_info = [0, 20]

class ThreePlayerGameStateSample:
    valid_actions = [{'action': 'fold', 'amount': 0}, {'action': 'call', 'amount': 10}, {'action': 'raise', 'amount': {'max': 35, 'min': 20}}]
    hole_card = ['S9', 'C5']
    round_state = {
            'dealer_btn': 1,
            'round_count': 2,
            'next_player': 0,
            'small_blind_amount': 5,
            'action_histories': {
                'turn': [
                    {'action': 'RAISE', 'amount': 10, 'add_amount': 10, 'paid': 10, 'uuid': 'uxrdiwvctvilasinweqven'}
                    ],
                'preflop': [
                    {'action': 'SMALLBLIND', 'amount': 5, 'add_amount': 5, 'uuid': 'sqmfwdkpcoagzqxpxnmxwm'},
                    {'action': 'BIGBLIND', 'amount': 10, 'add_amount': 5, 'uuid': 'uxrdiwvctvilasinweqven'},
                    {'action': 'CALL', 'amount': 10, 'uuid': 'ruypwwoqwuwdnauiwpefsw', 'paid': 10},
                    {'action': 'CALL', 'amount': 10, 'uuid': 'sqmfwdkpcoagzqxpxnmxwm', 'paid': 5}
                    ],
                'flop': [
                    {'action': 'CALL', 'amount': 0, 'uuid': 'sqmfwdkpcoagzqxpxnmxwm', 'paid': 0},
                    {'action': 'CALL', 'amount': 0, 'uuid': 'uxrdiwvctvilasinweqven', 'paid': 0},
                    {'action': 'RAISE', 'amount': 50, 'add_amount': 50, 'paid': 50, 'uuid': 'ruypwwoqwuwdnauiwpefsw'},
                    {'action': 'CALL', 'amount': 40, 'uuid': 'sqmfwdkpcoagzqxpxnmxwm', 'paid': 40},
                    {'action': 'CALL', 'amount': 50, 'uuid': 'uxrdiwvctvilasinweqven', 'paid': 50}
                    ]
                },
            'street': 'turn',
            'seats': [
                {'stack': 35, 'state': 'participating', 'name': 'p1', 'uuid': 'ruypwwoqwuwdnauiwpefsw'},
                {'stack': 0, 'state': 'allin', 'name': 'p2', 'uuid': 'sqmfwdkpcoagzqxpxnmxwm'},
                {'stack': 85, 'state': 'participating', 'name': 'p3', 'uuid': 'uxrdiwvctvilasinweqven'}
                ],
            'community_card': ['HJ', 'C8', 'D2', 'H4'],
            'pot': {'main': {'amount': 150}, 'side': [{'amount': 30, 'eligibles': ["dummy"]}]}
            }
    p1_action_histories = []
    p2_action_histories = []
    p3_action_histories = [{'action': 'RAISE', 'amount': 10, 'add_amount': 10, 'paid': 10, 'uuid': 'uxrdiwvctvilasinweqven'}]
    p1_round_action_histories = [
            [{'action': 'CALL', 'amount': 10, 'uuid': 'ruypwwoqwuwdnauiwpefsw', 'paid': 10}],
            [{'action': 'RAISE', 'amount': 50, 'add_amount': 50, 'paid': 50, 'uuid': 'ruypwwoqwuwdnauiwpefsw'}],
            None,
            None]
    p2_round_action_histories = [
            [
                {'action': 'SMALLBLIND', 'amount': 5, 'add_amount': 5, 'uuid': 'sqmfwdkpcoagzqxpxnmxwm'},
                {'action': 'CALL', 'amount': 10, 'uuid': 'sqmfwdkpcoagzqxpxnmxwm', 'paid': 5}
                ],
            [
                {'action': 'CALL', 'amount': 0, 'uuid': 'sqmfwdkpcoagzqxpxnmxwm', 'paid': 0},
                {'action': 'CALL', 'amount': 40, 'uuid': 'sqmfwdkpcoagzqxpxnmxwm', 'paid': 40}
                ],
            None,
            None]
    p3_round_action_histories = [
            [
                {'action': 'BIGBLIND', 'amount': 10, 'add_amount': 5, 'uuid': 'uxrdiwvctvilasinweqven'}
                ],
            [
                {'action': 'CALL', 'amount': 0, 'uuid': 'uxrdiwvctvilasinweqven', 'paid': 0},
                {'action': 'CALL', 'amount': 50, 'uuid': 'uxrdiwvctvilasinweqven', 'paid': 50}
                ],
            None,
            None]
    # player_pay_info = [pay_info.status, pay_info.amount]
    p1_pay_info = [0, 60]
    p2_pay_info = [1, 50]
    p3_pay_info = [0, 70]

