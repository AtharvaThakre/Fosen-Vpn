#!/usr/bin/env python3
"""
Fosen VPN - Simple Python VPN Implementation
===========================================

A lightweight VPN implementation with the following features:
- Encrypted tunneling using AES-256-GCM
- User authentication
- Client-server architecture
- GUI interface
- Command-line interface

Usage:
    Server: python vpn_server.py
    Client: python vpn_client.py
    GUI:    python vpn_gui.py
"""

import sys
import os
import subprocess
from typing import List


def check_dependencies() -> List[str]:
    """Check if required dependencies are installed"""
    missing = []
    
    try:
        import cryptography
    except ImportError:
        missing.append("cryptography")
    
    try:
        import colorama
    except ImportError:
        missing.append("colorama")
    
    return missing


def install_dependencies():
    """Install missing dependencies"""
    missing = check_dependencies()
    
    if not missing:
        print("✓ All dependencies are installed")
        return True
    
    print(f"Missing dependencies: {', '.join(missing)}")
    
    try:
        print("Installing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to install dependencies")
        print("Please install manually:")
        print(f"  pip install {' '.join(missing)}")
        return False


def run_server():
    """Run VPN server"""
    try:
        from vpn_server import VPNServer, VPNLogger
        import colorama
        
        print(f"{colorama.Fore.GREEN}{colorama.Style.BRIGHT}")
        print("=" * 50)
        print("       FOSEN VPN SERVER")
        print("=" * 50)
        print(f"{colorama.Style.RESET_ALL}")
        
        host = input("Server host (default: 0.0.0.0): ").strip() or "0.0.0.0"
        port = int(input("Server port (default: 8080): ").strip() or "8080")
        
        server = VPNServer(host, port)
        
        print(f"\n{colorama.Fore.YELLOW}Default users:{colorama.Style.RESET_ALL}")
        for username, password in server.users.items():
            print(f"  {username}: {password}")
        
        print(f"\n{colorama.Fore.CYAN}Starting server... Press Ctrl+C to stop{colorama.Style.RESET_ALL}")
        server.start()
        
    except KeyboardInterrupt:
        print(f"\n{colorama.Fore.YELLOW}Shutting down server...{colorama.Style.RESET_ALL}")
    except Exception as e:
        print(f"Server error: {e}")


def run_client():
    """Run VPN client"""
    try:
        from vpn_client import VPNClient, VPNLogger
        import colorama
        
        print(f"{colorama.Fore.BLUE}{colorama.Style.BRIGHT}")
        print("=" * 50)
        print("       FOSEN VPN CLIENT")
        print("=" * 50)
        print(f"{colorama.Style.RESET_ALL}")
        
        server_host = input("Server host (default: localhost): ").strip() or "localhost"
        server_port = int(input("Server port (default: 8080): ").strip() or "8080")
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        
        if not username or not password:
            print("Username and password are required!")
            return
        
        client = VPNClient(server_host, server_port, username, password)
        client.run_interactive()
        
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Client error: {e}")


def run_gui():
    """Run GUI interface"""
    try:
        from vpn_gui import main
        main()
    except ImportError as e:
        print(f"GUI error: {e}")
        print("Make sure tkinter is installed")
    except Exception as e:
        print(f"GUI error: {e}")


def show_help():
    """Show help information"""
    print("""
Fosen VPN - Simple Python VPN Implementation
===========================================

Usage:
    python fosen_vpn.py [command]

Commands:
    server    - Run VPN server
    client    - Run VPN client
    gui       - Run GUI interface (default)
    install   - Install dependencies
    help      - Show this help

Examples:
    python fosen_vpn.py            # Run GUI
    python fosen_vpn.py server     # Run server
    python fosen_vpn.py client     # Run client
    python fosen_vpn.py install    # Install dependencies

Default Users (for testing):
    admin    : admin123
    user1    : password1
    user2    : password2

Features:
    ✓ AES-256-GCM encryption
    ✓ User authentication
    ✓ Client-server architecture
    ✓ GUI interface
    ✓ Cross-platform support
    """)


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        command = "gui"
    else:
        command = sys.argv[1].lower()
    
    if command == "install":
        install_dependencies()
    elif command == "server":
        if check_dependencies():
            print("Dependencies missing. Run: python fosen_vpn.py install")
            return
        run_server()
    elif command == "client":
        if check_dependencies():
            print("Dependencies missing. Run: python fosen_vpn.py install")
            return
        run_client()
    elif command == "gui":
        if check_dependencies():
            print("Dependencies missing. Run: python fosen_vpn.py install")
            return
        run_gui()
    elif command == "help":
        show_help()
    else:
        print(f"Unknown command: {command}")
        print("Use 'python fosen_vpn.py help' for available commands")


if __name__ == "__main__":
    main()