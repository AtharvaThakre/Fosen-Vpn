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


class ClientHandler:
    """Handles individual client connections"""
    
    def __init__(self, socket: socket.socket, address: Tuple[str, int], users: Dict[str, str]):
        self.socket = socket
        self.address = address
        self.users = users
        self.encryption = None
        self.authenticated = False
        self.username = None
        self.running = True
        
    def handle(self):
        """Handle client connection"""
        try:
            VPNLogger.info(f"New client connection from {self.address}")
            
            while self.running:
                try:
                    data = self.socket.recv(4096)
                    if not data:
                        break
                    
                    msg_type, payload = VPNProtocol.parse_packet(data)
                    self._handle_message(msg_type, payload)
                    
                except Exception as e:
                    VPNLogger.error(f"Error handling client {self.address}: {e}")
                    break
        
        finally:
            self.socket.close()
            VPNLogger.info(f"Client {self.address} disconnected")
    
    def _handle_message(self, msg_type: int, payload: bytes):
        """Handle different message types"""
        if msg_type == VPNProtocol.MSG_HANDSHAKE:
            self._handle_handshake(payload)
        elif msg_type == VPNProtocol.MSG_AUTH:
            self._handle_auth(payload)
        elif msg_type == VPNProtocol.MSG_DATA:
            self._handle_data(payload)
        elif msg_type == VPNProtocol.MSG_KEEPALIVE:
            self._handle_keepalive()
        elif msg_type == VPNProtocol.MSG_DISCONNECT:
            self._handle_disconnect()
        else:
            VPNLogger.warning(f"Unknown message type from {self.address}: {msg_type}")
    
    def _handle_handshake(self, payload: bytes):
        """Handle handshake message"""
        try:
            data = json.loads(payload.decode())
            client_version = data.get('client_version')
            encryption_salt = base64.b64decode(data.get('encryption_salt', ''))
            
            if client_version != VPNProtocol.VERSION:
                VPNLogger.error(f"Version mismatch with {self.address}: {client_version}")
                return
            
            # Store salt for later encryption setup
            self.client_salt = encryption_salt
            
            # Send handshake response
            response_data = json.dumps({
                'server_version': VPNProtocol.VERSION,
                'status': 'ok'
            }).encode()
            
            packet = VPNProtocol.create_packet(VPNProtocol.MSG_HANDSHAKE, response_data)
            self.socket.send(packet)
            
            VPNLogger.info(f"Handshake completed with {self.address}")
            
        except Exception as e:
            VPNLogger.error(f"Handshake error with {self.address}: {e}")
    
    def _handle_auth(self, payload: bytes):
        """Handle authentication message"""
        try:
            if not hasattr(self, 'client_salt'):
                self._send_auth_failure()
                return
            
            # Try to decrypt with each user's password
            for username, password in self.users.items():
                try:
                    # Create encryption with user's password and client's salt
                    temp_encryption = VPNEncryption(password)
                    temp_encryption.salt = self.client_salt
                    temp_encryption.key = temp_encryption._derive_key()
                    
                    # Try to decrypt
                    decrypted = temp_encryption.decrypt(payload)
                    auth_data = json.loads(decrypted.decode())
                    
                    if auth_data.get('username') == username:
                        # Authentication successful
                        self.username = username
                        self.encryption = temp_encryption
                        self.authenticated = True
                        self._send_auth_success()
                        VPNLogger.success(f"User {username} authenticated from {self.address}")
                        return
                        
                except:
                    continue
            
            # If we get here, authentication failed
            self._send_auth_failure()
            VPNLogger.warning(f"Authentication failed for {self.address}")
            
        except Exception as e:
            VPNLogger.error(f"Authentication error with {self.address}: {e}")
            self._send_auth_failure()
    
    def _send_auth_success(self):
        """Send authentication success message"""
        packet = VPNProtocol.create_packet(VPNProtocol.MSG_AUTH_SUCCESS)
        self.socket.send(packet)
    
    def _send_auth_failure(self):
        """Send authentication failure message"""
        packet = VPNProtocol.create_packet(VPNProtocol.MSG_AUTH_FAILURE)
        self.socket.send(packet)
    
    def _handle_data(self, payload: bytes):
        """Handle data message (echo back for demo)"""
        if not self.authenticated:
            VPNLogger.warning(f"Unauthenticated data from {self.address}")
            return
        
        try:
            # Decrypt data
            decrypted = self.encryption.decrypt(payload)
            VPNLogger.info(f"Received from {self.username}@{self.address}: {decrypted.decode()}")
            
            # Echo back (in real VPN, this would be forwarded to destination)
            echo_data = f"Echo: {decrypted.decode()}"
            encrypted_echo = self.encryption.encrypt(echo_data.encode())
            packet = VPNProtocol.create_packet(VPNProtocol.MSG_DATA, encrypted_echo)
            self.socket.send(packet)
            
        except Exception as e:
            VPNLogger.error(f"Data handling error with {self.address}: {e}")
    
    def _handle_keepalive(self):
        """Handle keep-alive message"""
        # Send keep-alive response
        packet = VPNProtocol.create_packet(VPNProtocol.MSG_KEEPALIVE)
        self.socket.send(packet)
    
    def _handle_disconnect(self):
        """Handle disconnect message"""
        VPNLogger.info(f"Client {self.address} requested disconnect")
        self.running = False


class VPNServer:
    """VPN Server implementation"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8080):
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        self.clients = []
        
        # Default users (in production, use proper user management)
        self.users = {
            "admin": "admin123",
            "user1": "password1",
            "user2": "password2"
        }
    
    def start(self):
        """Start the VPN server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(10)
            
            self.running = True
            
            VPNLogger.success(f"VPN Server started on {self.host}:{self.port}")
            VPNLogger.info(f"Available users: {', '.join(self.users.keys())}")
            
            while self.running:
                try:
                    client_socket, address = self.socket.accept()
                    
                    # Handle client in separate thread
                    handler = ClientHandler(client_socket, address, self.users)
                    client_thread = threading.Thread(target=handler.handle, daemon=True)
                    client_thread.start()
                    
                    self.clients.append(handler)
                    
                except socket.error:
                    if self.running:
                        VPNLogger.error("Socket error in server loop")
                    break
        
        except Exception as e:
            VPNLogger.error(f"Server error: {e}")
        
        finally:
            self.stop()
    
    def stop(self):
        """Stop the VPN server"""
        self.running = False
        if self.socket:
            self.socket.close()
        VPNLogger.info("VPN Server stopped")
    
    def add_user(self, username: str, password: str):
        """Add a new user"""
        self.users[username] = password
        VPNLogger.info(f"User {username} added")
    
    def remove_user(self, username: str):
        """Remove a user"""
        if username in self.users:
            del self.users[username]
            VPNLogger.info(f"User {username} removed")


if __name__ == "__main__":
    print(f"{Fore.GREEN}{Style.BRIGHT}")
    print("=" * 50)
    print("       FOSEN VPN SERVER")
    print("=" * 50)
    print(f"{Style.RESET_ALL}")
    
    try:
        host = input("Server host (default: 0.0.0.0): ").strip() or "0.0.0.0"
        port = int(input("Server port (default: 8080): ").strip() or "8080")
        
        server = VPNServer(host, port)
        
        print(f"\n{Fore.YELLOW}Default users:{Style.RESET_ALL}")
        for username, password in server.users.items():
            print(f"  {username}: {password}")
        
        print(f"\n{Fore.CYAN}Starting server... Press Ctrl+C to stop{Style.RESET_ALL}")
        server.start()
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Shutting down server...{Style.RESET_ALL}")
    except Exception as e:
        VPNLogger.error(f"Server startup error: {e}")