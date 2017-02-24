# Getting fine-grained control of the game
You can run the game and get game result like this.

```python
>>> from pypokerengine.api.game import setup_config, start_poker
>>> config = setup_config(max_round=10, initial_stack=100, small_blind_amount=5)
>>> config.register_player(name="fish_player", algorithm=FishPlayer())
>>> config.register_player(name="honest_player", algorithm=HonestPlayer())
>>> game_result = start_poker(config, verbose=1)
```

But sometimes you want more fine-grained control of the game like stepwise simulation from current state.  
PyPokerEngine provides `Emulator` class whcih enables you to simulate the game as you want.  

In this tutorial, we will create `EmulatorPlayer` to understand how to use `Emulator` class.  
(`EmulatorPlayer` would not be practical AI but good example to learn about `Emulator`)

## How to use Emulator
### Register game settings on Emulator
First we need to setup `Emulator` object with game settings like number of player.

```python
from pypokerengine.api.emulator import Emulator

emulator = Emulator()
emulator.set_game_rule(nb_player=2, max_round=10, sb_amount=5, ante_amount=0)
```

### Register player's model on Emulator
To simulate the game, we need to create **model of player**.  
*model of player* defines how player behaves in the game.  

Creating *model of player* is completely same step to create a player.  
(Override `BasePokerPlayer` class and implement its abstracted methods.)

Here is the very simple model which always declares same action.  

```python
class OneActionModel(BasePokerPlayer):

    FOLD, CALL, MIN_RAISE, MAX_RAISE = 0, 1, 2, 3

    def set_action(self, action):
        self.action = action

    def declare_action(self, valid_actions, hole_card, round_state):
        if self.FOLD == self.action:
            return valid_actions[0]['action'], valid_actions[0]['amount']
        elif self.CALL == self.action:
            return valid_actions[1]['action'], valid_actions[1]['amount']
        elif self.MIN_RAISE == self.action:
            return valid_actions[2]['action'], valid_actions[2]['amount']['min']
        elif self.MAX_RAISE == self.action:
            return valid_actions[2]['action'], valid_actions[2]['amount']['max']
        else:
            raise Exception("Invalid action [ %s ] is set" % self.action)
```

Next thing to do is register our model with emulator by `emulator.register_player` method.  
In the simulation, `Emulator` calls `player_model.declare_action` and apply returned action
to the simulation game.

```python
p1_uuid = # uuid of player1. you would get this information from game_info object
p1_model = # setup model of player1
emulator.register_player(uuid1, p1_model)
```

### Set up game state object

Before start simulation, we need to setup the `game_state` object
which represents the start point of the simulation.  
You can setup `game_state` object from `round_state` object like this.  
(You receive `round_state` object in callback method of `BasePokerPlayer` like `declare_action`.)

```python
from pypokerengine.utils.game_state_utils import\
        restore_game_state, attach_hole_card, attach_hole_card_from_deck

def setup_game_state(round_state, my_hole_card):
    game_state = restore_game_state(round_state)
    for player_info in round_state['seats']:
        if uuid == self.uuid:
            # Hole card of my player should be fixed. Because we know it.
            game_state = attach_hole_card(game_state, uuid, my_hole_card)
        else:
            # We don't know hole card of opponents. So attach them at random from deck.
            game_state = attach_hole_card_from_deck(game_state, uuid)
```

`round_state` object represents public information of the game.  
This means that it does not include information about hole card of each player.  
So we need to restore that information on `game_state` object.

### Start simulation and get updated game state object

Ok, everything is ready. Now you can progress or stop the game as you want by these methods.

- `emulator.apply_action(game_state, action, bet_amount)`
    - Use this method if you want to progress the game step-by-step.
- `emulator.run_until_round_finish(game_state)`
    - Use this method if you want to progress the game round-by-round.
- `emulator.run_until_game_finish(game_state)`
    - Use this method if you want to see the final result of the simulation.

Each method returns updated game state and events objects.  
(events object contains information of what happend during simulation like "player1 declared call", "street is updated to FLOP")  

```
>>> emulator.set_game_rule(nb_player, max_round=10, sb_amount=5, ante_amount=0)
>>> next_turn_state, events = emulator.apply_action(current_state, 'call', 10)
>>> round_finish_state, events = emulator.run_until_round_finish(current_state)
>>> game_finish_state, events = emulator.run_until_game_finish(current_state)
>>>
>>> current_state['round_count'], current_state['street'], current_state['next_player']
(1, 0, 0)  # street_flg == 0 means PREFLOP
>>> next_turn_state['round_count'], next_turn_state['street'], next_turn_state['next_player']
(1, 0, 1)
>>> round_finish_state['round_count'], round_finish_state['street'], round_finish_state['next_player']
(1, 5, 0)  # street_flg == 5 means SHOWDOWN
>>> game_finish_state['round_count'], game_finish_state['street'], game_finish_state['next_player']
(10, 5, 0)  # simulation is finished at 10 round because we set max_round=10
```

For more detail about `Emulator` or game_state, events objects,  
please checkout [Emulator documentation](../documentation/about_emulator.md).

## Create EmulatorPlayer
To sum up this tutorial, we will create sample AI `EmulatorPlayer` which uses `Emulator` to make a decision.  

To get accurate simulation result, fine-tuned player modeling is necessary.  
But in this tutorial, we will match `EmulatorPlayer` against only `FishPlayer`.  
So we use `FishPlayer` itself as model of opponent player.

The decision logic of `EmulatorPlayer` is like this.

1. fix action to evaluate (FOLD, CALL, MIN_RAISE or MAX_RAISE)
2. keep declaring fixed action in the simulation until current round finishes
3. remember the stack of EmulatorPlayer when simulation finished
4. after tried all actions, choose one which leads highest stack after the simulation

The implementation would be like this.

```python
try_actions = [FOLD, CALL, MIN_RAISE, MAX_RAISE]
action_score = [0, 0, 0, 0]

for try_action in try_actions:
    # my_model <- setup my model to declare "try_action" anytime
    simulation_results = []
    for i in range(NB_SIMULATION):
        # updated_state <- run the simulation until current round finishes
        # result <- fetch stack of EmulatorPlayer in the updated_state
        simulation_results.append(result)
    # action_score <- average simulation_results

# best_action <- choose action which gets highest action_score
return best_action
```

We don't explaing implementation detail here.  
Please check out complete implementation of `EmulatorPlayer` from [here]().

Let's match the `EmulatorPlayer` against our first AI `FishPlayer`.

```python
>>> from pypokerengine.api.game import setup_config, start_poker
>>> config = setup_config(max_round=10, initial_stack=100, small_blind_amount=5)
>>> config.register_player(name="fish_player", algorithm=FishPlayer())
>>> config.register_player(name="emulator_player", algorithm=EmulatorPlayer())
>>> game_result = start_poker(config, verbose=1)
Started the round 1
Street "preflop" started. (community card = [])
[debug_info] --> hole_card of emulator player is ['S6', 'H6']
[debug_info] --> average stack after simulation when declares FOLD : 95.0
[debug_info] --> average stack after simulation when declares CALL : 104.09
[debug_info] --> average stack after simulation when declares MIN_RAISE : 117.46
[debug_info] --> average stack after simulation when declares MAX_RAISE : 131.6
"emulator_player" declared "raise:100"
"fish_player" declared "call:100"
Street "flop" started. (community card = ['HQ', 'D2', 'D8'])
Street "turn" started. (community card = ['HQ', 'D2', 'D8', 'S7'])
Street "river" started. (community card = ['HQ', 'D2', 'D8', 'S7', 'SQ'])
"['emulator_player']" won the round 1 (stack = {'emulator_player': 200, 'fish_player': 0})
```

`EmulatorPlayer` choosed ALLIN with hole card ['S6', 'H6'] and beated `FishPlayer`!!  
(This result may look good. But `EmulatorPlayer` makes silly decision in most of the cases.)
