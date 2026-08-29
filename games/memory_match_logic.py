"""Pure game rules for the animal memory matching game."""

import random
from dataclasses import dataclass


ANIMALS = ("🐶", "🐱", "🐰", "🦊", "🐼", "🐸", "🐵", "🦁", "🐯", "🐨")


@dataclass(frozen=True)
class Difficulty:
    """Board configuration for one difficulty level."""

    rows: int
    columns: int
    description: str

    @property
    def pair_count(self) -> int:
        return self.rows * self.columns // 2


DIFFICULTIES: dict[str, Difficulty] = {
    "🌱 轻松（6张）": Difficulty(2, 3, "先从 3 对动物开始"),
    "🌟 进阶（12张）": Difficulty(3, 4, "记住 6 对动物的位置"),
    "🚀 挑战（20张）": Difficulty(4, 5, "找出全部 10 对动物"),
}


def build_deck(
    pair_count: int,
    rng: random.Random | None = None,
) -> list[str]:
    """Create and shuffle a deck containing two cards per animal."""
    if not 1 <= pair_count <= len(ANIMALS):
        raise ValueError(f"pair_count must be between 1 and {len(ANIMALS)}")

    deck = list(ANIMALS[:pair_count]) * 2
    (rng or random.Random()).shuffle(deck)
    return deck


def cards_match(deck: list[str], first_index: int, second_index: int) -> bool:
    """Return whether two different card positions contain the same animal."""
    return first_index != second_index and deck[first_index] == deck[second_index]
