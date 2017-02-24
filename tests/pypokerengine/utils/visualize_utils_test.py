try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import sys
from tests.base_unittest import BaseUnitTest

import pypokerengine.utils.visualize_utils as U

class VisualizeUtilsTest(BaseUnitTest):

    def setUp(self):
        self.capture = StringIO()
        sys.stdout = self.capture

    def tearDown(self):
        sys.stdout = sys.__stdout__

    def test_visualize_game_start(self):
        s = U.visualize_game_start(game_info)
        self.assertIn("3 players game", s)
        self.assertIn("10 round", s)
        self.assertIn("start stack = 100", s)
        self.assertIn("ante = 5", s)
        self.assertIn("small blind = 10", s)
        self.assertIn("after 5 round", s)

    def test_visualize_round_start(self):
        s = U.visualize_round_start(2, ['C2', 'HQ'], seats)
        self.assertIn("Round 2 start", s)
        self.assertIn("C2", s)
        self.assertIn("HQ", s)
        self.assertIn("players information", s)

    def test_visualize_street_start(self):
        s = U.visualize_street_start("preflop", "dummy")
        self.assertIn("preflop", s)

    def test_visualize_declare_action(self):
        s = U.visualize_declare_action(valid_actions, ['CA', 'DK'], round_state)
        self.assertIn("fold", s)
        self.assertIn("call: 0", s)
        self.assertIn("raise: [20, 95]", s)
        self.assertIn("CA", s)
        self.assertIn("DK", s)
        self.assertIn("round state", s)

    def test_visualize_game_update(self):
        s = U.visualize_game_update(new_action, round_state)
        self.assertIn("p1", s)
        self.assertIn("ftwdqkystzsqwjrzvludgi", s)
        self.assertIn("raise: 30", s)

    def test_visualize_round_result(self):
        s = U.visualize_round_result(winners, hand_info, round_state)
        self.assertIn("winners", s)
        self.assertIn("hand info", s)
        self.assertIn("round state", s)

    def test_additonal_info(self):
        uuid = "hoge"
        self.assertIn(uuid, U.visualize_game_start(game_info, uuid))
        self.assertIn(uuid, U.visualize_round_start(2, ['C2', 'HQ'], seats, uuid))
        self.assertIn(uuid, U.visualize_street_start("preflop", "dummy", uuid))
        self.assertIn(uuid, U.visualize_declare_action(valid_actions, ['CA', 'DK'], round_state, uuid))
        self.assertIn(uuid, U.visualize_game_update(new_action, round_state, uuid))
        self.assertIn(uuid, U.visualize_round_result(winners, hand_info, round_state, uuid))


game_info = {
    'player_num': 3,
    'rule': {
        'ante': 5,
        'blind_structure': {
            5 : { "ante": 10, "small_blind": 20 },
            7 : { "ante": 15, "small_blind": 30 }
        },
        'max_round': 10,
        'initial_stack': 100,
        'small_blind_amount': 10
      },
      'seats': [
          {'stack': 100, 'state': 'participating', 'name': 'p1', 'uuid': 'ftwdqkystzsqwjrzvludgi'},
          {'stack': 100, 'state': 'participating', 'name': 'p2', 'uuid': 'bbiuvgalrglojvmgggydyt'},
          {'stack': 100, 'state': 'participating', 'name': 'p3', 'uuid': 'zkbpehnazembrxrihzxnmt'}
      ]
}

seats = [
    {'stack': 135, 'state': 'participating', 'name': 'p1', 'uuid': 'ftwdqkystzsqwjrzvludgi'},
    {'stack': 80, 'state': 'participating', 'name': 'p2', 'uuid': 'bbiuvgalrglojvmgggydyt'},
    {'stack': 40, 'state': 'participating', 'name': 'p3', 'uuid': 'zkbpehnazembrxrihzxnmt'}
]

valid_actions = [
    {'action': 'fold', 'amount': 0},
    {'action': 'call', 'amount': 0},
    {'action': 'raise', 'amount': {'max': 95, 'min': 20}}
]

round_state = {
    'round_count': 2,
    'dealer_btn': 1,
    'small_blind_pos': 2,
    'big_blind_pos': 0,
    'next_player': 0,
    'small_blind_amount': 10,
    'street': 'turn',
    'community_card': ['DJ', 'H6', 'S6', 'H5'],
    'seats': [
        {'stack': 95, 'state': 'participating', 'name': 'p1', 'uuid': 'ftwdqkystzsqwjrzvludgi'},
        {'stack': 20, 'state': 'participating', 'name': 'p2', 'uuid': 'bbiuvgalrglojvmgggydyt'},
        {'stack': 0, 'state': 'allin', 'name': 'p3', 'uuid': 'zkbpehnazembrxrihzxnmt'}
    ],
    'pot': {
        'main': {'amount': 165},
        'side': [{'amount': 20, 'eligibles': ['ftwdqkystzsqwjrzvludgi', 'bbiuvgalrglojvmgggydyt']}]
    },
    'action_histories': {
        'preflop': [
            {'action': 'ANTE', 'amount': 5, 'uuid': 'zkbpehnazembrxrihzxnmt'},
            {'action': 'ANTE', 'amount': 5, 'uuid': 'ftwdqkystzsqwjrzvludgi'},
            {'action': 'ANTE', 'amount': 5, 'uuid': 'bbiuvgalrglojvmgggydyt'},
            {'action': 'SMALLBLIND', 'amount': 10, 'add_amount': 10, 'uuid': 'zkbpehnazembrxrihzxnmt'},
            {'action': 'BIGBLIND', 'amount': 20, 'add_amount': 10, 'uuid': 'ftwdqkystzsqwjrzvludgi'},
            {'action': 'CALL', 'amount': 20, 'uuid': 'bbiuvgalrglojvmgggydyt', 'paid': 20},
            {'action': 'RAISE', 'amount': 30, 'add_amount': 10, 'paid': 20, 'uuid': 'zkbpehnazembrxrihzxnmt'},
            {'action': 'CALL', 'amount': 30, 'uuid': 'ftwdqkystzsqwjrzvludgi', 'paid': 10},
            {'action': 'CALL', 'amount': 30, 'uuid': 'bbiuvgalrglojvmgggydyt', 'paid': 10}
        ],
        'flop': [
            {'action': 'CALL', 'amount': 0, 'uuid': 'zkbpehnazembrxrihzxnmt', 'paid': 0},
            {'action': 'RAISE', 'amount': 30, 'add_amount': 30, 'paid': 30, 'uuid': 'ftwdqkystzsqwjrzvludgi'},
            {'action': 'CALL', 'amount': 30, 'uuid': 'bbiuvgalrglojvmgggydyt', 'paid': 30},
            {'action': 'CALL', 'amount': 20, 'uuid': 'zkbpehnazembrxrihzxnmt', 'paid': 20}
        ],
        'turn': [],
    }
}

new_action = {
    'player_uuid': 'ftwdqkystzsqwjrzvludgi',
    'action': 'raise',
    'amount': 30
}

winners = [
    {'stack': 300, 'state': 'participating', 'name': 'p1', 'uuid': 'ftwdqkystzsqwjrzvludgi'}
]

hand_info = [
    {
        'uuid': 'ftwdqkystzsqwjrzvludgi',
        'hand': {
            'hole': {'high': 14, 'low': 13},
            'hand': {'high': 6, 'strength': 'ONEPAIR', 'low': 0}
        }
    },
    {
        'uuid': 'bbiuvgalrglojvmgggydyt',
        'hand': {
            'hole': {'high': 12, 'low': 2},
            'hand': {'high': 6, 'strength': 'ONEPAIR', 'low': 0}
        }
    },
    {
        'uuid': 'zkbpehnazembrxrihzxnmt',
        'hand': {
            'hole': {'high': 10, 'low': 3},
            'hand': {'high': 6, 'strength': 'ONEPAIR', 'low': 0}
        }
    }
]
