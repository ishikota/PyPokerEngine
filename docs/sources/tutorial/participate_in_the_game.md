# Play poker with AI
The simple way to evaluate AI strength is **playing poker with AI**.  
In this tutorial, we will create `ConsolePlayer` to participate in the game via console.  

## Create ConsolePlayer
we create `ConsolePlayer` in the same way as [creating our first AI](../index.md).  
(Override `BasePokerPlayer` class and implement abstracted methods)

The requirements for `ConsolePlayer` are

1. display game information on console in formatted way
2. accept player's action from console and apply it on the game

So the implementation would be like this.  
(This code does not handle errors for simplicity.
You can check complete code from [here](https://github.com/ishikota/PyPokerEngine/blob/master/examples/players/console_player.py))

```
import pypokerengine.utils.visualize_utils as U

class ConsolePlayer(BasePokerPlayer):

    def declare_action(self, valid_actions, hole_card, round_state):
        print(U.visualize_declare_action(valid_actions, hole_card, round_state, self.uuid))
        action, amount = self._receive_action_from_console(valid_actions)
        return action, amount

    def receive_game_start_message(self, game_info):
        print(U.visualize_game_start(game_info, self.uuid))
        self._wait_until_input()

    def receive_round_start_message(self, round_count, hole_card, seats):
        print(U.visualize_round_start(round_count, hole_card, seats, self.uuid))
        self._wait_until_input()

    def receive_street_start_message(self, street, round_state):
        print(U.visualize_street_start(street, round_state, self.uuid))
        self._wait_until_input()

    def receive_game_update_message(self, new_action, round_state):
        print(U.visualize_game_update(new_action, round_state, self.uuid))
        self._wait_until_input()

    def receive_round_result_message(self, winners, hand_info, round_state):
        print(U.visualize_round_result(winners, hand_info, round_state, self.uuid))
        self._wait_until_input()

    def _wait_until_input(self):
        raw_input("Enter some key to continue ...")

    # FIXME: This code would be crash if receives invalid input.
    #        So you should add error handling properly.
    def _receive_action_from_console(self, valid_actions):
        action = raw_input("Enter action to declare >> ")
        if action == 'fold': amount = 0
        if action == 'call':  amount = valid_actions[1]['action']
        if action == 'raise':  amount = int(raw_input("Enter raise amount >> "))
        return action, amount
```

## Beat Our First AI by Our Own Hands
Now we are ready to play the game. Let's try to beat our first AI `FishPlayer`!!  

```python
from pypokerengine.api.game import setup_config, start_poker

config = setup_config(max_round=10, initial_stack=100, small_blind_amount=5)
config.register_player(name="fish_player", algorithm=FishPlayer())
config.register_player(name="human_player", algorithm=ConsolePlayer())
game_result = start_poker(config, verbose=0)  # verbose=0 because game progress is visualized by ConsolePlayer
```

Game informations would be displayed on console like below.

```python
-- Game start (UUID = qrnewmfzuyacjscxpfftgy) --
======================================================================
-- rule --
  - 2 players game
  - 10 round
  - start stack = 100
  -        ante = 0
  - small blind = 5
======================================================================
Enter some key to continue ... <ENTER>

-- Round 1 start (UUID = qrnewmfzuyacjscxpfftgy) --
======================================================================
-- hole card --
  - ['CA', 'D2']
-- players information --
  - 0 : fish_player (vhchlzkojrabhiomwdbpem) => state : participating, stack : 90
  - 1 : human_player (qrnewmfzuyacjscxpfftgy) => state : participating, stack : 95
======================================================================
Enter some key to continue ... <ENTER>

-- New street start (UUID = qrnewmfzuyacjscxpfftgy) --
======================================================================
-- street --
  - preflop
======================================================================
Enter some key to continue ...
```

Good! We have Ace in hole card ! Let's ALLIN !!

```
-- Declare your action (UUID = qrnewmfzuyacjscxpfftgy) --
======================================================================
-- valid actions --
  - fold
  - call: 10
  - raise: [15, 100]
-- hole card --
  - ['CA', 'D2']
-- round state --
  - dealer btn : fish_player
  - street : preflop
  - community card : []
  - pot : main = 15, side = []
  - players information
    - 0 : fish_player (vhchlzkojrabhiomwdbpem) => state : participating, stack : 90 <= BB
    - 1 : human_player (qrnewmfzuyacjscxpfftgy) => state : participating, stack : 95 <= SB, CURRENT
  - action histories
    - preflop
      - {'action': 'SMALLBLIND', 'player': 'human_player (uuid=qrnewmfzuyacjscxpfftgy)', 'amount': 5, 'add_amount': 5}
      - {'action': 'BIGBLIND', 'player': 'fish_player (uuid=vhchlzkojrabhiomwdbpem)', 'amount': 10, 'add_amount': 5}
======================================================================
Enter action to declare >> raise
Enter raise amount >> 100
```

FishPlayer declares CALL action as we expected !
```
-- Game update (UUID = qrnewmfzuyacjscxpfftgy) --
======================================================================
-- new action --
  - fish_player (vhchlzkojrabhiomwdbpem) declared call: 100
-- round state --
  - dealer btn : fish_player
  - street : preflop
  - community card : []
  - pot : main = 200, side = [{'amount': 0, 'eligibles': ['vhchlzkojrabhiomwdbpem', 'qrnewmfzuyacjscxpfftgy']}, {'amount': 0, 'eligibles': ['vhchlzkojrabhiomwdbpem', 'qrnewmfzuyacjscxpfftgy']}]
  - players information
    - 0 : fish_player (vhchlzkojrabhiomwdbpem) => state : allin, stack : 0 <= BB, CURRENT
    - 1 : human_player (qrnewmfzuyacjscxpfftgy) => state : allin, stack : 0 <= SB
  - action histories
    - preflop
      - {'action': 'SMALLBLIND', 'player': 'human_player (uuid=qrnewmfzuyacjscxpfftgy)', 'amount': 5, 'add_amount': 5}
      - {'action': 'BIGBLIND', 'player': 'fish_player (uuid=vhchlzkojrabhiomwdbpem)', 'amount': 10, 'add_amount': 5}
      - {'add_amount': 90, 'paid': 95, 'player': 'human_player (uuid=qrnewmfzuyacjscxpfftgy)', 'amount': 100, 'action': 'RAISE'}
      - {'action': 'CALL', 'player': 'fish_player (uuid=vhchlzkojrabhiomwdbpem)', 'amount': 100, 'paid': 90}
======================================================================
Enter some key to continue ...
```

Round result is ...

```
-- Round result (UUID = qrnewmfzuyacjscxpfftgy) --
======================================================================
-- winners --
  - fish_player (vhchlzkojrabhiomwdbpem) => state : allin, stack : 200
-- hand info --
  - fish_player (vhchlzkojrabhiomwdbpem)
    - hand => TWOPAIR (high=14, low=8)
    - hole => [14, 8]
  - human_player (qrnewmfzuyacjscxpfftgy)
    - hand => TWOPAIR (high=14, low=2)
    - hole => [14, 2]
-- round state --
  - dealer btn : fish_player
  - street : showdown
  - community card : ['H7', 'HA', 'S2', 'H8', 'D6']
  - pot : main = 200, side = [{'amount': 0, 'eligibles': ['vhchlzkojrabhiomwdbpem', 'qrnewmfzuyacjscxpfftgy']}, {'amount': 0, 'eligibles': ['vhchlzkojrabhiomwdbpem', 'qrnewmfzuyacjscxpfftgy']}]
  - players information
    - 0 : fish_player (vhchlzkojrabhiomwdbpem) => state : allin, stack : 200 <= BB
    - 1 : human_player (qrnewmfzuyacjscxpfftgy) => state : allin, stack : 0 <= SB
  - action histories
    - preflop
      - {'action': 'SMALLBLIND', 'player': 'human_player (uuid=qrnewmfzuyacjscxpfftgy)', 'amount': 5, 'add_amount': 5}
      - {'action': 'BIGBLIND', 'player': 'fish_player (uuid=vhchlzkojrabhiomwdbpem)', 'amount': 10, 'add_amount': 5}
      - {'add_amount': 90, 'paid': 95, 'player': 'human_player (uuid=qrnewmfzuyacjscxpfftgy)', 'amount': 100, 'action': 'RAISE'}
      - {'action': 'CALL', 'player': 'fish_player (uuid=vhchlzkojrabhiomwdbpem)', 'amount': 100, 'paid': 90}
======================================================================
```

OMG... FishPlayer also has Ace(the rank of Ace is 14) in his hole card...

We cannot beat FishPlayer.  
But I think you can understand how to compete with your own AIs.
