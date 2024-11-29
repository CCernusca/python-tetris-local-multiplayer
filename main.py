
import scripts.networking as net
import scripts.tetris as tetris
import scripts.display as display
import pygame as pg

def query_opponent():
    opponent_ip = input("Enter the IP-Address of your opponent: ")
    net.establish_connection(opponent_ip)

if __name__ == '__main__':
    print(f"Your IP-Address: {net.get_own_ip()}")
    
    # game_socket = None
    # while not game_socket:
    #     game_socket = query_opponent()

    game = tetris.TetrisGame()

    pg.init()
    pg.display.set_caption('Tetris')
    screen = pg.display.set_mode((400, 800))
    clock = pg.time.Clock()

    running = True

    while running:

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False
                if event.key == pg.K_LEFT:
                    game.move_left()
                if event.key == pg.K_RIGHT:
                    game.move_right()
                if event.key == pg.K_DOWN:
                    game.move_down()
                if event.key == pg.K_UP:
                    game.rotate()
    
        display.display_game(screen, game)

        clock.tick(60)
