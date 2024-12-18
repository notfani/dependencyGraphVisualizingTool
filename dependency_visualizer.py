import os
import zlib
import struct
import unittest
import subprocess
import os
from datetime import datetime, timezone
import toml


'''def load_config(config_path="config.toml"):
    """
    Читает конфигурационный файл в формате TOML.
    """
    try:
        with open(config_path, "r") as file:
            config = toml.load(file)
        return config
    except FileNotFoundError:
        print(f"Ошибка: Конфигурационный файл {config_path} не найден.")
        return None
    except toml.TomlDecodeError as e:
        print(f"Ошибка в синтаксисе файла {config_path}: {e}")
        return None

if config:
    plantuml_path = config["general"]["plantuml_path"]
    repo_path = config["general"]["repository_path"]
    since_date = config["general"]["since_date"]

    print(f"PlantUML путь: {plantuml_path}")
    print(f"Путь до репозитория: {repo_path}")
    print(f"Смотреть коммиты с даты: {since_date}")'''


PLANTUML_JAR_PATH = "plantuml.jar"
# Если timestamp — объект datetime
timestamp = datetime.now()  # Пример объекта datetime (текущая дата и время)
commit_date = timestamp.astimezone(timezone.utc)  # Преобразование во временную зону UTC

print("Commit Date (UTC):", commit_date)

# Функция для чтения объектов коммитов
def read_commit_object(commit_hash, git_dir):
    # Формируем путь к объекту
    object_dir = os.path.join(git_dir, "objects", commit_hash[:2])
    object_file = os.path.join(object_dir, commit_hash[2:])

    # Читаем сжатыми данные из файла
    with open(object_file, "rb") as f:
        compressed_data = f.read()

    # Декомпрессируем данные
    decompressed_data = zlib.decompress(compressed_data)

    # Извлекаем тип объекта и данные
    obj_type, obj_data = decompressed_data.split(b' ', 1)
    if obj_type != b'commit':
        raise ValueError(f"Expected commit object, but got {obj_type.decode()}")

    return obj_data


# Функция для извлечения информации из объекта коммита
def parse_commit(commit_data):
    # Разбейте строки из объекта коммита
    lines = commit_data.split(b"\n")
    if len(lines) < 2:
        raise ValueError("Invalid commit data. Too few lines.")

    # Ищем строку автора
    author_line = None
    parents = []
    for line in lines:
        if line.startswith(b"author"):
            author_line = line
        elif line.startswith(b"parent"):
            parent_hash = line.split()[1].decode()
            parents.append(parent_hash)

    if not author_line:
        raise ValueError("Invalid commit data. 'author' line missing.")

    # Проверяем правильность формата строки автора
    author_data = author_line.split(b" ", 1)[-1]
    if not author_line:
        raise ValueError("Invalid commit data. 'author' line missing.")

    timestamp = None  # Убедитесь, что у переменной есть значение по умолчанию
    try:
        timestamp = int(author_line.split()[-1].decode())  # Парсим временную метку
    except ValueError:
        raise ValueError("Invalid commit timestamp.")

    commit_date = datetime.utcfromtimestamp(timestamp)
    return commit_date, parents




# Чтение коммитов из репозитория
def get_commits_from_repo(repo_path, since_date):
    git_dir = os.path.join(repo_path, ".git")
    objects_dir = os.path.join(git_dir, "objects")

    commits = []
    for root, dirs, files in os.walk(objects_dir):
        for file in files:
            object_path = os.path.join(root, file)

            try:
                with open(object_path, "rb") as f:
                    decompressed_data = zlib.decompress(f.read())
                    if decompressed_data.startswith(b"commit"):
                        commit_date, parents = parse_commit(decompressed_data)
                        if commit_date >= since_date:
                            hash_value = os.path.basename(object_path)  # Берём имя файла (хэш)
                            commits.append({
                                "hash": hash_value,
                                "parents": parents,
                                "date": commit_date
                            })
            except Exception as e:
                print(f"Error processing file {object_path}: {e}")

    return commits




# Формирование графа в формате PlantUML


def build_plantuml_graph(commits, output_puml_path="graph.puml", output_image_path="graph.png"):
    # Генерация графа PlantUML
    graph = "@startuml\n"
    for commit in commits:
        for parent in commit["parents"]:
            graph += f'"{parent}" --> "{commit["hash"]}"\n'
        graph += f'"{commit["hash"]}"\n'
    graph += "@enduml\n"

    # Сохранение .puml файла
    with open(output_puml_path, "w") as puml_file:
        puml_file.write(graph)

    # Генерация изображения через PlantUML
    try:
        subprocess.run(
            ["java", "-jar", PLANTUML_JAR_PATH, output_puml_path, "-o", os.path.dirname(output_image_path)],
            check=True
        )
    except FileNotFoundError:
        print("Ошибка: файл plantuml.jar не найден. Убедитесь, что он находится в вашей системе.")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при создании изображения: {e}")

    # Возвращаем итоговый граф
    return graph


# Сохранение графа в файл
def save_graph_to_file(graph, output_path):
    print(f"Граф для сохранения:\n{graph}")
    with open(output_path, "w") as f:
        f.write(graph)



# Главная функция
def main(repo_path, since_date):
    commits = get_commits_from_repo(repo_path, since_date)
    graph = build_plantuml_graph(commits)
    save_graph_to_file(graph, "graph.puml")


# Пример для тестирования
if __name__ == "__main__":
    main("C:/Users/Богдан/GitHub/BananaNinja_Website", datetime(2024, 1, 9))  # Пример использования
