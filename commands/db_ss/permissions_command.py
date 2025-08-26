import disnake

from bot_init import bot, ss14_db
from commands.misc.check_roles import has_any_role_by_keys


@bot.command()
@has_any_role_by_keys("head_adt_team")
async def perm_add(ctx, nickname: str, title: str, admin_rank: str, server: str = "mrp"):
    """Добавляет нового администратора."""
    server = server.lower()
    name_server = server.lower()
    if server == "mrp":
        server = "main"
    elif server == "dev":
        pass
    else:
        await ctx.send("❌ Используйте аргумент `mrp` или `dev`.")

    player = ss14_db.fetch_player_data(nickname, server)
    if not player:
        await ctx.send(f"❌ Игрок `{nickname}` не найден в базе {name_server.upper()}.")
        return

    if ss14_db.fetch_admin_info(nickname, server):
        await ctx.send(f"⚠️ `{nickname}` уже является администратором на {name_server.upper()}")
        return

    rank = ss14_db.fetch_admin_rank(admin_rank, server)
    if not rank:
        await ctx.send(f"❌ Ранг `{admin_rank}` не найден на {server.upper()}")
        return

    ss14_db.permission_add_admin(player[1], title, rank[0], server)
    await ctx.send(f"✅ `{nickname}` добавлен как `{title}` ({admin_rank}).")

@bot.command()
@has_any_role_by_keys("head_adt_team")
async def perm_tweak(ctx, nickname: str, title: str, admin_rank: str, server: str = "mrp"):
    """Изменяет права существующего администратора."""
    server = server.lower()
    name_server = server.lower()
    if server == "mrp":
        server = "main"
    elif server == "dev":
        pass
    else:
        await ctx.send("❌ Используйте аргумент `mrp` или `dev`.")

    admin_id = ss14_db.get_user_id_admin_by_username(nickname, server)
    if not admin_id:
        await ctx.send(f"❌ `{nickname}` не является администратором в {name_server.upper()}.")
        return
    
    rank = ss14_db.fetch_admin_rank(admin_rank, server)
    if not rank:
        await ctx.send(f"❌ Ранг `{admin_rank}` не найден.")
        return

    ss14_db.permission_tweak_admin(title, rank[0], admin_id[0], server)
    await ctx.send(f"✅ `{nickname}` обновлен: `{title}` ({admin_rank}).")

@bot.command()
@has_any_role_by_keys("head_adt_team")
async def perm_del(ctx, nickname: str, server: str = "mrp"):
    """Удаляет администратора из таблицы."""
    server = server.lower()
    name_server = server.lower()
    if server == "mrp":
        server = "main"
    elif server == "dev":
        pass
    else:
        await ctx.send("❌ Используйте аргумент `mrp` или `dev`.")

    admin_id = ss14_db.get_user_id_admin_by_username(nickname, server)
    if not admin_id:
        await ctx.send(f"❌ `{nickname}` не найден среди администраторов {name_server.upper()}.")
        return

    ss14_db.permission_delete_admin(admin_id[0], server)
    await ctx.send(f"✅ `{nickname}` удален из списка администраторов {name_server.upper()}")

@bot.command()
@has_any_role_by_keys("head_adt_team")
async def admin_rank(ctx, server: str = "mrp"):
    """
    Выводит список всех админских рангов.
    Использование: &admin_rank [mrp/dev]
    """
    server = server.lower()
    name_server = server.lower()
    if server == "mrp":
        server = "main"
    elif server == "dev":
        pass
    else:
        await ctx.send("❌ Используйте аргумент `mrp` или `dev`.")

    ranks = ss14_db.fetch_admin_ranks(server)
    
    if not ranks:
        embed = disnake.Embed(
            title=f"🔧 Ранги {name_server.upper()} не найдены",
            description="В базе данных нет зарегистрированных рангов.",
            color=disnake.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    embed = disnake.Embed(
        title=f"📜 Ранги {name_server.upper()} ({len(ranks)})",
        color=disnake.Color.gold()
    )
    
    rank_list = "\n".join([f"🆔 `{rank_id}` | 🎖 `{name}`" for rank_id, name in ranks])
    embed.add_field(name="Ранги:", value=rank_list, inline=False)
    
    await ctx.send(embed=embed)
