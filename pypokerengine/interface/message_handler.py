from pypokerengine.players.base_poker_player import BasePokerPlayer

class MessageHandler:

  def __init__(self):
    self.algo_owner_map = {}

  def register_algorithm(self, uuid, algorithm):
    self.algo_owner_map[uuid] = algorithm

  def process_message(self, address, msg):
    receivers = self.__fetch_receivers(address)
    for receiver in receivers:
      if msg["type"] == 'ask':
        return receiver.respond_to_ask(msg["message"])
      elif msg["type"] == 'notification':
        receiver.receive_notification(msg["message"])
      else:
        raise ValueError("Received unexpected message which type is [%s]" % msg["type"])


  def __fetch_receivers(self, address):
    if address == -1:
      return self.algo_owner_map.values()
    else:
      if address not in self.algo_owner_map:
        raise ValueError("Received message its address [%s] is unknown" % address)
      return [self.algo_owner_map[address]]

