import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("127.0.0.1", 12345))
print("Connected to the elevator server!")
print("Format: target_floor up/down  e.g.  6 up")

while True:
    command = input("Enter hall call (or 'q' to quit): ")
    if command == "q":
        break
    client_socket.sendall(command.encode())

client_socket.close()
print("Disconnected.")