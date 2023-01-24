from netmiko import ConnectHandler
from netmiko import NetMikoTimeoutException, SSHException

def determine_device_type(ip, username, password):
    """
    Function to determine the type of network device
    :param ip: IP address of the device
    :param username: username for login
    :param password: password for login
    :return: type of device ('cisco_ios', 'eltex', 'huawei') or error message
    """
    device = {
        'device_type': 'cisco_ios',
        'ip': ip,
        'username': username,
        'password': password,
    }
    try:
        net_connect = ConnectHandler(**device)
    except (NetMikoTimeoutException, SSHException):
        device['device_type'] = 'cisco'
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

# Example of usage
ip = '192.168.1.1'
username = 'admin'
password = 'password'
device_type = determine_device_type(ip, username, password)
print(f'Device type: {device_type}')
