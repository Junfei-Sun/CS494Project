import socket
import threading
import json



host= 'localhost'
port= 8080


class User():
    def __init__(self, address, socket):
        self.caddress = address
        self.csocket = socket

class HandleRequest():
    """
    data = {
        username:
        type:
        status:
        info:
    }
    """
    usernames={}

    def __init__(self, user):
        self.user = user

    def deluser(user):
        try:
            HandleRequest.usernames.pop(user)
        except Exception as e:
            print(e)

    def send2Me(self, data):
        jData = json.dumps(data)
        self.user.csocket.send(jData.encode())
        print("send "+jData)

    def login(self, data):
        if self.user in HandleRequest.usernames.keys():
            data['status'] = False
            data['info'] = "You already login."
        elif data['username'] in HandleRequest.usernames.values():
            data['status'] = False
            data['info'] = "This username is already in use."
        else:
            data['status'] = True
            HandleRequest.usernames[self.user] = data['username']
        self.send2Me(data)

    def logout(self, data):
        print(HandleRequest.usernames[self.user]+"logout.")
        HandleRequest.deluser(self.user)

    def __main__(self, data):
        type = data['type']
        switch = {
            "login": self.login,
            "logout": self.logout, 
        }
        #try:
        return switch[type](data)
        """except Exception as e:
            print(e)
            data['status'] = False
            data['info'] = "Unkown error"
            return data
        """

class ClientThread(threading.Thread):
    def __init__(self, user):
        threading.Thread.__init__(self)
        self.user = user

    def run(self):
        #try:
        handle = HandleRequest(self.user)
        while True:
            request_data = self.user.csocket.recv(2048)
            data = json.loads(request_data.decode())
            print("Receive "+request_data.decode())
            if data['type'] == 'logout':
                break
            else:
                handle.__main__(data)
        #except Exception as e:
        #    print("Disconnect...")
        #    print(e)
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