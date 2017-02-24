import sys
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from tests.base_unittest import BaseUnitTest
from pypokerengine.engine.dealer import MessageSummarizer

class MessageSummarizerTest(BaseUnitTest):

    def setUp(self):
        self.summarizer = MessageSummarizer(verbose=2)

    def tearDown(self):
        sys.stdout = sys.__stdout__

    def test_verbose_silent(self):
        summarizer = MessageSummarizer(verbose=0)
        self.assertIsNone(summarizer.summarize(game_start_message))

    def test_suppress_duplicate_round_start(self):
        capture = StringIO()
        sys.stdout = capture
        msgs = [("uuid1", round_start_message), ("uuid2", round_start_message)]
        summarizer = MessageSummarizer(verbose=2)
        summarizer.summarize_messages(msgs)
        self.eq(1, capture.getvalue().count("round 1"))

    def test_summarize_game_start(self):
        summary = self.summarizer.summarize(game_start_message)
        #expected = "Started the game with player [p1, p2] for 10 round. (start stack=100, small blind=5)"
        self._check_words(["p1", "p2", "10", "100", "5"], summary)

    def test_summarize_round_start(self):
        summary = self.summarizer.summarize(round_start_message)
        #expected = "Started the round 1"
        self._check_words(["round", "1"], summary)

    def test_summarize_street_start(self):
        summary = self.summarizer.summarize(street_start_message)
        #expected = 'Street "preflop" started. (community card = [])'
        self._check_words(["preflop", "community card"], summary)

    def test_summarize_player_action(self):
        summary = self.summarizer.summarize(game_update_message)
        #expected = '"p1" declared "fold:0"'
        self._check_words(["p1", "fold"], summary)

    def test_summarize_round_result(self):
        summary = self.summarizer.summarize(round_result_message)
        #expected = '"p2" won the round 1 (stack = { p1 : 95, p2 : 105 })'
        self._check_words(["p2", "round 1", "95", "105"], summary)

    def test_summarize_game_result(self):
        summary = self.summarizer.summarize(game_result_message)
        #expected = 'Game finished. (stack = { p1 : 100, p2 : 100 })'
        self._check_words(["finished", "p1", "100", "p2", "100"], summary)

    def test_summarize_blind_level_update(self):
        summary = self.summarizer.summairze_blind_level_update(1, 2, 3, 4, 5)
        #expected = 'Blind level update at round-1 : Ante 2 -> 3, SmallBlind 4 -> 5'
        self._check_words(["1", "2", "3", "4", "5"], summary)

    def _check_words(self, targets, source):
        for target in targets:
            self.assertIn(target, source)


game_start_message = {
        'message': {
            'game_information': {
                'player_num': 2, 'rule': {
                    'max_round': 10, 'initial_stack': 100, 'small_blind_amount': 5
                    },
                'seats': [
                    {'stack': 100, 'state': 'participating', 'name': 'p1', 'uuid': 'tdtgocoxtiuouaksklkuom'},
                    {'stack': 100, 'state': 'participating', 'name': 'p2', 'uuid': 'oxuhsunewzxbqdrreemfcw'}
                    ]
                },
            'message_type': 'game_start_message'},
        'type': 'notification'
        }

round_start_message = {
        'message': {
            'hole_card': ['HJ', 'H7'],
            'seats': [
                {'stack': 95, 'state': 'participating', 'name': 'p1', 'uuid': 'xbwggirmqtqvbpcjzkcdyh'},
                {'stack': 90, 'state': 'participating', 'name': 'p2', 'uuid': 'wbjujtrhizogjrliknebeg'}
                ],
            'message_type': 'round_start_message', 'round_count': 1
            },
        'type': 'notification'
        }

street_start_message = {
        'message': {
            'round_state': {
                'dealer_btn': 0, 'street': 'preflop',
                'seats': [
                    {'stack': 95, 'state': 'participating', 'name': 'p1', 'uuid': 'xbwggirmqtqvbpcjzkcdyh'},
                    {'stack': 90, 'state': 'participating', 'name': 'p2', 'uuid': 'wbjujtrhizogjrliknebeg'}
                    ],
                'next_player': 0, 'community_card': [],
                'pot': {'main': {'amount': 15}, 'side': []}
                },
            'street': 'preflop', 'message_type': 'street_start_message'
            },
        'type': 'notification'
        }

game_update_message = {
        'message': {
            'action': {'player_uuid': 'xbwggirmqtqvbpcjzkcdyh', 'action': 'fold', 'amount': 0},
            'round_state': {
                'dealer_btn': 0, 'street': 'preflop',
                'seats': [
                        {'stack': 95, 'state': 'folded', 'name': 'p1', 'uuid': 'xbwggirmqtqvbpcjzkcdyh'},
                        {'stack': 90, 'state': 'participating', 'name': 'p2', 'uuid': 'wbjujtrhizogjrliknebeg'}
                        ],
                'next_player': 0, 'community_card': [],
                'pot': {'main': {'amount': 15}, 'side': []}
                },
            'message_type': 'game_update_message',
            'action_histories': {
                'action_histories': [
                    {'action': 'SMALLBLIND', 'amount': 5, 'add_amount': 5, 'uuid': 'xbwggirmqtqvbpcjzkcdyh'},
                    {'action': 'BIGBLIND', 'amount': 10, 'add_amount': 5, 'uuid': 'wbjujtrhizogjrliknebeg'},
                    {'action': 'FOLD', 'uuid': 'xbwggirmqtqvbpcjzkcdyh'}
                    ]
                }
            },
        'type': 'notification'
        }

round_result_message = {
        'message': {
            'round_state': {
                'dealer_btn': 0, 'street': 'showdown',
                'seats': [
                    {'stack': 95, 'state': 'folded', 'name': 'p1', 'uuid': 'xbwggirmqtqvbpcjzkcdyh'},
                    {'stack': 105, 'state': 'participating', 'name': 'p2', 'uuid': 'wbjujtrhizogjrliknebeg'}
                    ],
                'next_player': 0, 'community_card': ['DA', 'C4', 'ST', 'C9', 'D2'],
                'pot': {'main': {'amount': 15}, 'side': []}
                },
            'hand_info': [], 'message_type': 'round_result_message',
            'winners': [{'stack': 105, 'state': 'participating', 'name': 'p2', 'uuid': 'wbjujtrhizogjrliknebeg'}],
            'round_count': 1
            },
        'type': 'notification'
        }

game_result_message = {
        'message': {
            'game_information': {
                'player_num': 2,
                'rule': {'max_round': 10, 'initial_stack': 100, 'small_blind_amount': 5},
                'seats': [
                    {'stack': 100, 'state': 'participating', 'name': 'p1', 'uuid': 'hwahikajnavhrstujltget'},
                    {'stack': 100, 'state': 'participating', 'name': 'p2', 'uuid': 'avaqlxnghtblmombxvprzh'}
                    ]
                }, 'message_type': 'game_result_message'
            },
        'type': 'notification'
        }

