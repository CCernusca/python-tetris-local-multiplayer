
import scripts.networking as net
import scripts.tetris as tetris
import scripts.display as display
import pygame as pg

TILE_DISPLAY_SIZE = 30

UPDATE_FREQUENCY_CHANGE_FACTOR = 1.5

def query_opponent():
    opponent_ip = input("Enter the IP-Address of your opponent: ")
    net.establish_connection(opponent_ip)

if __name__ == '__main__':
    print(f"Your IP-Address: {net.get_own_ip()}")
    
    # game_socket = None
    # while not game_socket:
    #     game_socket = query_opponent()

    game = tetris.TetrisGame()
    game.update_frequency = 5

    games_display = display.GameDisplay(4, tetris.BOARD_SIZE)
    games_display.init_sprites()

    pg.init()
    pg.display.set_caption('Tetris')
    screen = pg.display.set_mode((1280, 720), pg.RESIZABLE)
    clock = pg.time.Clock()
    dt = 0

    running = True

    while running:

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False
                if event.key == pg.K_o:
                    game.debug = not game.debug
                    games_display.debug = not games_display.debug
                if event.key == pg.K_LEFT:
                    if game.current_piece_id is not None:
                        game.move_piece(game.current_piece_id, (0, -1))
                if event.key == pg.K_RIGHT:
                    if game.current_piece_id is not None:
                        game.move_piece(game.current_piece_id, (0, 1))
                if event.key == pg.K_DOWN:
                    if game.current_piece_id is not None:
                        game.rotate_piece(game.current_piece_id, 1)
                if event.key == pg.K_UP:
                    if game.current_piece_id is not None:
                        game.rotate_piece(game.current_piece_id, -1)
                if event.key == pg.K_SPACE:
                    if game.current_piece_id is not None:
                        game.hard_drop(game.current_piece_id)
                if event.key == pg.K_RETURN:
                    game.start()
                if event.key == pg.K_HASH:
                    game.resume() if game.stopped else game.stop()
                if event.key == pg.K_PLUS:
                    game.change_update_frequency(UPDATE_FREQUENCY_CHANGE_FACTOR)
                if event.key == pg.K_MINUS:
                    game.change_update_frequency(1 / UPDATE_FREQUENCY_CHANGE_FACTOR)

        game.update(dt)
    
        games_display.display_game(0, game)
        games_display.update_screen(screen)

        dt = clock.tick(60) / 1000
