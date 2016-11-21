from pypokerengine.players import BasePokerPlayer

class ConsolePlayer(BasePokerPlayer):

  def __init__(self, input_receiver=None):
    self.input_receiver = input_receiver if input_receiver else self.__gen_raw_input_wrapper()
    self.writer = ConsoleWriter(self)

  def declare_action(self, valid_actions, hole_card, round_state):
    self.writer.write_declare_action(valid_actions, hole_card, round_state)
    action, amount = self.__receive_action_from_console(valid_actions)
    return action, amount

  def receive_game_start_message(self, game_info):
    self.writer.write_game_start_message(game_info)
    self.__wait_until_input()

  def receive_round_start_message(self, round_count, hole_card, seats):
    self.writer.write_round_start_message(round_count, hole_card, seats)
    self.__wait_until_input()

  def receive_street_start_message(self, street, round_state):
    self.writer.write_street_start_message(street, round_state)
    self.__wait_until_input()

  def receive_game_update_message(self, new_action, round_state):
    self.writer.write_game_update_message(new_action, round_state)
    self.__wait_until_input()

  def receive_round_result_message(self, winners, hand_info, round_state):
    self.writer.write_round_result_message(winners, hand_info, round_state)
    self.__wait_until_input()

  def __wait_until_input(self):
    raw_input("Enter some key to continue ...")

  def __gen_raw_input_wrapper(self):
    return lambda msg: raw_input(msg)

  def __receive_action_from_console(self, valid_actions):
    flg = self.input_receiver('Enter f(fold), c(call), r(raise).\n >> ')
    if flg in self.__gen_valid_flg(valid_actions):
      if flg == 'f':
        return valid_actions[0]['action'], valid_actions[0]['amount']
      elif flg == 'c':
        return valid_actions[1]['action'], valid_actions[1]['amount']
      elif flg == 'r':
        valid_amounts = valid_actions[2]['amount']
        raise_amount = self.__receive_raise_amount_from_console(valid_amounts['min'], valid_amounts['max'])
        return valid_actions[2]['action'], raise_amount
    else:
      return self.__receive_action_from_console(valid_actions)

  def __gen_valid_flg(self, valid_actions):
    flgs = ['f', 'c']
    is_raise_possible = valid_actions[2]['amount']['min'] != -1
    if is_raise_possible:
      flgs.append('r')
    return flgs

  def __receive_raise_amount_from_console(self, min_amount, max_amount):
    raw_amount = self.input_receiver("valid raise range = [%d, %d]" % (min_amount, max_amount))
    try:
      amount = int(raw_amount)
      if min_amount <= amount and amount <= max_amount:
        return amount
      else:
        print "Invalid raise amount %d. Try again."
        return self.__receive_raise_amount_from_console(min_amount, max_amount)
    except:
      print "Invalid input received. Try again."
      return self.__receive_raise_amount_from_console(min_amount, max_amount)

class ConsoleWriter:

  def __init__(self, algo):
    self.algo = algo

  def write_declare_action(self, valid_actions, hole_card, round_state):
    print ' -- Declare your action %s --' % self.__gen_uuid_info()
    print '=============================================='
    print '-- hole card --'
    print ' hole card : %s' % hole_card
    print '-- valid actions --'
    print ' fold, call:%d, raise: [%d, %d]' % (valid_actions[1]['amount'], valid_actions[2]['amount']['min'], valid_actions[2]['amount']['max'])
    print '-- round state --'
    print ' Dealer Btn : %s ' % round_state['seats'][round_state['dealer_btn']]['name']
    print ' Street : %s' % round_state['street']
    print ' Community Card : %s' % round_state['community_card']
    print ' Pot : main = %d, side = %s' % (round_state['pot']['main']['amount'], round_state['pot']['side'])
    print ' Players'
    for position, player in enumerate(round_state['seats']):
      player_str = self.write_player(player, round_state)
      player_str = player_str.replace("NEXT", "CURRENT")
      print ' %d : %s' % (position, player_str)
    print '-- action histories --'
    fetch_name = lambda uuid: [player["name"] for player in round_state["seats"] if player["uuid"]==uuid][0]
    sort_key = lambda e: {"preflop":0, "flop":1, "turn":2, "river":3}[e[0]]
    for street, histories in sorted(round_state["action_histories"].iteritems(), key=sort_key):
      if len(histories) != 0:
        print "  %s" % street
        for original in histories:
          history = {k:v for k,v in original.iteritems()}
          uuid = history.pop("uuid")
          history["player"] = "%s (uuid=%s)" % (fetch_name(uuid), uuid)
          print "    %s" % history
    print '=============================================='

  def write_game_start_message(self, game_info):
    print ' -- Game Start %s --' % self.__gen_uuid_info()
    print '=============================================='
    print '-- rule --'
    print ' - %d players game' % game_info['player_num']
    print ' - %d round' % game_info['rule']['max_round']
    print ' - start stack = %d' % game_info['rule']['initial_stack']
    print ' - small blind = %d' % game_info['rule']['small_blind_amount']
    print '=============================================='

  def write_round_start_message(self, round_count, hole_card, seats):
    print ' -- Round %d Start %s --' % (round_count, self.__gen_uuid_info())
    print '=============================================='
    print '-- hole card --'
    print ' hole card : %s' % hole_card
    print ' Players'
    for position, player in enumerate(seats):
      print ' %d : %s' % (position, self.write_base_player(player))
    print '=============================================='

  def write_street_start_message(self, street, round_state):
    print ' -- Street Start %s --' % self.__gen_uuid_info()
    print '=============================================='
    print ' street = %s' % street
    print '=============================================='

  def write_game_update_message(self, new_action, round_state):
    print ' -- Game Update %s --' % self.__gen_uuid_info()
    print '=============================================='
    print '-- new action --'
    print ' player [%s] declared %s:%d' % (new_action['player_uuid'], new_action['action'], new_action['amount'])
    print '-- round state --'
    print ' Street : %s' % round_state['street']
    print ' Community Card : %s' % round_state['community_card']
    print ' Pot : main = %d, side = %s' % (round_state['pot']['main']['amount'], round_state['pot']['side'])
    print ' Dealer Btn : %s ' % round_state['seats'][round_state['dealer_btn']]['name']
    print ' Players'
    for position, player in enumerate(round_state['seats']):
      player_str = self.write_player(player, round_state)
      player_str = player_str.replace("NEXT", "CURRENT")
      print ' %d : %s' % (position, player_str)
    print '=============================================='

  def write_round_result_message(self, winners, hand_info, round_state):
    print ' -- Round Result %s --' % self.__gen_uuid_info()
    print '=============================================='
    print '-- winners --'
    for winner in winners:
      print ' %s' % self.write_base_player(winner)
    self.write_hand_info(hand_info)
    print '-- round state --'
    print ' Street : %s' % round_state['street']
    print ' Community Card : %s' % round_state['community_card']
    print ' Pot : main = %d, side = %s' % (round_state['pot']['main']['amount'], round_state['pot']['side'])
    print ' Dealer Btn : %s ' % round_state['seats'][round_state['dealer_btn']]['name']
    print ' Players'
    for position, player in enumerate(round_state['seats']):
      player_str = self.write_player(player, round_state)
      player_str = player_str.replace(", NEXT", "")
      print ' %d : %s' % (position, player_str)
    print '=============================================='

  def write_base_player(self, p):
    return '%s (%s) => state : %s, stack : %s' % (p['name'], p['uuid'], p['state'], p['stack'])

  def write_player(self, player, round_state):
    player_pos = round_state["seats"].index(player)
    is_sb = player_pos == round_state["small_blind_pos"]
    is_bb = player_pos == round_state["big_blind_pos"]
    base_str = self.write_base_player(player)
    batch = self.__gen_batch(is_sb, is_bb, self.__is_next_player(player, round_state))
    if len(batch)!=0:
      base_str = "%s <= %s" % (base_str, batch)
    return base_str

  def write_hand_info(self, hand_info):
    if len(hand_info) != 0: print '-- hand info --'
    for info in hand_info:
      hand, hole = info["hand"]["hand"], info["hand"]["hole"]
      print "player [%s]" % info["uuid"]
      print "  hand => %s (high=%d, low=%d)" % (hand["strength"], hand["high"], hand["low"])
      print "  hole => [%s, %s]" % (hole["high"], hole["low"])

  def __is_next_player(self, player, round_state):
    return round_state and not isinstance(round_state["next_player"], str)\
            and player == round_state["seats"][round_state["next_player"]]

  def __gen_batch(self, is_sb=False, is_bb=False, is_next=False):
    batches = []
    if is_sb: batches.append("SB")
    if is_bb: batches.append("BB")
    if is_next: batches.append("NEXT")
    return ", ".join(batches)

  def __gen_uuid_info(self):
    return '(UUID = %s)' % self.algo.uuid

