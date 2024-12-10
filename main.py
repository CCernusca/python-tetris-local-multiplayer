
import pygame as pg
import scripts.networking as net
import scripts.tetris as tetris
import scripts.display as display

def start():

    net.start_invitation_listener()

    while True:
        query = input("> ")
        if query == "":
            print(net.current_invitation)
            continue
        match(query.split()[0]):
            case "exit":
                net.stop_listeners()
                exit()

            case "clear":
                print("\033[H\033[J", end="")

            case "ip":
                print(net.get_own_ip())

            case "invite":
                ip = query.split()[1]
                net.send_invitation(ip)

            case "invitation":
                net.get_current_invitation()

            case "accept":
                valid = net.current_invitation

                net.accept_invitation()

                # Start game

                if valid:
                    pg.init()
                    pg.display.set_caption("Tetris")
                    screen = pg.display.set_mode((800, 600))
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

                        net.send_update(game.board)
                        game_display.display_game(0, game.board)
                        if net.opponent_board is not None:
                            game_display.display_game(1, net.opponent_board)
                        game_display.update_screen(screen)

                        dt = clock.tick(60) / 1000

            case "decline":
                net.decline_invitation()

            case _:
                print("Unknown command")

if __name__ == "__main__":
    start()
