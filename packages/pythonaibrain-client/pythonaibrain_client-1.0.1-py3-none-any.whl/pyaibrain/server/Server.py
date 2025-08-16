import socket
import threading
import os
from dotenv import load_dotenv

load_dotenv()
XOR_KEY = os.getenv("XOR_KEY")

host = '127.0.0.1'
port = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = []
aliases = []

def xor_cipher(text, key):
    result = ''
    key_index = 0
    for char in text:
        result += chr(ord(char) ^ ord(key[key_index]))
        key_index = (key_index + 1) % len(key)
    return result

def broadcast(message):
    for client in clients:
        client.send(message)

def handle_client(client):
    while True:
        try:
            encrypted_message = client.recv(1024)
            decoded_message = xor_cipher(encrypted_message.decode(), XOR_KEY)
            broadcast(encrypted_message)

        except Exception as e:
            index = clients.index(client)
            client.close()
            alias = aliases[index]
            clients.remove(client)
            aliases.remove(alias)
            broadcast(xor_cipher(f'{alias} has left the chat room!', XOR_KEY).encode())
            break

def recving():
    print(f"Server started on Host: {host}, Port: {port}\n")
    while True:
        client, address = server.accept()
        print(f"Connected with {address}")

        client.send(xor_cipher('Alias?', XOR_KEY).encode())
        alias_data = client.recv(1024)
        alias = xor_cipher(alias_data.decode(), XOR_KEY)

        aliases.append(alias)
        clients.append(client)

        print(f"The Alias of this client is {alias}")
        broadcast(xor_cipher(f"{alias} has connected!", XOR_KEY).encode())
        client.send(xor_cipher("You are now connected!", XOR_KEY).encode())
        #client.send(xor_cipher("To ask PythonAI, use: @pyai <your_message>", XOR_KEY).encode())

        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

if __name__ == '__main__':
    recving()
