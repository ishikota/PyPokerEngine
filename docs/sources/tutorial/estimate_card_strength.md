# How to Estimate Hand Strength
The hand strength is key factor to make a decision in poker.  
If our hole card is ['H4', 'D7'] and community cards are ['D3', 'C5', 'C6'],
we would take agreessive action.

We can make an estimate of hand strength. But how to teach it to our AI?  
One simple way is *running lots of simulations and use average win rate as estimation*.

In this tutorial, we will create `HonestPlayer` which declares CALL only if his hand is good.

## Estimate Hand Strength by simulation
The code to estimates win rate of hands in three players game would be like this.
```python
nb_simulation = 1000
nb_player = 3
hole_card = ['H4', 'D7']
community_card = ['D3', 'C5', 'C6']

def estimate_hand_strength(nb_simulation, nb_player, hole_card, community_card):
    simulation_results = []
    for i in range(nb_simulation):
        opponents_cards = []
        for j in range(nb_player-1):  # nb_opponents = nb_player - 1
            opponents_cards.append(draw_cards_from_deck(num=2))
        nb_need_community = 5 - len(community_card)
        community_card.append(draw_cards_from_deck(num=nb_need_community))
        result = observe_game_result(hole_card, community_card, opponents_cards)  # return 1 if win else 0
        simulation_results.append(result)
    average_win_rate = 1.0 * sum(simulation_results) / len(simulation_results)
    return average_win_rate
```

PyPokerEngine prepares this method for you as `pypokerengine.utils.card_utils.estimate_hole_card_win_rate`.  
Let's use it !!

```python
>>> from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate
>>> hole_card = gen_cards(['H4', 'D7'])
>>> community_card = gen_cards(['D3', 'C5', 'C6'])
>>> estimate_hole_card_win_rate(nb_simulation=1000, nb_player=3, hole_card=hole_card, community_card=community_card)
0.825
>>> estimate_hole_card_win_rate(nb_simulation=1000, nb_player=3, hole_card=hole_card, community_card=community_card)
0.838
```

## Create HonestPlayer
Ok. Let's start `HonestPlayer` development.  
The behavior of `HonestPlayer` is very simple (because he is honest).

1. declare CALL if estimation of win_rate is grater than 1/nb_player
2. declare FOLD othrewise

The code would be...
```python
from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate

NB_SIMULATION = 1000

class HonestPlayer(BasePokerPlayer):

    def declare_action(self, valid_actions, hole_card, round_state):
        community_card = round_state['community_card']
        win_rate = estimate_hole_card_win_rate(
                nb_simulation=NB_SIMULATION,
                nb_player=self.nb_player,
                hole_card=gen_cards(hole_card),
                community_card=gen_cards(community_card)
                )
        if win_rate >= 1.0 / self.nb_player:
            action = valid_actions[1]  # fetch CALL action info
        else:
            action = valid_actions[0]  # fetch FOLD action info
        return action['action'], action['amount']

    def receive_game_start_message(self, game_info):
        self.nb_player = game_info['player_num']

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass
```

Let's match `HonestPlayer` against `FishPlayer`.

```python
>>> from pypokerengine.api.game import setup_config, start_poker
>>> config = setup_config(max_round=10, initial_stack=100, small_blind_amount=5)
>>> config.register_player(name="fish_player", algorithm=FishPlayer())
>>> config.register_player(name="honest_player", algorithm=HonestPlayer())
>>> game_result = start_poker(config, verbose=1)
>>> for player_info in game_result["players"]:
...     print player_info
...
{'stack': 145, 'state': 'participating', 'name': 'fish_player', 'uuid': 'dziwzwkoqadaobrjxrfwog'}
{'stack': 55, 'state': 'participating', 'name': 'honest_player', 'uuid': 'lcyzcxzbkuzvoyzlkommyt'}
```

As you see, `HonestPlayer` cannot win `FishPlayer`.  
Because `HonestPlayer` always declares FOLD except when he has confident hands.  
This strategy may sound good but he loses lots of money until he goes to SHOWDOWN.

Creating practical poker AI is not easy unlike tick-tack-toe AI.  
It would require some game specific heuristics or machine learning techniques.  
But we believe that you can do it!!
