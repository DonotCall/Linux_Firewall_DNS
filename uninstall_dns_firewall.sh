#!/bin/bash

echo "[*] Stopping DNS Firewall service..."
sudo systemctl stop dns_firewall.service
sudo systemctl disable dns_firewall.service
sudo rm /etc/systemd/system/dns_firewall.service

echo "[*] Enabling systemd-resolved again..."
sudo systemctl enable systemd-resolved
sudo systemctl start systemd-resolved

echo "[*] Restoring default DNS (8.8.8.8)"
echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

echo "[+] DNS Firewall fully removed. System back to normal."
