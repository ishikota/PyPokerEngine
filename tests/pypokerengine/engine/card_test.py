from tests.base_unittest import BaseUnitTest
from pypokerengine.engine.card import Card

class CardTest(BaseUnitTest):

  def setUp(self):
    pass

  def test_to_string(self):
    self.eq(str(Card(Card.CLUB, 1)), "CA")
    self.eq(str(Card(Card.CLUB, 14)), "CA")
    self.eq(str(Card(Card.CLUB, 2)), "C2")
    self.eq(str(Card(Card.HEART, 10)), "HT")
    self.eq(str(Card(Card.SPADE, 11)), "SJ")
    self.eq(str(Card(Card.DIAMOND, 12)), "DQ")
    self.eq(str(Card(Card.DIAMOND, 13)), "DK")

  def test_to_id(self):
    self.eq(Card(Card.HEART, 3).to_id(), 29)
    self.eq(Card(Card.SPADE, 1).to_id(), 40)

  def test_from_id(self):
    self.eq(Card.from_id(1), Card(Card.CLUB, 1))
    self.eq(Card.from_id(29), Card(Card.HEART, 3))
    self.eq(Card.from_id(40), Card(Card.SPADE, 1))

  def test_from_str(self):
    self.eq(Card(Card.CLUB, 14), Card.from_str("CA"))
    self.eq(Card(Card.HEART, 10), Card.from_str("HT"))
    self.eq(Card(Card.SPADE, 9), Card.from_str("S9"))
    self.eq(Card(Card.DIAMOND, 12), Card.from_str("DQ"))
