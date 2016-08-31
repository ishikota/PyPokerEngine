# AI CALLBACK FORMAT

#### `declare_action(self, hole_card, valid_actions, round_state, action_histories)`
- hole_card
```
['SJ', 'ST']
```
- valid_actions
```
[
  {'action': 'fold', 'amount': 0},
  {'action': 'call', 'amount': 10},
  {'action': 'raise', 'amount': {'max': 105, 'min': 15}}
]
```
- round_state
```
{
  'dealer_btn': 1,
  'street': 'preflop',
  'seats': [
    {'stack': 85, 'state': 'participating', 'name': u'player1', 'uuid': 'ciglbcevkvoqzguqvnyhcb'},
    {'stack': 100, 'state': 'participating', 'name': u'player2', 'uuid': 'zjttlanhlvpqzebrwmieho'}
  ],
  'next_player': 1,
  'community_card': [],
  'pot': {
    'main': {'amount': 15},
    'side': []
  }
}
```
- action_histories
```
{
  'action_histories': [
    {'action': 'SMALLBLIND', 'amount': 5, 'add_amount': 5},
    {'action': 'BIGBLIND', 'amount': 10, 'add_amount': 5}
  ]
}
```

#### `receive_game_start_message(self, game_info)`
- game_info
```
{
  'player_num': 2,
  'rule': {'max_round': 10, 'initial_stack': 100, 'small_blind_amount': 5},
  'seats': [
    {'stack': 100, 'state': 'participating', 'name': u'player1', 'uuid': 'eztfoiwosxdarwgujfyivb'},
    {'stack': 100, 'state': 'participating', 'name': u'player2', 'uuid': 'jfsjzfyuvtverhaghbhqfy'}
  ]
}
```

#### `receive_round_start_message(self, hole_card, seats)`
- hole_card
```
['SJ', 'ST']
```
- seats
```
[
  {'stack': 95, 'state': 'participating', 'name': u'player1', 'uuid': 'eztfoiwosxdarwgujfyivb'}, 
  {'stack': 90, 'state': 'participating', 'name': u'player2', 'uuid': 'jfsjzfyuvtverhaghbhqfy'}
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
  'dealer_btn': 0,
  'street': 'preflop',
  'seats': [
    {'stack': 95, 'state': 'participating', 'name': u'player1', 'uuid': 'eztfoiwosxdarwgujfyivb'},
    {'stack': 90, 'state': 'participating', 'name': u'player2', 'uuid': 'jfsjzfyuvtverhaghbhqfy'}
  ],
  'next_player': 0,
  'community_card': [],
  'pot': {
    'main': {'amount': 15},
    'side': []
  }
}
```

#### `receive_game_update_message(self, action, round_state, action_histories)`
- action
```
{
  'player_uuid': 'eztfoiwosxdarwgujfyivb',
  'action': 'fold',
  'amount': 0
}
```
- round_state
```
{
  'dealer_btn': 0,
  'street': 'preflop',
  'seats': [
    {'stack': 95, 'state': 'folded', 'name': u'player1', 'uuid': 'eztfoiwosxdarwgujfyivb'},
    {'stack': 90, 'state': 'participating', 'name': u'player2', 'uuid': 'jfsjzfyuvtverhaghbhqfy'}
  ],
  'next_player': 0,
  'community_card': [],
  'pot': {
    'main': {'amount': 15},
    'side': []
  }
}
```
- action_histories
```
{
  'action_histories': [
    {'action': 'SMALLBLIND', 'amount': 5, 'add_amount': 5}, 
    {'action': 'BIGBLIND', 'amount': 10, 'add_amount': 5},
    {'action': 'FOLD'}
  ]
}
```

#### `receive_round_result_message(self, winners, round_state)`
- winners
```
[
  {'stack': 105, 'state': 'participating', 'name': u'player2', 'uuid': 'jfsjzfyuvtverhaghbhqfy'}
]
```
- round_state
```
{
  'dealer_btn': 0,
  'street': None,
  'seats': [
    {'stack': 95, 'state': 'participating', 'name': u'player1', 'uuid': 'eztfoiwosxdarwgujfyivb'}, 
    {'stack': 105, 'state': 'participating', 'name': u'player2', 'uuid': 'jfsjzfyuvtverhaghbhqfy'}
  ],
  'next_player': 0, 
  'community_card': [],
  'pot': {
    'main': {'amount': 0},
    'side': []
  }
}
```

