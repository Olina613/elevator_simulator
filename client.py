import socket

# 1. 建立 socket(跟 server 一樣的咒語)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 2. 主動連到 server 的地址(要跟 server 的 bind 一致)
client_socket.connect(("127.0.0.1", 12345))
print("Connected to the elevator server!")

while True:                                     # ← 讓警衛能連續下指令
    command = input("Enter command (or 'q' to quit): ")
    if command == "q":
        break                                   # ← 打 q 就離開迴圈
    client_socket.sendall(command.encode())     # ← 把指令 encode 成 bytes 送出

client_socket.close()
print("Disconnected.")