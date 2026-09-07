"""Tests for Jungle chess rules and the computer player."""

import random
import unittest

from games.jungle_chess_logic import (
    DENS,
    Move,
    Piece,
    apply_move,
    can_capture,
    choose_computer_move,
    get_winner,
    initial_board,
    legal_destinations,
    legal_moves,
    move_destination,
)


class InitialBoardTest(unittest.TestCase):
    def test_each_player_starts_with_eight_animals(self) -> None:
        board = initial_board()

        self.assertEqual(len(board), 16)
        self.assertEqual(
            sum(piece.owner == "red" for piece in board.values()),
            8,
        )
        self.assertEqual(
            sum(piece.owner == "blue" for piece in board.values()),
            8,
        )


class CaptureRulesTest(unittest.TestCase):
    def test_stronger_animal_captures_weaker_animal(self) -> None:
        board = {(2, 3): Piece("blue", "dog"), (2, 4): Piece("red", "cat")}
        self.assertTrue(can_capture(board, (2, 3), (2, 4)))

    def test_weaker_animal_cannot_capture_stronger_animal(self) -> None:
        board = {(2, 3): Piece("blue", "cat"), (2, 4): Piece("red", "dog")}
        self.assertFalse(can_capture(board, (2, 3), (2, 4)))

    def test_rat_captures_elephant_on_land(self) -> None:
        board = {(2, 3): Piece("blue", "rat"), (2, 4): Piece("red", "elephant")}
        self.assertTrue(can_capture(board, (2, 3), (2, 4)))
        self.assertFalse(can_capture(board, (2, 4), (2, 3)))

    def test_rat_cannot_capture_between_water_and_land(self) -> None:
        board = {(3, 1): Piece("blue", "rat"), (3, 0): Piece("red", "elephant")}
        self.assertFalse(can_capture(board, (3, 1), (3, 0)))

    def test_any_animal_captures_an_enemy_in_its_trap(self) -> None:
        board = {(0, 1): Piece("red", "rat"), (0, 2): Piece("blue", "elephant")}
        self.assertTrue(can_capture(board, (0, 1), (0, 2)))

    def test_animal_in_enemy_trap_cannot_capture_out(self) -> None:
        board = {(0, 2): Piece("blue", "elephant"), (0, 1): Piece("red", "rat")}
        self.assertFalse(can_capture(board, (0, 2), (0, 1)))


class MovementRulesTest(unittest.TestCase):
    def test_only_rat_enters_water(self) -> None:
        rat_board = {(3, 0): Piece("blue", "rat")}
        dog_board = {(3, 0): Piece("blue", "dog")}

        self.assertIn((3, 1), legal_destinations(rat_board, (3, 0)))
        self.assertNotIn((3, 1), legal_destinations(dog_board, (3, 0)))

    def test_lion_jumps_over_an_empty_river(self) -> None:
        board = {(3, 0): Piece("blue", "lion")}
        self.assertEqual(move_destination(board, (3, 0), (0, 1)), (3, 3))

    def test_rat_blocks_lion_river_jump(self) -> None:
        board = {
            (3, 0): Piece("blue", "lion"),
            (3, 1): Piece("red", "rat"),
        }
        self.assertIsNone(move_destination(board, (3, 0), (0, 1)))

    def test_player_cannot_enter_own_den(self) -> None:
        board = {(7, 3): Piece("blue", "rat")}
        self.assertNotIn(DENS["blue"], legal_destinations(board, (7, 3)))


class WinAndMoveTest(unittest.TestCase):
    def test_entering_enemy_den_wins(self) -> None:
        board = {(1, 3): Piece("blue", "rat"), (8, 6): Piece("red", "cat")}
        new_board = apply_move(board, Move((1, 3), DENS["red"]))
        self.assertEqual(get_winner(new_board, "red"), "blue")

    def test_capture_removes_the_defender(self) -> None:
        board = {(2, 3): Piece("blue", "dog"), (2, 4): Piece("red", "cat")}
        new_board = apply_move(board, Move((2, 3), (2, 4)))

        self.assertNotIn((2, 3), new_board)
        self.assertEqual(new_board[(2, 4)], Piece("blue", "dog"))

    def test_computer_prefers_an_available_capture(self) -> None:
        board = {
            (2, 3): Piece("red", "dog"),
            (2, 4): Piece("blue", "cat"),
            (8, 6): Piece("blue", "lion"),
        }
        move = choose_computer_move(board, "red", random.Random(5))

        self.assertEqual(move, Move((2, 3), (2, 4)))

    def test_immobile_player_loses(self) -> None:
        board = {
            (0, 0): Piece("red", "rat"),
            (1, 0): Piece("blue", "dog"),
            (0, 1): Piece("blue", "cat"),
        }
        self.assertEqual(legal_moves(board, "red"), [])
        self.assertEqual(get_winner(board, "red"), "blue")


if __name__ == "__main__":
    unittest.main()
