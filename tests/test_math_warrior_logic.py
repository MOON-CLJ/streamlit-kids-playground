"""Tests for Math Warrior rules and question generation."""

import random
import unittest

from games.math_warrior_logic import (
    DIFFICULTIES,
    Question,
    check_answer,
    generate_question,
    points_for_correct,
)


class GenerateQuestionTest(unittest.TestCase):
    def test_beginner_addition_stays_within_ten(self) -> None:
        config = DIFFICULTIES["🌱 新手（10以内加法）"]
        rng = random.Random(11)

        for _ in range(100):
            question = generate_question(config, rng)
            self.assertEqual(question.operation, "add")
            self.assertLessEqual(question.answer, 10)

    def test_warrior_questions_never_have_negative_answers(self) -> None:
        config = DIFFICULTIES["🌟 勇士（20以内加减）"]
        rng = random.Random(22)

        questions = [generate_question(config, rng) for _ in range(200)]

        self.assertEqual({question.operation for question in questions}, {"add", "subtract"})
        self.assertTrue(all(0 <= question.answer <= 20 for question in questions))

    def test_master_multiplication_uses_one_to_nine(self) -> None:
        config = DIFFICULTIES["🚀 大师（九九乘法）"]
        rng = random.Random(33)

        for _ in range(100):
            question = generate_question(config, rng)
            self.assertEqual(question.operation, "multiply")
            self.assertIn(question.left, range(1, 10))
            self.assertIn(question.right, range(1, 10))


class QuestionTest(unittest.TestCase):
    def test_formats_and_solves_each_operation(self) -> None:
        questions = [
            (Question(3, 4, "add"), "3 + 4 = ?", 7),
            (Question(9, 2, "subtract"), "9 − 2 = ?", 7),
            (Question(6, 7, "multiply"), "6 × 7 = ?", 42),
        ]

        for question, prompt, answer in questions:
            with self.subTest(operation=question.operation):
                self.assertEqual(question.prompt, prompt)
                self.assertEqual(question.answer, answer)
                self.assertTrue(check_answer(question, answer))
                self.assertFalse(check_answer(question, answer + 1))


class ScoreTest(unittest.TestCase):
    def test_streak_bonus_increases_and_is_capped(self) -> None:
        self.assertEqual(points_for_correct(1), 10)
        self.assertEqual(points_for_correct(3), 14)
        self.assertEqual(points_for_correct(6), 20)
        self.assertEqual(points_for_correct(20), 20)


if __name__ == "__main__":
    unittest.main()
