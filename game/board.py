"""Module responsible for the Othello board."""

from enum import Enum
from itertools import product
from numpy.typing import NDArray

import logging
import numpy as np
import pygame as pg

black_rgb = (0, 0, 0)
white_rgb = (255, 255, 255)
green_rgb = (0, 140, 0)

module_logger = logging.getLogger(__name__)


class Player(Enum):
    BLACK = (1, black_rgb)
    WHITE = (2, white_rgb)

    def rgb(self) -> tuple[int, int, int]:
        return self.value[1]

    def id(self) -> int:
        return self.value[0]

    def opposite(self) -> "Player":
        return Player.BLACK if self.id() == 2 else Player.WHITE

    def __str__(self) -> str:
        return self.name.lower()

    @classmethod
    def from_id(cls, val: int) -> "Player":
        for p in Player:
            if val == p.id():
                return p
        raise RuntimeError("Invalid id.")


class Board:
    LINE_WIDTH = 5
    SQUARE_SIZE = 100
    CIRCLE_RADIUS = 30

    def __init__(self, size: int = 8, player: Player = Player.BLACK):
        self.size: int = size
        length = size * Board.SQUARE_SIZE
        self.screen = pg.display.set_mode((length, length))
        self.board: NDArray[np.byte] = np.zeros((size, size), dtype=np.byte)
        self.player: Player = player
        mid_point = size // 2 - 1
        self.board[mid_point, mid_point] = Player.WHITE.id()
        self.board[mid_point, mid_point + 1] = Player.BLACK.id()
        self.board[mid_point + 1, mid_point] = Player.BLACK.id()
        self.board[mid_point + 1, mid_point + 1] = Player.WHITE.id()
        self.previous_board: NDArray[np.byte] = self.board
        self._draw()

    def update(self, *, column: int, row: int):
        """Update the board based on the position of the new stone."""
        board = self.board
        player = self.player
        size = self.size
        if board[row, column] != 0:
            module_logger.warning("Field already occupied.")
            return

        to_flip: list[tuple[int, int]] = []
        # check left
        if column > 1 and board[row, column - 1] == player.opposite().id():
            for index in range(column - 2, -1, -1):
                if board[row, index] == player.id():
                    to_flip.extend((row, c) for c in range(index + 1, column))
                    break

        # check right
        if column < size - 1 and board[row, column + 1] == player.opposite().id():
            for index in range(column + 2, size):
                if board[row, index] == player.id():
                    to_flip.extend((row, c) for c in range(column + 1, index))
                    break

        # check top
        if row > 1 and board[row - 1, column] == player.opposite().id():
            for index in range(row - 2, -1, -1):
                if board[index, column] == player.id():
                    to_flip.extend((r, column) for r in range(index + 1, row))
                    break

        # check bottom
        if row < size - 1 and board[row + 1, column] == player.opposite().id():
            for index in range(row + 2, size):
                if board[index, column] == player.id():
                    to_flip.extend((r, column) for r in range(row + 1, index))
                    break

        # check top-right
        if (
            row > 1
            and column < size - 1
            and board[row - 1, column + 1] == player.opposite().id()
        ):
            for r_index, c_index in zip(
                range(row - 2, -1, -1), range(column + 2, size)
            ):
                if board[r_index, c_index] == player.id():
                    positions = (
                        (r, c)
                        for r, c in zip(
                            range(r_index + 1, row), range(column + 1, c_index)
                        )
                    )
                    to_flip.extend(positions)
                    break

        # check top-left
        if (
            row > 1
            and column > 1
            and board[row - 1, column - 1] == player.opposite().id()
        ):
            for r_index, c_index in zip(
                range(row - 2, -1, -1), range(column - 2, -1, -1)
            ):
                if board[r_index, c_index] == player.id():
                    positions = (
                        (r, c)
                        for r, c in zip(
                            range(r_index + 1, row), range(c_index + 1, column)
                        )
                    )
                    to_flip.extend(positions)
                    break

        # check bottom-right
        if (
            row < size - 1
            and column < size - 1
            and board[row + 1, column + 1] == player.opposite().id()
        ):
            for r_index, c_index in zip(range(row + 2, size), range(column + 2, size)):
                if board[r_index, c_index] == player.id():
                    positions = (
                        (r, c)
                        for r, c in zip(
                            range(row + 1, r_index), range(column + 1, c_index)
                        )
                    )
                    to_flip.extend(positions)
                    break

        # check bottom-left
        if (
            row < size - 1
            and column > 1
            and board[row + 1, column - 1] == player.opposite().id()
        ):
            for r_index, c_index in zip(
                range(row + 2, size), range(column - 2, -1, -1)
            ):
                if board[r_index, c_index] == player.id():
                    positions = (
                        (r, c)
                        for r, c in zip(
                            range(row + 1, r_index), range(c_index + 1, column)
                        )
                    )
                    to_flip.extend(positions)
                    break

        if not to_flip:
            module_logger.warning("Invalid move.")
        else:
            self.previous_board = np.copy(board)
            module_logger.info(f"Flip stones {to_flip}")
            board[row, column] = player.id()
            for r, c in to_flip:
                board[r, c] = player.id()
            self._draw()
            self.player = player.opposite()

    def revert(self):
        """
        Discard the last move and go back to the previous state of the board.
        """
        if (self.board != self.previous_board).any():
            module_logger.info("Reverting to previous state.")
            self.board = self.previous_board
            self._draw()
            self.player = self.player.opposite()

    def pass_move(self):
        # ToDo check whether no move available
        self.player = self.player.opposite()

    def _draw(self):
        """Draws the current pieces on the board."""
        self.screen.fill(green_rgb)
        # draw lines
        length = self.size * Board.SQUARE_SIZE
        for i in range(self.size + 1):
            h_start = (0, i * Board.SQUARE_SIZE)
            h_end = (length, i * Board.SQUARE_SIZE)
            pg.draw.line(self.screen, black_rgb, h_start, h_end, Board.LINE_WIDTH)
            v_start = (i * Board.SQUARE_SIZE, 0)
            v_end = (i * Board.SQUARE_SIZE, length)
            pg.draw.line(self.screen, black_rgb, v_start, v_end, Board.LINE_WIDTH)
        # draw stones
        for row, column in product(range(self.size), repeat=2):
            if (val := self.board[row, column]) != 0:
                x_pos = (column + 1 / 2) * Board.SQUARE_SIZE
                y_pos = (row + 1 / 2) * Board.SQUARE_SIZE
                pg.draw.circle(
                    self.screen,
                    Player.from_id(val).rgb(),
                    (x_pos, y_pos),
                    Board.CIRCLE_RADIUS,
                )
