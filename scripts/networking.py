
import socket

PORT = 33333

def get_own_ip():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]

def establish_connection(ip, port=PORT):
	print(f"Trying to connect to {ip}:{port}...")
	try:
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
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
