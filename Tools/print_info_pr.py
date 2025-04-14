from github import Github
from datetime import datetime, timezone

import sys
sys.path.append("..")
from config import GITHUB, REPO_NAME, AUTHOR

GITHUB_TOKEN = GITHUB
REPO_NAME = f'{AUTHOR}/{REPO_NAME}'

g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

try:
    user = g.get_user()
    print(f"Успешная аутентификация: {user.login}")
except Exception as e:
    print(f"Ошибка аутентификации: {e}")

def get_cutoff_date():
    while True:
        date_str = input("Введите дату, до которой нужно сделать пробежку по PR (в формате ГГГГ-ММ-ДД): ")
        try:
            # Преобразуем строку в datetime и добавляем временную зону (UTC)
            return datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            print("Неверный формат даты. Пожалуйста, введите дату в формате ГГГГ-ММ-ДД.")

def parse_pr_body(body):
    if not body:
        return []

    keywords = ['add', 'remove', 'fix', 'tweak']
    lines = body.split('\n')
    parsed_texts = []

    # Флаг, указывающий, что мы находимся в блоке чейнджлога
    in_changelog = False

    for line in lines:
        # Если находим начало блока чейнджлога
        if line.strip().startswith("## Чейнджлог"):
            in_changelog = True
            continue

        # Если находим конец блока чейнджлога (пустая строка или новый заголовок)
        if in_changelog and (line.strip() == "" or line.strip().startswith("##")):
            in_changelog = False
            continue
        # Если мы внутри блока чейнджлога, ищем ключевые слова
        if in_changelog:
            # Удаляем лишние символы в начале строки (дефисы, пробелы)
            cleaned_line = line.lstrip(' -')
            for keyword in keywords:
                if cleaned_line.lower().startswith(f'{keyword}:'):  # Ищем ключевое слово с двоеточием
                    parsed_texts.append(keyword)  # Добавляем ключевое слово в список
                    break

    return parsed_texts

def main():
    # Получаем дату от пользователя
    CUTOFF_DATE = get_cutoff_date()
    print(f"Выбранная дата: {CUTOFF_DATE}")

    # Список для хранения результатов
    results = []

    # Получаем все замердженные PR
    pulls = repo.get_pulls(state='closed', sort='updated', direction='desc')
    print(f"Найдено PR: {pulls.totalCount}")

    for pr in pulls:
        print(f"\nОбработка PR #{pr.number}: {pr.title}, Merged: {pr.merged}, Merged at: {pr.merged_at}")
        
        # Если дата мерджа меньше CUTOFF_DATE, прерываем цикл
        if pr.merged_at and pr.merged_at < CUTOFF_DATE:
            print(f"PR #{pr.number} имеет дату мерджа {pr.merged_at}, что раньше {CUTOFF_DATE}. Остановка.")
            break

        if pr.merged and pr.merged_at and pr.merged_at >= CUTOFF_DATE:
            # # Выводим тело PR для отладки
            # print(f"Тело PR:\n{pr.body}")
            
            parsed_texts = parse_pr_body(pr.body)
            print(f"Найдено ключевых слов: {len(parsed_texts)}")
            if parsed_texts:
                # Добавляем название PR в результаты только один раз
                results.append(f"[{pr.title}]({pr.html_url})")

    # Выводим результаты
    if results:
        print("\nРезультаты:")
        for result in results:
            print(result)
    else:
        print("Нет подходящих PR для указанной даты.")
