import netmiko
import getpass
from concurrent.futures import ThreadPoolExecutor

# Функция для подключения к устройству
def connect_to_device(ip):
    try:
        # Подключение к устройству через SSH
        device = netmiko.ConnectHandler(ip=ip, username=username, password=password, device_type="cisco_ios")
        print(f"Успешно подключились к {ip} через SSH")
    except:
        try:
            # Подключение к устройству через Telnet
            device = netmiko.ConnectHandler(ip=ip, username=username, password=password, device_type="cisco_ios_telnet")
            print(f"Успешно подключились к {ip} через Telnet")
        except:
            print(f"Не удалось подключиться к {ip}")
            return

    # Определяем тип устройства и выбираем файл с командами
    if "cisco" in device.device_type:
        with open("cisco_cfg.txt") as f:
            commands = f.read().splitlines()
    elif "huawei" in device.device_type:
        with open("huawei_cfg.txt") as f:
            commands = f.read().splitlines()

    # Отправляем команды на устройство
    output = device.send_config_set(commands)
    print(output)

    # Закрываем соединение
    device.disconnect()

# Запрашиваем логин и пароль
username = input("Введите логин: ")
password = getpass.getpass("Введите пароль: ")

# Открываем файл со списком IP-адресов устройств
with open("ip_list.txt") as f:
    ip_list = f.read().splitlines()

# Используем ThreadPoolExecutor для параллельного подключения к устройствам
with ThreadPoolExecutor() as executor:
    executor.map(connect_to_device, ip_list)
