import socket
import time
import random

print("Starting network stress test...")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Send bursts of traffic to create congestion
for i in range(30):
    print(f"Burst {i+1}/30")
    # Send 100 packets rapidly
    for _ in range(100):
        data = b"x" * random.randint(10, 1000)
        sock.sendto(data, ('127.0.0.1', 8000))
        sock.sendto(data, ('127.0.0.1', 8001))
    time.sleep(2)  # 2 second pause between bursts

sock.close()
print("Stress test complete")