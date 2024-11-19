import argparse
from config import read_config
from git_parser import get_commits
from plantuml_generator import generate_plantuml
from visualizer import visualize_graph

def main():
    parser = argparse.ArgumentParser(description="Граф зависимостей коммитов git")
    parser.add_argument('config', help="Путь к конфигурационному файлу TOML")
    args = parser.parse_args()

    # Читаем конфигурацию
    config = read_config(args.config)

    # Получаем данные о коммитах
    commits = get_commits(config['repository']['path'], config['repository']['since'])

    # Генерируем PlantUML
    puml_file = 'graph.puml'
    generate_plantuml(commits, puml_file)

    # Визуализируем граф
    output = visualize_graph(config['visualizer']['path'], puml_file)
    if output:
        print(f"Граф сохранен: {output}")
    else:
        print("Ошибка при визуализации графа.")

if __name__ == "__main__":
    main()
