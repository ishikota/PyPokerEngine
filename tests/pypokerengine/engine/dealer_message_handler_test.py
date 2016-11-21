from tests.base_unittest import BaseUnitTest
from mock import Mock
from pypokerengine.engine.player import Player
from pypokerengine.engine.dealer import MessageHandler

class MessageHandlerTest(BaseUnitTest):

  def setUp(self):
    self.p1 = Player(uuid="uuid1", initial_stack=100, name="hoge")
    self.p1_algo = Mock()
    self.p2 = Player(uuid="uuid2", initial_stack=100, name="fuga")
    self.p2_algo = Mock()
    self.mh = MessageHandler()
    self.mh.register_algorithm(self.p1.uuid, self.p1_algo)
    self.mh.register_algorithm(self.p2.uuid, self.p2_algo)

  def test_process_message_when_ask(self):
    self.p1_algo.respond_to_ask.return_value = "fuga"
    ask_msg = { "type":"ask", "message":"hoge" }
    response = self.mh.process_message("uuid1", ask_msg)
    algo_args = self.p1_algo.respond_to_ask.call_args_list[0][0][0]
    self.eq("hoge", algo_args)
    self.eq("fuga", response)

  def test_process_message_when_notification(self):
    notification_msg = { "type":"notification", "message":"hoge" }
    self.mh.process_message("uuid1", notification_msg)
    algo_args = self.p1_algo.receive_notification.call_args_list[0][0][0]
    self.eq("hoge", algo_args)

  def test_process_message_when_broadcast(self):
    notification_msg = { "type":"notification", "message":"hoge" }
    self.mh.process_message(-1, notification_msg)
    p1_algo_args = self.p1_algo.receive_notification.call_args_list[0][0][0]
    self.eq("hoge", p1_algo_args)
    p2_algo_args = self.p2_algo.receive_notification.call_args_list[0][0][0]
    self.eq("hoge", p2_algo_args)

