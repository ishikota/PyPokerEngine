from functools import reduce

from pypokerengine.engine.pay_info import PayInfo
from pypokerengine.engine.poker_constants import PokerConstants as Const
from pypokerengine.engine.game_evaluator import GameEvaluator

class DataEncoder:

  PAY_INFO_PAY_TILL_END_STR = "participating"
  PAY_INFO_ALLIN_STR = "allin"
  PAY_INFO_FOLDED_STR = "folded"

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
    gen_hsh = lambda sidepot: \
            { "amount": sidepot["amount"], "eligibles": [p.uuid for p in sidepot["eligibles"]] }
    side = [ gen_hsh(sidepot) for sidepot in pots[1:] ]
    return { "main": main, "side": side }

  @classmethod
  def encode_game_information(self, config, seats):
    hsh = {
        "player_num" : len(seats.players),
        "rule": {
          "initial_stack": config["initial_stack"],
          "max_round": config["max_round"],
          "small_blind_amount": config["small_blind_amount"],
          "ante": config["ante"],
          "blind_structure": config["blind_structure"]
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
    all_street_histories = [[player.round_action_histories[street] for player in table.seats.players] for street in range(4)]
    past_street_histories = [histories for histories in all_street_histories if any([e is not None for e in histories])]
    current_street_histories = [player.action_histories for player in table.seats.players]
    street_histories = past_street_histories + [current_street_histories]
    street_histories = [self.__order_histories(table.sb_pos(), histories) for histories in street_histories]
    street_name = ["preflop", "flop", "turn", "river"]
    action_histories = { name:histories for name, histories in zip(street_name, street_histories) }
    return { "action_histories": action_histories }

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
        "next_player": state["next_player"],
        "small_blind_pos": state["table"].sb_pos(),
        "big_blind_pos": state["table"].bb_pos(),
        "round_count": state["round_count"],
        "small_blind_amount": state["small_blind_amount"]
    }
    hsh.update(self.encode_seats(state["table"].seats))
    hsh.update(self.encode_action_histories(state["table"]))
    return hsh


  @classmethod
  def __payinfo_to_str(self, status):
    if status == PayInfo.PAY_TILL_END:
      return self.PAY_INFO_PAY_TILL_END_STR
    if status == PayInfo.ALLIN:
      return self.PAY_INFO_ALLIN_STR
    if status == PayInfo.FOLDED:
      return self.PAY_INFO_FOLDED_STR

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
  def __order_histories(self, start_pos, player_histories):
    ordered_player_histories = [player_histories[(start_pos+i)%len(player_histories)] for i in range(len(player_histories))]
    all_player_histories = [histories[::] for histories in ordered_player_histories]
    max_len = max([len(h) for h in all_player_histories])
    unified_histories = [self.__unify_length(max_len, l) for l in all_player_histories]
    ordered_histories = reduce(lambda acc, zp: acc + list(zp), zip(*unified_histories), [])
    return [history for history in ordered_histories if not history is None]

  @classmethod
  def __unify_length(self, max_len, lst):
    for _ in range(max_len-len(lst)):
      lst.append(None)
    return lst


