"""
chat_server.py
XOR-encrypted chat server with Rich-powered admin dashboard, colored messages, emoji support, typing indicators, and chat logging.
Features:
- Private messaging /pm <alias> <message>
- List connected clients /list
- About menu /about
- Quit /quit
- Typing indicator
- Color-coded messages
- Emoji reactions /react <alias> <emoji>
- Dashboard shows last 10 messages, connected clients, typing status
- Daily log files
"""

import os
import socket
import threading
import random
from datetime import datetime
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.traceback import install
from rich.align import Align
from rich.text import Text

install()
console = Console()

load_dotenv()
XOR_KEY = os.getenv("KEY")
if not XOR_KEY:
    console.print("[bold red]ERROR:[/bold red] XOR_KEY missing in environment variables")
    raise ValueError("XOR_KEY missing in environment variables")

HOST, PORT = "127.0.0.1", 5555

clients = []
aliases = []
_KEY_BYTES = XOR_KEY.encode("utf-8")
chat_log = []
live_dashboard = None
typing_status = {}
alias_colors = {}
last_messages = {}

COLORS = ["cyan", "magenta", "green", "yellow", "blue", "bright_red", "bright_green"]

# -----------------------
# Encryption
# -----------------------
def xor_cipher(data, key, output_bytes=False):
    if isinstance(data, str):
        data_bytes = data.encode("utf-8")
    elif isinstance(data, bytes):
        data_bytes = data
    else:
        raise TypeError("data must be str or bytes")
    key_bytes = key.encode("utf-8") if isinstance(key, str) else key
    result = bytes([b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(data_bytes)])
    return result if output_bytes else result.decode("utf-8", errors="ignore")

def encrypt_text(text: str) -> bytes:
    return xor_cipher(text, _KEY_BYTES, output_bytes=True)

def decrypt_text(data: bytes) -> str:
    return xor_cipher(data, _KEY_BYTES)  # returns str

# -----------------------
# Logging
# -----------------------
def log_message(msg: str):
    timestamp = datetime.now().strftime("%H:%M:%S")
    full_msg = f"[{timestamp}] {msg}"
    chat_log.append(full_msg)
    date_file = datetime.now().strftime("%Y-%m-%d")
    with open(f"chat_{date_file}.log", "a", encoding="utf-8") as f:
        f.write(full_msg + "\n")

# -----------------------
# Networking
# -----------------------
def broadcast(message: bytes, sender=None):
    for client in clients.copy():
        try:
            if client != sender:
                client.sendall(message)
        except Exception:
            remove_client(client)

def send_private_message(sender_client, target_alias, message):
    if target_alias in aliases:
        idx = aliases.index(target_alias)
        target_client = clients[idx]
        sender_alias = aliases[clients.index(sender_client)]
        formatted_msg = f"[PM] {sender_alias}: {message}"
        target_client.sendall(encrypt_text(formatted_msg))
        sender_client.sendall(encrypt_text(f"[PM to {target_alias}] {message}"))
        log_message(formatted_msg)
        last_messages[target_alias] = formatted_msg
        if live_dashboard:
            live_dashboard.update(make_dashboard())
    else:
        sender_client.sendall(encrypt_text(f"[ERROR] No user with alias '{target_alias}' found."))

def list_clients(sender_client):
    client_list = ", ".join(aliases) if aliases else "No clients connected."
    sender_client.sendall(encrypt_text(f"[CLIENTS] {client_list}"))

def show_about(sender_client):
    about_text = Text()
    about_text.append("🎉 XOR Chat Server 🎉\n", style="bold magenta")
    about_text.append("Secure XOR-encrypted messages with private chat and dashboard.\n", style="cyan")
    about_text.append("💬 Commands:\n", style="green")
    about_text.append("  /pm <alias> <msg> - Private message\n", style="magenta")
    about_text.append("  /list - List connected clients\n", style="yellow")
    about_text.append("  /about - This info\n", style="blue")
    about_text.append("  /quit - Leave chat\n", style="red")
    about_text.append("  /react <alias> <emoji> - React to last message\n", style="bright_green")
    about_panel = Panel(Align.center(about_text), title="📝 About XOR Chat Server", style="bold cyan")
    sender_client.sendall(encrypt_text(str(about_panel.renderable)))

def react_message(sender_client, target_alias, emoji):
    if target_alias in last_messages:
        msg = f"{aliases[clients.index(sender_client)]} reacted to {target_alias}: {emoji}"
        log_message(msg)
        broadcast(encrypt_text(msg))
    else:
        sender_client.sendall(encrypt_text(f"[ERROR] No message from {target_alias} to react to."))

def remove_client(client):
    if client in clients:
        idx = clients.index(client)
        alias = aliases[idx]
        clients.pop(idx)
        aliases.pop(idx)
        typing_status.pop(alias, None)
        alias_colors.pop(alias, None)
        client.close()
        log_message(f"- {alias} disconnected")
        broadcast(encrypt_text(f"{alias} has left the chat room!"))
        console.print(f"[red]- {alias} disconnected[/red]")
        if live_dashboard:
            live_dashboard.update(make_dashboard())

# -----------------------
# Handle client
# -----------------------
def handle_client(client):
    while True:
        try:
            encrypted_message = client.recv(1024)
            if not encrypted_message:
                break
            msg = decrypt_text(encrypted_message)
            alias = aliases[clients.index(client)]

            if alias not in alias_colors:
                alias_colors[alias] = random.choice(COLORS)

            if msg.startswith(f"{alias}: "):
                msg = msg[len(alias) + 2:]

            # Commands
            if msg.startswith("/pm "):
                parts = msg.split(" ", 2)
                if len(parts) >= 3:
                    send_private_message(client, parts[1], parts[2])
                else:
                    client.sendall(encrypt_text("[ERROR] Usage: /pm <alias> <message>"))
                continue
            elif msg.strip().lower() == "/list":
                list_clients(client)
                continue
            elif msg.strip().lower() == "/about":
                show_about(client)
                continue
            elif msg.strip().lower().startswith("/react "):
                parts = msg.split(" ", 2)
                if len(parts) >= 3:
                    react_message(client, parts[1], parts[2])
                else:
                    client.sendall(encrypt_text("[ERROR] Usage: /react <alias> <emoji>"))
                continue
            elif msg.strip().lower() == "/quit":
                remove_client(client)
                break

            display_msg = f"{alias}: {msg}"
            last_messages[alias] = display_msg
            log_message(display_msg)
            console.print(Text(display_msg, style=alias_colors[alias]))
            broadcast(encrypt_text(display_msg), sender=client)
            if live_dashboard:
                live_dashboard.update(make_dashboard())

        except Exception:
            remove_client(client)
            break

# -----------------------
# Dashboard
# -----------------------
def make_dashboard():
    table = Table(title="📡 Chat Server Dashboard", style="bold cyan")
    table.add_column("Client Address", style="yellow", justify="left")
    table.add_column("Alias", style="magenta", justify="center")
    table.add_column("Total Clients", style="green", justify="center")
    table.add_column("Typing", style="bright_blue", justify="center")

    for i, client in enumerate(clients):
        try:
            address = f"{client.getpeername()[0]}:{client.getpeername()[1]}"
        except Exception:
            address = "Unknown"
        typing = "💭" if typing_status.get(aliases[i], False) else ""
        table.add_row(address, aliases[i], str(len(clients)), typing)

    chat_panel = Panel("\n".join(chat_log[-10:]), title="💬 Chat Log (last 10 messages)", style="white")
    dashboard = Table.grid(expand=True)
    dashboard.add_row(table, chat_panel)
    return dashboard

# -----------------------
# Server
# -----------------------
def recving():
    global live_dashboard
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    console.print(Panel.fit(f"🚀 Server started on [cyan]{HOST}[/cyan]:[magenta]{PORT}[/magenta]", title="Chat Server", style="bold green"))

    with Live(make_dashboard(), refresh_per_second=1, console=console) as live:
        live_dashboard = live
        while True:
            client, address = server.accept()
            console.print(f"[blue]+ Connected with {address}[/blue]")

            client.sendall(encrypt_text("Alias?"))
            alias_data = client.recv(1024)
            alias = decrypt_text(alias_data).strip()

            # ✅ Check for duplicate alias
            if alias in aliases:
                client.sendall(encrypt_text("[ERROR] Alias already in use. Disconnecting..."))
                client.close()
                continue

            aliases.append(alias)
            clients.append(client)
            typing_status[alias] = False
            log_message(f"+ {alias} has joined the chat!")
            broadcast(encrypt_text(f"{alias} has joined the chat!"))

            client.sendall(encrypt_text(
                "Connected! /quit /list /pm /about /react"
            ))
            live.update(make_dashboard())
            threading.Thread(target=handle_client, args=(client,), daemon=True).start()

def main():
    recving()

if __name__ == "__main__":
    main()
