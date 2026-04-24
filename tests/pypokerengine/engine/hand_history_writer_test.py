"""
Replicates the example hand history scenario:
  - 6 players, blinds 50/100
  - Preflop: player5 raises to 350, player6 + player1 call, others fold
  - Flop/Turn/River: check check check -> player5 bets 100, others call
  - player6 wins the pot

Key assertion: SUMMARY collected(X) == mid-hand "collected X from pot"
i.e. both values are the gross pot (1500), NOT the net profit (1050 = 1500 - 450).

Real PokerStars reference:
  *** SHOW DOWN ***
  player6 collected 1417 from pot          <- gross (rake deducted)
  *** SUMMARY ***
  Total pot 1500 | Rake 83
  Seat 9: player6 showed [8d As] and won (1417) with a pair of Eights  <- same 1417

  player6 invested 450 (350 preflop + 100 river) -> net = 1417 - 450 = 967
  SUMMARY uses 1417 (gross), NOT 967 (net).
  Our engine has no rake, so the gross pot is 1500.
"""

import re
import pytest
from pypokerengine.engine.hand_history_writer import PokerStarsHandHistoryWriter


# ---------------------------------------------------------------------------
# Hand parameters
# ---------------------------------------------------------------------------

PLAYERS = [
    # (name,      uuid,  starting stack)
    ("player1", "u1", 10361),
    ("player2", "u2", 10849),   # button
    ("player3", "u3",  9305),   # small blind
    ("player4", "u4", 10000),   # big blind
    ("player5", "u5", 10125),
    ("player6", "u6",  6919),
]

DEALER_BTN = 1   # player2 is the button (0-indexed)
SB_AMOUNT  = 50
BB_AMOUNT  = 100

# Investments per player:
#   player1:  350 preflop + 100 river = 450  (lost at showdown)
#   player2:  0                              (folded preflop, did not bet)
#   player3:  50 (SB)                        (folded preflop)
#   player4:  100 (BB)                       (folded preflop)
#   player5:  350 preflop + 100 river = 450  (lost at showdown)
#   player6:  350 preflop + 100 river = 450  (WON)
#
# Total pot: 50+100+350+350+350 + 100+100+100 = 1500

GROSS_POT = 1500

FINAL_STACKS = {
    "u1": 10361 - 450,              # 9911  -- lost at showdown
    "u2": 10849,                    # 10849 -- folded preflop without investing
    "u3":  9305 - 50,               # 9255  -- SB, folded preflop
    "u4": 10000 - 100,              # 9900  -- BB, folded preflop
    "u5": 10125 - 450,              # 9675  -- lost at showdown
    "u6":  6919 - 450 + GROSS_POT,  # 7969  -- WON
}

WINNER_UUID  = "u6"
WINNER_NAME  = "player6"
WINNER_GROSS = GROSS_POT    # 1500 -- correct value
WINNER_NET   = 7969 - 6919  # 1050 -- wrong value (what BUG produced)


# ---------------------------------------------------------------------------
# Fixture: run one hand and return the winner's history file as lines
# ---------------------------------------------------------------------------

@pytest.fixture
def history_lines(tmp_path):
    """
    Calls the writer directly with the same arguments the Dealer would pass.
    Returns the winner's (player6) history file as a list of lines.
    """
    tmpl = str(tmp_path / "{player}.txt")
    w = PokerStarsHandHistoryWriter(
        output_file=tmpl,
        table_name="TestTable",
    )

    # on_game_start
    w.on_game_start({
        "rule": {"small_blind_amount": SB_AMOUNT},
        "seats": [{"name": n, "uuid": u} for n, u, _ in PLAYERS],
    })

    # Starting seat list (used in on_round_start and action calls)
    seats_start = [
        {"uuid": u, "stack": s, "state": "participating", "name": n}
        for n, u, s in PLAYERS
    ]

    # Hole cards matching the reference hand (engine format: suit+rank)
    hole_cards = {
        "u1": ["C5", "D5"],   # player1: 5c 5d
        "u2": ["C2", "C3"],   # player2: placeholder
        "u3": ["D2", "D3"],   # player3: placeholder
        "u4": ["H6", "CT"],   # player4: 6h Tc
        "u5": ["ST", "CA"],   # player5: Ts Ac
        "u6": ["D8", "SA"],   # player6: 8d As
    }

    # on_round_start
    w.on_round_start(
        round_count=1,
        dealer_btn=DEALER_BTN,
        hole_cards_by_uuid=hole_cards,
        seats=seats_start,
    )

    # -- Preflop ----------------------------------------------------------
    w.on_street_start("preflop", [])
    w.on_action("u5", "raise",  350, seats_start)   # player5 raises to 350
    w.on_action("u6", "call",   350, seats_start)   # player6 calls 350
    w.on_action("u1", "call",   350, seats_start)   # player1 calls 350
    w.on_action("u2", "fold",     0, seats_start)   # player2 folds
    w.on_action("u3", "fold",     0, seats_start)   # player3 folds
    w.on_action("u4", "fold",     0, seats_start)   # player4 folds

    community_flop  = ["HJ", "C4", "S8"]
    community_turn  = ["HJ", "C4", "S8", "CK"]
    community_river = ["HJ", "C4", "S8", "CK", "H7"]

    # -- Flop: all check --------------------------------------------------
    w.on_street_start("flop", community_flop)
    w.on_action("u5", "call", 0, seats_start)
    w.on_action("u6", "call", 0, seats_start)
    w.on_action("u1", "call", 0, seats_start)

    # -- Turn: all check --------------------------------------------------
    w.on_street_start("turn", community_turn)
    w.on_action("u5", "call", 0, seats_start)
    w.on_action("u6", "call", 0, seats_start)
    w.on_action("u1", "call", 0, seats_start)

    # -- River: player5 bets 100, others call -----------------------------
    w.on_street_start("river", community_river)
    w.on_action("u5", "raise", 100, seats_start)
    w.on_action("u6", "call",  100, seats_start)
    w.on_action("u1", "call",  100, seats_start)

    # -- Round result -----------------------------------------------------
    seats_final = [
        {
            "uuid": u,
            "stack": FINAL_STACKS[u],
            "state": "participating" if u in ("u1", "u5", "u6") else "folded",
            "name": n,
        }
        for n, u, _ in PLAYERS
    ]
    round_state = {
        "seats": seats_final,
        "community_card": community_river,
        "pot": {"main": {"amount": GROSS_POT}, "side": []},
    }
    hand_info = [
        {"uuid": "u5", "hand": {"hand": {"strength": "HIGHCARD"}}},   # player5 loses
        {"uuid": "u6", "hand": {"hand": {"strength": "ONEPAIR"}}},    # player6 wins
        {"uuid": "u1", "hand": {"hand": {"strength": "ONEPAIR"}}},    # player1 loses
    ]
    winners = [{"uuid": WINNER_UUID, "name": WINNER_NAME, "stack": FINAL_STACKS[WINNER_UUID]}]
    w.on_round_result(winners, hand_info, round_state)

    filepath = str(tmp_path / f"{WINNER_NAME}.txt")
    with open(filepath) as f:
        return f.read().splitlines()


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def find_line(lines, pattern):
    """Returns the first line matching the pattern, or None."""
    for line in lines:
        if re.search(pattern, line):
            return line
    return None


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestGrossBugFix:
    """Bug fix: SUMMARY collected(Y) must use the gross pot, not the net profit."""

    def test_summary_collected_equals_gross_not_net(self, history_lines):
        """
        Bug: _write_summary used net profit (final_stack - start_stack = 1050).
        Fix: use the gross pot amount (pot_total = 1500).
        """
        line = find_line(history_lines, r"collected \(\d+\)")
        assert line is not None, "SUMMARY section is missing a 'collected (X)' line"

        amount = int(re.search(r"collected \((\d+)\)", line).group(1))

        assert amount != WINNER_NET, (
            f"SUMMARY collected is {WINNER_NET} -- bug is NOT fixed! "
            f"Expected {WINNER_GROSS} (gross)."
        )
        assert amount == WINNER_GROSS, (
            f"SUMMARY collected is {amount}, expected {WINNER_GROSS} (gross)."
        )

    def test_midhand_collected_equals_gross(self, history_lines):
        """Mid-hand 'collected X from pot' line must use the gross pot amount."""
        line = find_line(history_lines, r"collected \d+ from pot")
        assert line is not None, "Missing 'collected X from pot' line"

        amount = int(re.search(r"collected (\d+) from pot", line).group(1))
        assert amount == GROSS_POT, (
            f"Mid-hand collected is {amount}, expected {GROSS_POT}."
        )

    def test_midhand_and_summary_collected_are_identical(self, history_lines):
        """
        In PokerStars format the mid-hand and SUMMARY collected values must be identical.
        This is the invariant identified in the bug report.
        """
        mid_line  = find_line(history_lines, r"collected \d+ from pot")
        summ_line = find_line(history_lines, r"collected \(\d+\)")
        assert mid_line  is not None, "Missing mid-hand collected line"
        assert summ_line is not None, "Missing summary collected line"

        mid_amount  = int(re.search(r"collected (\d+) from pot", mid_line).group(1))
        summ_amount = int(re.search(r"collected \((\d+)\)", summ_line).group(1))

        assert mid_amount == summ_amount, (
            f"Mid-hand ({mid_amount}) and SUMMARY ({summ_amount}) differ. "
            f"PokerStars format requires these to be identical."
        )


class TestHandStructure:
    """Verifies the overall structure of the hand history output."""

    def test_all_sections_present(self, history_lines):
        """All mandatory *** SECTION *** headers must be present."""
        text = "\n".join(history_lines)
        for section in [
            "*** HOLE CARDS ***",
            "*** FLOP ***",
            "*** TURN ***",
            "*** RIVER ***",
            "*** SHOW DOWN ***",
            "*** SUMMARY ***",
        ]:
            assert section in text, f"Missing section: {section}"

    def test_hero_hole_cards_shown(self, history_lines):
        """The hero (player6) sees their own hole cards in the HOLE CARDS section."""
        line = find_line(history_lines, r"Dealt to player6")
        assert line is not None, "Missing 'Dealt to player6' line"
        # player6 holds 8d As
        assert "8d" in line or "D8" in line.upper(), (
            f"Expected 8d in hole cards line: {line}"
        )

    def test_total_pot_correct(self, history_lines):
        """The SUMMARY header must show the correct total pot."""
        line = find_line(history_lines, r"Total pot")
        assert line is not None, "Missing 'Total pot' line"
        pot = int(re.search(r"Total pot (\d+)", line).group(1))
        assert pot == GROSS_POT, f"Total pot is {pot}, expected {GROSS_POT}"

    def test_board_cards_in_summary(self, history_lines):
        """SUMMARY must include the Board line with community cards."""
        line = find_line(history_lines, r"^Board ")
        assert line is not None, "Missing 'Board [...]' line in SUMMARY"

    def test_winner_only_in_collected_lines(self, history_lines):
        """Only the winner (player6) should appear on collected lines."""
        for line in history_lines:
            if "collected" in line:
                assert WINNER_NAME in line, (
                    f"Unexpected player on collected line: {line}"
                )


class TestPreflopActions:
    """Preflop actions are written correctly."""

    def test_raise_written(self, history_lines):
        """player5 raises to 350 must appear in the hand history."""
        line = find_line(history_lines, r"player5.*raises to 350")
        assert line is not None, "Missing 'player5 raises to 350'"

    def test_calls_written(self, history_lines):
        """player6 and player1 each call 350 preflop."""
        assert find_line(history_lines, r"player6.*calls 350") is not None
        assert find_line(history_lines, r"player1.*calls 350") is not None

    def test_folds_written(self, history_lines):
        """player2, player3, and player4 all fold preflop."""
        for name in ("player2", "player3", "player4"):
            assert find_line(history_lines, rf"{name}.*folds") is not None, (
                f"Missing '{name} folds'"
            )


class TestPostflopActions:
    """Post-flop actions are written correctly."""

    def test_flop_checks(self, history_lines):
        """All three remaining players check on the flop."""
        text = "\n".join(history_lines)
        flop_start   = text.find("*** FLOP ***")
        turn_start   = text.find("*** TURN ***")
        flop_section = text[flop_start:turn_start]
        assert flop_section.count(": checks") == 3, (
            f"Expected 3 checks on the flop:\n{flop_section}"
        )

    def test_river_bet_and_calls(self, history_lines):
        """player5 bets 100 on the river; the other two call."""
        text = "\n".join(history_lines)
        river_start    = text.find("*** RIVER ***")
        showdown_start = text.find("*** SHOW DOWN ***")
        river_section  = text[river_start:showdown_start]
        assert "player5: bets 100" in river_section
        assert river_section.count(": calls 100") == 2

    def test_first_postflop_aggression_is_bet_not_raise(self, history_lines):
        """In PokerStars format the first post-flop aggression is 'bets', not 'raises'."""
        text = "\n".join(history_lines)
        river_start    = text.find("*** RIVER ***")
        showdown_start = text.find("*** SHOW DOWN ***")
        river_section  = text[river_start:showdown_start]
        assert "bets 100" in river_section, (
            "First river aggression should be written as 'bets', not 'raises'"
        )
        assert "raises to 100" not in river_section