import pickle, password, network

SERVERS = {}
CLIENTS = {}
SCORES = {}

def handle_client(connection, address):
    global clients

    while 1:
        try:
            message = pickle.loads(connection.recv(4096 ** 2))

            if message != "":
                print(f"[{address}] {message}")
                if message.startswith("[MOVE]"):
                    for conn in SERVERS[CLIENTS[connection]]:
                        if conn != connection:
                            SERVER.send(message, conn)

                elif message.startswith("[JOIN]"):
                    if message.replace("[JOIN]", "").strip() in SERVERS:
                        if len(SERVERS[message.replace("[JOIN]", "").strip()]) < 2:
                            SERVERS[message.replace("[JOIN]", "").strip()].append(connection)
                            CLIENTS[connection] = message.replace("[JOIN]", "").strip()
                            for conn in SERVERS[CLIENTS[connection]]:
                                SERVER.send("[STARTED]", conn)
                        else:
                            SERVER.send("[JOIN WITH CODE FULL]", connection)
                    else:
                        SERVER.send("[JOIN WITH CODE FAILED]", connection)

                elif message.strip() == "[JOIN RANDOM]":
                    serverFound = False
                    for server in SERVERS:
                        if len(SERVERS[server]) < 2:
                            serverFound = True
                            SERVERS[server].append(connection)
                            CLIENTS[connection] = server
                            if len(SERVERS[server]) == 2:
                                for conn in SERVERS[CLIENTS[connection]]:
                                    if conn != connection:
                                        SERVER.send("[STARTED]", conn)
                            break

                    if not serverFound:
                        a = password.passwordCreator()
                        SERVERS[a] = [connection]
                        CLIENTS[connection] = a
                        SERVER.send("[WAITING] " + a, connection)

                elif message.strip() == "[LEAVING WAIT]":
                    SERVERS.pop(CLIENTS[connection])
                    CLIENTS.pop(connection)

        except:
            if connection in CLIENTS:
                CLIENTS.pop(connection)

            for server in SERVERS:
                if connection in SERVERS[server]:
                    SERVERS[server].remove(connection)
                    if SERVERS[server] != []:
                        SERVER.send("[OPPONENT LEFT]", SERVERS[server][0])
                        CLIENTS.pop(SERVERS[server][0])
                        SERVERS.pop(server)
                    break

            SERVER.clients -= 1
            SERVER.CLIENTS.remove(connection)
            print(f"\n[CLIENT DISCONNECTED] [{address}] Just Disconnected!")
            print(f"[ACTIVE CONNECTIONS] {SERVER.clients}\n")
            break

    connection.close()

SERVER = network.Server(handle_client, 5555)
