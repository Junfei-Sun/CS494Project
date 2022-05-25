import socket
import threading

from requests import request


host= 'localhost'
port= 8080


class User():
    def __init__(self, address, socket):
        self.caddress = address
        self.csocket = socket

class HandleRequest():
    def __init__(self, user):
        self.user = user

    def __main__(self, data):
        print("recieve from {addr}".format(addr=self.user.caddress))
        print(data.decode())

class ClientThread(threading.Thread):
    def __init__(self, user):
        threading.Thread.__init__(self)
        self.user = user

    def run(self):
        try:
            handle = HandleRequest(self.user)
            request_data = self.user.csocket.recv(2048)
            handle.__main__(request_data)
        except Exception as e:
            print("Disconnect...")
            print(e)
        self.user.csocket.sendto("Reply from server.".encode(), (self.user.caddress))
        self.user.csocket.close()


class Server():
    def __main__(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host,port))
        server_socket.listen(5)

        while True:
            client_socket, client_address = server_socket.accept()
            user = User(client_address, client_socket)
            t = ClientThread(user)
            t.start()

if __name__ == "__main__":
    server=Server()
    server.__main__()