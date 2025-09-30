import os
import sys
import struct
import socket
import threading
import time
import json
import base64
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple

try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
except ImportError:
    print("Error: cryptography library not found. Install with: pip install cryptography")
    sys.exit(1)

try:
    from colorama import init, Fore, Style
    init()
except ImportError:
    print("Warning: colorama not found. Colors disabled.")
    class Fore:
        RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = RESET = ""
    class Style:
        BRIGHT = DIM = RESET_ALL = ""


class VPNProtocol:
    """VPN Protocol constants and utilities"""
    
    # Protocol constants
    MAGIC_BYTES = b'\xDE\xAD\xBE\xEF'
    VERSION = 1
    
    # Message types
    MSG_HANDSHAKE = 0x01
    MSG_AUTH = 0x02
    MSG_DATA = 0x03
    MSG_KEEPALIVE = 0x04
    MSG_DISCONNECT = 0x05
    MSG_AUTH_SUCCESS = 0x06
    MSG_AUTH_FAILURE = 0x07
    
    # Encryption settings
    AES_KEY_SIZE = 32  # 256-bit
    AES_IV_SIZE = 16   # 128-bit
    
    @staticmethod
    def create_packet(msg_type: int, data: bytes = b'') -> bytes:
        """Create a VPN protocol packet"""
        header = struct.pack('!4sBBI', VPNProtocol.MAGIC_BYTES, 
                           VPNProtocol.VERSION, msg_type, len(data))
        return header + data
    
    @staticmethod
    def parse_packet(data: bytes) -> Tuple[int, bytes]:
        """Parse a VPN protocol packet"""
        if len(data) < 10:
            raise ValueError("Packet too short")
        
        magic, version, msg_type, length = struct.unpack('!4sBBI', data[:10])
        
        if magic != VPNProtocol.MAGIC_BYTES:
            raise ValueError("Invalid magic bytes")
        
        if version != VPNProtocol.VERSION:
            raise ValueError(f"Unsupported version: {version}")
        
        if len(data) < 10 + length:
            raise ValueError("Incomplete packet")
        
        payload = data[10:10+length]
        return msg_type, payload


class VPNEncryption:
    """Handles encryption/decryption for VPN traffic"""
    
    def __init__(self, password: str):
        self.password = password.encode()
        self.salt = os.urandom(16)
        self.key = self._derive_key()
        
    def _derive_key(self) -> bytes:
        """Derive encryption key from password"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=VPNProtocol.AES_KEY_SIZE,
            salt=self.salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(self.password)
    
    def encrypt(self, data: bytes) -> bytes:
        """Encrypt data using AES-256-GCM"""
        iv = os.urandom(VPNProtocol.AES_IV_SIZE)
        cipher = Cipher(
            algorithms.AES(self.key),
            modes.GCM(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(data) + encryptor.finalize()
        return iv + encryptor.tag + ciphertext
    
    def decrypt(self, data: bytes) -> bytes:
        """Decrypt data using AES-256-GCM"""
        if len(data) < VPNProtocol.AES_IV_SIZE + 16:
            raise ValueError("Invalid encrypted data")
        
        iv = data[:VPNProtocol.AES_IV_SIZE]
        tag = data[VPNProtocol.AES_IV_SIZE:VPNProtocol.AES_IV_SIZE + 16]
        ciphertext = data[VPNProtocol.AES_IV_SIZE + 16:]
        
        cipher = Cipher(
            algorithms.AES(self.key),
            modes.GCM(iv, tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        return decryptor.update(ciphertext) + decryptor.finalize()


class VPNLogger:
    """Simple logging utility for VPN"""
    
    @staticmethod
    def log(level: str, message: str, color: str = ""):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if color:
            print(f"{color}[{timestamp}] {level}: {message}{Style.RESET_ALL}")
        else:
            print(f"[{timestamp}] {level}: {message}")
    
    @staticmethod
    def info(message: str):
        VPNLogger.log("INFO", message, Fore.CYAN)
    
    @staticmethod
    def success(message: str):
        VPNLogger.log("SUCCESS", message, Fore.GREEN)
    
    @staticmethod
    def warning(message: str):
        VPNLogger.log("WARNING", message, Fore.YELLOW)
    
    @staticmethod
    def error(message: str):
        VPNLogger.log("ERROR", message, Fore.RED)


class VPNClient:
    """VPN Client implementation"""
    
    def __init__(self, server_host: str, server_port: int, username: str, password: str):
        self.server_host = server_host
        self.server_port = server_port
        self.username = username
        self.password = password
        self.socket = None
        self.encryption = None
        self.connected = False
        self.running = False
        
    def connect(self) -> bool:
        """Connect to VPN server"""
        try:
            VPNLogger.info(f"Connecting to VPN server {self.server_host}:{self.server_port}")
            
            # Create socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((self.server_host, self.server_port))
            
            # Initialize encryption
            self.encryption = VPNEncryption(self.password)
            
            # Perform handshake
            if not self._handshake():
                return False
            
            # Authenticate
            if not self._authenticate():
                return False
            
            self.connected = True
            self.running = True
            VPNLogger.success("Connected to VPN server!")
            
            # Start keep-alive thread
            keepalive_thread = threading.Thread(target=self._keepalive_worker, daemon=True)
            keepalive_thread.start()
            
            return True
            
        except Exception as e:
            VPNLogger.error(f"Connection failed: {e}")
            return False
    
    def _handshake(self) -> bool:
        """Perform initial handshake"""
        try:
            # Send handshake
            handshake_data = json.dumps({
                'client_version': VPNProtocol.VERSION,
                'encryption_salt': base64.b64encode(self.encryption.salt).decode()
            }).encode()
            
            packet = VPNProtocol.create_packet(VPNProtocol.MSG_HANDSHAKE, handshake_data)
            self.socket.send(packet)
            
            # Receive response
            response = self.socket.recv(1024)
            msg_type, payload = VPNProtocol.parse_packet(response)
            
            if msg_type == VPNProtocol.MSG_HANDSHAKE:
                VPNLogger.info("Handshake successful")
                return True
            else:
                VPNLogger.error("Handshake failed")
                return False
                
        except Exception as e:
            VPNLogger.error(f"Handshake error: {e}")
            return False
    
    def _authenticate(self) -> bool:
        """Authenticate with server"""
        try:
            # Send authentication
            auth_data = json.dumps({
                'username': self.username,
                'timestamp': int(time.time())
            }).encode()
            
            encrypted_auth = self.encryption.encrypt(auth_data)
            packet = VPNProtocol.create_packet(VPNProtocol.MSG_AUTH, encrypted_auth)
            self.socket.send(packet)
            
            # Receive response
            response = self.socket.recv(1024)
            msg_type, payload = VPNProtocol.parse_packet(response)
            
            if msg_type == VPNProtocol.MSG_AUTH_SUCCESS:
                VPNLogger.success("Authentication successful")
                return True
            elif msg_type == VPNProtocol.MSG_AUTH_FAILURE:
                VPNLogger.error("Authentication failed")
                return False
            else:
                VPNLogger.error("Unexpected authentication response")
                return False
                
        except Exception as e:
            VPNLogger.error(f"Authentication error: {e}")
            return False
    
    def _keepalive_worker(self):
        """Send keep-alive messages"""
        while self.running and self.connected:
            try:
                time.sleep(30)  # Send keep-alive every 30 seconds
                if self.running:
                    packet = VPNProtocol.create_packet(VPNProtocol.MSG_KEEPALIVE)
                    self.socket.send(packet)
            except:
                break
    
    def send_data(self, data: bytes):
        """Send data through VPN tunnel"""
        if not self.connected:
            raise RuntimeError("Not connected to VPN server")
        
        try:
            encrypted_data = self.encryption.encrypt(data)
            packet = VPNProtocol.create_packet(VPNProtocol.MSG_DATA, encrypted_data)
            self.socket.send(packet)
        except Exception as e:
            VPNLogger.error(f"Failed to send data: {e}")
            raise
    
    def receive_data(self) -> bytes:
        """Receive data from VPN tunnel"""
        if not self.connected:
            raise RuntimeError("Not connected to VPN server")
        
        try:
            response = self.socket.recv(4096)
            if not response:
                raise ConnectionError("Connection closed by server")
            
            msg_type, payload = VPNProtocol.parse_packet(response)
            
            if msg_type == VPNProtocol.MSG_DATA:
                return self.encryption.decrypt(payload)
            elif msg_type == VPNProtocol.MSG_KEEPALIVE:
                return b''  # Keep-alive, no data
            else:
                VPNLogger.warning(f"Unexpected message type: {msg_type}")
                return b''
                
        except Exception as e:
            VPNLogger.error(f"Failed to receive data: {e}")
            raise
    
    def disconnect(self):
        """Disconnect from VPN server"""
        if self.connected:
            try:
                packet = VPNProtocol.create_packet(VPNProtocol.MSG_DISCONNECT)
                self.socket.send(packet)
            except:
                pass
        
        self.running = False
        self.connected = False
        
        if self.socket:
            self.socket.close()
            
        VPNLogger.info("Disconnected from VPN server")
    
    def run_interactive(self):
        """Run interactive client session"""
        if not self.connect():
            return
        
        try:
            VPNLogger.info("VPN tunnel established. Type 'quit' to disconnect.")
            
            while self.running:
                try:
                    # Simple echo test
                    message = input("Enter message to send (or 'quit'): ").strip()
                    
                    if message.lower() == 'quit':
                        break
                    
                    if message:
                        self.send_data(message.encode())
                        response = self.receive_data()
                        if response:
                            VPNLogger.success(f"Server echo: {response.decode()}")
                
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    VPNLogger.error(f"Communication error: {e}")
                    break
        
        finally:
            self.disconnect()


if __name__ == "__main__":
    print(f"{Fore.BLUE}{Style.BRIGHT}")
    print("=" * 50)
    print("       FOSEN VPN CLIENT")
    print("=" * 50)
    print(f"{Style.RESET_ALL}")
    
    # Get connection details
    try:
        server_host = input("Server host (default: localhost): ").strip() or "localhost"
        server_port = int(input("Server port (default: 8080): ").strip() or "8080")
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        
        if not username or not password:
            print("Username and password are required!")
            sys.exit(1)
        
        # Create and run client
        client = VPNClient(server_host, server_port, username, password)
        client.run_interactive()
        
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        VPNLogger.error(f"Client error: {e}")