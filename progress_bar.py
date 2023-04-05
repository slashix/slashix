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
            for i, chunk in enumerate(chunks):
                if i == len(chunks) - 1 and len(chunk) < chunk_size:
                    # Если это последний блок и он меньше 500 строк, то отправляем его целиком
                    ssh.send_config_set(chunk, delay_factor=2)
                    # Обновляем прогресс-бар
                    pbar.update(len(chunk))
                else:
                    # Иначе отправляем блок размером в 500 строк
                    ssh.send_config_set(chunk[:chunk_size], delay_factor=2)
                    # Обновляем прогресс-бар
                    pbar.update(chunk_size)

            # Закрываем прогресс-бар
            pbar.close()
    except Exception as error:
        print(error)

        
  ====================================

from netmiko import ConnectHandler
from tqdm import tqdm

def send_config_commands(device, command_list):
    try:
        with ConnectHandler(**device) as ssh:
            ssh.enable()

            # Разбиваем список команд на блоки по 500+ строк
            block_size = 500
            command_blocks = [command_list[i:i+block_size] for i in range(0, len(command_list), block_size)]

            # Инициализируем прогресс-бар
            pbar = tqdm(total=len(command_list))

            # Выполняем каждый блок команд
            for commands in command_blocks:
                ssh.send_config_set(commands, delay_factor=2)
                # Обновляем прогресс-бар
                pbar.update(len(commands))

            # Закрываем прогресс-бар
            pbar.close()
    except Exception as error:
        print(error)

