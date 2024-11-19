import subprocess
import os

def visualize_graph(plantuml_path, puml_file):
    """
    Визуализирует граф с помощью PlantUML.
    :param plantuml_path: Путь к программе PlantUML.
    :param puml_file: Путь к файлу PlantUML.
    :return: Путь к сгенерированному изображению или None, если произошла ошибка.
    """
    subprocess.run([plantuml_path, puml_file])
    output_file = puml_file.replace('.puml', '.png')
    if os.path.exists(output_file):
        return output_file
    return None
