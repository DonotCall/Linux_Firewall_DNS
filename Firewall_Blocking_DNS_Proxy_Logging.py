import socket
import threading
import time
import os
import sys
import subprocess
from dnslib import DNSRecord, DNSHeader, RCODE
from datetime import datetime

BLACKLIST_FILE = "domain.txt"
UPSTREAM_DNS = ("8.8.8.8", 53)
RELOAD_INTERVAL = 10
LOG_FILE = "dns_firewall.log"

blacklist = set()

def log_event(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}"
    print(entry)
    with open(LOG_FILE, "a") as f:
        f.write(entry + "\n")

def check_systemd_resolved():
    try:
        result = subprocess.run(['systemctl', 'is-active', 'systemd-resolved'],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.stdout.decode().strip() == 'active':
            log_event("[WARNING] systemd-resolved is running! Stop it to avoid port 53 conflicts.")
    except Exception as e:
        log_event(f"[INFO] Could not check systemd-resolved: {e}")

def load_blacklist():
    global blacklist
    if os.path.exists(BLACKLIST_FILE):
        with open(BLACKLIST_FILE, "r") as f:
            blacklist = set(line.strip().lower() for line in f if line.strip())
        log_event(f"[+] Blacklist loaded: {len(blacklist)} domains.")
    else:
        blacklist = set()
        log_event("[+] No blacklist file found. Running with empty blacklist.")

def blacklist_reloader():
    while True:
        load_blacklist()
        time.sleep(RELOAD_INTERVAL)

def handle_dns_request(data, addr, sock):
    try:
        request = DNSRecord.parse(data)
        qname = str(request.q.qname).rstrip('.').lower()
        log_event(f"[*] Query: {qname} from {addr[0]}")

        for domain in blacklist:
            if domain in qname:
                log_event(f"[BLOCKED] {qname} matched blacklist entry '{domain}'")
                reply = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)
                reply.header.rcode = RCODE.NXDOMAIN
                sock.sendto(reply.pack(), addr)
                return

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as proxy_sock:
            proxy_sock.sendto(data, UPSTREAM_DNS)
            proxy_sock.settimeout(5)
            response_data, _ = proxy_sock.recvfrom(4096)
            sock.sendto(response_data, addr)

    except Exception as e:
        log_event(f"[ERROR] Handling DNS request: {e}")

def start_dns_firewall():
    check_systemd_resolved()
    load_blacklist()
    threading.Thread(target=blacklist_reloader, daemon=True).start()

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("0.0.0.0", 53))
        log_event("[*] DNS Firewall running on UDP port 53... (Ctrl+C to stop)")

        while True:
            try:
                data, addr = sock.recvfrom(512)
                threading.Thread(target=handle_dns_request, args=(data, addr, sock), daemon=True).start()
            except Exception as e:
                log_event(f"[ERROR] Listener: {e}")

    except PermissionError:
        log_event("[FATAL] Permission denied. Run as root: 'sudo python3 dns_firewall_linux.py'")
    except OSError as e:
        log_event(f"[FATAL] Could not bind to port 53: {e}")
    except KeyboardInterrupt:
        log_event("\n[+] Stopping DNS Firewall.")
        sys.exit(0)

if __name__ == "__main__":
    start_dns_firewall()
