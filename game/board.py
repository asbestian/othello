"""Module responsible for the Othello board."""

import logging
from dataclasses import dataclass
from enum import Enum

import numpy as np
import pygame as pg
from numpy.typing import NDArray

BLACK_RGB = (0, 0, 0)
WHITE_RGB = (255, 255, 255)
GREEN_RGB = (0, 140, 0)

logger = logging.getLogger(__name__)


@dataclass(init=False)
class Position:
    row: int  # row index on the board from 0 to Board.SIZE - 1
    column: int  # column index on the board from 0 to Board.SIZE - 1

    def __init__(self, row: int, column: int) -> None:
        assert row >= 0 and row < Board.SIZE, f"Row index {row} is out of range."
        assert (
            column >= 0 and column < Board.SIZE
        ), f"Column index {column} is out of range."
        self.row = row
        self.column = column


class Player(Enum):
    BLACK = (1, BLACK_RGB)
    WHITE = (2, WHITE_RGB)

    @property
    def rgb(self) -> tuple[int, int, int]:
        return self.value[1]

    @property
    def id(self) -> int:
        return self.value[0]

    @property
    def other(self) -> "Player":
        return Player.BLACK if self == Player.WHITE else Player.WHITE

    @property
    def other_id(self) -> int:
        return self.other.id

    def __str__(self) -> str:
        return self.name.lower()

    @classmethod
    def from_id(cls, id: np.byte) -> "Player":
        if id == cls.BLACK.id:
            return cls.BLACK
        elif id == cls.WHITE.id:
            return cls.WHITE
        else:
            raise RuntimeError("Invalid id %d.", id)


class Board:
    """Represents the Othello board."""

    LINE_WIDTH = 5
    SQUARE_SIZE = 100
    CIRCLE_RADIUS = 30
    SIZE = 8

    def __init__(self, player: Player = Player.BLACK):
        length = Board.SIZE * Board.SQUARE_SIZE
        self.screen = pg.display.set_mode((length, length))
        self.board: NDArray[np.byte] = np.zeros((Board.SIZE, Board.SIZE), dtype=np.byte)
        self.player: Player = player
        mid_point = Board.SIZE // 2 - 1
        self.board[mid_point, mid_point] = Player.WHITE.id
        self.board[mid_point, mid_point + 1] = Player.BLACK.id
        self.board[mid_point + 1, mid_point] = Player.BLACK.id
        self.board[mid_point + 1, mid_point + 1] = Player.WHITE.id
        self.previous_board: NDArray[np.byte] = self.board
        self.getters = [
            self._get_left_stones_to_flip,
            self._get_right_stones_to_flip,
            self._get_top_stones_to_flip,
            self._get_bottom_stones_to_flip,
            self._get_top_right_stones_to_flip,
            self._get_top_left_stones_to_flip,
            self._get_bottom_right_stones_to_flip,
            self._get_bottom_left_stones_to_flip,
        ]
        self._draw()

    def _get_left_stones_to_flip(self, pos: Position) -> list[Position]:
        """Returns list of positions, left of given position, to flip if stone with given position is played by current player."""
        result: list[Position] = []
        row = pos.row
        col = pos.column
        if col > 1 and self.board[row, col - 1] == self.player.other_id:
            for index in range(col - 2, -1, -1):
                if self.board[row, index] == self.player.id:
                    result.extend(
                        Position(row=row, column=c) for c in range(index + 1, col)
                    )
                    break
        return result

    def _get_right_stones_to_flip(self, pos: Position) -> list[Position]:
        """Returns list of positions, right of given position, to flip if stone with given position is played by current player."""
        result: list[Position] = []
        row = pos.row
        column = pos.column
        if (
            column < Board.SIZE - 1
            and self.board[row, column + 1] == self.player.other_id
        ):
            for index in range(column + 2, Board.SIZE):
                if self.board[row, index] == self.player.id:
                    result.extend(
                        Position(row=row, column=c) for c in range(column + 1, index)
                    )
                    break
        return result

    def _get_top_stones_to_flip(self, pos: Position) -> list[Position]:
        """Returns list of positions, on top of given position, to flip if stone with given position is played by current player."""
        result: list[Position] = []
        row = pos.row
        column = pos.column
        if row > 1 and self.board[row - 1, column] == self.player.other_id:
            for index in range(row - 2, -1, -1):
                if self.board[index, column] == self.player.id:
                    result.extend(
                        Position(row=r, column=column) for r in range(index + 1, row)
                    )
                    break
        return result

    def _get_bottom_stones_to_flip(self, pos: Position) -> list[Position]:
        """Returns list of positions, bottom of given position, to flip if stone with given position is played by current player."""
        result: list[Position] = []
        row = pos.row
        column = pos.column
        if row < Board.SIZE - 1 and self.board[row + 1, column] == self.player.other_id:
            for index in range(row + 2, Board.SIZE):
                if self.board[index, column] == self.player.id:
                    result.extend(
                        Position(row=r, column=column) for r in range(row + 1, index)
                    )
                    break
        return result

    def _get_top_right_stones_to_flip(self, pos: Position) -> list[Position]:
        """Returns list of positions, top-right of given position, to flip if stone with given position is played by current player."""
        result: list[Position] = []
        row = pos.row
        column = pos.column
        if (
            row > 1
            and column < Board.SIZE - 1
            and self.board[row - 1, column + 1] == self.player.other_id
        ):
            for r_index, c_index in zip(
                range(row - 2, -1, -1), range(column + 2, Board.SIZE)
            ):
                if self.board[r_index, c_index] == self.player.id:
                    result.extend(
                        Position(row=r, column=c)
                        for r, c in zip(
                            range(r_index + 1, row), range(column + 1, c_index)
                        )
                    )
                    break
        return result

    def _get_top_left_stones_to_flip(self, pos: Position) -> list[Position]:
        """Returns list of positions, top-left of given position, to flip if stone with given position is played by current player."""
        result: list[Position] = []
        row = pos.row
        column = pos.column
        if (
            row > 1
            and column > 1
            and self.board[row - 1, column - 1] == self.player.other_id
        ):
            for r_index, c_index in zip(
                range(row - 2, -1, -1), range(column - 2, -1, -1)
            ):
                if self.board[r_index, c_index] == self.player.id:
                    result.extend(
                        Position(row=r, column=c)
                        for r, c in zip(
                            range(r_index + 1, row), range(c_index + 1, column)
                        )
                    )
                    break
        return result

    def _get_bottom_right_stones_to_flip(self, pos: Position) -> list[Position]:
        """Returns list of positions, bottom-right of given position, to flip if stone with given position is played by current player."""
        result: list[Position] = []
        row = pos.row
        column = pos.column
        if (
            row < Board.SIZE - 1
            and column < Board.SIZE - 1
            and self.board[row + 1, column + 1] == self.player.other_id
        ):
            for r_index, c_index in zip(
                range(row + 2, Board.SIZE), range(column + 2, Board.SIZE)
            ):
                if self.board[r_index, c_index] == self.player.id:
                    result.extend(
                        Position(row=r, column=c)
                        for r, c in zip(
                            range(row + 1, r_index), range(column + 1, c_index)
                        )
                    )
                    break
        return result

    def _get_bottom_left_stones_to_flip(self, pos: Position) -> list[Position]:
        """Returns list of positions, bottom-left of given position, to flip if stone with given position is played by current player."""
        result: list[Position] = []
        row = pos.row
        column = pos.column
        if (
            row < Board.SIZE - 1
            and column > 1
            and self.board[row + 1, column - 1] == self.player.other_id
        ):
            for r_index, c_index in zip(
                range(row + 2, Board.SIZE), range(column - 2, -1, -1)
            ):
                if self.board[r_index, c_index] == self.player.id:
                    result.extend(
                        Position(row=r, column=c)
                        for r, c in zip(
                            range(row + 1, r_index), range(c_index + 1, column)
                        )
                    )
                    break
        return result

    def update(self, *, column: int, row: int):
        """Update the board based on the given position."""
        board = self.board
        if board[row, column] != 0:
            logger.warning("Field already occupied.")
            return

        to_flip: list[Position] = []
        position = Position(row, column)

        for get_func in self.getters:
            to_flip.extend(get_func(position))

        if not to_flip:
            logger.warning("Invalid move for %s.", self.player.name)
        else:
            self.previous_board = np.copy(board)
            logger.debug("Flip stones %s", to_flip)
            board[row, column] = self.player.id
            for pos in to_flip:
                board[pos.row, pos.column] = self.player.id
            self._draw()
            self.player = self.player.other

    def revert(self):
        """
        Discard the last move and go back to the previous state of the board.
        """
        if (self.board != self.previous_board).any():
            logger.info("Reverting to previous state.")
            self.board = self.previous_board
            self._draw()
            self.player = self.player.other

    def pass_move(self) -> None:
        for row, column in np.argwhere(self.board == 0):
            pos = Position(row=row, column=column)
            for get_fct in self.getters:
                if get_fct(pos):
                    logger.warning(
                        "Passing is not permitted for %s as available move exists.",
                        self.player.name,
                    )
                    return
        self.player = self.player.other

    def score(self, player: Player) -> int:
        """Returns the current score for the given player."""
        return np.count_nonzero(self.board == player.id)

    def _draw(self):
        """Draws the current pieces on the board."""
        self.screen.fill(GREEN_RGB)
        # draw lines
        length = Board.SIZE * Board.SQUARE_SIZE
        for i in range(Board.SIZE + 1):
            h_start = (0, i * Board.SQUARE_SIZE)
            h_end = (length, i * Board.SQUARE_SIZE)
            pg.draw.line(self.screen, BLACK_RGB, h_start, h_end, Board.LINE_WIDTH)
            v_start = (i * Board.SQUARE_SIZE, 0)
            v_end = (i * Board.SQUARE_SIZE, length)
            pg.draw.line(self.screen, BLACK_RGB, v_start, v_end, Board.LINE_WIDTH)
        # draw stones
        for row, column in np.argwhere(self.board != 0):
            x_pos = (column + 1 / 2) * Board.SQUARE_SIZE
            y_pos = (row + 1 / 2) * Board.SQUARE_SIZE
            id = self.board[row, column]
            pg.draw.circle(
                self.screen,
                Player.from_id(id).rgb,
                (x_pos, y_pos),
                Board.CIRCLE_RADIUS,
            )
