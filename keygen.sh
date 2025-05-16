#!/bin/bash

CERT_DIR="config"
mkdir -p "$CERT_DIR"

echo "[*] Generating private key and self-signed certificate..."

openssl req -x509 -newkey rsa:2048 -keyout "$CERT_DIR/server.key" -out "$CERT_DIR/server.crt" -days 365 -nodes -subj "/CN=TermCrypt Server"

cat "$CERT_DIR/server.key" "$CERT_DIR/server.crt" > "$CERT_DIR/server.pem"

echo "[+] Certificate and key saved in $CERT_DIR/server.pem"
