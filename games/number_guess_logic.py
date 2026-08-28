"""Pure game rules for the number guessing game."""

from dataclasses import dataclass
from typing import Literal


GuessResult = Literal["too_low", "too_high", "correct"]


@dataclass(frozen=True)
class Difficulty:
    """Configuration for one difficulty level."""

    lower: int
    upper: int
    max_attempts: int
    description: str


DIFFICULTIES: dict[str, Difficulty] = {
    "🌱 轻松（1～10）": Difficulty(1, 10, 5, "适合第一次玩"),
    "🌟 进阶（1～50）": Difficulty(1, 50, 7, "需要一点推理"),
    "🚀 挑战（1～100）": Difficulty(1, 100, 8, "试试二分法吧"),
}


def evaluate_guess(target: int, guess: int) -> GuessResult:
    """Compare a guess with the target number."""
    if guess < target:
        return "too_low"
    if guess > target:
        return "too_high"
    return "correct"


def proximity_hint(target: int, guess: int, span: int) -> str:
    """Return an encouraging proximity hint for an incorrect guess."""
    distance = abs(target - guess)
    if distance <= max(1, span // 10):
        return "🔥 非常接近了！"
    if distance <= max(2, span // 4):
        return "🌤️ 已经不远啦！"
    return "🧭 再大胆调整一下。"
