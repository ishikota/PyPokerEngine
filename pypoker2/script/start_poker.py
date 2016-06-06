# Resolve path configucation
import os
import sys

root = os.path.join(os.path.dirname(__file__), "..", "..")
src_path = os.path.join(root, "pypoker2")
sys.path.append(root)
sys.path.append(src_path)



# Start script code from here
from pypoker2.interface.dealer import Dealer
from pypoker2.players.sample.fold_man import PokerPlayer

# Config values
max_round_count = 10
small_blind_amount = 5
initial_stack = 100
players_info = []

def setup_players_info():
  return [{ "name": "player %d" % i, "algorithm": PokerPlayer() } for i in range(3)]

def start_game(players_info):
  dealer = Dealer(small_blind_amount, initial_stack)
  for info in players_info:
    dealer.register_player(info["name"], info["algorithm"])
  dealer.start_game(max_round_count)
  dealer.summary_game_result()

def main():
  players_info = setup_players_info()
  start_game(players_info)

if __name__ == '__main__':
  main()
