import socket
host = "localhost"
port = 8080
 
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((host,port))
data = input("Input massage: ")
client_socket.sendto(data.encode(),(host,port))
data = client_socket.recv(1024)
client_socket.close()
print(data.decode())
