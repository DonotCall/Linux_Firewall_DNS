#!/bin/bash

echo "[*] Disabling systemd-resolved..."
sudo systemctl stop systemd-resolved
sudo systemctl disable systemd-resolved

echo "[*] Setting local DNS to 127.0.0.1"
echo "nameserver 127.0.0.1" | sudo tee /etc/resolv.conf

echo "[*] Enabling and starting DNS Firewall service"
sudo systemctl daemon-reload
sudo systemctl enable dns_firewall.service
sudo systemctl start dns_firewall.service

echo "[+] DONE. DNS Firewall is running. All DNS queries pass through it."