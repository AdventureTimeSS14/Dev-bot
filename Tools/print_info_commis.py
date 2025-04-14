from github import Github
from datetime import datetime, timezone, timedelta
import sys

sys.path.append("..")
from config import GITHUB, REPO_NAME, AUTHOR

GITHUB_TOKEN = GITHUB
REPO_FULL_NAME = f'{AUTHOR}/{REPO_NAME}'

g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_FULL_NAME)

def format_commit_md(commit):
    """Форматирует информацию о коммите для Discord"""
    author_name = commit.commit.author.name
    author_login = commit.author.login if commit.author else 'N/A'
    date = commit.commit.author.date.strftime("%Y-%m-%d %H:%M UTC")
    message = commit.commit.message.strip()
    files_changed = '\n'.join(f"- `{f.filename}` ({f.status})" for f in commit.files)

    return f"""**[{commit.sha[:7]}]({commit.html_url})**
**Автор:** {author_name} ({author_login})
**Дата:** {date}
**Сообщение:** {message}
**Изменения:**
{files_changed}
            """

def get_commits_for_date(date):
    """Получает коммиты за указанную дату"""
    start_date = date.replace(hour=0, minute=0, second=0)
    end_date = start_date + timedelta(days=1)
    return list(repo.get_commits(since=start_date, until=end_date))

def main():
    try:
        user = g.get_user()
        print(f"Успешная аутентификация: {user.login}\n")
    except Exception as e:
        print(f"Ошибка аутентификации: {e}")
        return

    while True:
        date_str = input("Введите дату (ГГГГ-ММ-ДД) или 'q' для выхода: ")
        if date_str.lower() == 'q':
            break

        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            commits = get_commits_for_date(date)

            if not commits:
                print(f"На {date.date()} коммитов не найдено.\n")
                continue

            print(f"\nНайдено коммитов: {len(commits)}\n")
            for commit in commits:
                print(format_commit_md(commit))
                print('-' * 60)

        except ValueError:
            print("Неверный формат даты. Используйте ГГГГ-ММ-ДД.\n")

if __name__ == "__main__":
    main()
