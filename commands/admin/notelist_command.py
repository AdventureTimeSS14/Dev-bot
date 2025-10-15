from bot_init import bot, ss14_db
import disnake
from dataConfig import ROLE_ACCESS_ADMIN
from disnake.ext.commands import has_any_role

'''Команда для просмотра заметок игрока'''
@has_any_role(*ROLE_ACCESS_ADMIN)
@bot.command(name="player_notes")
async def player_notes_command(ctx, nickname: str):
    notes = await ss14_db.search_notes_player(nickname)

    if not notes:
        embed = disnake.Embed(title="Заметки не найдены", description=f"{nickname} без заметок.", color=0xFF0000)
        await ctx.send(embed=embed)
        return

    embed = disnake.Embed(title=f"Заметки {nickname} ({len(notes)})", color=0x8B0000)
    
    for note in notes:
        note_id, created_at, message, severity, secret, last_edited_at, last_edited_by_id, player_id, last_seen_user_name, created_by_name = note
        created_str = created_at.strftime("%Y-%m-%d %H:%M:%S") if created_at else "?"
        message = message.replace('\n', ' ') if message else "Нет сообщения"
        info = f"**Дата:** {created_str}\n**Админ:** {created_by_name or '?'}\n**Сообщение:** {message}"
        if last_edited_at:
            edited_str = last_edited_at.strftime("%Y-%m-%d %H:%M:%S")
            info += f"\n**Редактировано:** {edited_str}"
        embed.add_field(name=f"---------------\nЗаметка #{note_id}", value=info, inline=False)

    await ctx.send(embed=embed)