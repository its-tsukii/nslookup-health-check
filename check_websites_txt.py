import socket
import requests
import ssl
from urllib.parse import urlparse

# Input and output files
WEBSITE_LIST_FILE = "websites.txt"
OUTPUT_FILE = "website_check_log.txt"

def read_websites(file_path):
    with open(file_path, 'r') as file:
        # Add https:// if not present
        return [("https://" + line.strip() if not line.strip().startswith(('http://', 'https://')) else line.strip()) for line in file if line.strip()]

def check_dns(domain):
    try:
        ip = socket.gethostbyname(domain)
        return ip
    except socket.gaierror:
        return None

def check_http(site):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
    }
    try:
        response = requests.get(site, headers=headers, timeout=5)
        if response.status_code == 200:
            return "HTTP OK"
        else:
            return f"HTTP Error: Status Code {response.status_code}"
    except requests.RequestException as e:
        return f"HTTP Error: {e}"

def check_ssl(domain):
    context = ssl.create_default_context()
    try:
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                ssock.getpeercert()
                return "SSL Valid"
    except Exception as e:
        return f"SSL Error: {e}"

def main():
    websites = read_websites(WEBSITE_LIST_FILE)

    with open(OUTPUT_FILE, "w") as log_file:
        for i, site in enumerate(websites, start=1):
            parsed = urlparse(site)
            domain = parsed.netloc or parsed.path

            result = ""
            ip = check_dns(domain)
            if not ip:
                result = "DNS Failed"
            else:
                http_status = check_http(site)
                if http_status != "HTTP OK":
                    result = http_status
                elif site.startswith("https://"):
                    ssl_status = check_ssl(domain)
                    result = ssl_status if "Error" in ssl_status else "working"
                else:
                    result = "working"

            log_line = f"{i}. {site} --> {result}"
            print(log_line)
            log_file.write(log_line + "\n")

    print(f"\nResults written to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
