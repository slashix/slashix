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
