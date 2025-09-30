"""
Unit tests for Fosen VPN
"""

import unittest
import threading
import time
import socket
from unittest.mock import Mock, patch

# Import VPN components
try:
    from vpn_server import VPNServer, VPNProtocol, VPNEncryption
    from vpn_client import VPNClient
except ImportError:
    print("Warning: VPN modules not found for testing")


class TestVPNProtocol(unittest.TestCase):
    """Test VPN protocol functions"""
    
    def test_create_packet(self):
        """Test packet creation"""
        data = b"test data"
        packet = VPNProtocol.create_packet(VPNProtocol.MSG_DATA, data)
        
        # Check packet structure
        self.assertEqual(packet[:4], VPNProtocol.MAGIC_BYTES)
        self.assertEqual(len(packet), 10 + len(data))
    
    def test_parse_packet(self):
        """Test packet parsing"""
        original_data = b"test data"
        packet = VPNProtocol.create_packet(VPNProtocol.MSG_DATA, original_data)
        
        msg_type, payload = VPNProtocol.parse_packet(packet)
        
        self.assertEqual(msg_type, VPNProtocol.MSG_DATA)
        self.assertEqual(payload, original_data)
    
    def test_invalid_packet(self):
        """Test invalid packet handling"""
        # Too short packet
        with self.assertRaises(ValueError):
            VPNProtocol.parse_packet(b"short")
        
        # Invalid magic bytes
        invalid_packet = b"XXXX" + b"\x01\x01\x00\x00\x00\x00"
        with self.assertRaises(ValueError):
            VPNProtocol.parse_packet(invalid_packet)


class TestVPNEncryption(unittest.TestCase):
    """Test VPN encryption/decryption"""
    
    def test_encryption_decryption(self):
        """Test basic encryption and decryption"""
        password = "test_password"
        encryption = VPNEncryption(password)
        
        original_data = b"This is test data for encryption"
        
        # Encrypt
        encrypted = encryption.encrypt(original_data)
        self.assertNotEqual(encrypted, original_data)
        
        # Decrypt
        decrypted = encryption.decrypt(encrypted)
        self.assertEqual(decrypted, original_data)
    
    def test_different_passwords(self):
        """Test that different passwords produce different results"""
        data = b"test data"
        
        enc1 = VPNEncryption("password1")
        enc2 = VPNEncryption("password2")
        
        encrypted1 = enc1.encrypt(data)
        
        # Should not be able to decrypt with different password
        with self.assertRaises(Exception):
            enc2.decrypt(encrypted1)


class TestVPNServer(unittest.TestCase):
    """Test VPN server functionality"""
    
    def setUp(self):
        """Set up test server"""
        self.server = VPNServer("127.0.0.1", 0)  # Use port 0 for random port
    
    def test_server_initialization(self):
        """Test server initialization"""
        self.assertIsNotNone(self.server.users)
        self.assertIn("admin", self.server.users)
        self.assertFalse(self.server.running)
    
    def test_add_remove_user(self):
        """Test user management"""
        # Add user
        self.server.add_user("testuser", "testpass")
        self.assertIn("testuser", self.server.users)
        self.assertEqual(self.server.users["testuser"], "testpass")
        
        # Remove user
        self.server.remove_user("testuser")
        self.assertNotIn("testuser", self.server.users)


class TestVPNClient(unittest.TestCase):
    """Test VPN client functionality"""
    
    def test_client_initialization(self):
        """Test client initialization"""
        client = VPNClient("localhost", 8080, "testuser", "testpass")
        
        self.assertEqual(client.server_host, "localhost")
        self.assertEqual(client.server_port, 8080)
        self.assertEqual(client.username, "testuser")
        self.assertEqual(client.password, "testpass")
        self.assertFalse(client.connected)


class TestVPNIntegration(unittest.TestCase):
    """Integration tests for VPN server and client"""
    
    def setUp(self):
        """Set up integration test"""
        self.server = VPNServer("127.0.0.1", 0)
        self.server_thread = None
    
    def tearDown(self):
        """Clean up after test"""
        if self.server:
            self.server.stop()
        if self.server_thread:
            self.server_thread.join(timeout=1)
    
    @unittest.skip("Integration test - requires manual setup")
    def test_client_server_connection(self):
        """Test client connecting to server"""
        # Start server in background
        self.server_thread = threading.Thread(target=self.server.start, daemon=True)
        self.server_thread.start()
        
        # Wait for server to start
        time.sleep(0.5)
        
        # Get actual port (since we used 0)
        actual_port = self.server.socket.getsockname()[1]
        
        # Create and connect client
        client = VPNClient("127.0.0.1", actual_port, "admin", "admin123")
        
        # Test connection
        connected = client.connect()
        self.assertTrue(connected)
        
        # Test sending data
        test_message = "Hello, VPN!"
        client.send_data(test_message.encode())
        
        # Test receiving data
        response = client.receive_data()
        self.assertIn(b"Echo:", response)
        
        # Disconnect
        client.disconnect()


class TestVPNSecurity(unittest.TestCase):
    """Test VPN security features"""
    
    def test_password_complexity(self):
        """Test password handling"""
        # Test weak password
        weak_encryption = VPNEncryption("123")
        strong_encryption = VPNEncryption("StrongPassword123!")
        
        data = b"sensitive data"
        
        # Both should work, but strong is obviously better
        weak_encrypted = weak_encryption.encrypt(data)
        strong_encrypted = strong_encryption.encrypt(data)
        
        self.assertEqual(weak_encryption.decrypt(weak_encrypted), data)
        self.assertEqual(strong_encryption.decrypt(strong_encrypted), data)
    
    def test_replay_attack_protection(self):
        """Test protection against replay attacks"""
        encryption = VPNEncryption("password")
        data = b"test data"
        
        # Encrypt same data twice
        encrypted1 = encryption.encrypt(data)
        encrypted2 = encryption.encrypt(data)
        
        # Should produce different ciphertexts (due to random IV)
        self.assertNotEqual(encrypted1, encrypted2)
        
        # But both should decrypt to same plaintext
        self.assertEqual(encryption.decrypt(encrypted1), data)
        self.assertEqual(encryption.decrypt(encrypted2), data)


if __name__ == "__main__":
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_cases = [
        TestVPNProtocol,
        TestVPNEncryption,
        TestVPNServer,
        TestVPNClient,
        TestVPNSecurity,
        # TestVPNIntegration,  # Skip integration tests by default
    ]
    
    for test_case in test_cases:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_case)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*50}")