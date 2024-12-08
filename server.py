import socket
import threading
import json

# Создаем сокет
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Задаем адрес и порт для прослушивания
server_address = ('localhost', 8880)
server_socket.bind(server_address)

# Начинаем прослушивание
server_socket.listen(5)
print('Сервер слушает на порту 8880...')

# Список для хранения подключенных клиентов
clients = []
clients_adress = []


chats = {}


def handle_client(_client_socket):

    while True:
        try:
            inf1 = _client_socket.recv(10096).decode('utf-8')
        except Exception as er:
            print(er)
            return None
        if not inf1:
            break
        for inf in inf1.split('---')[:-1]:

            data = json.loads(inf)
            _client_host, _client_port = data["host"], data["port"]
            # print(_client_host, _client_port)
            print(data)

################################################ TYPE MESSAGE IS CREATE_CHAT ################################################

            if data["type"] == "CREATE_CHAT":

                if data["chat_name"] in list(chats.keys()):

                    inf = {"type": "CREATE_CHAT", "created": False}

                    answer_data = (json.dumps(inf)+"---").encode('utf-8')

                    _client_socket.sendall(answer_data)
                    continue

                chats[data["chat_name"]] = {
                    "client_admin_name": data["my_name"],
                    "client_admin_ip:port": [_client_host, _client_port],
                    "client_socket": _client_socket
                }

                inf = {"type": "CREATE_CHAT", "created": True}

                answer_data = (json.dumps(inf) + "---").encode('utf-8')

                _client_socket.sendall(answer_data)
                continue

################################################ TYPE MESSAGE IS CREATE_CHAT ################################################

            if data["type"] == "DISCONNECT_FROM_CHAT":

                if data["chat_name"] in list(chats.keys()):

                    getter_socket = chats[data["chat_name"]]["client_socket"]

                    answer_data = (json.dumps(data) + "---").encode("utf-8")
                    getter_socket.sendall(answer_data)


################################################ TYPE MESSAGE IS CONNECT_TO_CHAT ################################################

            if data["type"] == "CONNECT_TO_CHAT":

                if data["chat_name"] not in list(chats.keys()):
                    inf = {"type": "CONNECT_REJECTED", "connected": False}
                    answer_data = (json.dumps(inf) + "---").encode('utf-8')

                    _client_socket.sendall(answer_data)

                    continue

                getter_socket = chats[data["chat_name"]]["client_socket"]

                data["host"] = _client_host
                data["port"] = _client_port

                answer_data = (json.dumps(data) + "---").encode("utf-8")
                getter_socket.sendall(answer_data)

################################################ TYPE MESSAGE IS CONNECT_TO_CHAT ################################################


################################################ TYPE MESSAGE IS CONNECT_REJECTED ################################################
            if data["type"] == "CONNECT_REJECTED":

                for client in clients:
                    if client["client_address"] == [data["host"], data["port"]]:
                        client["client_socket"].sendall((json.dumps(data)+'---').encode('utf-8'))
                        break
                continue
################################################ TYPE MESSAGE IS CONNECT_REJECTED ################################################


################################################ TYPE MESSAGE IS MASSAGE ################################################
            if data["type"] == "MESSAGE":

                for client in clients:
                    if client["client_address"] in data["getters_host:port"]:
                        client["client_socket"].sendall((json.dumps(data)+'---').encode('utf-8'))
################################################ TYPE MESSAGE IS MESSAGE ################################################


################################################ TYPE START_GENERATE_PK ################################################
            if data["type"] == "START_GENERATE_PK":

                for client in clients:
                    if client["client_address"] in data["getters_host:port"]:
                        client["client_socket"].sendall((json.dumps(data)+'---').encode('utf-8'))

                # client_socket.sendall((json.dumps(data)+'---').encode('utf-8'))
################################################ TYPE START_GENERATE_PK ################################################


################################################ TYPE GENERATE_PK ################################################
            if data["type"] == "GENERATE_PK":

                for client in clients:
                    if client["client_address"] == data["getters_host:port"][0]:
                        client["client_socket"].sendall((json.dumps(data)+'---').encode('utf-8'))
                        break

                # client_socket.sendall((json.dumps(data)+'---').encode('utf-8'))
################################################ TYPE GENERATE_PK ################################################




while True:

    client_socket, (client_host, client_port) = server_socket.accept()
    print(client_host, client_port)

    clients.append({"client_socket": client_socket, "client_address": [client_host, client_port]})

    client_handler = threading.Thread(target=handle_client, args=(client_socket,))
    client_handler.start()
