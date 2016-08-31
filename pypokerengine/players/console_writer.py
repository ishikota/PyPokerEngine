class ConsoleWriter:

  @classmethod
  def write_declare_action(self, hole_card, valid_actions, round_state, action_histories):
    write_player = lambda p: '%s (%s) => state : %s, stack : %s' % (p['name'], p['uuid'], p['state'], p['stack'])
    print ' -- Declare your action --'
    print '=============================================='
    print '-- hole card --'
    print ' hole card : %s' % hole_card
    print '-- valid actions --'
    print ' fold, call:%d, raise: [%d, %d]' % (valid_actions[1]['amount'], valid_actions[2]['amount']['min'], valid_actions[2]['amount']['max'])
    print '-- round state --'
    print ' Street : %s' % round_state['street']
    print ' Community Card : %s' % round_state['community_card']
    print ' Pot : main = %d, side = %s' % (round_state['pot']['main']['amount'], round_state['pot']['side'])
    print ' Players'
    for position, player in enumerate(round_state['seats']):
      print ' %d : %s' % (position, write_player(player))
    print '-- action histories --'
    for action in action_histories:
      print ' %s' % action
    print '=============================================='

  @classmethod
  def write_game_start_message(self, game_info):
    print ' -- Game Start --'
    print '=============================================='
    print '-- rule --'
    print ' - %d players game' % game_info['player_num']
    print ' - %d round' % game_info['rule']['max_round']
    print ' - start stack = %d' % game_info['rule']['initial_stack']
    print ' - small blind = %d' % game_info['rule']['small_blind_amount']
    print '=============================================='

  @classmethod
  def write_round_start_message(self, hole_card, seats):
    write_player = lambda p: '%s (%s) => state : %s, stack : %s' % (p['name'], p['uuid'], p['state'], p['stack'])
    print ' -- Round Start --'
    print '=============================================='
    print '-- hole card --'
    print ' hole card : %s' % hole_card
    print ' Players'
    for position, player in enumerate(seats):
      print ' %d : %s' % (position, write_player(player))
    print '=============================================='

  @classmethod
  def write_street_start_message(self, street, round_state):
    print ' -- Street Start --'
    print '=============================================='
    print ' street = %s' % street
    print '=============================================='

  @classmethod
  def write_game_update_message(self, action, round_state, action_histories):
    write_player = lambda p: '%s (%s) => state : %s, stack : %s' % (p['name'], p['uuid'], p['state'], p['stack'])
    print ' -- Game Update --'
    print '=============================================='
    print '-- new action --'
    print ' player [%s] declared %s:%d' % (action['player_uuid'], action['action'], action['amount'])
    print '-- round state --'
    print ' Street : %s' % round_state['street']
    print ' Community Card : %s' % round_state['community_card']
    print ' Pot : main = %d, side = %s' % (round_state['pot']['main']['amount'], round_state['pot']['side'])
    print ' Players'
    for position, player in enumerate(round_state['seats']):
      print ' %d : %s' % (position, write_player(player))
    print '=============================================='

  @classmethod
  def write_round_result_message(self, winners, round_state):
    write_player = lambda p: '%s (%s) => state : %s, stack : %s' % (p['name'], p['uuid'], p['state'], p['stack'])
    print ' -- Round Result --'
    print '=============================================='
    print '-- winners --'
    for winner in winners:
      print ' %s' % write_player(winner)
    print '-- round state --'
    print ' Street : %s' % round_state['street']
    print ' Community Card : %s' % round_state['community_card']
    print ' Pot : main = %d, side = %s' % (round_state['pot']['main']['amount'], round_state['pot']['side'])
    print ' Players'
    for position, player in enumerate(round_state['seats']):
      print ' %d : %s' % (position, write_player(player))
    print '=============================================='

