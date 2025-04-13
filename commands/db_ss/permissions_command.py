from datetime import datetime

import disnake
import psycopg2
import pytz

from bot_init import bot
from commands.db_ss.setup_db_ss14_mrp import (DB_HOST, DB_PASSWORD, DB_PORT,
                                              DB_USER)
from commands.misc.check_roles import has_any_role_by_keys


def get_db_params(server):
    db_name = "ss14" if server.lower() == "mrp" else "ss14_dev"
    return {
        'database': db_name,
        'user': DB_USER,
        'password': DB_PASSWORD,
        'host': DB_HOST,
        'port': DB_PORT
    }

def fetch_player(nickname, server):
    conn = psycopg2.connect(**get_db_params(server))
    cursor = conn.cursor()
    
    cursor.execute("SELECT user_id FROM public.player WHERE last_seen_user_name ILIKE %s", (nickname,))
    result = cursor.fetchone()
    
    cursor.close()
    conn.close()
    return result

def fetch_admin(nickname, server):
    conn = psycopg2.connect(**get_db_params(server))
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT a.user_id FROM public.admin a
        JOIN public.player p ON a.user_id = p.user_id
        WHERE p.last_seen_user_name ILIKE %s
    """, (nickname,))
    result = cursor.fetchone()
    
    cursor.close()
    conn.close()
    return result

def fetch_admin_rank(admin_rank, server):
    conn = psycopg2.connect(**get_db_params(server))
    cursor = conn.cursor()
    
    cursor.execute("SELECT admin_rank_id FROM public.admin_rank WHERE name ILIKE %s", (admin_rank,))
    result = cursor.fetchone()
    
    cursor.close()
    conn.close()
    return result

# Функция для получения списка рангов админов
def fetch_admin_ranks(server):
    db_name = "ss14" if server.lower() == "mrp" else "ss14_dev"
    DB_PARAMS = {
        'database': db_name,
        'user': DB_USER,
        'password': DB_PASSWORD,
        'host': DB_HOST,
        'port': DB_PORT
    }

    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()
    
    query = "SELECT admin_rank_id, name FROM public.admin_rank ORDER BY admin_rank_id ASC"
    cursor.execute(query)
    ranks = cursor.fetchall()

    cursor.close()
    conn.close()
    
    return ranks

@bot.command()
@has_any_role_by_keys("head_adt_team")
async def perm_add(ctx, nickname: str, title: str, admin_rank: str, server: str = "mrp"):
    """Добавляет нового администратора."""
    player = fetch_player(nickname, server)
    if not player:
        await ctx.send(f"❌ Игрок `{nickname}` не найден в базе {server.upper()}.")
        return
    
    if fetch_admin(nickname, server):
        await ctx.send(f"⚠️ `{nickname}` уже является администратором на {server.upper()}")
        return
    
    rank = fetch_admin_rank(admin_rank, server)
    if not rank:
        await ctx.send(f"❌ Ранг `{admin_rank}` не найден на {server.upper()}")
        return
    
    conn = psycopg2.connect(**get_db_params(server))
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO public.admin (user_id, title, admin_rank_id) VALUES (%s, %s, %s)
    """, (player[0], title, rank[0]))
    conn.commit()
    cursor.close()
    conn.close()
    await ctx.send(f"✅ `{nickname}` добавлен как `{title}` ({admin_rank}).")

@bot.command()
@has_any_role_by_keys("head_adt_team")
async def perm_tweak(ctx, nickname: str, title: str, admin_rank: str, server: str = "mrp"):
    """Изменяет права существующего администратора."""
    admin = fetch_admin(nickname, server)
    if not admin:
        await ctx.send(f"❌ `{nickname}` не является администратором в {server.upper()}.")
        return
    
    rank = fetch_admin_rank(admin_rank, server)
    if not rank:
        await ctx.send(f"❌ Ранг `{admin_rank}` не найден.")
        return
    
    conn = psycopg2.connect(**get_db_params(server))
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE public.admin SET title = %s, admin_rank_id = %s WHERE user_id = %s
    """, (title, rank[0], admin[0]))
    conn.commit()
    cursor.close()
    conn.close()
    await ctx.send(f"✅ `{nickname}` обновлен: `{title}` ({admin_rank}).")

@bot.command()
@has_any_role_by_keys("head_adt_team")
async def perm_del(ctx, nickname: str, server: str = "mrp"):
    """Удаляет администратора из таблицы."""
    admin = fetch_admin(nickname, server)
    if not admin:
        await ctx.send(f"❌ `{nickname}` не найден среди администраторов {server.upper()}.")
        return
    
    conn = psycopg2.connect(**get_db_params(server))
    cursor = conn.cursor()
    cursor.execute("DELETE FROM public.admin WHERE user_id = %s", (admin[0],))
    conn.commit()
    cursor.close()
    conn.close()
    await ctx.send(f"✅ `{nickname}` удален из списка администраторов {server.upper()}")

@bot.command()
@has_any_role_by_keys("head_adt_team")
async def admin_rank(ctx, server: str = "mrp"):
    """
    Выводит список всех админских рангов.
    Использование: &admin_rank [mrp/dev]
    """
    ranks = fetch_admin_ranks(server)
    
    if not ranks:
        embed = disnake.Embed(
            title=f"🔧 Ранги {server.upper()} не найдены",
            description="В базе данных нет зарегистрированных рангов.",
            color=disnake.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    embed = disnake.Embed(
        title=f"📜 Ранги {server.upper()} ({len(ranks)})",
        color=disnake.Color.gold()
    )
    
    rank_list = "\n".join([f"🆔 `{rank_id}` | 🎖 `{name}`" for rank_id, name in ranks])
    embed.add_field(name="Ранги:", value=rank_list, inline=False)
    
    await ctx.send(embed=embed)
