def generate_plantuml(commits, output_path):
    """
    Генерирует граф зависимостей в формате PlantUML.
    :param commits: Список коммитов.
    :param output_path: Путь для сохранения файла PlantUML.
    """
    lines = ['@startuml', 'digraph G {']
    for commit in commits:
        for parent in commit['parents']:
            lines.append(f'  "{commit["hash"]}" -> "{parent}"')
    lines.append('}')
    lines.append('@enduml')
    with open(output_path, 'w') as file:
        file.write('\n'.join(lines))
