# Pythonaibrain-Client

**TIGER AI secure encrypted socket client powered by pythonaibrain**

A Python-based terminal chat client that uses XOR encryption for secure communication.  

---

## Features

- Secure messaging with XOR cipher encryption
- Loads sensitive config (encryption key, host, port) from `.env`
- Multi-threaded send/receive for real-time chat
- Cross-platform terminal clear support (`cls` / `clear`)
- Easy to install and run as a CLI command `client-server`

---

## Project Structure

```

pythonaibrain-client/
├── pyaibrain/
│   └── client/
│       ├── **init**.py      # Main client code
│       └── .env             # Configuration file for keys & settings
├── pyproject.toml           # Project metadata & dependencies
├── README.md                # This file
└── LICENSE                  # License file

````

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- `pip` installed

### Installation

```bash
pip install pythonaibrain-client
```

## Connecting to the Server

To use this client, you need to connect to a running server.  

- Please install the **pythonaibrain** version 1.1.9 package which contains the AI server implementation.  
- Start the server using the commands or instructions provided with **pythonaibrain**.  
- Once the server is running, run this client (`client-server`) to connect and chat securely.
- Also you can run (`pyaibrain-server`) for normal chatting(Not a AI one).

## Usage

Run the client from terminal:

```bash
client-server
```

You will be prompted to enter your name, then the client will connect to the server and start the chat interface.

Also,

```python
from pyaibrain.client import ClientServer

cServer = ClientServer()
cServer.serve()
```

### Commands

* `clear` or `cls` to clear the terminal screen during chat

---

Also, run the pyaibrain-server from terminal:

```bash
pyaibrain-server
```

---

## Encryption Details

Messages are encrypted/decrypted with a simple XOR cipher using the key from `.env`.
*Note:* XOR is for demonstration and **not secure for production use**.

---

## Author

**Divyanshu Sinha**
Email: [divyanshu.sinha136@gmail.com](mailto:divyanshu.sinha136@gmail.com)

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## ✨ Preview

![Chat Preview](https://raw.githubusercontent.com/DivyanshuSinha136/pythonaibrain-client/main/Screenshot%20(153).png)

![Chat Preview](https://raw.githubusercontent.com/DivyanshuSinha136/pythonaibrain-client/main/Screenshot%20(152).png)
