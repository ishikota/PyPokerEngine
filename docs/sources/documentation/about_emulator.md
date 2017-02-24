# About Emulator
`Emulator` gives you a fine-grained control of the game.  
The common usage of `Emulator` would be

1. Set game settings on emulator
2. Setup GameState object which represents current game state
3. Run simulation and get updated GameState object

So the code would be like this.
```python
from pypokerengine.api.emulator import Emulator

# 1. Set game settings on emulator
emulator = Emulator()
emulator.set_game_rule(nb_player, final_round, sb_amount, ante)
emulator.set_game_rule(player_num=3, max_round=10, small_blind_amount=5, ante_amount=1)

# 2. Setup GameState object
players_info = {
    "uuid-1": { "name": "player1", "stack": 100 },
    "uuid-2": { "name": "player2", "stack": 100 },
    "uuid-3": { "name": "player3", "stack": 80 }
}
initial_state = emulator.generate_initial_game_state(players_info)
game_state, events = emulator.start_new_round(initial_state)

# 3. Run simulation and get updated GameState object
updated_state, events = emulator.apply_action(game_state, "call", 10)
```

You can run step-wise simulation with `Emulator`.  
This feature would be useful when you use reinforcement learning method.

## GameState object
We need to prepare GameState object before run simulation.  
You can setup GameState object in two ways.

### 1. Generate clean game state with Emulator
If you want to generate clean (initial) GameState object,
you use `emulator.generate_initial_game_state` method.

This method requires players information of the game in below format.

```python
players_info = {
  "uuid_of_player1": { "name": "name_of_player1", "stack": initial_stack_of_player1 },
  "uuid_of_player2": { "name": "name_of_player2", "stack": initial_stack_of_player2 },
  ...
}
```

So you can get clean GameState object like this.
```python
initial_game_state = emulator.generate_initial_game_state(players_info)
```

**Please do not forget to start the round manually by `emulator.start_new_round` before run simulation**  
(because clean GameState object represents the state before start the game).
```python
>>> initial_game_state
{'round_count': 0, 'next_player': None, 'street': 0, 'small_blind_amount': 5}, 'table': <pypokerengine.engine.table.Table instance at 0x10666cc68>}
>>> game_state, events = emulator.start_new_round(initial_game_state)
>>> game_state
{'round_count': 1, 'next_player': 0, 'street': 0, 'small_blind_amount': 5}, 'table': <pypokerengine.engine.table.Table instance at 0x1066bca28>}
```

### 2. Restore from `round_state` object
`round_state` object is the public information of the game state 
which passed by callback methods of `BasePokerPlayer` like `declare_action`.

If you want to generate the GameState object which represents state of `round_state`,
you can use `game_state_utils.restore_game_state(round_state)`.

`round_state` object represents public information of the game.
This means that it does not include information about hole card of each player.
So you need to restore that information on GameState object by your hand.

If you set hole card at random, you can use below code.
```python
from pypokerengine.utils.game_state_utils import restore_game_state, attach_hole_card_from_deck

game_state = restore_game_state(round_state)
for player in game_state["table"].seats.players:
    game_state = attach_hole_card_from_deck(game_state, player.uuid)
```

If you want to set specific card on specific player, the code would be...  
(below code sets holecard ['SA', 'DA'] on player which has uuid "uuid-1" and sets at random on others)
```python
from pypokerengine.utils.game_state_utils import restore_game_state, attach_hole_card_from_deck, attach_hole_card
from pypokerengine.utils.card_utils import gen_cards

game_state = restore_game_state(round_state)
for player in game_state["table"].seats.players:
    if player.uuid == "uuid-1":
        holecard = gen_cards(['SA', 'DA'])
        game_state = attach_hole_card(game_state, player.uuid, hole_card)
    else:
      game_state = attach_hole_card_from_deck(game_state, player.uuid)
```

## Event object
When you run simulation bia `Emulator`, you receive updated GameState object and list of Event object.  
Event object contains the information of event which happend during simulation.  

For example, Event objects of `emulator.start_new_round` would be ...
```python
>>> game_state, events = emulator.start_new_round(initial_state)
>>> events
[
  {
   'type': 'event_new_street',
   'street': 'preflop',
   'round_state': ...
  },
  {
   'type': 'event_ask_player',
   'uuid': 'uuid-1',
   'valid_actions': [{'action': 'fold', 'amount': 0}, ...]
  }
]
```

There are 4 types of Event object.

### 1. New Street Event
This event is contained if new street is started during simulation.  

- `type` : "event_new_street"
- `street` : one of ["preflop", "flop", "turn", "river"]
- `round_state`: `round_state` object of when this event was occurred

### 2. Ask Player Event
This event is contained when any player is asked his action.

- `type` : "event_ask_player"
- `uuid` : uuid of player who asked the action
- `valid_actions`: information of action which is valid in the situation.
- `round_state`: `round_state` object of when this event was occurred

### 3. Round Finish Event
This event is contained when a round is finished.

- `type` : "event_round_finish"
- `winners`: information about the winner of round
- `round_state`: `round_state` object of when this event was occurred

### 4. Game Finish Event
This event is contained when a game is finished.

- `type` : "event_game_finish"
- `players`: information about each player like his stack, uuid, ...

