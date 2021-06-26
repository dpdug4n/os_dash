import socket, osquery, pickle
from requests import get

CLIENT_HOST = "0.0.0.0"
CLIENT_PORT = 6667

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((CLIENT_HOST, CLIENT_PORT))
s.listen(5)
print(f'Listening on port: {CLIENT_PORT}...')

while True:
    try:
        server_socket, server_address = s.accept() 
        print(f"{server_address[0]}:{server_address[1]} Connected!")
        server_socket.send("true".encode())
        public_ip = str(get('https://api.ipify.org').text)
        server_socket.send(public_ip.encode())       
        data = server_socket.recv(4096).decode()
        print(f'Query received: {data}')
        try:
            instance = osquery.SpawnInstance("C:/Program Files/osquery/osqueryd/osqueryd.exe")
            instance.open()
            result = instance.client.query(data)
            instance.connection=None
            if result.status.code != 0:
                print("Error running the query: %s" % result.status.message)
                data = str("Error running the query: %s" % result.status.message) 
            elif result.response == []:
                print(result.reponse)
                data = "Error. Table may not exist on host."
            else:
                data = result.response
        except Exception as e:
            print(e)
        
        output = pickle.dumps(data)
        packet_size = str(len(output))
        server_socket.send(packet_size.encode())
        print(f'packet info sent: {packet_size} bytes')
        while True:
            data = server_socket.recv(4).decode()
            if data == "10-4":
                server_socket.sendall(output)
                break
            else:
                server_socket.send('Error'.encode())
                break      
        server_socket.close()
        print(f"{server_address[0]}:{server_address[1]} Disconnected!")
    except Exception as e:
        print(e)