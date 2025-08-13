import asyncio
import logging
import argparse
import sys

from swim.transport.udp import UDPTransport
from swim.transport.base import Transport

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

async def main(mode, host, port, target_host=None, target_port=None):
    """Run a simple transport example.
    
    Args:
        mode: 'sender' or 'receiver'
        host: Local host address
        port: Local port to bind to
        target_host: Remote host for sender mode
        target_port: Remote port for sender mode
    """
    transport = UDPTransport()
    await transport.bind((host, port))
    
    if mode == 'receiver':
        print(f"Receiver listening on {host}:{port}")
        
        async def on_message(data, addr):
            print(f"Received message from {addr[0]}:{addr[1]}: {data.decode()}")
            # Echo back
            await transport.send(f"Echo: {data.decode()}".encode(), addr)
        
        await transport.start_receiver(on_message)
        
        # Keep running until interrupted
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("Shutting down receiver...")
            
    elif mode == 'sender':
        if not target_host or not target_port:
            print("Error: target_host and target_port required for sender mode")
            return
            
        print(f"Sender started on {host}:{port}, targeting {target_host}:{target_port}")
        
        async def on_message(data, addr):
            print(f"Received response from {addr[0]}:{addr[1]}: {data.decode()}")
        
        await transport.start_receiver(on_message)
        
        try:
            while True:
                message = input("Enter message to send (or 'quit' to exit): ")
                if message.lower() == 'quit':
                    break
                    
                await transport.send(message.encode(), (target_host, target_port))
                await asyncio.sleep(0.1)  # Give time for response
        except KeyboardInterrupt:
            print("Shutting down sender...")
    
    await transport.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SWIM Transport Example")
    parser.add_argument('mode', choices=['sender', 'receiver'], help='Run as sender or receiver')
    parser.add_argument('--host', default='127.0.0.1', help='Local host address')
    parser.add_argument('--port', type=int, required=True, help='Local port')
    parser.add_argument('--target-host', help='Target host for sender mode')
    parser.add_argument('--target-port', type=int, help='Target port for sender mode')
    
    args = parser.parse_args()
    
    try:
        asyncio.run(main(args.mode, args.host, args.port, args.target_host, args.target_port))
    except KeyboardInterrupt:
        print("Program terminated")