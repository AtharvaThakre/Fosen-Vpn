# Fosen VPN

A lightweight, secure VPN implementation built with Python featuring AES-256-GCM encryption, user authentication, and both GUI and command-line interfaces.

## 🌟 Features

- **Strong Encryption**: AES-256-GCM encryption for secure data transmission
- **User Authentication**: Multi-user support with password-based authentication
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **GUI Interface**: Easy-to-use graphical interface for both server and client
- **Command Line**: Full CLI support for automated deployments
- **Lightweight**: Minimal dependencies and resource usage
- **Modular Design**: Clean, extensible codebase

## 🚀 Quick Start

### Installation

1. Clone the repository:
```bash
git clone https://github.com/AtharvaThakre/Fosen-Vpn.git
cd Fosen-Vpn
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Or use the built-in installer:
```bash
python fosen_vpn.py install
```

### Usage

#### GUI Mode (Recommended)
```bash
python fosen_vpn.py gui
```
or simply:
```bash
python fosen_vpn.py
```

#### Server Mode
```bash
python fosen_vpn.py server
```

#### Client Mode
```bash
python fosen_vpn.py client
```

## 📁 Project Structure

```
Fosen-Vpn/
├── fosen_vpn.py      # Main entry point
├── vpn_server.py     # VPN server implementation
├── vpn_client.py     # VPN client implementation
├── vpn_gui.py        # GUI interface
├── config.ini        # Configuration file
├── test_vpn.py       # Unit tests
├── requirements.txt  # Dependencies
└── README.md         # This file
```

## 🔧 Configuration

Edit `config.ini` to customize server and client settings:

```ini
[server]
host = 0.0.0.0
port = 8080
max_clients = 50

[client]
server_host = localhost
server_port = 8080
connect_timeout = 10

[users]
admin = admin123
user1 = password1
user2 = password2
```

## 🔐 Default Users

For testing purposes, the following users are pre-configured:

| Username | Password   |
|----------|------------|
| admin    | admin123   |
| user1    | password1  |
| user2    | password2  |

## 🛠️ Technical Details

### Architecture
- **Client-Server Model**: Traditional VPN architecture with centralized server
- **Protocol**: Custom protocol with magic bytes and message types
- **Encryption**: AES-256-GCM with PBKDF2 key derivation
- **Transport**: TCP sockets for reliable communication

### Security Features
- **Key Derivation**: PBKDF2 with 100,000 iterations
- **Authenticated Encryption**: GCM mode prevents tampering
- **Random IV**: Each message uses a unique initialization vector
- **Session Management**: Automatic keep-alive and timeout handling

### Message Types
- `MSG_HANDSHAKE`: Initial connection setup
- `MSG_AUTH`: User authentication
- `MSG_DATA`: Encrypted data transmission
- `MSG_KEEPALIVE`: Connection maintenance
- `MSG_DISCONNECT`: Clean disconnection

## 🧪 Testing

Run the test suite:
```bash
python test_vpn.py
```

Or run specific tests:
```bash
python -m unittest test_vpn.TestVPNProtocol
```

## 📋 Requirements

- Python 3.7+
- cryptography>=41.0.7
- colorama>=0.4.6 (optional, for colored output)
- tkinter (usually included with Python)

## 🖥️ GUI Screenshots

### Server Interface
- Server configuration and control
- Real-time connection logs
- User management
- Status monitoring

### Client Interface
- Connection settings
- Secure messaging
- Connection status
- Real-time communication

## 💡 Usage Examples

### Starting a VPN Server
```python
from vpn_server import VPNServer

server = VPNServer("0.0.0.0", 8080)
server.add_user("newuser", "securepassword")
server.start()
```

### Connecting a VPN Client
```python
from vpn_client import VPNClient

client = VPNClient("server.example.com", 8080, "username", "password")
if client.connect():
    client.send_data(b"Hello, VPN!")
    response = client.receive_data()
    print(response)
```

## 🔒 Security Considerations

1. **Change Default Passwords**: Always change default user passwords in production
2. **Use Strong Passwords**: Implement password complexity requirements
3. **Certificate Validation**: Consider adding certificate-based authentication
4. **Network Security**: Use firewalls and network segmentation
5. **Logging**: Monitor connection logs for suspicious activity

## 🚧 Known Limitations

- **Educational Purpose**: This is a demonstration VPN, not suitable for production use
- **No IP Routing**: Does not handle actual IP packet routing like commercial VPNs
- **Limited Protocol Support**: Currently supports TCP-based communication only
- **No Traffic Routing**: Real network traffic routing requires additional implementation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **cryptography** library for robust encryption
- **Python** community for excellent networking libraries
- **Tkinter** for cross-platform GUI support

## 📞 Support

For support, please open an issue on GitHub or contact the maintainer.

## ⚠️ Disclaimer

This VPN implementation is for educational purposes only. It demonstrates VPN concepts and secure communication but should not be used as a replacement for commercial VPN solutions in production environments.

---

**Happy Coding! 🎉**