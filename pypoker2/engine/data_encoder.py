from pypoker2.engine.pay_info import PayInfo
from pypoker2.engine.round_manager import RoundManager
from pypoker2.engine.game_evaluator import GameEvaluator

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
    return { "TODO": "under construction" }

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
    return { "TODO": "under construction" }

  @classmethod
  def encode_winners(self, winners):
    return { "TODO": "under construction" }

  @classmethod
  def encode_round_state(self, round_manager, table):
    return { "TODO": "under construction" }

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
    if street == RoundManager.PREFLOP:
      return "preflop"
    if street == RoundManager.FLOP:
      return "flop"
    if street == RoundManager.TURN:
      return "turn"
    if street == RoundManager.RIVER:
      return "river"
    if street == RoundManager.SHOWDOWN:
      return "showdown"

