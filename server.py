import socket
from elevator import Elevator
import threading

elevator1 = Elevator("1")
elevator2 = Elevator("2")

# 1. 建立一個 socket 物件
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 2. 綁定地址:127.0.0.1 是「本機」,12345 是門牌號(port)
server_socket.bind(("127.0.0.1", 12345))

# 3. 開始監聽,等人來連
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
                print("Invalid command format. Use: <elevator> <floor>")
                continue
            which_elevator = parts[0]
            target_floor = int(parts[1])

            if which_elevator == "1":
                t = threading.Thread(target=elevator1.move, args=(target_floor,))
                t.start()
            elif which_elevator == "2":
                t = threading.Thread(target=elevator2.move, args=(target_floor,))
                t.start()
            else:
                print("Unknown elevator. Use 1 or 2.")

        client_connection.close()
except KeyboardInterrupt:
    print("\nServer shutting down...")
finally:
    server_socket.close() 