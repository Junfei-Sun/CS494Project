from collections import UserList
import socket
import threading
import json
import time



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
    usernames = {}    #key is User object, value is username
    userFile = open("AllUsernames.txt", "r")
    userList = userFile.read()
    userFile.close

    def __init__(self, user):
        self.user = user
        self.reciverList = []

    def getUser(self, nameList):
        return [k for k, u in HandleRequest.usernames.items() if u in nameList]

    def deluser(user):
        try:
            HandleRequest.usernames.pop(user)
        except Exception as e:
            print(e)

    def send2Me(self, data):
        jData = json.dumps(data)
        self.user.csocket.send(jData.encode())
        print("Send "+jData)

    def send2User(self, data, recv):
        jData = json.dumps(data)
        for r in recv:
            r.csocket.send(jData.encode())
        print("Send to "+ repr(self.reciverList)+". Msg: "+repr(jData))

    def register(self, data):
        userTxt=open("AllUsernames.txt", "a")
        if data['username'] in HandleRequest.userList:
            userTxt.close()
            userFile = open("AllUsernames.txt", "r")
            HandleRequest.userList = userFile.read().split("\n")
            userFile.close
            data['status'] = False
            data['info'] = "This username is already in use. Please login."
        else:
            userTxt.write(data['username']+"\n")
            userTxt.close()
            userFile = open("AllUsernames.txt", "r")
            HandleRequest.userList = userFile.read().split("\n")
            userFile.close
            data['status'] = True
            data['info'] = "Successfully registered."
        self.send2Me(data)
        return True

    def login(self, data):
        if data['username'] in HandleRequest.usernames.values():
            data['status'] = False
            data['info'] = "You already login."
        elif data['username'] not in HandleRequest.userList:
            data['status'] = False
            data['info'] = "Please register first."
        else:
            HandleRequest.usernames[self.user] = data['username']
            data['status'] = True
            data['info'] = "Successfully login."
        self.send2Me(data)
        return True

    def logout(self, data):
        print(HandleRequest.usernames[self.user]+" logout.")
        data['status'] = True
        data['info'] = "Successfully logout."
        self.send2Me(data)
        HandleRequest.deluser(self.user)
        return False

    def listUsers(self, data):
        data['status'] = True
        data['info'] = list(HandleRequest.usernames.values())
        self.send2Me(data)
        return True

    def chatWith(self, data):
        if HandleRequest.usernames[self.user] > data['to']:
            fileName = HandleRequest.usernames[self.user] + "_" + data['to'] + ".txt"
        else:
            fileName = data['to'] + "_" + HandleRequest.usernames[self.user] + ".txt"
        userFile = open(fileName, "a")
        userFile.close()
        userFile = open(fileName, "r")
        msg = userFile.read()
        userFile.close()
        msg = msg.split('\n')
        unreadMsg = []
        unread = False
        for line in msg:
            if "unread" in line:
                unread = True
                newMsg = line.split("$#@")
                newMsg = newMsg[0]+"  From: "+newMsg[1]+"    "+newMsg[2]
                unreadMsg.append(newMsg)
        if unread == True:
            self.reciverList = []
            self.reciverList.append(data['to'])
            data['status'] = True
            data['info'] = "Start to chat with "+data['to']
            data['msg'] = unreadMsg
            self.send2Me(data)
            if "notChatWith" not in data.keys():
                rdata = {'type': "enterChat", 'to': HandleRequest.usernames[self.user]}
                jData = json.dumps(rdata)
                recv = self.getUser(self.reciverList)
                recv[0].csocket.send(jData.encode())

        else:
            self.reciverList = []
            self.reciverList.append(data['to'])
            data['status'] = True
            data['info'] = "Start to chat with "+data['to']
            self.send2Me(data)
            if "notChatWith" not in data.keys():
                rdata = {'type': "enterChat", 'to': HandleRequest.usernames[self.user]}
                jData = json.dumps(rdata)
                recv = self.getUser(self.reciverList)
                recv[0].csocket.send(jData.encode())
        return True

    def sendMsg(self, data):
        if len(self.reciverList) == 1:
            if HandleRequest.usernames[self.user] > self.reciverList[0]:
                fileName = HandleRequest.usernames[self.user] + "_" + self.reciverList[0] + ".txt"
            else:
                fileName = self.reciverList[0] + "_" + HandleRequest.usernames[self.user] + ".txt"
            userFile = open(fileName, "a")
            t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            # time $#@ from $#@ msg $#@ unread. But unread need ping().
            formatMsg = t +"$#@"+ HandleRequest.usernames[self.user] +"$#@"+ data['msg'] +"\n"
            userFile.write(formatMsg)
            userFile.close()

            recv = self.getUser(self.reciverList)
            data['status'] = True
            data['type'] = "recieve"
            data['from'] = HandleRequest.usernames[self.user]
            self.send2User(data, recv)
        return True


    def __main__(self, data):
        type = data['type']
        switch = {
            "login": self.login,
            "logout": self.logout, 
            "register": self.register,
            "listUsers": self.listUsers,
            "chatWith": self.chatWith,
            ">>": self.sendMsg,
        }
        try:
            return switch[type](data)
        except Exception as e:
            print(e)
            data['status'] = False
            data['info'] = "Unkown error"
            return self.send2Me(data)
        

class ClientThread(threading.Thread):
    def __init__(self, user):
        threading.Thread.__init__(self)
        self.user = user

    def run(self):
        try:
            handle = HandleRequest(self.user)
            while True:
                request_data = self.user.csocket.recv(2048)
                data = json.loads(request_data.decode())
                print("Receive "+request_data.decode())
                keepRun = handle.__main__(data)
                if not keepRun:
                    break
        except Exception as e:
            print("Disconnect with error...")
            print(e)
        finally:
            #print(repr(HandleRequest.usernames[self.user])+" logout.")
            #HandleRequest.deluser(self.user)
            self.user.csocket.close()


class Server():
    def __main__(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host,port))
        server_socket.listen(5)

        threads = []
        while True:
            try:
                client_socket, client_address = server_socket.accept()
                user = User(client_address, client_socket)
                t = ClientThread(user)
                threads+=[t]
                t.start()
            except KeyboardInterrupt:
                print('KeyboardInterrupt:')
                for th in threads:
                    th.stop()
                break
        server_socket.close()

if __name__ == "__main__":
    server=Server()
    server.__main__()