import socket
import threading
import time
import numpy as np
import scripts.tetris as tetris

INVITATION_PORT = 33333
INVITATION_RESPONSE_PORT = 33334
UPDATE_PORT = 33335

current_invitation = None
current_opponent = None
update_socket = None  # Persistent socket for updates

opponent_board = None

stop_invitation_listener = threading.Event()
stop_receive_listener = threading.Event()
stop_update_listener = threading.Event()

def get_own_ip():
	with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
		s.connect(("8.8.8.8", 80))
		return s.getsockname()[0]

def start_invitation_listener():
	def invite_listener():
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind(("0.0.0.0", INVITATION_PORT))
		s.listen(1)
		s.settimeout(0.1)
		print(f"Started invitation listener at {get_own_ip()}:{INVITATION_PORT}")
		while not stop_invitation_listener.is_set():
			try:
				conn, addr = s.accept()
				if conn.recv(1024).decode() == "INVITE":
					ip = addr[0]
					print(f"Received invitation from {ip}")
					global current_invitation
					current_invitation = ip
			except socket.timeout:
				continue
		s.close()

	listener = threading.Thread(target=invite_listener)
	listener.start()

	time.sleep(0.1)  # Allow the thread to start before continuing

	return listener

def start_invitation_response_listener():
	def invitation_response_listener():
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind(("0.0.0.0", INVITATION_RESPONSE_PORT))
		s.listen(1)
		s.settimeout(0.1)
		print(f"Started invitation response listener at {get_own_ip()}:{INVITATION_RESPONSE_PORT}")
		while not stop_receive_listener.is_set():
			try:
				conn, addr = s.accept()
				if conn.recv(1024).decode() == "ACCEPT":
					print(f"{addr[0]} accepted invitation")
					conn.close()
					start_update_listener()
					global current_opponent, update_socket
					current_opponent = addr[0]
					update_socket = create_update_socket(addr[0])  # Create persistent socket
					break
				elif conn.recv(1024).decode() == "DECLINE":
					print(f"{addr[0]} declined invitation")
					conn.close()
					break
			except socket.timeout:
				continue
		s.close()

	listener = threading.Thread(target=invitation_response_listener)
	listener.start()

	time.sleep(0.1)  # Allow the thread to start before continuing

	return listener

def start_update_listener():
	def update_listener():
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind(("0.0.0.0", UPDATE_PORT))
		s.listen(1)
		s.settimeout(0.1)
		print(f"Started update listener at {get_own_ip()}:{UPDATE_PORT}")
		conn = None
		addr = None
		try:
			while not stop_update_listener.is_set():
				if conn is None:
					try:
						conn, addr = s.accept()
						print(f"Persistent listening update connection established with {addr[0]}")
					except socket.timeout:
						continue
				else:
					try:
						message = conn.recv(1024).decode()
						if message.startswith("UPDATE"):
							print(f"Received update from {addr[0]}: <{message.strip('UPDATE')}>")
							global opponent_board
							opponent_board = decode_board(message.strip("UPDATE"))
					except (socket.error, ConnectionResetError) as e:
						print(f"Connection lost with {addr[0]}: {e}")
						conn.close()
						conn = None
		finally:
			if conn:
				conn.close()
			s.close()

	listener = threading.Thread(target=update_listener)
	listener.start()

	time.sleep(0.1)  # Allow the thread to start before continuing

	return listener


def create_update_socket(ip):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((ip, UPDATE_PORT))
	s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)# Enable Keep-Alive
	print(f"Persistent sending update socket connected to {ip}:{UPDATE_PORT}")
	return s


def close_update_socket():
	global update_socket
	if update_socket:
		update_socket.close()
		update_socket = None
		print("Persistent update socket closed")

def get_current_invitation():
	global current_invitation
	if current_invitation:
		print(f"Invitation from {current_invitation}")
	else:
		print("No invitation")

def send_invitation(ip):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((ip, INVITATION_PORT))
	s.send("INVITE".encode())
	s.close()
	print(f"Invitation sent to {ip}")
	start_invitation_response_listener()

def accept_invitation():
	global current_invitation, current_opponent, update_socket
	if current_invitation:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((current_invitation, INVITATION_RESPONSE_PORT))
		s.send("ACCEPT".encode())
		s.close()
		print(f"Invitation from {current_invitation} accepted")
		current_opponent = current_invitation
		# Start own connection if opponent is not player, as one connection is already started in start_invitation_response_listener
		if current_invitation != get_own_ip():
			start_update_listener()
			update_socket = create_update_socket(current_opponent)  # Create persistent socket
		current_invitation = None
	else:
		print("No invitation")

def decline_invitation():
	global current_invitation
	if current_invitation:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((current_invitation, INVITATION_RESPONSE_PORT))
		s.send("DECLINE".encode())
		s.close()
		print(f"Invitation from {current_invitation} declined")
		current_invitation = None
	else:
		print("No invitation")

def stop_listeners():
	global update_socket
	stop_invitation_listener.set()
	stop_receive_listener.set()
	stop_update_listener.set()
	close_update_socket()

def encode_board(board):
	return "".join(str(x) for x in np.array(board).flatten())

def decode_board(board):
	return np.array([int(x) for x in board]).reshape(*tetris.BOARD_SIZE)

def send_update(board):
	global update_socket, current_opponent
	if update_socket:
		try:
			update = encode_board(board)
			update_socket.send(f"UPDATE{update}".encode())
			print(f"Sent update to {current_opponent}: <{update}>")
		except socket.error as e:
			print(f"Failed to send update: {e}. Attempting to reconnect...")
			close_update_socket()
			if current_opponent:
				update_socket = create_update_socket(current_opponent)
	else:
		print("No opponent or persistent update socket")

