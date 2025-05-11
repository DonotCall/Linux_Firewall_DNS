# 📦 DNS Firewall for Linux

### An Automated Local DNS Filtering Firewall using Python & Systemd

## ✅ Project Overview

This project builds a **lightweight DNS firewall** for Linux machines.
It runs as a **systemd service**, automatically intercepts all DNS queries, blocks unwanted domains based on a live blacklist (`domain.txt`), and forwards safe queries to real upstream DNS (default: Google DNS `8.8.8.8`).

Ideal for:

* Home lab / Raspberry Pi network firewall
* Linux workstation DNS filter
* Educational research project
* Malware & phishing domain blocking

## ✅ Features

* Runs automatically at boot (`systemd`)
* Live blacklist reloading every 10 sec
* Logs all DNS requests (`dns_firewall.log`)
* Easy setup and uninstall scripts
* Supports any Linux distro (Debian, Ubuntu, Kali, Fedora, Arch etc.)

## ✅ Folder Structure

dnsfirewall/
│
├── dns_firewall_linux.py       → main Python firewall
├── domain.txt                  → list of blocked domains
├── setup_dns_firewall.sh       → script to setup + start firewall
├── uninstall_dns_firewall.sh   → script to uninstall + restore DNS
└── /etc/systemd/system/
    └── dns_firewall.service    → systemd service file (manual step)
---

## ✅ Requirements

* Linux machine (physical or virtual)
* Python 3.6+
* Root (sudo) access

Install dependencies:

sudo apt update
sudo apt install python3 python3-pip -y
pip3 install dnslib


## ✅ Usage Guide

### 1️⃣ Place all files inside folder: `dnsfirewall`

### 2️⃣ Edit systemd service and Copy to the mentioned path


👉 Replace `/home/ubuntu` with your actual full path.

Save as:

/etc/systemd/system/dns_firewall.service

### 3️⃣ Run setup script

cd ~/dnsfirewall
chmod +x setup_dns_firewall.sh
./setup_dns_firewall.sh

✅ Your DNS firewall is now active.

### 4️⃣ Test it

nslookup facebook.com 127.0.0.1     # Should be blocked (NXDOMAIN)
nslookup google.com 127.0.0.1       # Should be allowed

# Logs:

tail -f ~/dnsfirewall/dns_firewall.log


## ✅ Example domain.txt

facebook.com
ads.google.com
malware-site.com

👉 Add any domain name (one per line) to block it.
👉 No restart needed. File reloads every 10 seconds.


## ✅ Uninstall (fully restore system)

cd ~/dnsfirewall
chmod +x uninstall_dns_firewall.sh
./uninstall_dns_firewall.sh

Restores:

* DNS resolver back to `8.8.8.8`
* Removes firewall service
* Re-enables `systemd-resolved`

---

## ✅ Safety Tip

To prevent automatic overwrite of `/etc/resolv.conf`:

sudo chattr +i /etc/resolv.conf

Remove lock:

sudo chattr -i /etc/resolv.conf

---

## 🎉 Congratulations!

You now have a fully working **Python DNS firewall service** ready for lab use, research, or home network protection 🚀


## ✅ Credits

Developed with help of:

* Python 3
* dnslib library
* systemd


# END
