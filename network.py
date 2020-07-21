import socket

class Server(object):
    def __init__(self, handle_client, PORT, HOST=socket.gethostbyname(socket.gethostname())):
        import pickle
        import threading
        self.SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.HOST = HOST
        self.PORT = PORT
        self.ADDR = (HOST, PORT)
        self.HOSTED = False
        self.clients = 0
        self.CLIENTS = []
        self.handle_client = handle_client
        self.pickle = pickle
        self.threading = threading
        self.host()
        threading.Thread(target=self.get_clients).start()

    def get_clients(self):
        self.SOCKET.listen()
        print(f"[LISTENING] Server is listening on {self.HOST}\n")

        while 1:
            try:
                connection, address = self.SOCKET.accept()
            except:
                continue

            if connection in self.CLIENTS:
                connection.close()
                continue

            self.clients += 1
            print(f"\n[NEW CONNECTION] {address} Just Connected!")
            print(f"[ACTIVE CONNECTIONS] {self.clients}\n")

            self.CLIENTS.append(connection)

            self.threading.Thread(target=self.handle_client, args=(connection, address)).start()

    def send(self, message, connection):
        return connection.send(self.pickle.dumps(message))

    def host(self):
        if not self.HOSTED:
            self.HOSTED = True
            return self.SOCKET.bind(self.ADDR)

    def close(self):
        self.SOCKET.close()

class Client(object):
    def __init__(self, handle_message, HOST, PORT, bytes_limit):
        import socket
        import pickle
        import threading
        self.SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.HOST = HOST
        self.PORT = PORT
        self.ADDR = (HOST, PORT)
        self.handle_message = handle_message
        self.pickle = pickle
        self.CONNECTED = False
        self.bytes = bytes_limit
        self.connect()
        threading.Thread(target=self.get_messages).start()

    def send(self, message):
        return self.SOCKET.send(self.pickle.dumps(message))

    def get_messages(self):
        while 1:
            message = self.pickle.loads(self.SOCKET.recv(self.bytes))
            self.handle_message(message)

    def connect(self):
        if not self.CONNECTED:
            self.CONNECTED = True
            return self.SOCKET.connect(self.ADDR)

    def close(self):
        self.SOCKET.close()
