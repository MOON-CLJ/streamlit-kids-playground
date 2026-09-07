"""Rules and computer-player logic for Jungle chess (Dou Shou Qi)."""

import random
from dataclasses import dataclass
from typing import Literal


Player = Literal["red", "blue"]
PieceKind = Literal[
    "rat",
    "cat",
    "dog",
    "wolf",
    "leopard",
    "tiger",
    "lion",
    "elephant",
]
Position = tuple[int, int]
Board = dict[Position, "Piece"]

ROWS = 9
COLUMNS = 7
DIRECTIONS: tuple[Position, ...] = ((-1, 0), (1, 0), (0, -1), (0, 1))

PIECE_RANKS: dict[PieceKind, int] = {
    "rat": 1,
    "cat": 2,
    "dog": 3,
    "wolf": 4,
    "leopard": 5,
    "tiger": 6,
    "lion": 7,
    "elephant": 8,
}

PIECE_EMOJIS: dict[PieceKind, str] = {
    "rat": "🐭",
    "cat": "🐱",
    "dog": "🐶",
    "wolf": "🐺",
    "leopard": "🐆",
    "tiger": "🐯",
    "lion": "🦁",
    "elephant": "🐘",
}

PIECE_NAMES: dict[PieceKind, str] = {
    "rat": "鼠",
    "cat": "猫",
    "dog": "狗",
    "wolf": "狼",
    "leopard": "豹",
    "tiger": "虎",
    "lion": "狮",
    "elephant": "象",
}

WATER: frozenset[Position] = frozenset(
    (row, column)
    for row in (3, 4, 5)
    for column in (1, 2, 4, 5)
)
DENS: dict[Player, Position] = {"red": (0, 3), "blue": (8, 3)}
TRAPS: dict[Player, frozenset[Position]] = {
    "red": frozenset({(0, 2), (0, 4), (1, 3)}),
    "blue": frozenset({(8, 2), (8, 4), (7, 3)}),
}


@dataclass(frozen=True)
class Piece:
    """One animal belonging to a player."""

    owner: Player
    kind: PieceKind

    @property
    def rank(self) -> int:
        return PIECE_RANKS[self.kind]


@dataclass(frozen=True)
class Move:
    """A move from one board position to another."""

    source: Position
    destination: Position


def opponent(player: Player) -> Player:
    """Return the other player."""
    return "blue" if player == "red" else "red"


def initial_board() -> Board:
    """Create the standard starting position."""
    placements: tuple[tuple[Position, Player, PieceKind], ...] = (
        ((0, 0), "red", "lion"),
        ((0, 6), "red", "tiger"),
        ((1, 1), "red", "dog"),
        ((1, 5), "red", "cat"),
        ((2, 0), "red", "rat"),
        ((2, 2), "red", "leopard"),
        ((2, 4), "red", "wolf"),
        ((2, 6), "red", "elephant"),
        ((8, 6), "blue", "lion"),
        ((8, 0), "blue", "tiger"),
        ((7, 5), "blue", "dog"),
        ((7, 1), "blue", "cat"),
        ((6, 6), "blue", "rat"),
        ((6, 4), "blue", "leopard"),
        ((6, 2), "blue", "wolf"),
        ((6, 0), "blue", "elephant"),
    )
    return {
        position: Piece(owner, kind)
        for position, owner, kind in placements
    }


def _in_bounds(position: Position) -> bool:
    row, column = position
    return 0 <= row < ROWS and 0 <= column < COLUMNS


def move_destination(
    board: Board,
    source: Position,
    direction: Position,
) -> Position | None:
    """Resolve a one-step move or a lion/tiger river jump."""
    piece = board.get(source)
    if piece is None:
        return None

    row_delta, column_delta = direction
    destination = (source[0] + row_delta, source[1] + column_delta)
    if not _in_bounds(destination):
        return None

    if destination not in WATER:
        return destination

    if piece.kind == "rat":
        return destination

    if piece.kind not in {"lion", "tiger"}:
        return None

    while destination in WATER:
        blocker = board.get(destination)
        if blocker is not None and blocker.kind == "rat":
            return None
        destination = (
            destination[0] + row_delta,
            destination[1] + column_delta,
        )

    return destination if _in_bounds(destination) else None


def can_capture(board: Board, source: Position, destination: Position) -> bool:
    """Return whether the source piece may capture the destination piece."""
    attacker = board.get(source)
    defender = board.get(destination)
    if attacker is None or defender is None or attacker.owner == defender.owner:
        return False

    source_in_water = source in WATER
    destination_in_water = destination in WATER
    if source_in_water != destination_in_water:
        return False

    defender_is_trapped = destination in TRAPS[attacker.owner]
    attacker_is_trapped = source in TRAPS[defender.owner]
    if defender_is_trapped:
        return True
    if attacker_is_trapped:
        return False

    if attacker.kind == "rat" and defender.kind == "elephant":
        return True
    if attacker.kind == "elephant" and defender.kind == "rat":
        return False

    return attacker.rank >= defender.rank


def legal_moves(board: Board, player: Player) -> list[Move]:
    """List every legal move for a player."""
    moves: list[Move] = []
    for source, piece in board.items():
        if piece.owner != player:
            continue

        for direction in DIRECTIONS:
            destination = move_destination(board, source, direction)
            if destination is None or destination == DENS[player]:
                continue

            occupant = board.get(destination)
            if occupant is None or can_capture(board, source, destination):
                moves.append(Move(source, destination))

    return moves


def legal_destinations(board: Board, source: Position) -> set[Position]:
    """Return legal destinations for the piece at a position."""
    piece = board.get(source)
    if piece is None:
        return set()
    return {
        move.destination
        for move in legal_moves(board, piece.owner)
        if move.source == source
    }


def apply_move(board: Board, move: Move) -> Board:
    """Apply a legal move and return a new board."""
    piece = board.get(move.source)
    if piece is None or move not in legal_moves(board, piece.owner):
        raise ValueError("Illegal move")

    new_board = dict(board)
    new_board.pop(move.source)
    new_board[move.destination] = piece
    return new_board


def get_winner(board: Board, next_player: Player | None = None) -> Player | None:
    """Return the winner after a move, including blocked-player wins."""
    for den_owner, den in DENS.items():
        occupant = board.get(den)
        if occupant is not None and occupant.owner != den_owner:
            return occupant.owner

    red_exists = any(piece.owner == "red" for piece in board.values())
    blue_exists = any(piece.owner == "blue" for piece in board.values())
    if red_exists and not blue_exists:
        return "red"
    if blue_exists and not red_exists:
        return "blue"

    if next_player is not None and not legal_moves(board, next_player):
        return opponent(next_player)
    return None


def choose_computer_move(
    board: Board,
    player: Player,
    rng: random.Random | None = None,
) -> Move | None:
    """Choose a simple move, prioritizing wins, captures, and forward progress."""
    moves = legal_moves(board, player)
    if not moves:
        return None

    enemy_den = DENS[opponent(player)]
    scored_moves: list[tuple[int, Move]] = []
    for move in moves:
        score = 0
        captured = board.get(move.destination)
        if move.destination == enemy_den:
            score += 10_000
        if captured is not None:
            score += 1_000 + captured.rank * 50
        if move.destination in TRAPS[opponent(player)]:
            score += 40

        old_distance = abs(move.source[0] - enemy_den[0]) + abs(
            move.source[1] - enemy_den[1]
        )
        new_distance = abs(move.destination[0] - enemy_den[0]) + abs(
            move.destination[1] - enemy_den[1]
        )
        score += (old_distance - new_distance) * 5
        scored_moves.append((score, move))

    best_score = max(score for score, _ in scored_moves)
    best_moves = [move for score, move in scored_moves if score == best_score]
    return (rng or random.Random()).choice(best_moves)
