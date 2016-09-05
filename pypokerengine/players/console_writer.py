class ConsoleWriter:

  def __init__(self, algo):
    self.algo = algo

  def write_declare_action(self, hole_card, valid_actions, round_state, action_histories):
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
    for action in action_histories:
      print ' %s' % action
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

  def write_game_update_message(self, action, round_state, action_histories):
    print ' -- Game Update %s --' % self.__gen_uuid_info()
    print '=============================================='
    print '-- new action --'
    print ' player [%s] declared %s:%d' % (action['player_uuid'], action['action'], action['amount'])
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
    is_sb = player_pos == round_state["dealer_btn"]
    is_bb = player_pos == (round_state["dealer_btn"] + 1) % len(round_state["seats"])
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
    return round_state and player == round_state["seats"][round_state["next_player"]]

  def __gen_batch(self, is_sb=False, is_bb=False, is_next=False):
    batches = []
    if is_sb: batches.append("SB")
    if is_bb: batches.append("BB")
    if is_next: batches.append("NEXT")
    return ", ".join(batches)

  def __gen_uuid_info(self):
    return '(UUID = %s)' % self.algo.uuid

