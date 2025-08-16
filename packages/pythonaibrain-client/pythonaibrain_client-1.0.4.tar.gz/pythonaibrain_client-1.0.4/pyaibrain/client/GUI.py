from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, QScrollArea, QFrame
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QColor, QPalette
import socket
import sys
from datetime import datetime
import random

# -------------------------------
# XOR encryption helpers
# -------------------------------
XOR_KEY = "your_key_here"
_KEY_BYTES = XOR_KEY.encode("utf-8")

def xor_cipher(data, key):
    if isinstance(data, str):
        data_bytes = data.encode("utf-8")
    else:
        data_bytes = data
    key_bytes = key.encode("utf-8") if isinstance(key, str) else key
    return bytes([b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(data_bytes)])

def encrypt_text(text):
    return xor_cipher(text, _KEY_BYTES)

def decrypt_text(data):
    return xor_cipher(data, _KEY_BYTES).decode("utf-8", errors="ignore")

# -------------------------------
# Networking
# -------------------------------
HOST = "127.0.0.1"
PORT = 5555
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

USER_COLORS = ["#34B7F1", "#25D366", "#FFAB00", "#FF3D00", "#9C27B0", "#607D8B"]
alias_colors = {}

# -------------------------------
# Receiver thread
# -------------------------------
class ReceiverThread(QThread):
    new_message = Signal(str, str)  # sender, message

    def run(self):
        while True:
            try:
                msg = client_socket.recv(1024)
                if not msg:
                    break
                msg_dec = decrypt_text(msg)
                if msg_dec.startswith(f"{alias}: "):
                    continue
                parts = msg_dec.split(":", 1)
                if len(parts) == 2:
                    sender, message = parts
                    self.new_message.emit(sender.strip(), message.strip())
                else:
                    self.new_message.emit("System", msg_dec)
            except:
                self.new_message.emit("System", "[ERROR] Connection lost!")
                break

# -------------------------------
# Chat GUI
# -------------------------------
class ChatClient(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("XOR Chat - PySide6")
        self.setGeometry(200, 100, 500, 650)
        self.setStyleSheet("background-color: #1e1e1e; color: white;")

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)

        # Scrollable chat area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.chat_layout.addStretch()
        self.scroll_area.setWidget(self.chat_widget)
        self.layout.addWidget(self.scroll_area)

        # Message input
        self.input_layout = QHBoxLayout()
        self.msg_input = QLineEdit()
        self.msg_input.setPlaceholderText("Type a message...")
        self.msg_input.returnPressed.connect(self.send_message)
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.send_message)
        self.send_btn.setStyleSheet("background-color: #34B7F1; color: white;")
        self.input_layout.addWidget(self.msg_input)
        self.input_layout.addWidget(self.send_btn)
        self.layout.addLayout(self.input_layout)

        # Start receiver
        self.receiver_thread = ReceiverThread()
        self.receiver_thread.new_message.connect(self.add_message)
        self.receiver_thread.start()

    def add_message(self, sender, message):
        frame = QFrame()
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(5,5,5,5)

        time = datetime.now().strftime("%H:%M")
        if sender not in alias_colors:
            alias_colors[sender] = random.choice(USER_COLORS)
        bubble_color = "#34B7F1" if sender == alias else alias_colors[sender]

        label = QLabel(f"{message}\n[{time}]")
        label.setWordWrap(True)
        label.setStyleSheet(f"background-color: {bubble_color}; padding:8px; border-radius:10px;")
        label.setMaximumWidth(300)

        if sender == alias:
            layout.addStretch()
            layout.addWidget(label)
        else:
            layout.addWidget(label)
            layout.addStretch()

        self.chat_layout.insertWidget(self.chat_layout.count()-1, frame)
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())

    def send_message(self):
        msg = self.msg_input.text().strip()
        if msg:
            self.add_message(alias, msg)
            try:
                client_socket.sendall(encrypt_text(msg))
            except:
                self.add_message("System", "[ERROR] Cannot send message!")
            self.msg_input.clear()

# -------------------------------
# Main
# -------------------------------
alias = input("Enter your name: ").strip()
client_socket.sendall(encrypt_text(alias))

app = QApplication(sys.argv)
window = ChatClient()
window.show()
sys.exit(app.exec())
