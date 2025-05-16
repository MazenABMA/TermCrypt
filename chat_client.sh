#!/bin/bash

SERVER_IP=$1
PORT=${2:-4443}

if [ -z "$SERVER_IP" ]; then
  echo "Usage: $0 <server_ip> [port]"
  exit 1
fi

NICK="Anonymous"
PIPE="/tmp/termcrypt_$$"

# Create named pipe
mkfifo "$PIPE"

# Start OpenSSL client reading from pipe (background)
openssl s_client -quiet -connect "$SERVER_IP:$PORT" -no_ign_eof < "$PIPE" &
OPENSSL_PID=$!

# Open pipe for writing (fd 3), won't block because OpenSSL is reading
exec 3> "$PIPE"

# Cleanup on exit
cleanup() {
  rm -f "$PIPE"
  kill $OPENSSL_PID 2>/dev/null
  exec 3>&-
  echo "Disconnected."
  exit 0
}
trap cleanup INT TERM

echo "[*] Connected to $SERVER_IP:$PORT"
echo "[*] Type /help for commands. Press Ctrl+C to exit."

while true; do
    read -rp "> " MSG

    if [[ "$MSG" == /exit ]]; then
        echo "Exiting..."
        break

    elif [[ "$MSG" == /help ]]; then
        echo -e "/nick <name>   → set your display name"
        echo -e "/send <file>   → send encrypted file"
        echo -e "/exit          → exit chat"
        continue

    elif [[ "$MSG" =~ ^/nick[[:space:]]+(.+) ]]; then
        NICK="${BASH_REMATCH[1]}"
        echo "[*] Nickname set to: $NICK"
        continue

    elif [[ "$MSG" =~ ^/send[[:space:]]+(.+) ]]; then
        FILE="${BASH_REMATCH[1]}"
        if [[ ! -f "$FILE" ]]; then
            echo "[!] File not found: $FILE"
        else
            echo "[*] Sending file: $FILE"
            ./file_send.sh "$SERVER_IP" 5555 "$FILE" mysecret &
            echo "[INFO] $NICK sent file '$FILE'" >&3
        fi
        continue

    else
        # Send normal chat message
        echo "[$NICK@TermCrypt]> $MSG" >&3
    fi
done

cleanup
