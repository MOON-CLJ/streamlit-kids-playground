"""Tests for the number guessing game rules."""

import unittest

from games.number_guess_logic import evaluate_guess, proximity_hint


class EvaluateGuessTest(unittest.TestCase):
    def test_reports_low_guess(self) -> None:
        self.assertEqual(evaluate_guess(7, 4), "too_low")

    def test_reports_high_guess(self) -> None:
        self.assertEqual(evaluate_guess(7, 9), "too_high")

    def test_reports_correct_guess(self) -> None:
        self.assertEqual(evaluate_guess(7, 7), "correct")


class ProximityHintTest(unittest.TestCase):
    def test_very_close_guess_gets_hot_hint(self) -> None:
        self.assertIn("非常接近", proximity_hint(50, 53, 100))

    def test_far_guess_gets_adjustment_hint(self) -> None:
        self.assertIn("大胆调整", proximity_hint(90, 10, 100))


if __name__ == "__main__":
    unittest.main()
