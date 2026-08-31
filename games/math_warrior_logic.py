"""Pure rules and question generation for Math Warrior."""

import random
from dataclasses import dataclass
from typing import Literal


Operation = Literal["add", "subtract", "multiply"]


@dataclass(frozen=True)
class Difficulty:
    """Configuration for one Math Warrior difficulty."""

    question_count: int
    operations: tuple[Operation, ...]
    limit: int
    description: str


@dataclass(frozen=True)
class Question:
    """One arithmetic question."""

    left: int
    right: int
    operation: Operation

    @property
    def symbol(self) -> str:
        return {"add": "+", "subtract": "−", "multiply": "×"}[self.operation]

    @property
    def answer(self) -> int:
        if self.operation == "add":
            return self.left + self.right
        if self.operation == "subtract":
            return self.left - self.right
        return self.left * self.right

    @property
    def prompt(self) -> str:
        return f"{self.left} {self.symbol} {self.right} = ?"

    @property
    def explanation(self) -> str:
        return f"{self.left} {self.symbol} {self.right} = {self.answer}"


DIFFICULTIES: dict[str, Difficulty] = {
    "🌱 新手（10以内加法）": Difficulty(
        question_count=5,
        operations=("add",),
        limit=10,
        description="完成 5 道 10 以内的加法题",
    ),
    "🌟 勇士（20以内加减）": Difficulty(
        question_count=8,
        operations=("add", "subtract"),
        limit=20,
        description="完成 8 道 20 以内的加减法题",
    ),
    "🚀 大师（九九乘法）": Difficulty(
        question_count=10,
        operations=("multiply",),
        limit=9,
        description="完成 10 道九九乘法题",
    ),
}


def generate_question(
    difficulty: Difficulty,
    rng: random.Random | None = None,
) -> Question:
    """Generate a question that stays within the difficulty's limits."""
    generator = rng or random.Random()
    operation = generator.choice(difficulty.operations)

    if operation == "add":
        total = generator.randint(2, difficulty.limit)
        left = generator.randint(0, total)
        return Question(left, total - left, operation)

    if operation == "subtract":
        left = generator.randint(1, difficulty.limit)
        right = generator.randint(0, left)
        return Question(left, right, operation)

    return Question(
        generator.randint(1, difficulty.limit),
        generator.randint(1, difficulty.limit),
        operation,
    )


def check_answer(question: Question, answer: int) -> bool:
    """Return whether an answer solves the question."""
    return answer == question.answer


def points_for_correct(streak: int) -> int:
    """Award a small, capped bonus for consecutive correct answers."""
    return 10 + min(max(streak - 1, 0) * 2, 10)
