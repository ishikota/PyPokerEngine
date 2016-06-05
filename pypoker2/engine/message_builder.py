class MessageBuilder:

  @classmethod
  def game_start_message(self, config, seats):
    pass

  @classmethod
  def round_start_message(self, round_count, player_pos, seats):
    pass

  @classmethod
  def street_start_message(self, round_manager, table):
    pass

  @classmethod
  def ask_message(self, player_pos, round_manager, table):
    pass

  @classmethod
  def game_update_message(self, player_pos, action, amount, round_manager, table):
    pass

  @classmethod
  def round_result_message(self, round_count, winners, round_manager, table):
    pass

  @classmethod
  def game_result_message(self, seats):
    pass

