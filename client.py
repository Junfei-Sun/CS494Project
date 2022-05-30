import socket
import json
import threading
 
host = "localhost"
port = 8080
 

class Handle():
    def __init__(self, socket):
        self.socket = socket

    def help(self):
        print("****************************")
        print(" Menu Command ")
        print("****************************")      
        print("register USERNAME")
        print("login USERNAME")
        print("logout")
        print("listUsers")
        print("chatWith USERNAME")
        print("****************************")  
        print("Room Command")
        print("****************************")  
        print(">> MSG")
        return True

    def sendType(self, data):
        sData = {"type": data[0]}
        jData = json.dumps(sData)
        self.socket.send(jData.encode())
        return True

    def sendName(self, data):
        sData = {"type": data[0], "username": data[1]}
        jData = json.dumps(sData)
        self.socket.send(jData.encode())
        return True

    def sendTo(self, data):
        if len(data) == 3 and data[2] == "0":
            sData = {"type": data[0], "to": data[1], "notChatWith": False}
            jData = json.dumps(sData)
            self.socket.send(jData.encode())
            return True
        else:
            sData = {"type": data[0], "to": data[1]}
            jData = json.dumps(sData)
            self.socket.send(jData.encode())
            return True

    def sendMsg(self, data):
        sData = {"type": data[0], "msg": data[1]}
        jData = json.dumps(sData)
        self.socket.send(jData.encode())
        return True

    def __main__(self, data):
        type = data[0]
        """
        register    reply
        login   reply
        logout  reply
        listUsers   reply
        chatWith    reply
        >>  noreply
        """
        try:
            if type == "help":
                return self.help()
            elif type == "register":
                return self.sendName(data)
            elif type == "login":
                return self.sendName(data)
            elif type == "logout":
                self.sendType(data)
                return False
            elif type == "listUsers":
                return self.sendType(data)
            elif type == "chatWith":
                return self.sendTo(data)
            elif type == ">>":
                return self.sendMsg(data)
            else:
                print("Incorrect command. If need help, enter help as Command.")
                return False

        except Exception as e:
            print("Unkown error. If need help, enter help as Command.")
            print(data)
            print(e)
            return False

class listenThread(threading.Thread):
    def __init__(self, csocket, handle):
        threading.Thread.__init__(self)
        self.sock = csocket
        self.handle = handle

    def run(self):
        while True:
            try:
                recvData = self.sock.recv(1024)
                data = json.loads(recvData.decode())
                if data['type'] == "recieve":
                    print(data['msg'])
                elif data['type'] == "enterChat":
                    rdata = ["chatWith", data['to'], "0"]
                    self.handle.sendTo(rdata)
                else:
                    if data['status'] == True:
                        print("Execution succeed. From server: "+repr(data['info']))
                    elif data['status']  == False:
                        print("Execution failed. From server: "+repr(data['info']))
                    else:
                        print("Holyshit..."+repr(data))
                    if data['type'] == "logout":
                        break

            except Exception as e:
                print("Disconnect...")
                break

class Client():
    def __main__(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect((host,port))
        except Exception as e:
            print(e)
        print("Connect to Server.\nInput format: Command Information. If need help, enter help as Command.")
        handle = Handle(client_socket)
        t = listenThread(client_socket, handle)
        t.start()
        while True:
            rawData = input()
            data = rawData.split()
            if data[0] == "exit":
                break
            else:
                keepRun = handle.__main__(data)
            if not keepRun:
                return


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
