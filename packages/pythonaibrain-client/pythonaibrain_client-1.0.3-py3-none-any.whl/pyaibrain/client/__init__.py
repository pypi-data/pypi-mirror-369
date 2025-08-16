import socket
import threading
import os
import sys
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown
from datetime import datetime
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML

console = Console()
session = PromptSession()

prompt_style = Style.from_dict({
    'prompt': 'bold green',
})

class ClientServer:
    def __init__(self, host='127.0.0.1', port=5555):
        load_dotenv()
        self.alias = None
        self.host = host
        self.port = port
        self.key = os.getenv("KEY")
        if not self.key:
            console.print("[bold red]ERROR:[/] Encryption KEY not found in .env file.")
            sys.exit(1)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = True

        # Emoji shortcut dictionary
        self.emoji_map = {
            '/smile': '😄',
            '/wave': '👋',
            '/heart': '❤️',
            '/thumbsup': '👍',
            '/laugh': '😂',
            '/cry': '😢',
            '/fire': '🔥',
            '/star': '⭐',
            # add more shortcuts here
        }

    def xor_cipher(self, text, key):
        result = ''
        key_index = 0
        for char in text:
            result += chr(ord(char) ^ ord(key[key_index]))
            key_index = (key_index + 1) % len(key)
        return result

    def connect(self):
        console.print(Panel.fit(f"Connecting to [green]{self.host}[/]:[cyan]{self.port}[/]", title="Client Server"))
        while self.running:
            try:
                self.client.connect((self.host, self.port))
                console.print("[bold green]Connected to the server![/]")
                break
            except ConnectionRefusedError:
                console.print("[yellow]Server not found, retrying...[/]", end='\r')
            except Exception as e:
                console.print(f"[red]Connection error:[/] {e}")
                break

    def receive(self):
        while self.running:
            try:
                message = self.client.recv(1024).decode()
                if not message:
                    console.print("[red]Disconnected from server[/]")
                    self.running = False
                    break
                if message == self.xor_cipher("Alias?", self.key):
                    self.client.send(self.xor_cipher(self.alias, self.key).encode())
                else:
                    decrypted = self.xor_cipher(message, self.key)
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    console.print(f"[dim]{timestamp}[/] [cyan]{decrypted}[/]\n")
            except Exception:
                console.print("[red]Internal Server Error! Closing connection.[/]")
                self.running = False
                self.client.close()
                break

    def print_help(self):
        help_md = """
# Help - Client Commands

* Type your messages and press Enter to send.
* Use **clear** or **cls** to clear the screen.
* Type **@help** to see this help message.
* Emoji shortcuts you can use anywhere in your message:

  * `/smile` → 😄
  * `/wave` → 👋
  * `/heart` → ❤️
  * `/thumbsup` → 👍
  * `/laugh` → 😂
  * `/cry` → 😢
  * `/fire` → 🔥
  * `/star` → ⭐

"""

        for shortcut, emoji in self.emoji_map.items():
            help_md += f"  - `{shortcut}` → {emoji}\n"

        md = Markdown(help_md)
        console.print(Panel(md, title=":information_source: Help", border_style="cyan"))

    def send(self):
        console.print("[bold yellow]:wave: Welcome! Type your messages below. Use 'clear' or 'cls' to clear the screen. Type '@help' for commands.[/]")
        while self.running:
            try:
                with patch_stdout():
                    user_input = session.prompt(
                        HTML(f'<prompt>{self.alias}&gt; </prompt>'),
                        style=prompt_style
                    ).strip()
                if not user_input:
                    continue

                if user_input.lower() in ['clear', 'cls']:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    continue

                if user_input.lower() == '@help':
                    self.print_help()
                    continue

                # Replace shortcuts with emojis
                for shortcut, emoji in self.emoji_map.items():
                    user_input = user_input.replace(shortcut, emoji)

                message = f"{self.alias}: {user_input}"
                encrypted = self.xor_cipher(message, self.key)
                self.client.send(encrypted.encode())
            except (KeyboardInterrupt, EOFError):
                console.print("\n[bold red]Exiting...[/]")
                self.running = False
                self.client.close()
                break
            except Exception as e:
                console.print(f"[red]Error sending message:[/] {e}")
                self.running = False
                break

    def serve(self):
        self.alias = Prompt.ask("Enter your name").strip()
        if not self.alias:
            console.print("[red]Alias cannot be empty! Exiting.[/]")
            return
        self.connect()
        if not self.running:
            return
        receive_thread = threading.Thread(target=self.receive, daemon=True)
        send_thread = threading.Thread(target=self.send, daemon=True)
        receive_thread.start()
        send_thread.start()
        receive_thread.join()
        send_thread.join()

def main():
    client = ClientServer()
    client.serve()

if __name__ == "__main__":
    main()
