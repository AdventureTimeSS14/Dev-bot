from .github_processor import validate_user


async def validate_and_return_if_invalid(ctx):
    """
    Проверяет пользователя перед выполнением команды.
    Возвращает True, если пользователь валиден, иначе False.
    """
    if not await validate_user(ctx):
        return False
    return True
