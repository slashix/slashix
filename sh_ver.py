import netmiko # импорт модуля netmiko
import concurrent.futures # импорт модуля concurrent.futures

# Определяем список IP-адресов коммутаторов
switch_ips = ["192.168.1.1", "192.168.1.2", "192.168.1.3"]

# Определяем параметры соединения
switch = {
    "device_type": "auto", # автоопределение типа устройства
    "username": "admin", # имя пользователя
    "password": "password", # пароль
}

def run_commands(ip): # функция для выполнения команд
    switch["host"] = ip # задаем IP-адрес устройства для подключения
    net_connect = ConnectHandler(**switch) # создаем соединение с устройством
    device_type = net_connect.device_type # определяем тип устройства
    if device_type == "cisco_ios": # если тип устройства Cisco
        with open("cisco.txt", "r") as file: # открываем файл с командами
            commands = file.read().splitlines() # читаем команды из файла и преобразуем их в список
    elif device_type == "huawei": # если тип устройства Huawei
        with open("huawei.txt", "r") as file: # открываем файл с командами
            commands = file.read().splitlines() # читаем команды из файла и преобразуем их в список
    else:
        print(f"{ip} is unsupported device")
        return
    for command in commands: # для каждой команды из списка
        output = net_connect.send_command(command) # выполняем команду
        print(f"Вывод для команды {command} на {ip}: {output}") # выводим полученную информацию
    net_connect.disconnect() # закрываем соединение

with ThreadPoolExecutor() as executor: # создаем пул потоков
    results = [executor.submit(run_commands, ip) for ip in switch_ips] # для каждого IP вызываем функцию run_commands
