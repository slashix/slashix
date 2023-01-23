from netmiko import ConnectHandler
from concurrent.futures import ThreadPoolExecutor

# Define a list of Cisco switch IP addresses
switch_ips = ["192.168.1.1", "192.168.1.2", "192.168.1.3"]

# Define the connection parameters
cisco_switch = {
    "device_type": "cisco_ios",
    "username": "admin",
    "password": "password",
}

def show_version(ip):
    cisco_switch["host"] = ip
    net_connect = ConnectHandler(**cisco_switch)
    output = net_connect.send_command("show version")
    print(f"Output for {ip}: {output}")
    net_connect.disconnect()

with ThreadPoolExecutor() as executor:
    results = [executor.submit(show_version, ip) for ip in switch_ips]
