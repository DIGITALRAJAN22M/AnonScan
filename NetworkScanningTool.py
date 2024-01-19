import socket

DEVELOPER = "ANONDGR"

# ANSI escape codes for text color
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

def display_developer_info():
    print(GREEN + DEVELOPER.center(80, '=') + RESET)

def is_host_active(ip_address):
    try:
        # Attempt to create a socket connection
        socket.create_connection((ip_address, 80), timeout=1)
        return True
    except (socket.timeout, socket.error):
        return False

def get_domain_name(ip_address):
    try:
        domain_name, _, _ = socket.gethostbyaddr(ip_address)
        return domain_name
    except socket.herror:
        return "Unknown"

def scan_ports(ip_address, start_port, end_port):
    open_ports = []
    closed_ports = []

    total_ports = end_port - start_port + 1
    scanned_ports = 0

    print(f"Scanning ports {start_port} to {end_port} on {ip_address} ({get_domain_name(ip_address)})...")

    for port in range(start_port, end_port + 1):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)

        result = sock.connect_ex((ip_address, port))

        if result == 0:
            open_ports.append(port)
        else:
            closed_ports.append(port)

        sock.close()

        scanned_ports += 1
        remaining_ports = total_ports - scanned_ports

        print(f"Progress: {scanned_ports}/{total_ports} ports scanned. {remaining_ports} ports remaining.", end='\r')

    print("\nScan completed.")

    return open_ports, closed_ports

def get_service_version(ip_address, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            s.connect((ip_address, port))
            s.sendall(b'VERSION_REQUEST')  # You may need to adjust this based on the expected service behavior
            data = s.recv(1024)
        return data.decode('utf-8') if data else "Version not available"
    except (socket.timeout, socket.error):
        return "Version not available"

def get_services(ip_address, open_ports):
    services = []
    for port in open_ports:
        try:
            service_name = socket.getservbyport(port)
            service_version = get_service_version(ip_address, port)
            services.append((port, service_name, service_version))
        except OSError:
            services.append((port, "Unknown", "Version not available"))

    return services

def main():
    display_developer_info()

    ip_address = input("Enter the IP address to scan: ")

    if is_host_active(ip_address):
        print(GREEN + "Host is active." + RESET)
    else:
        print(RED + "Host is not active." + RESET)
        return

    start_port = int(input("Enter the starting port: "))
    end_port = int(input("Enter the ending port: "))

    open_ports, closed_ports = scan_ports(ip_address, start_port, end_port)

    print("\nOpen ports:")
    for port in open_ports:
        print(GREEN + f"Port {port} is open." + RESET)

    print("\nClosed ports:")
    for port in closed_ports:
        print(RED + f"Port {port} is closed." + RESET)

    services = get_services(ip_address, open_ports)
    print("\nServices running on open ports:")
    print("{:<10} {:<20} {:<20}".format("Port", "Service", "Version"))
    for port, service, version in services:
        print("{:<10} {:<20} {:<20}".format(port, service, version))

if __name__ == "__main__":
    main()
