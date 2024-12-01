
import scripts.networking as net

if __name__ == "__main__":

	print(f"Your IP-Address: {net.get_own_ip()}")

	listener = net.start_invitation_listener()
	manager = net.start_manager()

	net.create_party()

	while net.running:
		
		# Do actions
		net.query_action()

	listener.join()
	manager.join()

	print("Program stopped")
