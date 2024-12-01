
import socket
import threading
import time
import json

PORT = 33333

current_invitation = {}
open_invitations = {}

host = None
players = {}

to_kick = []
to_join = []

running = True
stop_listener = threading.Event()
stop_manager = threading.Event()

def get_own_ip():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]

def establish_connection(ip, port=PORT):
	print(f"Trying to connect to {ip}:{port}...")
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((ip, port))
		print(f"Successfully connected to {ip}:{port}")
		return s
	except socket.gaierror:
		print(f"Invalid IP address: {ip}")
	except ConnectionRefusedError:
		print(f"Connection refused by {ip}:{port}")
	except TimeoutError:
		print(f"Connection to {ip}:{port} timed out")
	except Exception as e:
		print(f"An unexpected error occurred: {e}")
	return None

def start_invitation_listener():
	def invite_listener():
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind(("0.0.0.0", PORT))
		s.listen(1)
		s.settimeout(0.1)
		print(f"Listening for invitations on port {PORT}")
		while not stop_listener.is_set():
			try:
				conn, addr = s.accept()
				if conn.recv(1024).decode() == "INVITE":
					ip = addr[0]
					print(f"\rReceived invitation from {ip}\n> ", end="")
					global current_invitation
					current_invitation = {ip: conn}
			except socket.timeout:
				continue
		s.close()
		print("Invitation listener stopped")
	
	listener = threading.Thread(target=invite_listener)
	listener.start()

	time.sleep(0.1)  # Allow the thread to start before continuing

	return listener

def answer_invitations():
	global current_invitation
	if current_invitation:
		ip, sock = current_invitation.popitem()
		if input(f"Accept invitation from {ip}? (y/n): ").lower() == "y":
			sock.send("JOIN".encode())
			global host, players

			if host is None:
				# Dissolve party
				dissolve_party()
			else:
				# Leave party
				print(f"Leaving party of {host['ip']}")
				send_host("LEAVE")

			# Join party of ip
			host = {"ip": ip, "socket": sock}
			players = None
		else:
			sock.send("DECLINE".encode())
			sock.close()
		current_invitation = ""

def send_all(message: str):
	if host is None:
		for player in players:
			send_player(player, message)

def send_host(message: str):
	if host is not None:
		host["socket"].send(message.encode())

def send_player(player, message: str):
	if player not in players:
		print(f"{player} is not in the party")
	else:
		players[player].send(message.encode())

def invite_player(ip):
	sock = establish_connection(ip)
	if sock is not None:
		sock.send("INVITE".encode())
		print(f"Invited {ip}")
	else:
		print(f"Failed to invite {ip}")
	open_invitations[ip] = sock

def add_player(ip, socket):
	to_join.append((ip, socket))

def kick_player(ip):
	send_player(ip, "KICK")
	players[ip].close()
	global to_kick
	to_kick.append(ip)
	print(f"Kicked {ip}")

def create_party():
	global host, players
	host = None
	players = {}
	print("Party created")

def dissolve_party():
	global host, players
	send_all("DISSOLVE")
	for player in players:
		players[player].close()
	players = None
	print("Party dissolved")

def query_action():
	global host, players
	action = input("> ").split()

	# Ignore empty lines
	if len(action) == 0:
		return

	# Invite ip to party, if you are host
	elif action[0] == "invite":
		if host is None:
			try:
				if action[1] == get_own_ip():
					print("You cannot invite yourself")
				else:
					invite_player(action[1])
			except IndexError:
				print("Missing IP address")
		else:
			print(f"Only the host ({host["ip"]}) can invite players")
	
	# Answer invitations
	elif action[0] == "invitation":
		if current_invitation:
			answer_invitations()
		else:
			print("No invitations")

	# Leave party / stop program if you are host
	elif action[0] == "leave":
		if host is None:
			stop_all()
		else:
			print("Leaving party")
			send_host("LEAVE")
			create_party()
	
	# Kick player from party
	elif action[0] == "kick":
		if host is None:
			try:
				if action[1] == get_own_ip():
					print("You cannot kick yourself")
				else:
					kick_player(action[1])
			except IndexError:
				print("Missing IP address")
		else:
			print(f"Only the host ({host['ip']}) can kick players")
	
	# List players
	elif action[0] == "list":
		if host is None:
			print(f"Host: You ({get_own_ip()})")
			if len(players) == 0:
				print("No players")
			else:
				[print(player) for player in players]
		else:
			send_host("LIST")
			info = json.loads(host["socket"].recv(1024).decode())
			print(f"Host: {info["host"]}")
			[print(player) for player in info["players"]]
	
	else:
		print("Unknown command")

def start_manager():
	global stop_manager
	stop_manager.clear()
	def manage():
		global host, players
		while not stop_manager.is_set():
			# Host jobs
			if host is None:
				for player in players:
					socket = players[player]
					try:
						request = socket.recv(1024)

						if request.decode() == "LEAVE":
							socket.close()
							global to_kick
							to_kick.append(player)
							print(f"\r{player} left party\n> ", end="")
						
						elif request.decode() == "LIST":
							info = {"host": get_own_ip(), "players": list(players.keys())}
							socket.send(json.dumps(info).encode())
						
						else:
							print(f"\rUnknown request {request.decode()} from {player}\n> ", end="")
					except:
						print(f"\rConnection with {player} closed\n> ", end="")
				
				for invitation in open_invitations:
					socket = open_invitations[invitation]
					if socket is not None:
						request = socket.recv(1024)
						if request.decode() == "DECLINE":
							print(f"\r{invitation} declined invitation\n> ", end="")
							socket.close()
							open_invitations.pop(invitation)
						elif request.decode() == "JOIN":
							print(f"\r{invitation} joined party\n> ", end="")
							global to_join
							to_join.append((invitation, socket))
			
			# Player jobs
			else:
				request = host["socket"].recv(1024)
				if request.decode() == "DISSOLVE":
					create_party()
		
		# Manager stopped, which means player is exiting program
		dissolve_party()
		send_host("LEAVE")
	
	manager = threading.Thread(target=manage)
	manager.start()

	time.sleep(0.1)  # Allow the thread to start before continuing

	return listener

def stop_all():
	print("Stopping program")
	global stop_listener, stop_manager, running
	stop_manager.set()
	stop_listener.set()
	running = False

if __name__ == "__main__":

	print(f"Your IP-Address: {get_own_ip()}")

	listener = start_invitation_listener()

	create_party()

	while running:

		for ip in to_kick:
			players.pop(ip)
		to_kick = []
		for ip, sock in to_join:
			players[ip] = sock
		to_join = []
		
		# Do actions
		query_action()

	listener.join()

	print("Program stopped")
