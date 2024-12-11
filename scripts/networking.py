
import socket
import threading
import time
import pygame as pg
import numpy as np
import scripts.tetris as tetris
import scripts.display as display

INVITATION_PORT = 33333
INVITATION_RESPONSE_PORT = 33334
UPDATE_PORT = 33335

current_invitation = None
current_opponent = None

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
		while not stop_update_listener.is_set():
			try:
				conn, addr = s.accept()
				message = conn.recv(1024).decode()
				if message.startswith("UPDATE"):
					print(f"Received update from {addr[0]}: <{message.strip('UPDATE')}>")
					global opponent_board
					opponent_board = decode_board(message.strip("UPDATE"))
			except socket.timeout:
				continue
		s.close()

	listener = threading.Thread(target=update_listener)
	listener.start()

	time.sleep(0.1)  # Allow the thread to start before continuing

	return listener

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
	global current_invitation, current_opponent
	if current_invitation:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((current_invitation, INVITATION_RESPONSE_PORT))
		s.send("ACCEPT".encode())
		s.close()
		print(f"Invitation from {current_invitation} accepted")
		current_opponent = current_invitation
		current_invitation = None
		start_update_listener()
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
	stop_invitation_listener.set()
	stop_receive_listener.set()
	stop_update_listener.set()

def encode_board(board):
	return "".join(str(x) for x in np.array(board).flatten())

def decode_board(board):
	return np.array([int(x) for x in board]).reshape(*tetris.BOARD_SIZE)

def send_update(board):
	global current_opponent
	if current_opponent:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((current_opponent, UPDATE_PORT))
		s.send(f"UPDATE{encode_board(board)}".encode())
		s.close()
	else:
		print("No opponent")
