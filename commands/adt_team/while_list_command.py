import disnake
from disnake.ext import commands
from commands.misc.check_roles import has_any_role_by_id
from config import HEAD_ADT_TEAM
from bot_init import bot

# ID роли, которую будем добавлять или удалять
WL_ROLE_ID = 1060239440930418828
# ID канала, куда будет отправляться сообщение
CHANNEL_ID = 1351277093140303913

@bot.slash_command(name="wl_add", description="Добавить роль White List указанному пользователю")
@has_any_role_by_id(HEAD_ADT_TEAM)
async def wl_add(interaction: disnake.ApplicationCommandInteraction, user: disnake.Member):
    """
    Добавляет роль White List пользователю.
    """
    role = disnake.utils.get(interaction.guild.roles, id=WL_ROLE_ID)

    if not role:
        await interaction.response.send_message("❌ Роль не найдена.", ephemeral=True)
        return

    if role in user.roles:
        await interaction.response.send_message(f"ℹ️ {user.mention} уже имеет роль `{role.name}`.", ephemeral=True)
        return

    try:
        await user.add_roles(role)

        # Создание Embed
        embed = disnake.Embed(
            title="✅ Добавление в White List",
            description=f"**🎉 {user.mention} был принят в White List!**",
            color=disnake.Color.green(),
            timestamp=disnake.utils.utcnow()
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="👾 Имя", value=f"{user.display_name}", inline=False)
        embed.add_field(name="👤 Никнейм", value=f"`{user.name}`", inline=False)
        embed.add_field(name="🆔 ID пользователя", value=f"`{user.id}`", inline=False)
        embed.set_footer(text=f"Команду выполнил: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

        # Отправка Embed в указанный канал
        channel = interaction.guild.get_channel(CHANNEL_ID)
        await channel.send(embed=embed)

        await interaction.response.send_message(f"✅ Роль `{role.name}` успешно добавлена для {user.mention}.")

    except disnake.Forbidden:
        await interaction.response.send_message(f"⚠️ У меня нет прав для добавления роли `{role.name}` пользователю {user.mention}.", ephemeral=True)
    except disnake.HTTPException as e:
        await interaction.response.send_message(f"❌ Ошибка при добавлении роли: {e}", ephemeral=True)

@bot.slash_command(name="wl_del", description="Удалить роль White List у указанного пользователя")
@has_any_role_by_id(HEAD_ADT_TEAM)
async def wl_del(interaction: disnake.ApplicationCommandInteraction, user: disnake.Member):
    """
    Удаляет роль White List у пользователя.
    """
    role = disnake.utils.get(interaction.guild.roles, id=WL_ROLE_ID)

    if not role:
        await interaction.response.send_message("❌ Роль не найдена.", ephemeral=True)
        return

    if role not in user.roles:
        await interaction.response.send_message(f"ℹ️ {user.mention} не имеет роль `{role.name}`.", ephemeral=True)
        return

    try:
        await user.remove_roles(role)

        # Создание Embed
        embed = disnake.Embed(
            title="🚫 Удаление из White List",
            description=f"**{user.mention} был удалён из White List.**",
            color=disnake.Color.red(),
            timestamp=disnake.utils.utcnow()
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="👾 Имя", value=f"{user.display_name}", inline=False)
        embed.add_field(name="👤 Никнейм", value=f"`{user.name}`", inline=False)
        embed.add_field(name="🆔 ID пользователя", value=f"`{user.id}`", inline=False)
        embed.set_footer(text=f"Команду выполнил: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

        # Отправка Embed в указанный канал
        channel = interaction.guild.get_channel(CHANNEL_ID)
        await channel.send(embed=embed)

        await interaction.response.send_message(f"🚫 Роль `{role.name}` успешно удалена у {user.mention}.")

    except disnake.Forbidden:
        await interaction.response.send_message(f"⚠️ У меня нет прав для удаления роли `{role.name}` у пользователя {user.mention}.", ephemeral=True)
    except disnake.HTTPException as e:
        await interaction.response.send_message(f"❌ Ошибка при удалении роли: {e}", ephemeral=True)
