class PayInfo:

  PAY_TILL_END = 0
  ALLIN  = 1
  FOLDED = 2

  def __init__(self):
    self.amount = 0
    self.status = self.PAY_TILL_END

  def update_by_pay(self, amount):
    self.amount += amount

  def update_to_fold(self):
    self.status = self.FOLDED

  def update_to_allin(self):
    self.status = self.ALLIN

