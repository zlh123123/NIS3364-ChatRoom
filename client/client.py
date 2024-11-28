import socket


def start_client(host="127.0.0.1", port=12345):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    print(f"已连接到服务器 {host}:{port}")

    try:
        while True:
            message = input("输入消息: ")
            if message.lower() == "exit":
                break
            client_socket.sendall(message.encode())
            data = client_socket.recv(1024)
            print(f"服务器回复: {data.decode()}")
    finally:
        client_socket.close()


if __name__ == "__main__":
    start_client()
