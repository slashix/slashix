from netmiko import ConnectHandler
from netmiko import NetMikoTimeoutException, SSHException

def determine_device_type(ip, username, password, method='ssh'):
    try:
        device = {
            'device_type': 'cisco_ios',
            'ip': ip,
            'username': username,
            'password': password,
            'method': method,
        }
        net_connect = ConnectHandler(**device)
        prompt = net_connect.find_prompt()
        version = net_connect.send_command("show version")
        if '>' in prompt and '<' in prompt:
            device_type = 'huawei'
        elif '>' in prompt or '#' in prompt:
            if "Cisco" in version:
                device_type = 'cisco_ios'
            else:
                device_type = 'eltex'
        else:
            device_type = 'unknown'
        return device_type
    except (NetMikoTimeoutException, SSHException) as e:
        if method == 'ssh':
            return determine_device_type(ip, username, password, method='telnet')
        else:
            return f"Error: {e}"

# Example of usage
ip = '192.168.1.1'
username = 'admin'
password = 'password'
device_type = determine_device_type(ip, username, password)
print(f'Device type: {device_type}')
