import socket
from elevator import Elevator

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
            print(f"Client {client_address} says: {data.decode()}")

        client_connection.close()
except KeyboardInterrupt:
    print("\nServer shutting down...")
finally:
    server_socket.close()      # ← 不管怎麼結束,都確保把 socket 關乾淨