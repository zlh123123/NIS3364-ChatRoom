import socket
import threading

clients = []


def start_server(host="127.0.0.1", port=12345):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"服务器启动，监听端口 {port}...")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"连接来自 {addr}")
        clients.append(client_socket)
        threading.Thread(target=handle_client, args=(client_socket,)).start()


def handle_client(client_socket):
    with client_socket:
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break
                broadcast(data, client_socket)
            except ConnectionResetError:
                break
        clients.remove(client_socket)


def broadcast(message, sender_socket):
    for client in clients:
        if client != sender_socket:
            try:
                client.sendall(message)
            except:
                clients.remove(client)


if __name__ == "__main__":
    start_server()
