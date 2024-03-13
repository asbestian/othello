import logging

import pygame as pg
from pygame.event import EventType

from game.board import Board, Player

logger = logging.getLogger("main")


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
                    elif event.key == pg.K_p:  # pass
                        board.pass_move
                    elif event.key == pg.K_q:  # quit
                        done = True
                    elif event.key == pg.K_r:  # revert
                        board.revert()
                    elif event.key == pg.K_s:  # score
                        logger.info(
                            "Current score of %s: %d",
                            Player.BLACK,
                            board.score(Player.BLACK),
                        )
                        logger.info(
                            "Current score of %s: %d",
                            Player.WHITE,
                            board.score(Player.WHITE),
                        )
                case EventType(type=pg.QUIT):
                    done = True
                case EventType(type=pg.MOUSEBUTTONDOWN):
                    x = pg.mouse.get_pos()[0] // Board.SQUARE_SIZE
                    y = pg.mouse.get_pos()[1] // Board.SQUARE_SIZE
                    logger.debug(f"{board.player} on row:{y} and column:{x}")
                    board.update(column=x, row=y)
        pg.display.flip()
    pg.quit()
    logger.info("Score of %s: %d", Player.BLACK, board.score(Player.BLACK))
    logger.info("Score of %s: %d", Player.WHITE, board.score(Player.WHITE))


if __name__ == "__main__":
    main()
