from netmiko import ConnectHandler
from tqdm import tqdm

def send_config_commands(device, command_list):
    try:
        with ConnectHandler(**device) as ssh:
            ssh.enable()

            # Инициализируем прогресс-бар
            pbar = tqdm(total=len(command_list))

            # Выполняем каждую команду из списка
            for command in command_list:
                ssh.send_config_set(command, delay_factor=2)
                # Обновляем прогресс-бар
                pbar.update(1)

            # Закрываем прогресс-бар
            pbar.close()
    except Exception as error:
        print(error)
        
==================================
import math
from netmiko import ConnectHandler
from tqdm import tqdm

def send_config_commands(device, command_list):
    try:
        with ConnectHandler(**device) as ssh:
            ssh.enable()

            # Инициализируем прогресс-бар
            pbar = tqdm(total=len(command_list))

            # Разбиваем список команд на блоки размером в 500 строк
            chunk_size = 500
            chunks = [command_list[i:i+chunk_size] for i in range(0, len(command_list), chunk_size)]

            # Выполняем каждый блок команд
            for chunk in chunks:
                ssh.send_config_set(chunk, delay_factor=2)
                # Обновляем прогресс-бар
                pbar.update(len(chunk))

            # Закрываем прогресс-бар
            pbar.close()
    except Exception as error:
        print(error)
