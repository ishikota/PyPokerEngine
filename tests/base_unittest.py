import unittest
from mock import Mock
from nose.tools import *

class BaseUnitTest(unittest.TestCase):

  def eq(self, expected, target):
    return self.assertEqual(expected, target)

  def neq(self, expected, target):
    return self.assertNotEqual(expected, target)

  def true(self, target):
    return self.assertTrue(target)

  def false(self, target):
    return self.assertFalse(target)

