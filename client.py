import socket
import json
 
host = "localhost"
port = 8080
 

class Handle():
    def __init__(self, socket):
        self.socket = socket

    def login(self, data):
        sData = {"type": "login", "username": data[1]}
        jData = json.dumps(sData)
        self.socket.send(jData.encode())

    def logout(self, data):
        sData = {"type": "logout"}
        jData = json.dumps(sData)
        self.socket.send(jData.encode())

    def help(self, data):
        print("****************************")
        print(" Opreation Menu ")
        print("****************************")      
        print("register USERNAME")
        print("login USERNAME")
        print("logout USERNAME")
        print("startshat USERNAME")
        print("createchatroom ROOMNAME")
        print("joinchatroom ROOMNAME")
        print("userlist")
        print("roomlist\n")
        print("Type to Perform Operation: ")

    def __main__(self, data):
        type = data[0]
        switch = {
            "help": self.help,
            #"register": self.register
            "login": self.login,
            "logout": self.logout,
            #"startchat":self.startchat
            #"createchatroom":self.createchatroom
            #"joinchatroom":self.joinchatroom
            #"userlist":self.userlist
            #"roomlist":self.roomlist
        }
        try:
            return switch[type](data)
        except Exception as e:
            print(type)
            print(data)
            print(e)

class Client():
    def __main__(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect((host,port))
        except Exception as e:
            print(e)
        print("Connect to Server.\nInput format: Command Information. If need help, enter help as Command.")
        handle = Handle(client_socket)
        while True:
            rawData = input()
            data = rawData.split()
            if(data[0]=="exit"):
                break
            else:
                handle.__main__(data)
            recvData = client_socket.recv(1024)
            print(recvData.decode())

if __name__ == "__main__":
    client=Client()
    client.__main__()


"""
data = input("Input massage: ")
client_socket.sendto(data.encode(),(host,port))
data = client_socket.recv(1024)
client_socket.close()
print(data.decode())
"""
