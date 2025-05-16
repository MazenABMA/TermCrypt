#!/bin/bash

PORT=${1:-5555}
PASSWORD=$2
SAVE_DIR="received_files"
mkdir -p "$SAVE_DIR"

if [[ -z "$PASSWORD" ]]; then
  echo "Usage: $0 [port] <password>"
  exit 1
fi

echo "[*] Waiting for encrypted file on port $PORT..."

# Kill watcher in background
(
  while true; do
    read -rp "[command]> " CMD
    if [[ "$CMD" == "/kill" ]]; then
      echo "[*] Kill command received. Terminating receiver..."
      pkill -P $$  # Kills all child processes of this script
      kill $$      # Kill this script
    fi
  done
) &

# Store watcher PID in case needed
WATCHER_PID=$!

# Start receiving
openssl s_server -quiet -accept "$PORT" -cert config/server.pem | \
  openssl enc -d -aes-256-cbc -pbkdf2 -pass pass:"$PASSWORD" | \
  tar xz -C "$SAVE_DIR"

echo "[+] File received and decrypted in $SAVE_DIR/"
echo "[*] Receiver stopped."

# Kill background watcher (in case script exits normally)
kill $WATCHER_PID 2>/dev/null
