import socket
from elevator import Elevator, dispatch

elevator1 = Elevator("1")
elevator2 = Elevator("2")
elevators = [elevator1, elevator2]

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("127.0.0.1", 12345))
server_socket.listen()
print("Server is waiting for a connection...")

try:
    while True:
        client_connection, client_address = server_socket.accept()
        print(f"Connected by {client_address}")

        while True:
            data = client_connection.recv(1024)
            if not data:
                print(f"Client {client_address} disconnected.")
                break
            command = data.decode()
            print(f"Client {client_address} says: {command}")

            parts = command.split()
            if len(parts) != 2:
                print("Invalid format. Use: <floor> <up/down>")
                continue

            call_floor = int(parts[0])
            call_direction = parts[1]
            if call_direction not in ("up", "down"):
                print("Direction must be 'up' or 'down'.")
                continue

            # 智慧派車:選最適合的電梯,把樓層加進它的佇列
            chosen = dispatch(elevators, call_floor, call_direction)
            print(f"--> Dispatching Elevator {chosen.name} to floor {call_floor}")
            chosen.add_request(call_floor)

        client_connection.close()
except KeyboardInterrupt:
    print("\nServer shutting down...")
finally:
    server_socket.close()