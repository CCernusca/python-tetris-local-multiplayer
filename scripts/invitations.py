
import socket
import threading
import time

try:
	import scripts.networking as net
except ModuleNotFoundError:
	import networking as net

# IP addresses of all players who have sent invitations which the player has yet to answer
invitations = set()
# IP addresses of all players invitations have been sent to, which have not been answered yet
open_invitations = set()

class InvitationListener:
	def __init__(self, port=net.INVITATION_PORT):
		self.port = port
		self.stop_event = threading.Event()
		self.thread = None

	def start(self):
		if self.thread is not None:
			print("Invitation listener already started")
			return
		def listener():
			print(f"Starting invitation listener at {net.get_own_ip()}:{self.port}")
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.bind(("0.0.0.0", self.port))
			s.listen(5)
			s.settimeout(0.1)
			while not self.stop_event.is_set():
				try:
					conn, addr = s.accept()
					if conn.recv(1024).decode() == "INVITE":
						ip = addr[0]
						print(f"Received invitation from {ip}")
						invitations.add(ip)
					conn.close()
				except socket.timeout:
					continue
			s.close()

		self.thread = threading.Thread(target=listener)
		self.thread.start()

		time.sleep(0.1)  # Allow the thread to start before continuing

	def stop(self):
		self.stop_event.set()
		self.thread.join()
		print("Invitation listener stopped")

class InvitationResponseListener:
	def __init__(self, port=net.INVITATION_RESPONSE_PORT):
		self.port = port
		self.stop_event = threading.Event()
		self.thread = None

	def start(self):
		if self.thread is not None:
			print("Invitation response listener already started")
			return
		def listener():
			print(f"Starting invitation response listener at {net.get_own_ip()}:{self.port}")
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.bind(("0.0.0.0", self.port))
			s.listen(5)
			s.settimeout(0.1)
			while not self.stop_event.is_set():
				try:
					conn, addr = s.accept()
					ip = addr[0]
					if ip in open_invitations:
						response = conn.recv(1024).decode()
						if response == "ACCEPT":
							self.handle_accept(ip)
						elif response == "DECLINE":
							self.handle_decline(ip)
					conn.close()
				except socket.timeout:
					continue
			s.close()

		self.thread = threading.Thread(target=listener)
		self.thread.start()

		time.sleep(0.1)  # Allow the thread to start before continuing

	def stop(self):
		self.stop_event.set()
		self.thread.join()
		print("Invitation response listener stopped")
	
	def handle_accept(self, ip):
		print(f"Invitation to {ip} was accepted")
		
		open_invitations.remove(ip)
		create_update_connection(ip)
	
	def handle_decline(self, ip):
		print(f"Invitation to {ip} was declined")

		open_invitations.remove(ip)

#TODO Rework updating system, which includes creating update connection
def create_update_connection(ip):
	net.start_update_listener()
	net.update_socket = net.create_update_socket(ip)

def send_invitation(ip):
	print(f"Sending invitation to {ip}")
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((ip, net.INVITATION_PORT))
	s.send("INVITE".encode())
	s.close()

	open_invitations.add(ip)

def accept_invitation(ip):
	print(f"Accepting invitation from {ip}")
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((ip, net.INVITATION_RESPONSE_PORT))
	s.send("ACCEPT".encode())
	s.close()

	invitations.remove(ip)
	if ip != net.get_own_ip():  # Only one connection needed in singleplayer
		create_update_connection(ip)

def decline_invitation(ip):
	print(f"Declining invitation from {ip}")
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((ip, net.INVITATION_RESPONSE_PORT))
	s.send("DECLINE".encode())
	s.close()

	invitations.remove(ip)
