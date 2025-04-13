import disnake

from config import AUTHOR, GLOBAL_SESSION, REPOSITORIES


async def validate_repository(ctx, repo_key):
    """
    Проверяет правильность указанного ключа репозитория.
    """
    if repo_key not in REPOSITORIES:
        await ctx.send(
            "❌ Неверный ключ репозитория. Укажите корректный ключ: `n` или `o`."
        )
        return None
    return f"{AUTHOR}/{REPOSITORIES[repo_key]}"


async def fetch_github_data(url, params=None):
    """
    Выполняет запрос к GitHub API и возвращает данные.
    """
    try:
        response = GLOBAL_SESSION.get(url, params=params)
        if response.status_code != 200:
            print(
                f"❌ Ошибка при запросе данных с GitHub: {response.status_code}"
            )
            return None
        return response.json()
    except Exception as e:
        print(f"❌ Ошибка при выполнении запроса к GitHub API: {e}")
        return None


async def create_embed_list(
    title, items, color, formatter, max_items_per_embed=25
):
    """
    Создаёт список Embed на основе переданных данных.
    """
    embed_list = []
    current_embed = disnake.Embed(title=title, color=color)

    for i, item in enumerate(items):
        # Создаем новый Embed, если достигнуто максимальное количество элементов
        if i % max_items_per_embed == 0 and i > 0:
            embed_list.append(current_embed)
            current_embed = disnake.Embed(title=title, color=color)

        # Добавляем поле, используя переданную функцию форматирования
        current_embed.add_field(**formatter(item))

    # Добавляем последний Embed в список
    if len(current_embed.fields) > 0:
        embed_list.append(current_embed)

    return embed_list


async def send_embeds(ctx, embed_list):
    """
    Отправляет список Embed сообщений в канал Discord.
    """
    for embed in embed_list:
        try:
            await ctx.send(embed=embed)
        except disnake.HTTPException as exc:
            await ctx.send(f"❌ Ошибка отправки сообщения: {exc}")
