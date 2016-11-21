# SAMPLE OF CALLBACK ARGUMENTS
`BasePokerPlayer` class requires you to implement following 6 methods.
- `declare_action(self, valid_actions, hole_card, round_state)`
- `receive_game_start_message(self, game_info)`
- `receive_round_start_message(self, round_count, hole_card, seats)`
- `receive_street_start_message(self, street, round_state)`
- `receive_game_update_message(self, new_action, round_state)`
- `receive_round_result_message(self, winners, hand_info, round_state)`

In this document, we show actual argument of each callback method sampled from real game.

#### `declare_action(self, valid_actions, hole_card, round_state)`
- valid_actions
```
[
  {'action': 'fold', 'amount': 0},
  {'action': 'call', 'amount': 0},
  {'action': 'raise', 'amount': {'max': 120, 'min': 20}}
]
```
- hole_card
```
['CJ', 'S2']
```
- round_state
```
{
  'round_count': 3,
  'dealer_btn': 2,
  'next_player': 2,
  'small_blind_pos': 0,
  'big_blind_pos': 1,
  'small_blind_amount': 10,
  'street': 'flop',
  'community_card': ['HK', 'CQ', 'DQ'],
  'seats': [
    {'stack': 80, 'state': 'participating', 'name': 'p1', 'uuid': 'zjwhieqjlowtoogemqrjjo'},
    {'stack': 0, 'state': 'allin', 'name': 'p2', 'uuid': 'xgbpujiwtcccyicvfqffgy'},
    {'stack': 120, 'state': 'participating', 'name': 'p3', 'uuid': 'pnqfqsvgwkegkuwnzucvxw'}
  ],
  'pot': {
    'main': {'amount': 100}, 
    'side': [{'amount': 0, 'eligibles': ['zjwhieqjlowtoogemqrjjo', 'xgbpujiwtcccyicvfqffgy']}]
   },
  'action_histories': {
    'preflop': [
      {'action': 'ANTE', 'amount': 5, 'uuid': 'zjwhieqjlowtoogemqrjjo'},
      {'action': 'ANTE', 'amount': 5, 'uuid': 'xgbpujiwtcccyicvfqffgy'},
      {'action': 'ANTE', 'amount': 5, 'uuid': 'pnqfqsvgwkegkuwnzucvxw'},
      {'action': 'SMALLBLIND', 'amount': 10, 'add_amount': 10, 'uuid': 'zjwhieqjlowtoogemqrjjo'},
      {'action': 'BIGBLIND', 'amount': 20, 'add_amount': 10, 'uuid': 'xgbpujiwtcccyicvfqffgy'},
      {'action': 'RAISE', 'amount': 30, 'add_amount': 10, 'paid': 25, 'uuid': 'pnqfqsvgwkegkuwnzucvxw'},
      {'action': 'CALL', 'amount': 30, 'uuid': 'zjwhieqjlowtoogemqrjjo', 'paid': 20},
      {'action': 'CALL', 'amount': 30, 'uuid': 'xgbpujiwtcccyicvfqffgy', 'paid': 10}
    ],
    'flop': [
      {'action': 'CALL', 'amount': 0, 'uuid': 'zjwhieqjlowtoogemqrjjo', 'paid': 0}
     ]
  }
 }

```

#### `receive_game_start_message(self, game_info)`
- game_info
```
{
  'player_num': 3,
  'rule': {
    'max_round': 10,
    'initial_stack': 100,
    'small_blind_amount': 5,
    'ante': 0,
    'blind_structure': {
      3: {'ante': 5, 'small_blind': 10}
    }
  },
  'seats': [
    {'stack': 100, 'state': 'participating', 'name': 'p1', 'uuid': 'zjwhieqjlowtoogemqrjjo'},
    {'stack': 100, 'state': 'participating', 'name': 'p2', 'uuid': 'xgbpujiwtcccyicvfqffgy'},
    {'stack': 100, 'state': 'participating', 'name': 'p3', 'uuid': 'pnqfqsvgwkegkuwnzucvxw'}
   ]
}
```

#### `receive_round_start_message(self, round_count, hole_card, seats):`
- round_count
```
3
```
- hole_card
```
['H5', 'D4']
```
- seats
```
[
  {'stack': 100, 'state': 'participating', 'name': 'p1', 'uuid': 'zjwhieqjlowtoogemqrjjo'},
  {'stack': 10, 'state': 'participating', 'name': 'p2', 'uuid': 'xgbpujiwtcccyicvfqffgy'},
  {'stack': 145, 'state': 'participating', 'name': 'p3', 'uuid': 'pnqfqsvgwkegkuwnzucvxw'}
]
```

#### `receive_street_start_message(self, street, round_state)`
- street
```
'preflop'
```
- round_state
```
{
  'round_count': 3,
  'street': 'preflop',
  'small_blind_pos': 0,
  'big_blind_pos': 1,
  'dealer_btn': 2,
  'next_player': 2,
  'small_blind_amount': 10,
  'seats': [
    {'stack': 100, 'state': 'participating', 'name': 'p1', 'uuid': 'zjwhieqjlowtoogemqrjjo'}, 
    {'stack': 10, 'state': 'participating', 'name': 'p2', 'uuid': 'xgbpujiwtcccyicvfqffgy'}, 
    {'stack': 145, 'state': 'participating', 'name': 'p3', 'uuid': 'pnqfqsvgwkegkuwnzucvxw'}
  ], 
  'community_card': [],
  'pot': {'main': {'amount': 45}, 'side': []}
  'action_histories': {
    'preflop': [
      {'action': 'ANTE', 'amount': 5, 'uuid': 'zjwhieqjlowtoogemqrjjo'},
      {'action': 'ANTE', 'amount': 5, 'uuid': 'xgbpujiwtcccyicvfqffgy'},
      {'action': 'ANTE', 'amount': 5, 'uuid': 'pnqfqsvgwkegkuwnzucvxw'},
      {'action': 'SMALLBLIND', 'amount': 10, 'add_amount': 10, 'uuid': 'zjwhieqjlowtoogemqrjjo'},
      {'action': 'BIGBLIND', 'amount': 20, 'add_amount': 10, 'uuid': 'xgbpujiwtcccyicvfqffgy'}
    ]
  }
}
```

#### `receive_game_update_message(self, new_action, round_state)`
- new_action
```
{
  'player_uuid': 'zjwhieqjlowtoogemqrjjo',
   'action': 'raise',
   'amount': 10
}
```
- round_state
```
{
  'round_count': 2,
  'street': 'turn',
  'dealer_btn': 1,
  'small_blind_pos': 2,
  'big_blind_pos': 0,
  'next_player': 0,
  'small_blind_amount': 5,
  'community_card': ['CT', 'H9', 'S3', 'CA'],
  'pot': {
    'main': {'amount': 150},
    'side': [{'amount': 10, 'eligibles': ['zjwhieqjlowtoogemqrjjo']}]
  },
  'seats': [
    {'stack': 95, 'state': 'participating', 'name': 'p1', 'uuid': 'zjwhieqjlowtoogemqrjjo'},
    {'stack': 45, 'state': 'participating', 'name': 'p2', 'uuid': 'xgbpujiwtcccyicvfqffgy'},
    {'stack': 0, 'state': 'allin', 'name': 'p3', 'uuid': 'pnqfqsvgwkegkuwnzucvxw'}
   ]
  'action_histories': {
    'preflop': [
      {'action': 'SMALLBLIND', 'amount': 5, 'add_amount': 5, 'uuid': 'pnqfqsvgwkegkuwnzucvxw'},
      {'action': 'BIGBLIND', 'amount': 10, 'add_amount': 5, 'uuid': 'zjwhieqjlowtoogemqrjjo'},
      {'action': 'CALL', 'amount': 10, 'uuid': 'xgbpujiwtcccyicvfqffgy', 'paid': 10},
      {'action': 'CALL', 'amount': 10, 'uuid': 'pnqfqsvgwkegkuwnzucvxw', 'paid': 5},
      {'action': 'CALL', 'amount': 10, 'uuid': 'zjwhieqjlowtoogemqrjjo', 'paid': 0}
     ],
     'flop': [
       {'action': 'RAISE', 'amount': 40, 'add_amount': 40, 'paid': 40, 'uuid': 'pnqfqsvgwkegkuwnzucvxw'},
       {'action': 'CALL', 'amount': 40, 'uuid': 'zjwhieqjlowtoogemqrjjo', 'paid': 40},
       {'action': 'CALL', 'amount': 40, 'uuid': 'xgbpujiwtcccyicvfqffgy', 'paid': 40}
     ],
    'turn': [
      {'action': 'RAISE', 'amount': 10, 'add_amount': 10, 'paid': 10, 'uuid': 'zjwhieqjlowtoogemqrjjo'}
    ]
  }
}
```

#### `receive_round_result_message(self, winners, hand_info, round_state)`
- winners
```
[
  {'stack': 150, 'state': 'allin', 'name': 'p3', 'uuid': 'pnqfqsvgwkegkuwnzucvxw'}
]
```
- hand_info
```
[
  {
    'uuid': 'zjwhieqjlowtoogemqrjjo',
    'hand': {
      'hole': {'high': 13, 'low': 3},
      'hand': {'high': 3, 'strength': 'ONEPAIR', 'low': 0}
     }
  },
  {
    'uuid': 'xgbpujiwtcccyicvfqffgy',
    'hand': {
      'hole': {'high': 8, 'low': 4},
      'hand': {'high': 8, 'strength': 'HIGHCARD', 'low': 4}
    }
  },
  {
    'uuid': 'pnqfqsvgwkegkuwnzucvxw',
    'hand': {
      'hole': {'high': 10, 'low': 3},
      'hand': {'high': 10, 'strength': 'TWOPAIR', 'low': 3}
     }
  }
]
```
- round_state
```
{
  'round_count': 2,
  'dealer_btn': 1,
  'small_blind_pos': 2
  'big_blind_pos': 0,
  'next_player': 0,
  'small_blind_amount': 5,
  'street': 'showdown',
  'seats': [
    {'stack': 115, 'state': 'participating', 'name': 'p1', 'uuid': 'zjwhieqjlowtoogemqrjjo'},
    {'stack': 35, 'state': 'participating', 'name': 'p2', 'uuid': 'xgbpujiwtcccyicvfqffgy'},
    {'stack': 150, 'state': 'allin', 'name': 'p3', 'uuid': 'pnqfqsvgwkegkuwnzucvxw'}
  ],
  'community_card': ['CT', 'H9', 'S3', 'CA', 'H2'],
  'pot': {
    'main': {'amount': 150}, 
    'side': [{'amount': 20, 'eligibles': ['zjwhieqjlowtoogemqrjjo', 'xgbpujiwtcccyicvfqffgy']}]
   }
  'action_histories': {
    'preflop': [
      {'action': 'SMALLBLIND', 'amount': 5, 'add_amount': 5, 'uuid': 'pnqfqsvgwkegkuwnzucvxw'},
      {'action': 'BIGBLIND', 'amount': 10, 'add_amount': 5, 'uuid': 'zjwhieqjlowtoogemqrjjo'},
      {'action': 'CALL', 'amount': 10, 'uuid': 'xgbpujiwtcccyicvfqffgy', 'paid': 10},
      {'action': 'CALL', 'amount': 10, 'uuid': 'pnqfqsvgwkegkuwnzucvxw', 'paid': 5},
      {'action': 'CALL', 'amount': 10, 'uuid': 'zjwhieqjlowtoogemqrjjo', 'paid': 0}
    ],
    'flop': [
      {'action': 'RAISE', 'amount': 40, 'add_amount': 40, 'paid': 40, 'uuid': 'pnqfqsvgwkegkuwnzucvxw'},
      {'action': 'CALL', 'amount': 40, 'uuid': 'zjwhieqjlowtoogemqrjjo', 'paid': 40},
      {'action': 'CALL', 'amount': 40, 'uuid': 'xgbpujiwtcccyicvfqffgy', 'paid': 40}
    ]
    'turn': [
      {'action': 'RAISE', 'amount': 10, 'add_amount': 10, 'paid': 10, 'uuid': 'zjwhieqjlowtoogemqrjjo'},
      {'action': 'CALL', 'amount': 10, 'uuid': 'xgbpujiwtcccyicvfqffgy', 'paid': 10}
    ],
    'river': [
      {'action': 'CALL', 'amount': 0, 'uuid': 'zjwhieqjlowtoogemqrjjo', 'paid': 0},
      {'action': 'CALL', 'amount': 0, 'uuid': 'xgbpujiwtcccyicvfqffgy', 'paid': 0}
    ],

  }
 }
```

