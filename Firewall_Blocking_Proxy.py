import socket
import threading
import time
import os
from dnslib import DNSRecord, DNSHeader, RCODE

BLACKLIST_FILE = "domain.txt"
UPSTREAM_DNS = ("8.8.8.8", 53)  # or your preferred DNS
RELOAD_INTERVAL = 10  # seconds to reload blacklist file dynamically

blacklist = set()

def load_blacklist():
    """
    Load blacklisted domains from file.
    """
    global blacklist
    if os.path.exists(BLACKLIST_FILE):
        with open(BLACKLIST_FILE, "r") as f:
            blacklist = set(line.strip().lower() for line in f if line.strip())
        print(f"[+] Blacklist loaded: {len(blacklist)} domains.")
    else:
        blacklist = set()

def blacklist_reloader():
    """
    Background thread to reload blacklist file periodically.
    """
    while True:
        load_blacklist()
        time.sleep(RELOAD_INTERVAL)

def handle_dns_request(data, addr, sock):
    """
    Handle incoming DNS requests.
    """
    try:
        request = DNSRecord.parse(data)
        qname = str(request.q.qname).rstrip('.').lower()
        print(f"[*] Query: {qname}")

        for domain in blacklist:
            if domain in qname:
                print(f"[!] BLOCKED: {qname}")
                reply = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)
                reply.header.rcode = RCODE.NXDOMAIN
                sock.sendto(reply.pack(), addr)
                return

        # Forward to real DNS
        proxy_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        proxy_sock.sendto(data, UPSTREAM_DNS)
        proxy_sock.settimeout(5)
        response_data, _ = proxy_sock.recvfrom(4096)
        sock.sendto(response_data, addr)

    except Exception as e:
        print(f"[!] Error handling DNS request: {e}")

def start_dns_proxy():
    """
    Start the DNS firewall proxy server.
    """
    load_blacklist()
    threading.Thread(target=blacklist_reloader, daemon=True).start()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", 53))  # listen on UDP port 53

    print("[*] DNS Firewall Proxy running on UDP port 53...")

    while True:
        try:
            data, addr = sock.recvfrom(512)
            threading.Thread(target=handle_dns_request, args=(data, addr, sock)).start()
        except KeyboardInterrupt:
            print("\n[+] Stopping DNS firewall.")
            break
        except Exception as e:
            print(f"[!] Listener error: {e}")

if __name__ == "__main__":
    start_dns_proxy()