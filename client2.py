import random
import socket
import threading
import json
import AES


def connect_to_server(ip, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (ip, port)
    client_socket.connect(server_address)
    return client_socket


def connect_to_server_func(ip, port, functions):
    try:
        client_socket = connect_to_server(ip, int(port))
    except Exception as er:
        functions["show_alert_dialog"]("Connection to server error!")
        return None
    else:
        start_listening(functions, client_socket)

        return client_socket


p = 10**13
g = 5


class ChatUsers:
    def __init__(self):
        self.chat_users = []

    def set(self, newlist):
        self.chat_users = newlist


class PrKey:
    def __init__(self):
        self.pr_key = 1

    def get(self):
        return self.pr_key

    def generate_self_key(self):
        self.pr_key = random.randint(10**10, 10**13)


class MsgKey:
    def __init__(self):
        self.key = 1

    def get(self):
        return self.key

    def set(self, atr):
        self.key = atr


private_self_key = PrKey()
message_key = MsgKey()

_chat_users = ChatUsers()
__chat_users = ChatUsers()

chat_users = []  # ADMIN
chat_users_hostport = []  # ADMIN

_chat_users_hostport = []  # USER


def generate_keypair(p, g, private_key):
    public_key = pow(g, private_key, p)
    return public_key


def receive_messages(client_socket, functions):
    is_connected = False
    position = None

    while True:
        # Принимаем и выводим сообщения от сервера
        try:
            inf1 = client_socket.recv(10096).decode('utf-8').split('---')
        except Exception as err:
            print(err)
            functions["server_disconnected"]()
            return None

        if inf1[0] == '':
            continue

        for _inf_ in inf1[:-1]:

            host, port = client_socket.getsockname()
            data = json.loads(_inf_)

            ############################################ ADMIN USER #####################################################
            if data["type"] == "CREATE_CHAT":

                if data["created"]:
                    chat_users.append(
                        {
                            "name": functions["get_my_name"](),
                            "host:port": [host, port]
                        }
                    )

                    chat_users_hostport.append([host, port])
                    functions["chat_created"]()
                else:
                    functions["chat_uncreated"]()

            if data["type"] == "CONNECT_TO_CHAT":

                if data["my_name"] in _chat_users.chat_users:
                    hostport_user = [data["host"], data["port"]]
                    chat_users_hostport.append(hostport_user)
                    user = {
                        "name": data["my_name"],
                        "host:port": hostport_user
                    }

                    inf = {
                        "type": "MESSAGE",
                        "type-1": "CONNECTED",
                        "getters_host:port": [user["host:port"]],
                        "host": host,
                        "port": port
                    }
                    answer = (json.dumps(inf) + '---').encode('utf-8')
                    client_socket.sendall(answer)

                    chat_users.append(user)
                    inf = {
                        "type": "MESSAGE",
                        "type-1": "NEW_CLIENT",
                        "getters_host:port": chat_users_hostport,
                        "new_user": user,
                        "chat_users": chat_users,
                        "host": host,
                        "port": port
                    }
                    answer = (json.dumps(inf) + '---').encode('utf-8')

                    client_socket.sendall(answer)

                    _chat_users.chat_users.remove(user["name"])
                else:
                    inf = {
                        "type": "CONNECT_REJECTED",
                        "host": data["host"],
                        "port": data["port"]
                    }
                    answer = (json.dumps(inf) + '---').encode('utf-8')
                    client_socket.sendall(answer)
            if data["type"] == "DISCONNECT_FROM_CHAT":

                chat_users_hostport.remove([data["host"], data["port"]])

                deld_us = None

                for us in chat_users:
                    if us["host:port"] == [data["host"], data["port"]]:
                        chat_users.remove(us)
                        deld_us = us
                        break

                inf = {
                    "type": "MESSAGE",
                    "type-1": "DISCONNECTED",
                    "host": host,
                    "port": port,
                    "getters_host:port": [[data["host"], data["port"]]]
                }
                answer = (json.dumps(inf) + '---').encode('utf-8')
                client_socket.sendall(answer)

                inf = {
                    "type": "MESSAGE",
                    "type-1": "USER_DISCONNECTED",
                    "host": host,
                    "port": port,
                    "getters_host:port": chat_users_hostport,
                    "user_rem": deld_us
                }
                answer = (json.dumps(inf) + '---').encode('utf-8')
                client_socket.sendall(answer)
            ############################################ ADMIN USER #####################################################

            ############################################ USER ###########################################################
            if data["type"] == "CONNECT_REJECTED":
                functions["connect_rejected"]()

            if data["type"] == "MESSAGE":

                if data["type-1"] == "NEW_CLIENT":

                    if not is_connected:
                        is_connected = True
                        for i in range(len(data["chat_users"])):
                            if data["chat_users"][i]["host:port"] == [host, port]:
                                position = i
                    __chat_users.set(data["chat_users"])
                    for ius in data["chat_users"]:
                        if ius["host:port"] not in _chat_users_hostport:
                            _chat_users_hostport.append(ius["host:port"])
                    functions["add_user"](data["chat_users"])

                if data["type-1"] == "CONNECTED":
                    functions["connected"]()

                if data["type-1"] == "USER_DISCONNECTED":
                    print(__chat_users.chat_users)
                    print(_chat_users_hostport)
                    __chat_users.chat_users.remove(data["user_rem"])
                    _chat_users_hostport.remove(data["user_rem"]["host:port"])
                    functions["user_delete"](data["user_rem"]["name"])

                if data["type-1"] == "DISCONNECTED":
                    functions["chat_disconnected"]()

                if data["type-1"] == "MESSAGE":
                    functions["add_message"](AES.decrypt_text(str(message_key.get()), data["message"]), data["my_name"])

            if data["type"] == "START_GENERATE_PK":
                private_self_key.generate_self_key()

                public_key = generate_keypair(p, g, private_self_key.get())

                inf = {
                    "type": "GENERATE_PK",
                    "host": host,
                    "port": port,
                    "getters_host:port": [_chat_users_hostport[(position + 1) % len(_chat_users_hostport)]],
                    "public_key": public_key,
                    "cycle": 0
                }
                answer = (json.dumps(inf) + '---').encode('utf-8')
                client_socket.sendall(answer)

            if data["type"] == "GENERATE_PK":
                print(_chat_users_hostport)
                print(chat_users_hostport)
                if data["cycle"] + 1 == len(_chat_users_hostport)-1:

                    message_key.set(generate_keypair(p, data["public_key"], private_self_key.get()))

                else:

                    public_key = generate_keypair(p, data["public_key"], private_self_key.get())

                    inf = {
                        "type": "GENERATE_PK",
                        "host": host,
                        "port": port,
                        "getters_host:port": [_chat_users_hostport[(position + 1) % len(_chat_users_hostport)]],
                        "public_key": public_key,
                        "cycle": data["cycle"] + 1
                    }

                    answer = (json.dumps(inf) + '---').encode('utf-8')
                    client_socket.sendall(answer)

            ############################################ USER ###########################################################


############################################ ADMIN USER #####################################################
def create_chat(client_socket, my_name, chat_name, func):
    host, port = client_socket.getsockname()

    f = func()
    _chat_users.set(f)

    inf = {
        "type": "CREATE_CHAT",
        "my_name": my_name,
        "chat_name": chat_name,
        "host": host,
        "port": port
    }

    data = (json.dumps(inf) + "---").encode("utf-8")
    client_socket.sendall(data)


def start_generate_pk(client_socket):
    host, port = client_socket.getsockname()
    inf = {
        "type": "START_GENERATE_PK",
        "host": host,
        "port": port,
        "getters_host:port": _chat_users_hostport
    }
    data = (json.dumps(inf) + "---").encode("utf-8")
    client_socket.sendall(data)


############################################ ADMIN USER #####################################################


############################################ USER #####################################################
def connect_to_chat(client_socket, chat_name, my_name):
    host, port = client_socket.getsockname()
    inf = {
        "type": "CONNECT_TO_CHAT",
        "my_name": my_name,
        "chat_name": chat_name,
        "host": host,
        "port": port
    }
    data = (json.dumps(inf) + "---").encode("utf-8")
    client_socket.sendall(data)


def disconnect_from_chat(client_socket, chat_name):
    host, port = client_socket.getsockname()
    inf = {
        "type": "DISCONNECT_FROM_CHAT",

        "host": host,
        "port": port,
        "getters_host:port": _chat_users_hostport,
        "chat_name": chat_name
    }
    data = (json.dumps(inf) + "---").encode("utf-8")
    client_socket.sendall(data)


def send_message(client_socket, my_name, message):
    host, port = client_socket.getsockname()
    inf = {
        "type": "MESSAGE",
        "type-1": "MESSAGE",
        "message": AES.encrypt_text(str(message_key.get()), message),
        "my_name": my_name,
        "host": host,
        "port": port,
        "getters_host:port": _chat_users_hostport
    }
    data = (json.dumps(inf) + "---").encode("utf-8")
    client_socket.sendall(data)


############################################ USER #####################################################


def start_listening(functions, client_socket):
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket, functions))
    receive_thread.start()
