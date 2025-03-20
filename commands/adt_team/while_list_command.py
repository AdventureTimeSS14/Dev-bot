import disnake
from disnake.ext import commands

from bot_init import bot

# ID роли, которую будем добавлять или удалять
WL_ROLE_ID = 1060239440930418828

@bot.slash_command(name="add_wl", description="Добавить роль White List указанному пользователю")
async def add_wl(interaction: disnake.ApplicationCommandInteraction, user: disnake.Member):
    """
    Добавляет роль White List пользователю.
    """
    # Ищем роль по ID
    role = disnake.utils.get(interaction.guild.roles, id=WL_ROLE_ID)

    if not role:
        await interaction.response.send_message("Роль не найдена.", ephemeral=True)
        return

    if role in user.roles:
        await interaction.response.send_message(f"{user.mention} уже имеет роль {role.name}.", ephemeral=True)
        return

    try:
        await user.add_roles(role)
        await interaction.response.send_message(f"Роль {role.name} успешно добавлена для {user.mention}.")
    except disnake.Forbidden:
        await interaction.response.send_message(f"У меня нет прав для добавления роли {role.name} пользователю {user.mention}.", ephemeral=True)
    except disnake.HTTPException as e:
        await interaction.response.send_message(f"Произошла ошибка при добавлении роли: {e}", ephemeral=True)

@bot.slash_command(name="del_wl", description="Удалить роль White List у указанного пользователя")
async def del_wl(interaction: disnake.ApplicationCommandInteraction, user: disnake.Member):
    """
    Удаляет роль White List у пользователя.
    """
    # Ищем роль по ID
    role = disnake.utils.get(interaction.guild.roles, id=WL_ROLE_ID)

    if not role:
        await interaction.response.send_message("Роль не найдена.", ephemeral=True)
        return

    if role not in user.roles:
        await interaction.response.send_message(f"{user.mention} не имеет роль {role.name}.", ephemeral=True)
        return

    try:
        await user.remove_roles(role)
        await interaction.response.send_message(f"Роль {role.name} успешно удалена у {user.mention}.")
    except disnake.Forbidden:
        await interaction.response.send_message(f"У меня нет прав для удаления роли {role.name} у пользователя {user.mention}.", ephemeral=True)
    except disnake.HTTPException as e:
        await interaction.response.send_message(f"Произошла ошибка при удалении роли: {e}", ephemeral=True)
