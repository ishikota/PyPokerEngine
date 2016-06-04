class ActionChecker:

  DEFAULT_MIN_RAISE = 5

  def correct_action(self, players, player_pos, action, amount=None):
    pass

  def is_illegal(self, players, player_pos, action, amount=None):
    if action == 'fold':
      return False
    elif action == 'call':
      return self.__is_short_of_money(players[player_pos], amount)\
          or self.__is_illegal_call(players, amount)
    elif action == 'raise':
      return self.__is_short_of_money(players[player_pos], amount) \
          or self.__is_illegal_raise(players, amount)

  def need_amount_for_action(self, player, amount):
    return amount - player.paid_sum()

  def agree_amount(self, players):
    last_raise = self.__fetch_last_raise(players)
    return last_raise["amount"] if last_raise else 0


  def __is_illegal_call(self, players, amount):
    return amount != self.agree_amount(players)

  def __is_illegal_raise(self, players, amount):
    return self.__min_raise_amount(players) > amount

  def __min_raise_amount(self, players):
    raise_ = self.__fetch_last_raise(players)
    return raise_["amount"] + raise_["add_amount"] if raise_ else self.DEFAULT_MIN_RAISE

  def __is_short_of_money(self, player, amount):
    return player.stack < amount - player.paid_sum()

  def __fetch_last_raise(self, players):
    all_histories = [p.action_histories for p in players]
    all_histories = reduce(lambda acc, e: acc + e, all_histories)  # flatten
    raise_histories = [h for h in all_histories if h["action"] == "RAISE"]
    if len(raise_histories) == 0:
      return None
    else:
      return max(raise_histories, key=lambda h: h["amount"])  # maxby

