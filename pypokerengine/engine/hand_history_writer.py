"""
PokerStars Hand History Writer
==============================
Writes one hand history file per player in PokerStars format, matching
the perspective-based layout of real PokerStars hand histories: each file
shows only that player's hole cards, making the output compatible with
third-party tools such as PokerTracker and HoldemManager.

Usage:
    from pypokerengine.api.game import setup_config, start_poker
    from pypokerengine.engine.hand_history_writer import PokerStarsHandHistoryWriter

    # output_file must contain {player} — one file is created per player.
    writer = PokerStarsHandHistoryWriter("histories/{player}.txt")

    config = setup_config(max_round=100, initial_stack=10000, small_blind_amount=1)
    config.register_player(name="p1", algorithm=MyBot())
    config.register_player(name="p2", algorithm=OtherBot())

    start_poker(config, verbose=0, hand_history_writer=writer)
    # Creates: histories/p1.txt  (p1's hole cards shown)
    #          histories/p2.txt  (p2's hole cards shown)
"""

import os
import uuid
from datetime import datetime


# ---------------------------------------------------------------------------
# Card conversion helpers
# ---------------------------------------------------------------------------

def _ps_card(engine_card: str) -> str:
    """
    Converts an engine card string to PokerStars format.
    Engine format:     suit+rank, e.g. "H9", "DA", "ST", "CT", "C2"
    PokerStars format: rank+suit, e.g. "9h", "Ad", "Ts", "Tc", "2c"
    """
    if not engine_card or len(engine_card) < 2:
        return "??"
    suit = engine_card[0].lower()   # H->h, D->d, S->s, C->c
    rank = engine_card[1:]          # 9, A, T, J, Q, K, 2...
    return f"{rank}{suit}"


def _ps_cards(engine_cards: list) -> str:
    """Converts a list of engine card strings to PokerStars bracket notation: [9h Ad Ts]"""
    return "[" + " ".join(_ps_card(c) for c in engine_cards) + "]"


def _player_name_by_uuid(seats: list, target_uuid: str) -> str:
    for s in seats:
        if s["uuid"] == target_uuid:
            return s["name"]
    return target_uuid[:8]


# ---------------------------------------------------------------------------
# Writer
# ---------------------------------------------------------------------------

class PokerStarsHandHistoryWriter:
    """
    Writes one hand history file per player in PokerStars format.

    Each file is identical except for the HOLE CARDS section, where only
    that player's own cards are shown — exactly as real PokerStars files work.

    Parameters:
        output_file : Path template containing {player}, e.g. "histories/{player}.txt".
                      The directory is created automatically if it does not exist.
        stakes      : Stakes string, e.g. "$1/$2". Auto-derived from blinds if omitted.
        table_name  : Table name written in the hand header.
    """

    def __init__(
        self,
        output_file: str = "{player}_history.txt",
        stakes: str | None = None,
        table_name: str = "PyPokerEngine",
    ):
        if "{player}" not in output_file:
            raise ValueError(
                "output_file must contain {player}, e.g. 'histories/{player}.txt'. "
                "One file is written per player."
            )
        self.output_file = output_file
        self.table_name = table_name
        self._stakes = stakes
        self._sb_amount = 0
        self._bb_amount = 0
        self._seats_meta = []   # stable list set once at game_start: [{name, uuid, seat_no}]
        self._reset_round()

    # ------------------------------------------------------------------
    # Engine callbacks — called by Dealer
    # ------------------------------------------------------------------

    def on_game_start(self, game_info: dict):
        """Called once when the game session begins."""
        rule = game_info["rule"]
        self._sb_amount = rule["small_blind_amount"]
        self._bb_amount = self._sb_amount * 2
        self._stakes = self._stakes or f"${self._sb_amount}/${self._bb_amount}"

        self._seats_meta = [
            {"name": p["name"], "uuid": p["uuid"], "seat_no": i + 1}
            for i, p in enumerate(game_info["seats"])
        ]

        # Create output directories up front so we don't fail mid-game
        for meta in self._seats_meta:
            path = self.output_file.format(player=meta["name"])
            dirpath = os.path.dirname(path)
            if dirpath:
                os.makedirs(dirpath, exist_ok=True)

    def on_round_start(self, round_count: int, dealer_btn: int,
                       hole_cards_by_uuid: dict, seats: list):
        """
        Called at the start of each hand, after hole cards have been dealt.

        hole_cards_by_uuid: {uuid: ["H9", "DA"]}
        seats:              encoded seat list from round_state
        """
        self._reset_round()
        self._round_count = round_count
        self._hand_id = int(uuid.uuid4()) % (10 ** 15)
        self._dealer_btn = dealer_btn
        self._hole_cards = hole_cards_by_uuid
        self._stacks_at_start = {s["uuid"]: s["stack"] for s in seats}

        self._write_header(seats)
        self._write_blinds()
        # Mark where HOLE CARDS section begins; dealt lines are injected per-player in _flush
        self._lines.append("*** HOLE CARDS ***")
        self._hole_cards_insert_idx = len(self._lines)

    def on_street_start(self, street: str, community_card: list):
        """Called at the start of each betting street."""
        self._current_street = street
        self._street_first_raise[street] = True  # next aggression on this street is a bet

        if street == "preflop":
            return  # already written in on_round_start

        if street == "flop":
            self._lines.append(f"*** FLOP *** {_ps_cards(community_card)}")
        elif street == "turn":
            self._lines.append(
                f"*** TURN *** {_ps_cards(community_card[:3])} {_ps_cards(community_card[3:4])}"
            )
        elif street == "river":
            self._lines.append(
                f"*** RIVER *** {_ps_cards(community_card[:4])} {_ps_cards(community_card[4:5])}"
            )

    def on_action(self, actor_uuid: str, action: str, amount: int, seats: list):
        """
        Called after each player action.

        action: "fold" | "call" | "raise"
        amount: absolute total bet size (not add_amount)
        """
        name = _player_name_by_uuid(self._seats_meta, actor_uuid)
        street = self._current_street

        if action == "fold":
            self._lines.append(f"{name}: folds")
        elif action == "call":
            if amount == 0:
                self._lines.append(f"{name}: checks")
            else:
                self._lines.append(f"{name}: calls {amount}")
        elif action == "raise":
            # PokerStars convention: first aggression post-flop is "bets X",
            # subsequent aggression is "raises to Y".
            if self._street_first_raise.get(street, True) and street != "preflop":
                self._lines.append(f"{name}: bets {amount}")
            else:
                self._lines.append(f"{name}: raises to {amount}")
            self._street_first_raise[street] = False

        # Sync stacks
        for s in seats:
            for meta in self._seats_meta:
                if meta["uuid"] == s["uuid"]:
                    meta["stack"] = s["stack"]

    def on_round_result(self, winners: list, hand_info: list, round_state: dict):
        """Called at the end of each hand."""
        seats = round_state["seats"]
        final_stacks = {s["uuid"]: s["stack"] for s in seats}

        # Showdown: all remaining players' cards are revealed (same in every file)
        active = [s for s in seats if s["state"] != "folded"]
        if len(active) > 1:
            self._lines.append("*** SHOW DOWN ***")
            for hi in hand_info:
                u = hi.get("uuid")
                if u and u in self._hole_cards:
                    name = _player_name_by_uuid(self._seats_meta, u)
                    cards = _ps_cards(self._hole_cards[u])
                    strength = hi.get("hand", {}).get("hand", {}).get("strength", "")
                    self._lines.append(f"{name}: shows {cards} ({strength})")

        # Pot collected lines — write GROSS amount (PokerStars standard).
        # In PokerStars format, 'X collected Y from pot' means Y is the gross pot
        # amount taken out, not the net profit. Net profit = gross - invested.
        pot = round_state.get("pot", {})
        pot_total = pot.get("main", {}).get("amount", 0)
        for sp in pot.get("side", []):
            pot_total += sp.get("amount", 0)

        # Store gross winnings per winner uuid so _write_summary can use the same value.
        # PokerStars requires the SUMMARY collected(Y) to be identical to the mid-hand
        # 'collected Y from pot' line — both must be the GROSS pot, not net profit.
        self._gross_winnings = {}
        if winners:
            gross_per_winner = pot_total // len(winners)
            for winner in winners:
                self._gross_winnings[winner["uuid"]] = gross_per_winner
                self._lines.append(f"{winner['name']} collected {gross_per_winner} from pot")

        self._write_summary(round_state)
        self._flush()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _reset_round(self):
        self._round_count = 0
        self._hand_id = None
        self._dealer_btn = 0
        self._hole_cards = {}
        self._lines = []
        self._hole_cards_insert_idx = None
        self._street_first_raise = {}
        self._current_street = "preflop"
        self._stacks_at_start = {}
        self._gross_winnings = {}   # uuid -> gross chips collected from pot this hand

    def _write_header(self, seats: list):
        ts = datetime.now().strftime("%Y/%m/%d %H:%M:%S ET")
        nb = len(self._seats_meta)
        btn_seat_no = self._dealer_btn + 1

        self._lines.append(
            f"PokerStars Hand #{self._hand_id}: "
            f"Hold'em No Limit ({self._stakes}) - {ts}"
        )
        self._lines.append(
            f"Table '{self.table_name}' {nb}-max Seat #{btn_seat_no} is the button"
        )
        stack_map = {s["uuid"]: s["stack"] for s in seats}
        for meta in self._seats_meta:
            stack = stack_map.get(meta["uuid"], 0)
            self._lines.append(f"Seat {meta['seat_no']}: {meta['name']} ({stack} in chips)")

    def _write_blinds(self):
        """Writes the small blind and big blind posting lines."""
        nb = len(self._seats_meta)
        btn = self._dealer_btn

        if nb == 2:
            # Heads-up: dealer posts small blind
            sb_idx, bb_idx = btn, (btn + 1) % nb
        else:
            sb_idx = (btn + 1) % nb
            bb_idx = (btn + 2) % nb

        self._lines.append(f"{self._seats_meta[sb_idx]['name']}: posts small blind {self._sb_amount}")
        self._lines.append(f"{self._seats_meta[bb_idx]['name']}: posts big blind {self._bb_amount}")

    def _write_summary(self, round_state: dict):
        seats = round_state["seats"]
        community = round_state.get("community_card", [])
        pot = round_state.get("pot", {})
        pot_total = pot.get("main", {}).get("amount", 0)
        for sp in pot.get("side", []):
            pot_total += sp.get("amount", 0)

        self._lines.append("*** SUMMARY ***")
        self._lines.append(f"Total pot {pot_total} | Rake 0")

        if community:
            self._lines.append(f"Board {_ps_cards(community)}")

        nb = len(self._seats_meta)
        btn = self._dealer_btn
        sb_idx = btn if nb == 2 else (btn + 1) % nb
        bb_idx = (btn + 1) % nb if nb == 2 else (btn + 2) % nb
        btn_seat_no = self._dealer_btn + 1

        folded_uuids = {s["uuid"] for s in seats if s["state"] == "folded"}

        for i, meta in enumerate(self._seats_meta):
            parts = [f"Seat {meta['seat_no']}: {meta['name']}"]

            if meta["seat_no"] == btn_seat_no:
                parts.append("(button)")
            if i == sb_idx:
                parts.append("(small blind)")
            if i == bb_idx:
                parts.append("(big blind)")

            # FIX: use the gross pot collected (same value as mid-hand 'collected X from pot')
            # rather than the net profit (final_stack - start_stack).
            # Real PokerStars format:
            #   *** SHOW DOWN ***
            #   dhduncan collected 1417 from pot          ← gross
            #   *** SUMMARY ***
            #   Seat 9: dhduncan … and won (1417) …       ← same gross, NOT net (967)
            gross = self._gross_winnings.get(meta["uuid"], 0)
            if gross > 0:
                parts.append(f"collected ({gross})")
            elif meta["uuid"] in folded_uuids:
                parts.append("folded")
            else:
                parts.append("lost")

            self._lines.append(" ".join(parts))

        self._lines.append("")  # Blank line between hands

    def _flush(self):
        """
        Writes one file per player. The only difference between files is the
        HOLE CARDS section: each file shows only that player's own dealt cards.
        """
        idx = self._hole_cards_insert_idx

        for meta in self._seats_meta:
            cards = self._hole_cards.get(meta["uuid"])
            dealt_lines = (
                [f"Dealt to {meta['name']} {_ps_cards(cards)}"] if cards else []
            )
            lines = self._lines[:idx] + dealt_lines + self._lines[idx:]

            filepath = self.output_file.format(player=meta["name"])
            with open(filepath, "a", encoding="utf-8") as f:
                for line in lines:
                    f.write(line + "\n")