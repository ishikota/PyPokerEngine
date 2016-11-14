import pypokerengine.api.game as G

from nose.tools import raises
from tests.base_unittest import BaseUnitTest
from examples.players.fold_man import PokerPlayer as FoldMan

class GameTest(BaseUnitTest):

    def test_start_poker(self):
        config = G.Config(1, 100, 10)
        config.register_player("p1", FoldMan())
        config.register_player("p2", FoldMan())
        result = G.start_poker(config)
        p1, p2 = [result["message"]["game_information"]["seats"][i] for i in range(2)]
        self.eq("p1", p1["name"])
        self.eq(90, p1["stack"])
        self.eq("p2", p2["name"])
        self.eq(110, p2["stack"])

    def test_start_poker_validation_when_no_player(self):
        config = G.Config(1, 100, 10)
        with self.assertRaises(Exception) as e:
            result = G.start_poker(config)
        self.assertIn("no player", e.exception.message)

    def test_start_poker_validation_when_one_player(self):
        config = G.Config(1, 100, 10)
        config.register_player("p1", FoldMan())
        with self.assertRaises(Exception) as e:
            result = G.start_poker(config)
        self.assertIn("only 1 player", e.exception.message)

    @raises(TypeError)
    def test_register_player_when_invalid(self):
        config = G.Config(1, 100, 10)
        config.register_player("p1", "dummy")

