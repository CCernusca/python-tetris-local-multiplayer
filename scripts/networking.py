
import socket
import threading
import sys

PORT = 33333

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

current_invitations = {}

def start_invitation_listener():
	def invite_listener():
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind(("0.0.0.0", PORT))
		s.listen(1)
		print(f"Listening for invitations on port {PORT}")
		while True:
			conn, addr = s.accept()
			if conn.recv(1024).decode() == "INVITE":
				ip = addr[0]
				print(f"Received invitation from {ip}")
				global current_invitations
				current_invitations = {ip: conn}
	
	threading.Thread(target=invite_listener).start()

def answer_invitations():
	global current_invitations
	if current_invitations:
		ip, sock = current_invitations.popitem()
		if input(f"Accept invitation from {ip}? (y/n): ").lower() == "y":
			sock.send("JOIN".encode())
		else:
			sock.send("DECLINE".encode())
			sock.close()
		current_invitations = ""

class Lobby:

	def __init__(self, owner_ip: str):
		self.player_ips = [owner_ip]
		self.owner_ip = owner_ip
		self.sockets = {}
		print(f"Created lobby with owner {owner_ip}")
	
	def invite_ip(self, ip: str):
		if ip in self.player_ips:
			print(f"{ip} is already in the lobby")
			return
		print(f"Inviting {ip} to the lobby...")
		sock = establish_connection(ip)
		if sock is not None:
			sock.send("INVITE".encode())
			if sock.recv(1024).decode() == "JOIN":
				self.player_ips.append(ip)
				print(f"Successfully invited {ip} to the lobby")
				self.sockets[ip] = sock
			else:
				print(f"{ip} rejected the invitation")
	
	def remove_ip(self, ip: str):
		if ip == get_own_ip():
			print("You cannot remove yourself from the lobby")
		else:
			self.player_ips.remove(ip)
			self.sockets[ip].close()
			self.sockets.pop(ip)
	
	def command(self):
		cmd = list(input("> ").split())

		if len(cmd) == 0:
			return
		
		if cmd[0] == "leave":
			print("Leaving...")
			sys.exit()
			return

		if cmd[0] == "invitations":
			answer_invitations()
			return

		if self.owner_ip == get_own_ip():
			if cmd[0] == "invite":
				self.invite_ip(cmd[1])
			elif cmd[0] == "remove":
				self.remove_ip(cmd[1])
			elif cmd[0] == "list":
				for ip in self.player_ips:
					print(ip)
			elif cmd[0] == "start":
				...
			else:
				print("Invalid command")
		else:
			print("You are not the owner of this lobby")
