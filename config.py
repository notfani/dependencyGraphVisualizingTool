import toml

def read_config(config_path):
    """
    Читает конфигурационный файл TOML.
    :param config_path: Путь к конфигурационному файлу.
    :return: Словарь с конфигурацией.
    """
    with open(config_path, 'r') as file:
        return toml.load(file)
