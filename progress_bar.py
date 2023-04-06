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


==========================
from netmiko import ConnectHandler
from tqdm import tqdm

def send_config_commands(device, command_list):
    try:
        with ConnectHandler(**device) as ssh:
            ssh.enable()

            # Делим список команд на блоки по 500+ строк
            block_list = []
            block = []
            for command in command_list:
                block.append(command)
                if "commit" in command:
                    block_list.append(block)
                    block = []
            if block:
                block_list.append(block)

            # Инициализируем прогресс-бар
            pbar = tqdm(total=len(command_list))

            # Выполняем каждый блок команд
            for block in block_list:
                block_len = len(block)
                commands_str = "\n".join(block)
                ssh.send_config_set(commands_str, delay_factor=2)
                # Обновляем прогресс-бар
                pbar.update(block_len)

            # Закрываем прогресс-бар
            pbar.close()

    except Exception as error:
        print(error)
======================================
def sendconfigcommands(devicearg, commandsarg):
    if cont != “Y”:
        sys.exit(“действие отменено пользователем”)
    try:
        with ConnectHandler(**devicearg) as ssh:
            ssh.enable()
            # Делим список команд на блоки по 500+ строк
            blocklist = []
            block = []
            for command in commandsarg:
                block.append(command)
                if “commit” in command:
                    blocklist.append(block)
                    block = []
            if block:
                blocklist.append(block)
            # Инициализируем прогресс-бар
            pbar = tqdm(total=len(commandsarg))
            # Выполняем каждый блок команд
            for block in blocklist:
                block_len = len(block)
                with ConnectHandler(**devicearg) as ssh_block:
                    ssh_block.enable()
                    commandsstr = “\n”.join(block)
                    ssh_block.sendconfigset(commandsstr, exitconfigmode=False)
                # Обновляем прогресс-бар
                pbar.update(block_len)
            # Закрываем прогресс-бар
            pbar.close()
    except netmiko.NetMikoAuthenticationException as err:
        print(err)
    except netmiko.NetMikoTimeoutException as err:
        print(err)
    except netmiko.exceptions.ReadTimeout as err:
        print(err, “Can't print the output”)

