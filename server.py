import socket
import threading
import json
import time
import os



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
        msg:
    }
    """
    usernames = {}    #key is User object, value is username
    userFile = open("AllUsernames.txt", "r")
    userList = userFile.read().split("\n")
    userFile.close

    def __init__(self, user):
        self.user = user
        self.reciverList = []
        self.singleChat = False
        self.groupChat = False
        self.roomName = ""

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
        #用户是否已注册
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
        """
        data = {
            "type" = chatWith,
            "to" = toName
        }
        """
        if data['to'] not in HandleRequest.userList:
            data['status'] = False
            data['info'] = "The target user does not exist. List of registered users: "+repr(HandleRequest.userList)
            self.send2Me(data)
            return True

        #读取unread消息
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
        unreadMsg = ""
        unread = False
        recv = self.getUser(data['to'])
        fromUser = ""
        #msg format: time + FromUser + msg + unread
        for line in msg:
            if "unread" in line:
                unread = True
                newMsg = line.split("$#@")
                fromUser = newMsg[1]
                newMsg = newMsg[0]+"  From: "+newMsg[1]+"    "+newMsg[2] + "\n"
                unreadMsg = unreadMsg + newMsg

        #如果存在未读消息，冰鞋现用户不是发送消息的用户，发送未读消息
        if unread == True and HandleRequest.usernames[self.user] != fromUser:
            self.reciverList = []
            self.reciverList.append(data['to'])
            self.groupChat = False
            self.singleChat = True
            data['status'] = True
            data['info'] = "Start to chat with "+data['to']
            data['msg'] = unreadMsg
            data['type'] = "recieve"
            data['from'] = fromUser
            if not recv:
                data['info'] = "The target user is not online. You can still send messages, which will appear when the other person starts a chat with you."
            self.send2Me(data)

            #remove unread flag
            fileData = ""
            for line in msg:
                newMsg = line.split("$#@")
                line += "\n"
                if len(newMsg) == 4:
                    newData = newMsg[0] +"$#@"+ newMsg[1] +"$#@"+ newMsg[2] +"\n"
                    line = newData
                fileData += line
            userFile = open(fileName, "w")
            userFile.write(fileData)
            userFile.close()

            #拉目标用户开始聊天
            if "notChatWith" not in data.keys() and recv:
                rdata = {'type': "enterChat", 'to': HandleRequest.usernames[self.user]}
                jData = json.dumps(rdata)
                recv[0].csocket.send(jData.encode())
        else:
            self.reciverList = []
            self.reciverList.append(data['to'])
            self.groupChat = False
            self.singleChat = True
            data['status'] = True
            data['info'] = "Start to chat with "+data['to']
            if not recv:
                data['info'] = "The target user is not online. You can still send messages, which will appear when the other person starts a chat with you."
            self.send2Me(data)
            if "notChatWith" not in data.keys() and recv:
                rdata = {'type': "enterChat", 'to': HandleRequest.usernames[self.user]}
                jData = json.dumps(rdata)
                recv[0].csocket.send(jData.encode())
        return True

    def sendMsg(self, data):
        #data['type'] = ">>"
        #data['msg'] = msg
        if self.singleChat:
            #保存消息
            if HandleRequest.usernames[self.user] > self.reciverList[0]:
                fileName = HandleRequest.usernames[self.user] + "_" + self.reciverList[0] + ".txt"
            else:
                fileName = self.reciverList[0] + "_" + HandleRequest.usernames[self.user] + ".txt"
            userFile = open(fileName, "a")
            t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            msg = ""
            for m in data['msg']:
                msg = msg + m + " "
            recv = self.getUser(self.reciverList)
            # time $#@ from $#@ msg $#@ unread.
            if not recv:
                formatMsg = t +"$#@"+ HandleRequest.usernames[self.user] +"$#@"+ msg +"$#@"+ "unread\n"
            else:
                formatMsg = t +"$#@"+ HandleRequest.usernames[self.user] +"$#@"+ msg +"\n"
            userFile.write(formatMsg)
            userFile.close()

            #将消息发给用户
            if not recv:
                data['status'] = True
                data['info'] = "The target user is not online. Message has been saved."
                self.send2Me(data)
            else:
                data['status'] = True
                data['type'] = "recieve"
                data['from'] = HandleRequest.usernames[self.user]
                data['msg'] = msg
                self.send2User(data, recv)

        elif self.groupChat:
            #保存消息
            userFile = open("%s.txt" % self.roomName, "a")
            t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            msg = ""
            for m in data['msg']:
                msg = msg + m + " "
            recv = self.getUser(self.reciverList)
            formatMsg = t +"$#@"+ HandleRequest.usernames[self.user] +"$#@"+ msg +"\n"
            userFile.write(formatMsg)
            userFile.close()

            #将消息发给用户
            data['status'] = True
            data['type'] = "recieve"
            data['from'] = HandleRequest.usernames[self.user]
            data['msg'] = msg
            self.send2User(data, recv)

        else:
            data['status'] = False
            data['info'] = "Please enter chatWith or enterRoom to choose a reciever. Current recever list: " + repr(self.reciverList)
            data.pop('msg')
            self.send2Me(data)
        return True

    def createRoom(self, data):
        path = os.getcwd()
        files = os.listdir(path)
        rooms = []
        for f in files:
            if "room" in f:
                rooms.append(f)
        roomName = ""
        #如果还没有房间文件
        if "room_1.txt" not in rooms:
            roomFile = open("room_1.txt", "w")
            roomFile.write("NameList:\n")
            roomFile.write(HandleRequest.usernames[self.user]+"\n")
            roomFile.write("Messages:\n")
            roomFile.close()
            roomName = "room_1"
        else:
            #如果有房间文件，获取现在最大的房间编号，新房间的编号就是原先最大房间号加一
            for r in rooms:
                if r > roomName:
                    roomName = r
            rn = roomName.split("_")
            rNum = int(rn[1]) +1
            roomName = "room_"+str(rNum)
            roomFile = open("%s.txt" % roomName, "w")
            roomFile.write("NameList:\n")
            roomFile.write(HandleRequest.usernames[self.user]+"\n")
            roomFile.write("Messages:\n")
            roomFile.close()

        data['status'] = True
        data['info'] = "Room created successfully. The room name is "+roomName
        self.send2Me(data)
        return True

    def enterRoom(self, data):
        #msg format: time + From name + msg
        #读取最新的十条消息
        roomName = data['roomName']
        path = os.getcwd()
        files = os.listdir(path)
        rooms = []
        for f in files:
            if "room" in f:
                rooms.append(f)
        if roomName+".txt" not in rooms:
            data['status'] = False
            data['info'] = "Room name is wrong. Here are all the room names: "+repr(rooms)
            self.send2Me(data)
        else:
            roomFile = open("%s.txt" % roomName, "r")
            fileContent = roomFile.read()
            roomFile.close()
            #获得消息在文件的位置
            pos = fileContent.find("Messages:")
            newFile = fileContent
            fileLines = fileContent.split("\n")
            msgPos = 0
            for i in range(len(fileLines)):
                if fileLines[i] == "Messages:":
                    msgPos = i
            users = fileLines[1:msgPos]
            #将新进入房间的用户，加入房间的userList
            if HandleRequest.usernames[self.user] not in users:
                newFile = newFile[:pos] + HandleRequest.usernames[self.user] + '\n' + newFile[pos:]
                roomFile = open("%s.txt" % roomName, "w")
                roomFile.writelines(newFile)
                roomFile.close()
                users.append(HandleRequest.usernames[self.user])
            #读取十条消息和发送消息
            self.reciverList = users
            self.groupChat = True
            self.singleChat = False
            self.roomName = roomName
            msgLen = len(fileLines[msgPos+1:])
            msg = ""
            #这是还没有任何消息的情况，不加这个判断下面的循环中会报错
            if msgLen == 1 and fileLines[msgPos+1] == "":
                data['status'] = True
                data['msg'] = msg
                data['from'] = roomName
                data['type'] = "recieve"
                self.send2Me(data)
            else:
                for m in range(msgLen-1):
                    if msgLen - m <= 10:
                        msgctnt = fileLines[m+msgPos+1].split("$#@")
                        msg += msgctnt[0] + "  From: " + msgctnt[1] + "    " + msgctnt[2] + "\n"
                data['status'] = True
                data['msg'] = msg
                data['from'] = roomName
                data['type'] = "recieve"
                self.send2Me(data)
        return True

    def listRooms(self, data):
        path = os.getcwd()
        files = os.listdir(path)
        rooms = []
        for f in files:
            if "room" in f:
                rooms.append(f)
        data['status'] = True
        data['info'] = "Room: "+repr(rooms)
        self.send2Me(data)
        return True

    def listRoomUsers(self, data):
        if not self.groupChat:
            data['status'] = False
            data['info'] = "listRoomUsers command can only be used after you have entered a room."
            self.send2Me(data)
        else:
            data['status'] = True
            data['info'] = self.reciverList
            self.send2Me(data)
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
            "createRoom": self.createRoom,
            "enterRoom": self.enterRoom,
            "listRooms": self.listRooms,
            "listRoomUsers": self.listRoomUsers,
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
        #创建服务器socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host,port))
        server_socket.listen(5)

        threads = []
        #监听连接
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