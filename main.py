import logging

import pygame as pg
from pygame.event import EventType

from game.board import Board

module_logger = logging.getLogger("main")


def main():
    logging.basicConfig(level=logging.INFO)
    pg.init()
    pg.display.set_caption("Othello")
    done = False
    board = Board()
    while not done:
        for event in pg.event.get():
            match event:
                case EventType(type=pg.KEYDOWN):
                    if event.key == pg.K_p:
                        board.pass_move()
                    elif event.key == pg.K_q:
                        done = True
                    elif event.key == pg.K_r:
                        board.revert()
                case EventType(type=pg.QUIT):
                    done = True
                case EventType(type=pg.MOUSEBUTTONDOWN):
                    x = pg.mouse.get_pos()[0] // Board.SQUARE_SIZE
                    y = pg.mouse.get_pos()[1] // Board.SQUARE_SIZE
                    module_logger.debug(f"{board.player} on row:{y} and column:{x}")
                    board.update(column=x, row=y)
        pg.display.flip()
    pg.quit()


if __name__ == "__main__":
    main()
