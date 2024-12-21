
import scripts.networking as net
import scripts.session as session
import scripts.invitations as inv

def start():

    inv_listener = inv.InvitationListener()
    inv_listener.start()

    inv_res_handler = inv.InvitationResponseListener()
    inv_res_handler.start()

    while True:

        if net.update_socket is not None:
            session.start_game()

        query = input("> ")
        if query == "":
            continue
        match(query.split()[0]):
            case "exit":
                inv_listener.stop()
                inv_res_handler.stop()
                exit()

            case "clear":
                print("\033[H\033[J", end="")

            case "ip":
                print(net.get_own_ip())

            case "invite":
                ip = query.split()[1]
                inv.send_invitation(ip)

            case "invitations":
                print(inv.invitations)

            case "accept":
                ip = query.split()[1]
                inv.accept_invitation(ip)

            case "decline":
                ip = query.split()[1]
                inv.decline_invitation(ip)

            case _:
                print("Unknown command")

if __name__ == "__main__":
    start()
