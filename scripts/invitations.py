
import socket
import threading
import time
from queue import Queue

def get_own_ip():
	with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
		s.connect(("8.8.8.8", 80))
		return s.getsockname()[0]

class InvitationListener:
	def __init__(self, port=33333):
		self.port = port
		self.stop_event = threading.Event()
		self.invitations = Queue()  # Thread-safe queue to store incoming invitations

	def start(self):
		def listener():
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.bind(("0.0.0.0", self.port))
			s.listen(5)
			s.settimeout(0.1)
			print(f"Started invitation listener at {get_own_ip()}:{self.port}")
			while not self.stop_event.is_set():
				try:
					conn, addr = s.accept()
					if conn.recv(1024).decode() == "INVITE":
						ip = addr[0]
						print(f"Received invitation from {ip}")
						self.invitations.put(ip)
					conn.close()
				except socket.timeout:
					continue
			s.close()

		self.thread = threading.Thread(target=listener)
		self.thread.start()

	def stop(self):
		self.stop_event.set()
		self.thread.join()
		print("Invitation listener stopped")

	def get_invitations(self):
		invitations = []
		while not self.invitations.empty():
			invitations.append(self.invitations.get())
		return invitations

class InvitationResponseHandler:
	def __init__(self, port=33334):
		self.port = port
		self.stop_event = threading.Event()
		self.open_invitations = {}

	def start(self):
		def listener():
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.bind(("0.0.0.0", self.port))
			s.listen(5)
			s.settimeout(0.1)
			print(f"Started invitation response listener at {get_own_ip()}:{self.port}")
			while not self.stop_event.is_set():
				try:
					conn, addr = s.accept()
					ip = addr[0]
					response = conn.recv(1024).decode()
					if response in ["ACCEPT", "DECLINE"]:
						print(f"{ip} {response.lower()}ed the invitation")
						self.handle_response(ip, response)
					conn.close()
				except socket.timeout:
					continue
			s.close()

		self.thread = threading.Thread(target=listener)
		self.thread.start()

	def stop(self):
		self.stop_event.set()
		self.thread.join()
		print("Invitation response listener stopped")

	def add_invitation(self, ip):
		if ip not in self.open_invitations:
			self.open_invitations[ip] = threading.Event()

	def handle_response(self, ip, response):
		if ip in self.open_invitations:
			if response == "ACCEPT":
				self.open_invitations[ip].set()
			elif response == "DECLINE":
				del self.open_invitations[ip]

	def wait_for_response(self, ip, timeout=10):
		if ip in self.open_invitations:
			event = self.open_invitations[ip]
			accepted = event.wait(timeout)
			if accepted:
				print(f"Invitation to {ip} was accepted")
				return True
			else:
				print(f"Invitation to {ip} timed out or was declined")
				return False
		return False

# Usage example
if __name__ == "__main__":
	invitation_listener = InvitationListener()
	invitation_listener.start()

	response_handler = InvitationResponseHandler()
	response_handler.start()

	def simulate_invitations():
		ips = ["192.168.1.100", "192.168.1.101", "192.168.1.102"]
		for ip in ips:
			print(f"Simulating invitation from {ip}")
			response_handler.add_invitation(ip)
			time.sleep(2)

	invitation_simulator = threading.Thread(target=simulate_invitations)
	invitation_simulator.start()

	try:
		while True:
			new_invitations = invitation_listener.get_invitations()
			print(invitation_listener.invitations.queue)
			print(response_handler.open_invitations)
			for ip in new_invitations:
				response_handler.add_invitation(ip)
			time.sleep(1)
	except KeyboardInterrupt:
		invitation_listener.stop()
		response_handler.stop()
		invitation_simulator.join()
