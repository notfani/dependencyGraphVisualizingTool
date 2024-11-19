import subprocess
from datetime import datetime

def get_commits(repo_path, since_date):
    """
    Получает список коммитов из git-репозитория.
    :param repo_path: Путь к git-репозиторию.
    :param since_date: Дата, начиная с которой нужно получить коммиты.
    :return: Список словарей с информацией о коммитах.
    """
    result = subprocess.run(
        ['git', '-C', repo_path, 'log', '--pretty=format:%H %P %at', f'--since={since_date}'],
        stdout=subprocess.PIPE,
        text=True
    )
    commits = []
    for line in result.stdout.splitlines():
        commit_hash, *parents, timestamp = line.split()
        commits.append({
            'hash': commit_hash,
            'parents': parents,
            'date': datetime.fromtimestamp(int(timestamp)),
        })
    return commits
