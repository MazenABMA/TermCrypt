# TermCrypt
TermCrypt is a real-time chat and file sharing system with end-to-end encryption. It leverages socket programming and secure encryption to provide private communication channels between clients over a network. Built with a user-friendly GUI for seamless chatting and encrypted file transfer.









Features

    Real-time encrypted messaging using a shared secret key

    Secure file sharing with password protection

    Client-server architecture based on socket communication

    Chat and file transfer in separate tabs

    Graceful connection and session handling

    Chat logging and message display

    Simple, lightweight GUI built with Tkinter

   Support multi-client group chat with secure sessions







Getting Started
Prerequisites

    Python 3.7+

    Bash shell scripts for client/server (included)

    Required Python packages (Tkinter comes preinstalled with Python)

Installation

    Clone the repo:

git clone https://github.com/MazenABMA/TermCrypt.git
cd TermCrypt

Make scripts executable:

chmod +x chat_client.sh file_send.sh file_recv.sh

Run the GUI:

    python3 Client.py

and run the chat_server.sh !  or if want to run multi clients then run the multi.py
Usage

    Enter the server IP and port to connect

    Type messages in the chat tab and send them

    Use the file tab to send or receive files securely

    Communication is encrypted end-to-end using a secret key

Architecture

    GUI: Tkinter-based interface for chat and file sharing

    Chat: Uses subprocess to run encrypted chat client bash script

    File Sharing: Secure file send/receive via password-protected scripts , to run run the SendFile.py

    Encryption: (To be implemented) AES or other symmetric encryption for message confidentiality

Roadmap

    Add native encryption/decryption within GUI

    Implement key exchange protocols for dynamic secret keys

        Add logging and error handling improvements