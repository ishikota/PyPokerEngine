from itertools import groupby
from functools import reduce
from treys import Card as TreysCard, Evaluator


class HandEvaluator:

    HIGHCARD      = 0
    ONEPAIR       = 1 << 8
    TWOPAIR       = 1 << 9
    THREECARD     = 1 << 10
    STRAIGHT      = 1 << 11
    FLASH         = 1 << 12
    FULLHOUSE     = 1 << 13
    FOURCARD      = 1 << 14
    STRAIGHTFLASH = 1 << 15

    HAND_STRENGTH_MAP = {
        HIGHCARD:      "HIGHCARD",
        ONEPAIR:       "ONEPAIR",
        TWOPAIR:       "TWOPAIR",
        THREECARD:     "THREECARD",
        STRAIGHT:      "STRAIGHT",
        FLASH:         "FLASH",
        FULLHOUSE:     "FULLHOUSE",
        FOURCARD:      "FOURCARD",
        STRAIGHTFLASH: "STRAIGHTFLASH",
    }

    # PyPokerEngine card.rank  →  treys rank char
    _RANK_CHARS = {
        2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7',
        8: '8', 9: '9', 10: 'T', 11: 'J', 12: 'Q', 13: 'K', 14: 'A',
    }

    # PyPokerEngine card.suit (CLUB=2, DIAMOND=4, HEART=8, SPADE=16)  →  treys suit char
    _SUIT_CHARS = {2: 'c', 4: 'd', 8: 'h', 16: 's'}

    # treys Evaluator.get_rank_class() returns 1-9 (1 = best hand)
    _TREYS_CLASS_TO_STRENGTH = {
        0: STRAIGHTFLASH,
        1: STRAIGHTFLASH,
        2: FOURCARD,
        3: FULLHOUSE,
        4: FLASH,
        5: STRAIGHT,
        6: THREECARD,
        7: TWOPAIR,
        8: ONEPAIR,
        9: HIGHCARD,
    }

    _evaluator = Evaluator()

    # ── Public API ────────────────────────────────────────────────────────────

    @classmethod
    def gen_hand_rank_info(cls, hole, community):
        hand = cls.eval_hand(hole, community)
        row_strength = cls.__mask_hand_strength(hand)
        strength = cls.HAND_STRENGTH_MAP[row_strength]
        return {
            "hand": {
                "strength": strength,
                "high":     cls.__mask_hand_high_rank(hand),
                "low":      cls.__mask_hand_low_rank(hand),
            },
            "hole": {
                "high": cls.__mask_hole_high_rank(hand),
                "low":  cls.__mask_hole_low_rank(hand),
            },
        }

    @classmethod
    def eval_hand(cls, hole, community):
        ranks    = sorted(card.rank for card in hole)
        hole_flg = ranks[1] << 4 | ranks[0]
        hand_flg = cls.__calc_hand_info_flg(hole, community) << 8
        return hand_flg | hole_flg

    # ── Core evaluation (treys decides the hand class) ────────────────────────

    @classmethod
    def __calc_hand_info_flg(cls, hole, community):
        all_cards = hole + community
        strength  = cls.__detect_strength(hole, community)

        if strength == cls.STRAIGHTFLASH: return strength | cls.__eval_straightflash(all_cards)
        if strength == cls.FOURCARD:      return strength | cls.__eval_fourcard(all_cards)
        if strength == cls.FULLHOUSE:     return strength | cls.__eval_fullhouse(all_cards)
        if strength == cls.FLASH:         return strength | cls.__eval_flash(all_cards)
        if strength == cls.STRAIGHT:      return strength | cls.__eval_straight(all_cards)
        if strength == cls.THREECARD:     return strength | cls.__eval_threecard(all_cards)
        if strength == cls.TWOPAIR:       return strength | cls.__eval_twopair(all_cards)
        if strength == cls.ONEPAIR:       return strength | cls.__eval_onepair(all_cards)
        return cls.__eval_holecard(hole)

    @classmethod
    def __detect_strength(cls, hole, community):
        """Use treys to correctly classify the best 5-card hand from all 7 cards.
        Falls back to simple detection when there are fewer than 3 community cards."""
        if len(community) >= 3:
            t_hole = [cls.__to_treys(c) for c in hole]
            t_comm = [cls.__to_treys(c) for c in community]
            t_rank = cls._evaluator.evaluate(t_comm, t_hole)
            return cls._TREYS_CLASS_TO_STRENGTH[cls._evaluator.get_rank_class(t_rank)]
        # Pre-flop: only hole cards available
        return cls.ONEPAIR if hole[0].rank == hole[1].rank else cls.HIGHCARD

    @classmethod
    def __to_treys(cls, card):
        return TreysCard.new(cls._RANK_CHARS[card.rank] + cls._SUIT_CHARS[card.suit])

    # ── Rank extractors ───────────────────────────────────────────────────────

    @classmethod
    def __eval_holecard(cls, hole):
        ranks = sorted(card.rank for card in hole)
        return ranks[1] << 4 | ranks[0]

    @classmethod
    def __eval_onepair(cls, cards):
        rank, memo = 0, 0
        for card in cards:
            mask = 1 << card.rank
            if memo & mask:
                rank = max(rank, card.rank)
            memo |= mask
        return rank << 4

    @classmethod
    def __eval_twopair(cls, cards):
        pairs, memo = [], 0
        for card in cards:
            mask = 1 << card.rank
            if memo & mask:
                pairs.append(card.rank)
            memo |= mask
        top2 = sorted(pairs, reverse=True)[:2]
        return top2[0] << 4 | top2[1]

    @classmethod
    def __eval_threecard(cls, cards):
        rank = -1
        bit_memo = reduce(lambda m, c: m + (1 << (c.rank - 1) * 3), cards, 0)
        for r in range(2, 15):
            bit_memo >>= 3
            if (bit_memo & 7) >= 3:
                rank = r
        return rank << 4

    @classmethod
    def __eval_straight(cls, cards):
        ranks = set(card.rank for card in cards)
        if 14 in ranks:          # Ace can play low
            ranks.add(1)
        best = -1
        for low in range(1, 11): # low card 1..10  →  high card 5..14
            if all(r in ranks for r in range(low, low + 5)):
                best = low + 4
        return best << 4 if best != -1 else 0

    @classmethod
    def __eval_flash(cls, cards):
        best = (-1, -1)
        fetch_suit = lambda c: c.suit
        fetch_rank = lambda c: c.rank
        for _suit, grp in groupby(sorted(cards, key=fetch_suit), key=fetch_suit):
            g = sorted(grp, key=fetch_rank, reverse=True)
            if len(g) >= 5:
                candidate = (g[0].rank, g[1].rank)
                if candidate > best:
                    best = candidate
        return best[0] << 4 | best[1]

    @classmethod
    def __eval_fullhouse(cls, cards):
        fetch_rank = lambda c: c.rank
        threes, twos = [], []
        for rank, grp in groupby(sorted(cards, key=fetch_rank), key=fetch_rank):
            g = list(grp)
            if len(g) >= 3:
                threes.append(rank)
            if len(g) >= 2:
                twos.append(rank)
        # A second three-of-a-kind contributes as the pair
        twos = [r for r in twos if r not in threes]
        if len(threes) == 2:
            twos.append(min(threes))
        best_three = max(threes) if threes else None
        best_two   = max(twos)   if twos   else None
        return best_three << 4 | best_two

    @classmethod
    def __eval_fourcard(cls, cards):
        fetch_rank = lambda c: c.rank
        for rank, grp in groupby(sorted(cards, key=fetch_rank), key=fetch_rank):
            if len(list(grp)) >= 4:
                return rank << 4
        return 0

    @classmethod
    def __eval_straightflash(cls, cards):
        """Highest straight flush in any suit; wheel-aware via __eval_straight."""
        fetch_suit = lambda c: c.suit
        best = -1
        for _suit, grp in groupby(sorted(cards, key=fetch_suit), key=fetch_suit):
            g = list(grp)
            if len(g) >= 5:
                val = cls.__eval_straight(g)
                if val:
                    best = max(best, val >> 4)
        return best << 4 if best != -1 else 0

    # ── Bit-mask helpers (unchanged) ──────────────────────────────────────────

    @classmethod
    def __mask_hand_strength(cls, bit):
        mask = 511 << 16
        return (bit & mask) >> 8

    @classmethod
    def __mask_hand_high_rank(cls, bit):
        return (bit & (15 << 12)) >> 12

    @classmethod
    def __mask_hand_low_rank(cls, bit):
        return (bit & (15 << 8)) >> 8

    @classmethod
    def __mask_hole_high_rank(cls, bit):
        return (bit & (15 << 4)) >> 4

    @classmethod
    def __mask_hole_low_rank(cls, bit):
        return bit & 15