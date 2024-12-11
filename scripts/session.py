
import threading
import pygame as pg
import scripts.networking as net
import scripts.tetris as tetris
import scripts.display as display

def start_game():

    pg.init()
    pg.display.set_caption("Tetris")
    screen = pg.display.set_mode((1280, 720), pg.RESIZABLE)
    clock = pg.time.Clock()
    dt = 0

    game_display = display.GameDisplay(2)
    game_display.init_sprites()
    game = tetris.TetrisGame(game_display)

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    exit()
                if event.key == pg.K_LEFT:
                    if game.current_piece_id is not None:
                        game.move_piece(game.current_piece_id, (0, -1))
                if event.key == pg.K_RIGHT:
                    if game.current_piece_id is not None:
                        game.move_piece(game.current_piece_id, (0, 1))
                if event.key == pg.K_DOWN:
                    if game.current_piece_id is not None:
                        game.hard_drop = True
                if event.key == pg.K_UP:
                    if game.current_piece_id is not None:
                        game.rotate_piece(game.current_piece_id, -1)
                if event.key == pg.K_RETURN:
                    game.start()
            if event.type == pg.KEYUP:
                if event.key == pg.K_DOWN:
                    game.hard_drop = False

        game.update(dt)

        update_thread = threading.Thread(target=net.send_update, args=(game.board,))
        update_thread.start()

        game_display.display_game(0, game.board)
        if net.opponent_board is not None:
            game_display.display_game(1, net.opponent_board)
        game_display.update_screen(screen)

        dt = clock.tick(60) / 1000
