#!/bin/bash

SERVER_IP=$1
PORT=${2:-5555}
FILE=$3
PASSWORD=$4

if [[ -z "$SERVER_IP" || -z "$FILE" || -z "$PASSWORD" ]]; then
  echo "Usage: $0 <server_ip> [port] <file_path> <password>"
  exit 1
fi

if [[ ! -e "$FILE" ]]; then
  echo "[!] File '$FILE' not found!"
  exit 1
fi

echo "[*] Sending $FILE to $SERVER_IP:$PORT ..."

# Strip full path to avoid extraction issues
tar cz -C "$(dirname "$FILE")" "$(basename "$FILE")" | \
openssl enc -aes-256-cbc -salt -pbkdf2 -pass pass:"$PASSWORD" | \
openssl s_client -quiet -connect "$SERVER_IP:$PORT" -no_ign_eof

if [[ $? -eq 0 ]]; then
  echo "[+] File sent securely."
else
  echo "[!] File send failed!"
fi
