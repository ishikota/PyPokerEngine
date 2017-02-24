from nose.tools import raises
from tests.base_unittest import BaseUnitTest
from pypokerengine.utils.game_state_utils import restore_game_state,\
        attach_hole_card, replace_community_card,\
        attach_hole_card_from_deck, replace_community_card_from_deck
from pypokerengine.engine.card import Card
from pypokerengine.engine.poker_constants import PokerConstants as Const

class GameStateUtils(BaseUnitTest):

    def test_attach_hole_card_from_deck(self):
        game_state = restore_game_state(TwoPlayerSample.round_state)
        self.eq(48, game_state["table"].deck.size())
        processed1 = attach_hole_card_from_deck(game_state, "tojrbxmkuzrarnniosuhct")
        processed2 = attach_hole_card_from_deck(processed1, "pwtwlmfciymjdoljkhagxa")
        self.eq(44, processed2["table"].deck.size())
        self.eq(48, game_state["table"].deck.size())

    def test_replace_community_card_from_deck(self):
        origianl = restore_game_state(TwoPlayerSample.round_state)

        origianl["street"] = Const.Street.PREFLOP
        game_state = replace_community_card_from_deck(origianl)
        self.eq(48, game_state["table"].deck.size())
        self.eq(0, len(game_state["table"].get_community_card()))

        origianl["street"] = Const.Street.FLOP
        game_state = replace_community_card_from_deck(origianl)
        self.eq(45, game_state["table"].deck.size())
        self.eq(3, len(game_state["table"].get_community_card()))

        origianl["street"] = Const.Street.TURN
        game_state = replace_community_card_from_deck(origianl)
        self.eq(44, game_state["table"].deck.size())
        self.eq(4, len(game_state["table"].get_community_card()))

        origianl["street"] = Const.Street.RIVER
        game_state = replace_community_card_from_deck(origianl)
        self.eq(43, game_state["table"].deck.size())
        self.eq(5, len(game_state["table"].get_community_card()))

    def test_attach_hole_card(self):
        game_state = restore_game_state(TwoPlayerSample.round_state)
        to_card = lambda s: Card.from_str(s)
        hole1, hole2 = [to_card(c) for c in ["SA", "DA"]], [to_card(c) for c in ["HK", "C2"]]
        processed1 = attach_hole_card(game_state, "tojrbxmkuzrarnniosuhct", hole1)
        processed2 = attach_hole_card(processed1, "pwtwlmfciymjdoljkhagxa", hole2)
        players = processed2["table"].seats.players
        self.eq(hole1, players[0].hole_card)
        self.eq(hole2, players[1].hole_card)
        self.eq([0,0], [len(p.hole_card) for p in game_state["table"].seats.players])

    @raises(Exception)
    def test_attach_hole_card_when_uuid_is_wrong(self):
        game_state = restore_game_state(TwoPlayerSample.round_state)
        attach_hole_card(game_state, "hoge", "dummy_hole")

    @raises(Exception)
    def test_attach_hole_card_when_same_uuid_players_exist(self):
        game_state = restore_game_state(TwoPlayerSample.round_state)
        p1, p2 = game_state["table"].seats.players[:2]
        p2.uuid = p1.uuid
        attach_hole_card(game_state, p1.uuid, "dummy_hole")

    def test_replace_community_card(self):
        game_state = restore_game_state(TwoPlayerSample.round_state)
        to_card = lambda s: Card.from_str(s)
        cards = [to_card(c) for c in  ['SA', 'DA', 'CA', 'HA']]
        processed = replace_community_card(game_state, cards)
        self.eq(cards, processed["table"].get_community_card())
        self.neq(cards, game_state["table"].get_community_card())

    def test_restore_game_state_two_players_game(self):
        restored = restore_game_state(TwoPlayerSample.round_state)
        table = restored["table"]
        players = restored["table"].seats.players
        self.eq(1, restored["next_player"])
        self.eq(2, restored["street"])
        self.eq(3, restored["round_count"])
        self.eq(5, restored["small_blind_amount"])
        self.eq(0, table.dealer_btn)
        self.eq(0, table.sb_pos())
        self.eq(1, table.bb_pos())
        self.eq(['D5', 'D9', 'H6', 'CK'], [str(card) for card in table.get_community_card()])
        self._assert_deck(table.deck, [Card.from_str(s) for s in ['D5', 'D9', 'H6', 'CK']])
        self.eq(2, len(players))
        self._assert_player(["p1", "tojrbxmkuzrarnniosuhct", [], 65, TwoPlayerSample.p1_round_action_histories,\
                TwoPlayerSample.p1_action_histories, 0, 35], players[0])
        self._assert_player(["p2", "pwtwlmfciymjdoljkhagxa", [], 80, TwoPlayerSample.p2_round_action_histories,\
                TwoPlayerSample.p2_action_histories, 0, 20], players[1])

    def test_restore_game_state_three_players_game(self):
        restored = restore_game_state(ThreePlayerGameStateSample.round_state)
        table = restored["table"]
        players = restored["table"].seats.players
        self.eq(0, restored["next_player"])
        self.eq(2, restored["street"])
        self.eq(2, restored["round_count"])
        self.eq(5, restored["small_blind_amount"])
        self.eq(1, table.dealer_btn)
        self.eq(1, table.sb_pos())
        self.eq(2, table.bb_pos())
        self.eq(['HJ', 'C8', 'D2', 'H4'], [str(card) for card in table.get_community_card()])
        self._assert_deck(table.deck, [Card.from_str(s) for s in ['HJ', 'C8', 'D2', 'H4']])
        self.eq(3, len(players))
        self._assert_player(["p1", "ruypwwoqwuwdnauiwpefsw", [], 35, ThreePlayerGameStateSample.p1_round_action_histories,\
                ThreePlayerGameStateSample.p1_action_histories, 0, 60], players[0])
        self._assert_player(["p2", "sqmfwdkpcoagzqxpxnmxwm", [], 0, ThreePlayerGameStateSample.p2_round_action_histories,\
                ThreePlayerGameStateSample.p2_action_histories, 1, 50], players[1])
        self._assert_player(["p3", "uxrdiwvctvilasinweqven", [], 85, ThreePlayerGameStateSample.p3_round_action_histories,\
                ThreePlayerGameStateSample.p3_action_histories, 0, 70], players[2])

    def test_restore_game_state_when_ante_is_on(self):
        restored = restore_game_state(TwoPlayerSample.round_state_ante_on)
        players = restored["table"].seats.players
        self.eq(40, players[0].pay_info.amount)
        self.eq(25, players[1].pay_info.amount)

    def _assert_player(self, expected_data, player):
        self.eq(expected_data[0], player.name)
        self.eq(expected_data[1], player.uuid)
        self.eq(expected_data[2], player.hole_card)
        self.eq(expected_data[3], player.stack)
        self.eq(expected_data[4], player.round_action_histories)
        self.eq(expected_data[5], player.action_histories)
        self.eq(expected_data[6], player.pay_info.status)
        self.eq(expected_data[7], player.pay_info.amount)


    def _assert_deck(self, deck, exclude_cards):
        self.eq(52-len(exclude_cards), deck.size())
        for card in exclude_cards:
            self.assertNotIn(card, deck.deck)

class TwoPlayerSample:
    valid_actions = [{'action': 'fold', 'amount': 0}, {'action': 'call', 'amount': 15}, {'action': 'raise', 'amount': {'max': 80, 'min': 30}}]
    hole_card = ['CA', 'S3']
    round_state = {
            'dealer_btn': 0,
            'round_count': 3,
            'small_blind_amount': 5,
            'next_player': 1,
            'small_blind_pos': 0,
            'big_blind_pos': 1,
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

    round_state_ante_on = {
            'dealer_btn': 0,
            'round_count': 3,
            'small_blind_amount': 5,
            'next_player': 1,
            'small_blind_pos': 0,
            'big_blind_pos': 1,
            'street': 'turn',
            'community_card': ['D5', 'D9', 'H6', 'CK'],
            'pot': {'main': {'amount': 55}, 'side': []},
            'seats': [
                {'stack': 65, 'state': 'participating', 'name': 'p1', 'uuid': 'tojrbxmkuzrarnniosuhct'},
                {'stack': 80, 'state': 'participating', 'name': 'p2', 'uuid': 'pwtwlmfciymjdoljkhagxa'}
                ],
            'action_histories': {
                'preflop': [
                    {'action': 'ANTE', 'amount': 5, 'uuid': 'tojrbxmkuzrarnniosuhct'},
                    {'action': 'ANTE', 'amount': 5, 'uuid': 'pwtwlmfciymjdoljkhagxa'},
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
            'small_blind_pos': 1,
            'big_blind_pos': 2,
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

