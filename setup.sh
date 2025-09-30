#!/bin/bash

echo "======================================="
echo "   Fosen VPN - Linux/macOS Setup Script"
echo "======================================="
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3 from your package manager"
    exit 1
fi

echo "Python found!"
python3 --version

echo
echo "Installing required packages..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo
    echo "Warning: Some packages may have failed to install"
    echo "You can try installing them manually:"
    echo "  pip3 install cryptography colorama"
    echo
fi

echo
echo "======================================="
echo "Setup complete!"
echo
echo "To run the VPN:"
echo "  GUI Mode:    python3 fosen_vpn.py"
echo "  Server Mode: python3 fosen_vpn.py server"
echo "  Client Mode: python3 fosen_vpn.py client"
echo "  Help:        python3 fosen_vpn.py help"
echo "======================================="