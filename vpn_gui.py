import os
import sys
import socket
import threading
import time
import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Optional

# Import VPN components
try:
    from vpn_client import VPNClient, VPNLogger
    from vpn_server import VPNServer
except ImportError:
    print("Error: VPN modules not found")
    sys.exit(1)


class VPNServerGUI:
    """GUI for VPN Server"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Fosen VPN Server")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        self.server: Optional[VPNServer] = None
        self.server_thread: Optional[threading.Thread] = None
        self.running = False
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Fosen VPN Server", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Server configuration
        config_frame = ttk.LabelFrame(main_frame, text="Server Configuration", padding="10")
        config_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        
        # Host
        ttk.Label(config_frame, text="Host:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.host_var = tk.StringVar(value="0.0.0.0")
        host_entry = ttk.Entry(config_frame, textvariable=self.host_var)
        host_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Port
        ttk.Label(config_frame, text="Port:").grid(row=0, column=2, sticky=tk.W, padx=(10, 10))
        self.port_var = tk.StringVar(value="8080")
        port_entry = ttk.Entry(config_frame, textvariable=self.port_var, width=10)
        port_entry.grid(row=0, column=3, sticky=tk.W)
        
        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, columnspan=3, pady=(0, 10))
        
        self.start_button = ttk.Button(control_frame, text="Start Server", 
                                      command=self.start_server)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(control_frame, text="Stop Server", 
                                     command=self.stop_server, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Status
        self.status_var = tk.StringVar(value="Server stopped")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, 
                                font=("Arial", 10, "bold"))
        status_label.grid(row=3, column=0, columnspan=3, pady=(0, 10))
        
        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="Server Log", padding="5")
        log_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=70)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # User management
        user_frame = ttk.LabelFrame(main_frame, text="User Management", padding="10")
        user_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        user_frame.columnconfigure(1, weight=1)
        
        ttk.Label(user_frame, text="Username:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(user_frame, textvariable=self.username_var)
        username_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Label(user_frame, text="Password:").grid(row=0, column=2, sticky=tk.W, padx=(10, 5))
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(user_frame, textvariable=self.password_var, show="*")
        password_entry.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=(0, 10))
        
        add_user_button = ttk.Button(user_frame, text="Add User", command=self.add_user)
        add_user_button.grid(row=0, column=4, padx=(10, 0))
        
    def log_message(self, message: str):
        """Add message to log"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        
    def start_server(self):
        """Start the VPN server"""
        try:
            host = self.host_var.get().strip()
            port = int(self.port_var.get().strip())
            
            if not host:
                messagebox.showerror("Error", "Host cannot be empty")
                return
            
            self.server = VPNServer(host, port)
            self.server_thread = threading.Thread(target=self._run_server, daemon=True)
            self.server_thread.start()
            
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.status_var.set(f"Server running on {host}:{port}")
            self.running = True
            
            self.log_message(f"VPN Server started on {host}:{port}")
            self.log_message("Default users: admin/admin123, user1/password1, user2/password2")
            
        except ValueError:
            messagebox.showerror("Error", "Invalid port number")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start server: {e}")
    
    def _run_server(self):
        """Run server in separate thread"""
        try:
            self.server.start()
        except Exception as e:
            self.log_message(f"Server error: {e}")
    
    def stop_server(self):
        """Stop the VPN server"""
        if self.server:
            self.server.stop()
            self.server = None
        
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("Server stopped")
        self.running = False
        
        self.log_message("VPN Server stopped")
    
    def add_user(self):
        """Add a new user"""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Username and password cannot be empty")
            return
        
        if self.server:
            self.server.add_user(username, password)
            self.log_message(f"User '{username}' added")
        else:
            messagebox.showwarning("Warning", "Server not running")
        
        self.username_var.set("")
        self.password_var.set("")
    
    def run(self):
        """Run the GUI"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Handle window closing"""
        if self.running:
            self.stop_server()
        self.root.destroy()


class VPNClientGUI:
    """GUI for VPN Client"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Fosen VPN Client")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        self.client: Optional[VPNClient] = None
        self.connected = False
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Fosen VPN Client", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Connection configuration
        config_frame = ttk.LabelFrame(main_frame, text="Connection Settings", padding="10")
        config_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        config_frame.columnconfigure(3, weight=1)
        
        # Server host
        ttk.Label(config_frame, text="Server:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.host_var = tk.StringVar(value="localhost")
        host_entry = ttk.Entry(config_frame, textvariable=self.host_var)
        host_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Port
        ttk.Label(config_frame, text="Port:").grid(row=0, column=2, sticky=tk.W, padx=(10, 5))
        self.port_var = tk.StringVar(value="8080")
        port_entry = ttk.Entry(config_frame, textvariable=self.port_var, width=10)
        port_entry.grid(row=0, column=3, sticky=tk.W)
        
        # Username
        ttk.Label(config_frame, text="Username:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5))
        self.username_var = tk.StringVar(value="admin")
        username_entry = ttk.Entry(config_frame, textvariable=self.username_var)
        username_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Password
        ttk.Label(config_frame, text="Password:").grid(row=1, column=2, sticky=tk.W, padx=(10, 5))
        self.password_var = tk.StringVar(value="admin123")
        password_entry = ttk.Entry(config_frame, textvariable=self.password_var, show="*")
        password_entry.grid(row=1, column=3, sticky=(tk.W, tk.E))
        
        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, columnspan=3, pady=(0, 10))
        
        self.connect_button = ttk.Button(control_frame, text="Connect", 
                                        command=self.connect_vpn)
        self.connect_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.disconnect_button = ttk.Button(control_frame, text="Disconnect", 
                                           command=self.disconnect_vpn, state=tk.DISABLED)
        self.disconnect_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Status
        self.status_var = tk.StringVar(value="Disconnected")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, 
                                font=("Arial", 10, "bold"))
        status_label.grid(row=3, column=0, columnspan=3, pady=(0, 10))
        
        # Communication area
        comm_frame = ttk.LabelFrame(main_frame, text="Communication", padding="5")
        comm_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        comm_frame.columnconfigure(0, weight=1)
        comm_frame.rowconfigure(0, weight=1)
        
        # Log area
        self.log_text = scrolledtext.ScrolledText(comm_frame, height=12, width=70)
        self.log_text.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Message input
        msg_frame = ttk.Frame(comm_frame)
        msg_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))
        msg_frame.columnconfigure(0, weight=1)
        
        self.message_var = tk.StringVar()
        message_entry = ttk.Entry(msg_frame, textvariable=self.message_var)
        message_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        message_entry.bind("<Return>", lambda e: self.send_message())
        
        send_button = ttk.Button(msg_frame, text="Send", command=self.send_message)
        send_button.grid(row=0, column=1)
    
    def log_message(self, message: str, color: str = "black"):
        """Add message to log"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
    
    def connect_vpn(self):
        """Connect to VPN server"""
        try:
            host = self.host_var.get().strip()
            port = int(self.port_var.get().strip())
            username = self.username_var.get().strip()
            password = self.password_var.get().strip()
            
            if not all([host, username, password]):
                messagebox.showerror("Error", "All fields are required")
                return
            
            self.client = VPNClient(host, port, username, password)
            
            # Connect in separate thread
            connect_thread = threading.Thread(target=self._connect_thread, daemon=True)
            connect_thread.start()
            
        except ValueError:
            messagebox.showerror("Error", "Invalid port number")
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {e}")
    
    def _connect_thread(self):
        """Connect to server in separate thread"""
        try:
            if self.client.connect():
                self.connected = True
                self.root.after(0, self._on_connected)
                
                # Listen for messages
                while self.connected and self.client.connected:
                    try:
                        data = self.client.receive_data()
                        if data:
                            self.root.after(0, lambda: self.log_message(f"Received: {data.decode()}"))
                    except:
                        break
            else:
                self.root.after(0, lambda: messagebox.showerror("Error", "Failed to connect"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Connection error: {e}"))
    
    def _on_connected(self):
        """Update UI when connected"""
        self.connect_button.config(state=tk.DISABLED)
        self.disconnect_button.config(state=tk.NORMAL)
        self.status_var.set("Connected")
        self.log_message("Connected to VPN server!")
    
    def disconnect_vpn(self):
        """Disconnect from VPN server"""
        self.connected = False
        if self.client:
            self.client.disconnect()
            self.client = None
        
        self.connect_button.config(state=tk.NORMAL)
        self.disconnect_button.config(state=tk.DISABLED)
        self.status_var.set("Disconnected")
        self.log_message("Disconnected from VPN server")
    
    def send_message(self):
        """Send message through VPN"""
        if not self.connected or not self.client:
            messagebox.showwarning("Warning", "Not connected to VPN")
            return
        
        message = self.message_var.get().strip()
        if not message:
            return
        
        try:
            self.client.send_data(message.encode())
            self.log_message(f"Sent: {message}")
            self.message_var.set("")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send message: {e}")
    
    def run(self):
        """Run the GUI"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Handle window closing"""
        if self.connected:
            self.disconnect_vpn()
        self.root.destroy()


def main():
    """Main function to choose between server and client"""
    root = tk.Tk()
    root.withdraw()  # Hide main window
    
    choice = messagebox.askyesnocancel(
        "Fosen VPN",
        "Choose application type:\n\nYes = VPN Server\nNo = VPN Client\nCancel = Exit"
    )
    
    root.destroy()
    
    if choice is True:
        # Run VPN Server
        app = VPNServerGUI()
        app.run()
    elif choice is False:
        # Run VPN Client
        app = VPNClientGUI()
        app.run()
    # If cancelled, just exit


if __name__ == "__main__":
    main()