
import scripts.networking as net
import scripts.session as session

def start():

    net.start_invitation_listener()

    while True:

        if net.current_opponent:
            session.start_game()

        query = input("> ")
        if query == "":
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
                net.accept_invitation()

            case "decline":
                net.decline_invitation()

            case _:
                print("Unknown command")

if __name__ == "__main__":
    start()
