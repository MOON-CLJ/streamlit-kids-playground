"""Tests for the animal memory matching rules."""

import random
import unittest
from collections import Counter

from games.memory_match_logic import ANIMALS, build_deck, cards_match


class BuildDeckTest(unittest.TestCase):
    def test_builds_two_cards_for_each_animal(self) -> None:
        deck = build_deck(4, random.Random(42))

        self.assertEqual(len(deck), 8)
        self.assertEqual(set(deck), set(ANIMALS[:4]))
        self.assertTrue(all(count == 2 for count in Counter(deck).values()))

    def test_rejects_too_many_pairs(self) -> None:
        with self.assertRaises(ValueError):
            build_deck(len(ANIMALS) + 1)

    def test_seeded_shuffle_is_repeatable(self) -> None:
        first = build_deck(5, random.Random(7))
        second = build_deck(5, random.Random(7))

        self.assertEqual(first, second)


class CardsMatchTest(unittest.TestCase):
    def test_matches_equal_animals_at_different_positions(self) -> None:
        self.assertTrue(cards_match(["🐶", "🐱", "🐶"], 0, 2))

    def test_does_not_match_different_animals(self) -> None:
        self.assertFalse(cards_match(["🐶", "🐱"], 0, 1))

    def test_does_not_match_a_card_with_itself(self) -> None:
        self.assertFalse(cards_match(["🐶", "🐶"], 0, 0))


if __name__ == "__main__":
    unittest.main()
