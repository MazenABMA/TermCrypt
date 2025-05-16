#!/bin/bash

CERT="config/server.pem"
PORT=4443
LOGFILE="logs/chat.log"

mkdir -p logs

echo "[*] Starting TermCrypt chat server on port $PORT..."
echo "[*] Logging to $LOGFILE"
echo "[*] Waiting for client to connect..."

openssl s_server -quiet -accept "$PORT" -cert "$CERT" | tee -a "$LOGFILE"
