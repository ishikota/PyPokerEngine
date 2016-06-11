from pypokerengine.engine.pay_info import PayInfo
from pypokerengine.engine.poker_constants import PokerConstants as Const
from pypokerengine.engine.game_evaluator import GameEvaluator

class DataEncoder:

  @classmethod
  def encode_player(self, player, holecard=False):
    hash_ = {
        "name": player.name,
        "uuid": player.uuid,
        "stack": player.stack,
        "state": self.__payinfo_to_str(player.pay_info.status)
        }
    if holecard:
      hole_hash = {"hole_card": [str(card) for card in player.hole_card]}
      hash_.update(hole_hash)
    return hash_

  @classmethod
  def encode_seats(self, seats):
    return {
        "seats": [self.encode_player(player) for player in seats.players]
        }

  @classmethod
  def encode_pot(self, players):
    pots = GameEvaluator.create_pot(players)
    main = { "amount": pots[0]["amount"] }
    gen_hsh = lambda sidepot: { "amount": sidepot["amount"], "eligibles": sidepot["eligibles"] }
    side = [ gen_hsh(sidepot) for sidepot in pots[1:] ]
    return { "main": main, "side": side }

  @classmethod
  def encode_game_information(self, config, seats):
    hsh = {
        "player_num" : len(seats.players),
        "rule": {
          "initial_stack": config["initial_stack"],
          "max_round": config["max_round"],
          "small_blind_amount": config["small_blind_amount"]
        }
    }
    hsh.update(self.encode_seats(seats))
    return hsh

  @classmethod
  def encode_valid_actions(self, call_amount, min_bet_amount, max_bet_amount):
    return {
        "valid_actions": [
          { "action": "fold", "amount": 0 },
          { "action": "call", "amount": call_amount },
          { "action": "raise", "amount": { "min": min_bet_amount, "max": max_bet_amount } }
        ]
    }

  @classmethod
  def encode_action(self, player, action, amount):
    return {
        "player_uuid": player.uuid,
        "action": action,
        "amount": amount
        }

  @classmethod
  def encode_street(self, street):
    return {
        "street": self.__street_to_str(street)
        }

  @classmethod
  def encode_action_histories(self, table):
    return { "action_histories": self.__order_histories(table.dealer_btn, table.seats.players) }

  @classmethod
  def encode_winners(self, winners):
    return { "winners": self.__encode_players(winners) }

  @classmethod
  def encode_round_state(self, state):
    hsh = {
        "street": self.__street_to_str(state["street"]),
        "pot": self.encode_pot(state["table"].seats.players),
        "community_card": [str(card) for card in state["table"].get_community_card()],
        "dealer_btn": state["table"].dealer_btn,
        "next_player": state["next_player"]
    }
    hsh.update(self.encode_seats(state["table"].seats))
    return hsh


  @classmethod
  def __payinfo_to_str(self, status):
    if status == PayInfo.PAY_TILL_END:
      return "participating"
    if status == PayInfo.ALLIN:
      return "allin"
    if status == PayInfo.FOLDED:
      return "folded"

  @classmethod
  def __street_to_str(self, street):
    if street == Const.Street.PREFLOP:
      return "preflop"
    if street == Const.Street.FLOP:
      return "flop"
    if street == Const.Street.TURN:
      return "turn"
    if street == Const.Street.RIVER:
      return "river"
    if street == Const.Street.SHOWDOWN:
      return "showdown"

  @classmethod
  def __encode_players(self, players):
    return [self.encode_player(player) for player in players]

  @classmethod
  def __order_histories(self, start_pos, players):
    ordered_players = [players[(start_pos+i)%len(players)] for i in range(len(players))]
    all_player_histories = [p.action_histories[::] for p in ordered_players]
    max_len = max([len(h) for h in all_player_histories])
    unified_histories = [self.__unify_length(max_len, l) for l in all_player_histories]
    ordered_histories = reduce(lambda acc, zp: acc + list(zp), zip(*unified_histories), [])
    return [history for history in ordered_histories if not history is None]

  @classmethod
  def __unify_length(self, max_len, lst):
    for _ in range(max_len-len(lst)):
      lst.append(None)
    return lst


