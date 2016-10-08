# PyPokerEngine
Poker engine for poker AI development in Python

# Tutorial
This tutorial leads you to start point of poker AI development!!
#### TODO list of this tutorial
1. Create simple AI which always returns same action.
2. Play AI vs AI poker game and see its result.

#### Clone this repository
Before start AI development, we need to clone this repository like below.
```
cd /Users/kota/dev
git clone https://github.com/ishikota/PyPokerEngine
```
We assume you cloned PyPokerEngine directory at `/Users/kota/dev` in following section.

## Create first AI
In this section, we create AI which always declare FOLD action.  
To create poker AI, what we do is following

1. Create PokerPlayer class which is subclass of [`PypokerEngine.players.BasePokerPlayer`](https://github.com/ishikota/PyPokerEngine/blob/master/pypokerengine/players/base_poker_player.py).
2. Implement abstract methods which inherits from `BasePokerPlayer` class.


Create below file. (We assume you saved at `/Users/kota/dev/fold_player.py`)  
(**CAUTION:** Class name of AI must be **`PokerPlayer`**. Because our script create instance of your AI by using class name)

```python
from pypokerengine.players.base_poker_player import BasePokerPlayer

class PokerPlayer(BasePokerPlayer):  # Class name must be PokerPlayer !!

  def declare_action(self, hole_card, valid_actions, round_state, action_histories):
    return 'fold', 0   # action returned here is sent to the poker engine

  def receive_game_start_message(self, game_info):
    pass

  def receive_round_start_message(self, hole_card, seats):
    pass

  def receive_street_start_message(self, street, round_state):
    pass

  def receive_game_update_message(self, action, round_state, action_histories):
    pass

  def receive_round_result_message(self, winners, round_state):
    pass

  def receive_game_result_message(self, seats):
    pass
```
If you are interested in what each callback method receives, See [AI_CALLBACK_FORMAT.md](https://github.com/ishikota/PyPokerEngine/blob/master/AI_CALLBACK_FORMAT.md).

## Play AI vs AI poker game
In this secrtion, we start poker game which is played by our AI and see its result.  
To start the game, what we do is following

1. Create game config file
2. Start the game with created config file
3. See its result

### Create config.json
Create json formatted config file like below. (We assume you saved at `/Users/kota/dev/config.json`)  

```json
{
  "max_round_count"    : 10,
  "small_blind_amount" : 5,
  "initial_stack"      : 100,
  "players_info" : [
    {
      "name" : "player1",
      "algorithm_path": "/Users/kota/dev/fold_player.py"
    },
    {
      "name" : "player2",
      "algorithm_path": "/Users/kota/dev/fold_player.py"
    },
    {
      "name" : "player3",
      "algorithm_path": "/Users/kota/dev/fold_player.py"
    }
  ]
}

```

### Start the game with our AI
Run below command will start the poker game!!  
```
PyPokerEngine/script/start_poker --config_path /Users/kota/dev/config.json
```
Game is played by 3 AI players for 10 rounds. (because we defined in config.json)  
After finished the game, game result will be output on console like below.
```json
{
   "game_information":{
      "player_num":3,
      "rule":{
         "max_round":10,
         "initial_stack":100,
         "small_blind_amount":5
      },
      "seats":[
         {
            "stack":95,
            "state":"participating",
            "name":"player1",
            "uuid":"xzdccxhiwcljedqyyekgej"
         },
         {
            "stack":105,
            "state":"participating",
            "name":"player2",
            "uuid":"nbrabjbrgpatztgevxmqnl"
         },
         {
            "stack":100,
            "state":"participating",
            "name":"player3",
            "uuid":"tahxlyrdwaahrdjvhwhizb"
         }
      ]
   },
   "message_type":"game_result_message"
}
```
