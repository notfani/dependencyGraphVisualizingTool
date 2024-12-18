import unittest
import zlib
from datetime import datetime
from io import StringIO
import os

from dependency_visualizer import (
    read_commit_object,
    parse_commit,
    get_commits_from_repo,
    build_plantuml_graph,
    save_graph_to_file,
)


class TestDependencyVisualizer(unittest.TestCase):
    def setUp(self):
        """
        Настраиваем тестовый репозиторий с несколькими объектами коммитов.
        """
        self.repo_path = "test_repo"
        self.git_dir = os.path.join(self.repo_path, ".git")
        os.makedirs(os.path.join(self.git_dir, "objects", "12"), exist_ok=True)
        os.makedirs(os.path.join(self.git_dir, "objects", "34"), exist_ok=True)

        # Коммит 1 (хэш 34567890abcdef)
        with open(os.path.join(self.git_dir, "objects", "12", "34567890abcdef"), "wb") as f:
            f.write(zlib.compress(
                b"commit 45\n"
                b"parent abcdef1234567890\n"
                b"author Author One <author1@example.com> 1609459200\n\n"
                b"First test commit message"
            ))

        # Коммит 2 (хэш abcdef1234567890)
        with open(os.path.join(self.git_dir, "objects", "12", "abcdef1234567890"), "wb") as f:
            f.write(zlib.compress(
                b"commit 40\n"
                b"author Author Two <author2@example.com> 1612137600\n\n"
                b"Second test commit message"
            ))

        # Коммит 3 (хэш 567890abcdef)
        with open(os.path.join(self.git_dir, "objects", "34", "567890abcdef"), "wb") as f:
            f.write(zlib.compress(
                b"commit 50\n"
                b"parent 34567890abcdef\n"
                b"author Author Three <author3@example.com> 1614556800\n\n"
                b"Third test commit message"
            ))

    def tearDown(self):
        """
        Удаляем тестовую структуру после завершения тестов.
        """
        for root, dirs, files in os.walk(self.repo_path, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(self.repo_path)

    def test_get_commits_from_repo(self):
        """
        Считываем коммиты из тестовой директории и проверяем, что все объекты обработаны корректно.
        """
        commits = get_commits_from_repo(self.repo_path, datetime(2020, 1, 1))

        # Убедитесь, что все три коммита найдены
        self.assertEqual(len(commits), 3, "Ожидается 3 коммита")
        hashes = [commit["hash"] for commit in commits]
        self.assertIn("34567890abcdef", hashes, "Первый коммит отсутствует")
        self.assertIn("abcdef1234567890", hashes, "Второй коммит отсутствует")
        self.assertIn("567890abcdef", hashes, "Третий коммит отсутствует")


    def test_read_commit_object(self):
        """
        Проверяем, что данные объектов коммитов читаются корректно.
        """
        commit_hash = "34567890abcdef"
        commit_data = read_commit_object(commit_hash, self.git_dir)
        self.assertIsInstance(commit_data, bytes)

    def test_parse_commit(self):
        """
        Проверяем, что парсинг объектов коммита возвращает корректные данные.
        """
        commit_data = (
            b"commit 45\n"
            b"parent abcdef1234567890\n"
            b"author Author Name <author@example.com> 1609459200\n\n"
            b"Commit message"
        )
        commit_date, parents = parse_commit(commit_data)
        self.assertEqual(commit_date, datetime(2021, 1, 1))
        self.assertEqual(parents, ["abcdef1234567890"])

    def test_build_plantuml_graph(self):
        commits = [
            {"hash": "34567890abcdef", "parents": ["abcdef1234567890"]},
            {"hash": "567890abcdef", "parents": ["34567890abcdef"]},
            {"hash": "abcdef1234567890", "parents": []}
        ]
        graph = build_plantuml_graph(commits)

        # Проверяем прямую связь или зеркальную (если порядок не важен)
        self.assertTrue(
            '"abcdef1234567890" --> "34567890abcdef"' in graph or
            '"34567890abcdef" --> "abcdef1234567890"' in graph,
            "Связь между 'abcdef1234567890' и '34567890abcdef' отсутствует"
        )
        self.assertIn('"34567890abcdef" --> "567890abcdef"', graph)

    def test_save_graph_to_file(self):
        """
        Проверяем, что граф сохраняется в файл корректно.
        """
        graph = "@startuml\n\"1234567890abcdef\"\n@enduml\n"
        save_graph_to_file(graph, "test_graph.puml")
        with open("test_graph.puml", "r") as f:
            saved_graph = f.read()
        self.assertEqual(saved_graph, graph)

    def test_save_graph_with_multiple_commits(self):
        """
        Проверяем, что граф с несколькими коммитами сохраняется в файл корректно.
        """
        # Задаём три коммита с их хэшами и родителями
        commits = [
            {"hash": "abcdef1234567890", "parents": []},
            {"hash": "34567890abcdef", "parents": ["abcdef1234567890"]},
            {"hash": "567890abcdef", "parents": ["34567890abcdef"]}
        ]

        # Строим граф из коммитов
        graph = build_plantuml_graph(commits)

        # Сохраняем граф в файл
        save_graph_to_file(graph, "test_graph_multiple.puml")

        # Читаем сохранённый файл
        with open("test_graph_multiple.puml", "r") as f:
            saved_graph = f.read()

        # Проверяем корректность сохранённого графа
        self.assertIn('"abcdef1234567890"', saved_graph)
        self.assertIn('"abcdef1234567890" --> "34567890abcdef"', saved_graph)
        self.assertIn('"34567890abcdef"', saved_graph)
        self.assertIn('"34567890abcdef" --> "567890abcdef"', saved_graph)
        self.assertIn('"567890abcdef"', saved_graph)
        self.assertIn("@startuml", saved_graph)
        self.assertIn("@enduml", saved_graph)


if __name__ == "__main__":
    unittest.main()
