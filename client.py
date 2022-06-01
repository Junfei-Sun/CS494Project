import socket
import json
import threading
 
host = "localhost"
port = 8080
 

class Handle():
    def __init__(self, socket):
        self.socket = socket
        self.login = False

    def help(self):
        print("****************************")
        print(" Menu Command ")
        print("****************************")      
        print("register USERNAME")
        print("login USERNAME")
        print("logout")
        print("listUsers")
        print("chatWith USERNAME")
        print("listRooms")
        print("createRoom")
        print("enterRoom ROOMNAME")
        print("leaveRoom ROOMNAME")
        print("towho")
        print("****************************")  
        print("Room Command")
        print("****************************")  
        print(">> MSG")
        print("listRoomUsers")
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
        #Restrict the situation of being pulled into the chat, and do not limit the two parties who will chat in an infinite loop chatWith each other to pull people
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
        sData = {"type": data[0], "msg": data[1:]}
        jData = json.dumps(sData)
        self.socket.send(jData.encode())
        return True

    def sendRoom(self, data):
        sData = {"type": data[0], "roomName": data[1]}
        jData = json.dumps(sData)
        self.socket.send(jData.encode())
        return True

    def sendFile(self, data, content):
        sData = {"type": data[0], "fileName": data[1], "fileContent": content}
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
        It doesn't matter whether there is any return information, now assign a thread to the listener function
        """
        if not self.login and type not in ['register', 'login']:
            print("please log in first.")
            return True

        try:
            if type == "help":
                return self.help()
            elif type == "register":
                return self.sendName(data)
            elif type == "login":
                self.login = True
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
            elif type == "createRoom":
                return self.sendType(data)
            elif type == "enterRoom":
                return self.sendRoom(data)
            elif type == "listRooms":
                return self.sendType(data)
            elif type == "listRoomUsers":
                return self.sendType(data)
            elif type == "leaveRoom":
                return self.sendRoom(data)
            elif type == "towho":
                return self.sendType(data)
            elif type == "file>>":
                filename = data[1]
                try:
                    userFile = open(filename, "r")
                except IOError:
                    print("Filename is wrong.")
                    return True
                fileContent = userFile.read()
                userFile.close()
                return self.sendFile(data, fileContent)
            else:
                print("Incorrect command. If need help, enter help as Command.")
                return True

        except Exception as e:
            print("Unkown error. If need help, enter help as Command.")
            print(data)
            print(e)
            return True

class listenThread(threading.Thread):
    #Client's listener thread
    def __init__(self, csocket, handle):
        threading.Thread.__init__(self)
        self.sock = csocket
        self.handle = handle

    def run(self):
        while True:
            try:
                recvData = self.sock.recv(2048)
            except ConnectionResetError:
                print("The server has been disconnected for an unknown reason.")
                self.sock.close()
                break
                
            data = json.loads(recvData.decode())
            #receive message
            if data['type'] == "recieve":
                if "info" in data.keys():
                    print(data['info'])
                print("From: "+ data['from'])
                print(data['msg'])
            #pulled into the room
            elif data['type'] == "enterChat":
                rdata = ["chatWith", data['to'], "0"]
                self.handle.sendTo(rdata)
            elif data['type'] == "file>>":
                fileName = "recv_"+data['fileName']
                fileContent = data['fileContent']
                userFile = open(fileName, "w")
                userFile.write(fileContent)
                userFile.close()
                print("Received file: "+fileName)
            else:
                if data['status'] == True:
                    print("Execution succeed. From server: "+repr(data['info']))
                elif data['status']  == False:
                    print("Execution failed. From server: "+repr(data['info']))
                else:
                    print("Holyshit..."+repr(data))
                if data['type'] == "logout":
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
        #read input
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
