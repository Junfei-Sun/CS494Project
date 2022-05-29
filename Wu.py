import os
def create_room(roomname):# call the function when would like to create a room
    room=open("%s.txt"%roomname, "w")
    room.write("NameList:\n")
    # room.writelines(namelist)
    room.write("Message:")
    # room.write(message)
    room.close()
def add_content(roomname,content):# call the function when add chat content
    file = open("%s.txt" % roomname, "a")
    file.write("\n")
    file.write(content)
    file.close()
def update_name(roomname,namelist):# call the function when update the member in the room
    for name in namelist:
        file = open("%s.txt" % roomname, "r")
        text = file.read()
        pos = text.find("Message:")
        if pos != -1:
            text = text[:pos] + name + '\n' + text[pos:]
            file = open("%s.txt" % roomname, "w")
            file.writelines(text)
            file.close()

def Newest_msg_show(roomname,newest):# call the function to just show newest several messages
    file = open("%s.txt" % roomname, "r")
    text = file.read()
    pos = text.find("Message:")
    text = text[pos+len("Message"):]
    text=text.split('\n')[-newest:]
    for line in text:
        print(line)

def All_msg_show(roomname): #call the function to just show newest several messages
    file = open("%s.txt" % roomname, "r")
    text = file.read()
    pos = text.find("Message:")
    text = text[pos+len("Message")+2:]
    text = text.split('\n')
    for line in text:
        line = line.split('$#@')
        print(line[0]+' '+line[1])
def Unread_msg_show(roomname):
    file = open("%s.txt" % roomname, "r")
    text = file.read()
    pos = text.find("Message:")
    text = text[pos + len("Message") + 2:]
    text = text.split('\n')
    for line in text:
        line = line.split('$#@')
        if len(line) == 4:
            if line[3] == 'unread':
                print(line[0] + ' ' + line[1]+ ' '+line[2])

def List_ALL_Users(namelist,registedlist):# to list all users
    print("Here is the online users:",namelist)
    print("Here is the registed users:",registedlist)

def List_ALL_Rooms(roomlist):# to list all room
    print("Here is the room list:",roomlist)

def List_room_userlist(roomname):#to list all users in the room
    file = open("%s.txt"%roomname,"r")
    text = file.read()
    pos = text.find("Message:")
    text=text[:pos]
    print("%s in the %s room"%(text,roomname))

def delete_user(roomname,name):# we will call the function when user exit the room
    file = open("%s.txt"%roomname,"r")
    text = file.read()
    pos = text.find("Message:")
    text2=text[pos:]
    text=text[:pos]
    pos2=text.find(name)
    text=text[:pos2]+text[pos2+len(name)+1:]
    text=text+text2
    file = open("%s.txt" % roomname, "w")
    file.writelines(text)
    file.close()

def Message_format_forchat(time,name,message,ifread):#combine time name and content to reture a proper format of the message
    return time+'$#@'+name+'$#@'+message+'$#@'+ifread

def Message_format_group(time,name,message):#combine time name and content to reture a proper format of the message
    return time+'$#@'+name+'$#@'+message


#test example
name='hello'
namelist=["Jerry","David"]
message="2021.01.03 3:21:56$#@how are you "
message1="2021.01.03 3:21:56$#@how are you1$#@unread"
message2="2021.01.03 3:21:56$#@how are you2$#@unread"
message3="2021.01.033:21:56$#@how are you3$#@unread"
create_room(name)
add_content(name,message)
update_name(name,namelist)
add_content(name,message1)
add_content(name,message2)
add_content(name,message3)
# Newest_msg_show(name,3)
del_name = "Jerry"
delete_user(name,del_name)
# file = open("hello.txt")
# lines=file.readlines()
# text=file.readlines()
# print(text)
# Unread_msg_show(name)
All_msg_show(name)