# Fosen VPN

A lightweight, secure VPN implementation built with Python featuring AES-256-GCM encryption, user authentication, and both GUI and command-line interfaces.

## 🌟 Features

- **Strong Encryption**: AES-256-GCM encryption for secure data transmission
- **Global Server Network**: 10 countries with multiple server locations
- **Smart Server Selection**: Auto-select best servers based on load and ping
- **Real-time Server Stats**: Live server load monitoring and ping estimates
- **User Authentication**: Multi-user support with password-based authentication
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **GUI Interface**: Modern graphical interface with location map and server stats
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
├── fosen_vpn.py        # Main entry point
├── vpn_server.py       # VPN server implementation
├── vpn_client.py       # VPN client implementation
├── vpn_gui.py          # GUI interface with location selection
├── vpn_locations.py    # Server location management
├── config.ini          # Configuration file
├── test_vpn.py         # Unit tests
├── requirements.txt    # Dependencies
├── setup.bat           # Windows setup script
├── setup.sh            # Linux/macOS setup script
└── README.md           # This file
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

## 🌍 Available Server Locations

| Country | Flag | Servers | Cities |
|---------|------|---------|--------|
| United States | 🇺🇸 | 5 | New York, Miami, Los Angeles, San Francisco, Chicago |
| United Kingdom | 🇬🇧 | 3 | London, Manchester |
| Germany | 🇩🇪 | 3 | Frankfurt, Berlin |
| Japan | 🇯🇵 | 3 | Tokyo, Osaka |
| Canada | 🇨🇦 | 2 | Toronto, Vancouver |
| France | 🇫🇷 | 2 | Paris |
| Netherlands | 🇳🇱 | 2 | Amsterdam |
| Singapore | 🇸🇬 | 2 | Singapore |
| Australia | 🇦🇺 | 2 | Sydney, Melbourne |
| Switzerland | 🇨🇭 | 1 | Zurich |

## 🖥️ GUI Screenshots

### Server Interface
- Server configuration and control
- Real-time connection logs
- User management
- Server location overview with statistics
- Status monitoring

### Client Interface
- **Location Selection**: Choose from 10 countries with multiple servers
- **Smart Connect**: Auto-select best server based on load and ping
- **Real-time Stats**: Live server load and ping information
- **Connection Status**: Visual connection status with server details
- **Secure Messaging**: End-to-end encrypted communication

## 🌐 How to Use Server Locations

### GUI Method (Recommended)

1. **Launch the VPN Client**:
   ```bash
   python fosen_vpn.py
   ```
   Choose "No" to run the client.

2. **Select Your Location**:
   - Use the **Country** dropdown to select your preferred country
   - The **Server** dropdown will show available servers with load and ping info
   - Green 🟢 = Low load (excellent), Yellow 🟡 = Medium load (good), Red 🔴 = High load (busy)

3. **Auto-Select Best Server**:
   - Click **"🚀 Best Server"** to automatically select the globally best server
   - The system will choose based on lowest server load

4. **Manual Server Selection**:
   - Choose any country from the dropdown
   - Select a specific server based on city, load, and ping
   - Server info shows: City, Load percentage, Status, and estimated ping

5. **Connect**:
   - Enter your username and password
   - Click **"🔗 Connect to VPN"**
   - Connection status will show your selected server location

## 💡 Usage Examples

### Working with Server Locations
```python
from vpn_locations import VPNServerLocation

# Initialize location manager
locations = VPNServerLocation()

# Get all available countries
countries = locations.get_countries()
print("Available countries:", countries)

# Get servers for a specific country
us_servers = locations.get_servers_by_country("United States")
for server in us_servers:
    print(f"{server['name']} - {server['city']} (Load: {server['load']}%)")

# Auto-select best server globally
best_country, best_server = locations.get_best_server()
print(f"Best server: {best_server['name']} in {best_country}")
```

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
from vpn_locations import VPNServerLocation

# Select best server automatically
locations = VPNServerLocation()
country, server = locations.get_best_server()

# Connect to VPN (using localhost for demo)
client = VPNClient("localhost", 8080, "username", "password")
if client.connect():
    client.send_data(b"Hello, VPN!")
    response = client.receive_data()
    print(f"Connected via {server['name']} in {country}")
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