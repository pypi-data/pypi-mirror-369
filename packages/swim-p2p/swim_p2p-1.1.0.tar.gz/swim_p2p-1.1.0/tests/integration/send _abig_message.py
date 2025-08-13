import socket
import json

# Create a large message (over 1400 bytes)
large_data = {
    "type": "TEST",
    "data": "x" * 2000,  # 2000 character string
    "from": "127.0.0.1:9999"
}

# Send to the Lifeguard node
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
message = json.dumps(large_data).encode()
print(f"Sending {len(message)} byte message...")
sock.sendto(message, ('127.0.0.1', 8000))
sock.close()