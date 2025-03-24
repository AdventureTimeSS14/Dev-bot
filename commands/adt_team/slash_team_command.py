from datetime import date

import disnake
from disnake import Option

from bot_init import bot
from commands.dbCommand.get_db_connection import get_db_connection
from commands.misc.check_roles import has_any_role_by_id
from config import ADMIN_TEAM, HEAD_ADT_TEAM, HEAD_DISCORD_ADMIN, VACATION_ROLE


@bot.slash_command(
    name="team_add_vacation",
    description="Выдача отпуска пользователю с указанием срока и причины."
)
@has_any_role_by_id(HEAD_ADT_TEAM, HEAD_DISCORD_ADMIN)
async def team_add_vacation_slash(
    inter: disnake.ApplicationCommandInteraction,
    user: disnake.Member = Option(name="user", description="Пользователь, которому выдать отпуск", required=True),
    end_date: str = Option(name="end_date", description="Дата окончания отпуска (например, 01.04.2025)", required=True),
    reason: str = Option(name="reason", description="Причина отпуска", required=True)
):
    """
    Выдача отпуска пользователю. Добавляется роль отпуска с указанием срока и причины.
    """

    try:
        # Очистка и проверка формата даты
        end_date = end_date.strip('"\' ')
        day, month, year = map(int, end_date.split('.'))
        vacation_end = date(year, month, day) 

        # Проверяем, что дата не в прошлом
        if vacation_end < date.today():
            await inter.response.send_message("❌ Ошибка: Дата окончания отпуска не может быть в прошлом.")
            return
        
        # Форматируем для SQL
        sql_date = vacation_end.strftime('%Y-%m-%d')

    except ValueError:
        await inter.response.send_message("❌ Ошибка: Неверный формат даты. Используйте дд.мм.гггг (например, 22.02.2025)")
        return
    except Exception as e:
        await inter.response.send_message(f"❌ Критическая ошибка: {str(e)}")
        print(f"[add_vacation] Ошибка парсинга даты: {str(e)}")
        return

    # Получаем роль отпуска
    role_vacation = inter.guild.get_role(VACATION_ROLE)
    if not role_vacation:
        await inter.response.send_message("❌ Ошибка: Роль отпуска не найдена на сервере.")
        return

    # Проверяем, есть ли у пользователя уже роль отпуска
    if role_vacation in user.roles:
        await inter.response.send_message(
            f"❌ {user.mention} уже имеет роль {role_vacation.name}."
        )
        return

    # Получаем канал для уведомлений
    admin_channel = bot.get_channel(ADMIN_TEAM)
    if not admin_channel:
        await inter.response.send_message("❌ Ошибка: Канал уведомлений не найден.")
        return

    conn = None
    cursor = None

    try:
        # Подключение к БД (без await, так как mariadb синхронный)
        conn = get_db_connection()
        cursor = conn.cursor()

        # Вставка данных
        cursor.execute(
            "INSERT INTO vacation_team (discord_id, data_end_vacation, reason) VALUES (%s, %s, %s)",
            (user.id, sql_date, reason)
        )
        conn.commit()

        # Добавляем роль отпуска пользователю
        await user.add_roles(role_vacation)
        await inter.response.send_message(
            f"✅ Роль {role_vacation.name} успешно добавлена {user.mention}."
        )

        # Создаем Embed для уведомления в админ-канале
        embed = disnake.Embed(
            title="Выдача отпуска",
            description=(
                f"{inter.author.mention}({inter.author.name}) "
                f"выдал(а) отпуск для {user.mention}({user.name})."
            ),
            color=disnake.Color.purple(),
        )
        embed.add_field(name="Пользователь", value=user.mention, inline=False)
        embed.add_field(name="Срок отпуска", value=f"**{end_date}**", inline=True)
        embed.add_field(name="Причина", value=f"**{reason}**", inline=False)
        embed.set_author(name=inter.author.name, icon_url=inter.author.avatar.url)
        embed.set_footer(text="Желаем хорошего отдыха!")

        # Отправляем Embed в админ-канал
        await admin_channel.send(embed=embed)

    except disnake.Forbidden:
        await inter.response.send_message(
            "⚠️ Ошибка: У бота недостаточно прав для добавления роли."
        )
    except disnake.HTTPException as e:
        await inter.response.send_message(f"❌ Ошибка: Не удалось добавить роль. Подробнее: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        await inter.response.send_message("❌ Произошла непредвиденная ошибка.")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@bot.slash_command(
    name="team_end_vacation",
    description="Завершает отпуск пользователя, удаляя роль отпуска."
)
@has_any_role_by_id(HEAD_ADT_TEAM, HEAD_DISCORD_ADMIN)
async def team_end_vacation_slash(
    inter: disnake.ApplicationCommandInteraction,
    user: disnake.Member = Option(name="user", description="Пользователь, у которого завершить отпуск")
):
    """
    Завершает отпуск указанного пользователя, удаляя роль отпуска.
    """

    # Получаем роль отпуска
    role_vacation = inter.guild.get_role(VACATION_ROLE)
    if not role_vacation:
        await inter.response.send_message("❌ Ошибка: Роль отпуска не найдена на сервере.")
        return

    # Проверяем, есть ли у пользователя роль отпуска
    if role_vacation not in user.roles:
        await inter.response.send_message(f"❌ У {user.mention} нет роли {role_vacation.name}.")
        return

    # Получаем канал для уведомлений
    admin_channel = bot.get_channel(ADMIN_TEAM)
    if not admin_channel:
        await inter.response.send_message("❌ Ошибка: Канал уведомлений не найден.")
        return

    conn = None
    cursor = None

    try:
        # Подключение к базе данных
        conn = get_db_connection()
        cursor = conn.cursor()
        # Удаление записи из БД
        cursor.execute("DELETE FROM vacation_team WHERE discord_id = %s", (user.id,))
        conn.commit()
        
        # Удаляем роль отпуска у пользователя
        await user.remove_roles(role_vacation)
        await inter.response.send_message(
            f"✅ Роль {role_vacation.name} успешно снята с {user.mention}."
        )

        # Создаем Embed для уведомления в админ-канал
        embed = disnake.Embed(
            title="Окончание отпуска",
            description=(
                f"{inter.author.mention}({inter.author.name}) "
                f"завершил(а) отпуск для {user.mention}({user.name})."
            ),
            color=disnake.Color.purple(),
        )
        embed.set_author(name=inter.author.name, icon_url=inter.author.avatar.url)
        embed.add_field(name="Пользователь", value=user.mention, inline=False)
        embed.add_field(name="Действие", value="Закрытие отпуска", inline=False)

        # Отправляем Embed в админ-канал
        await admin_channel.send(embed=embed)

    except disnake.Forbidden:
        await inter.response.send_message("⚠️ Ошибка: У бота недостаточно прав для снятия роли.")
    except disnake.HTTPException as e:
        await inter.response.send_message(f"❌ Ошибка: Не удалось снять роль. Подробнее: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        await inter.response.send_message("❌ Произошла непредвиденная ошибка.")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@bot.slash_command(
    name="team_extend_vacation",
    description="Продлевает отпуск пользователя, обновляя срок и причину."
)
@has_any_role_by_id(HEAD_ADT_TEAM, HEAD_DISCORD_ADMIN)
async def team_extend_vacation_slash(
    inter: disnake.ApplicationCommandInteraction,
    user: disnake.Member = Option(name="user", description="Пользователь, которому продлеваем отпуск", required=True),
    new_end_date: str = Option(name="new_end_date", description="Новая дата окончания отпуска", required=True),
    reason: str = Option(name="reason", description="Причина продления отпуска", required=True)
):
    """
    Продление отпуска пользователю. Обновляется срок отпуска и причина.
    """
    try:
        # Очистка и проверка формата даты
        new_end_date = new_end_date.strip('"\' ')
        day, month, year = map(int, new_end_date.split('.'))
        vacation_end = date(year, month, day)

        # Проверяем, что дата не в прошлом
        if vacation_end < date.today():
            await inter.response.send_message("❌ Ошибка: Новая дата окончания отпуска не может быть в прошлом.")
            return

        # Форматируем для SQL
        sql_date = vacation_end.strftime('%Y-%m-%d')

    except ValueError:
        await inter.response.send_message("❌ Ошибка: Неверный формат даты. Используйте дд.мм.гггг (например, 22.02.2025)")
        return
    except Exception as e:
        await inter.response.send_message(f"❌ Критическая ошибка: {str(e)}")
        print(f"[extend_vacation] Ошибка парсинга даты: {str(e)}")
        return

    # Получаем роль отпуска
    role_vacation = inter.guild.get_role(VACATION_ROLE)
    if not role_vacation:
        await inter.response.send_message("❌ Ошибка: Роль отпуска не найдена на сервере.")
        return

    # Проверяем, есть ли у пользователя роль отпуска
    if role_vacation not in user.roles:
        await inter.response.send_message(
            f"❌ {user.mention} не имеет роли {role_vacation.name}, поэтому продлить отпуск невозможно.", 
            ephemeral=True
        )
        return

    # Получаем канал для уведомлений
    admin_channel = bot.get_channel(ADMIN_TEAM)
    if not admin_channel:
        await inter.response.send_message("❌ Ошибка: Канал уведомлений не найден.")
        return

    conn = None
    cursor = None

    try:
        # Подключение к базе данных
        conn = get_db_connection()
        cursor = conn.cursor()

        # Обновление записи в БД
        cursor.execute("UPDATE vacation_team SET data_end_vacation = %s, reason = %s WHERE discord_id = %s",
                       (sql_date, reason, user.id))
        conn.commit()

        # Создаем Embed для уведомления в админ-канале
        embed = disnake.Embed(
            title="Продление отпуска",
            description=(
                f"{inter.author.mention} ({inter.author.name}) "
                f"продлил(а) отпуск для {user.mention} ({user.name})."
            ),
            color=disnake.Color.purple(),
        )
        embed.add_field(name="Пользователь", value=user.mention, inline=False)
        embed.add_field(name="Новый срок отпуска", value=f"**{new_end_date}**", inline=True)
        embed.add_field(name="Причина продления", value=f"**{reason}**", inline=False)
        embed.set_author(name=inter.author.name, icon_url=inter.author.avatar.url)
        embed.set_footer(text="Желаем хорошего продолжения отдыха!")

        # Отправляем Embed в админ-канал
        await admin_channel.send(embed=embed)

        # Ответ пользователю
        await inter.response.send_message(
            f"✅ Срок отпуска {user.mention} был успешно продлен до {new_end_date}."
        )

    except disnake.Forbidden:
        await inter.response.send_message("⚠️ Ошибка: У бота недостаточно прав для отправки уведомлений.")
    except disnake.HTTPException as e:
        await inter.response.send_message(f"❌ Ошибка: Не удалось продлить отпуск. Подробнее: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        await inter.response.send_message("❌ Произошла непредвиденная ошибка.")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



@bot.slash_command(
    name="team_tweak",
    description="Изменяет роль пользователя, заменяя одну на другую с указанием причины."
)
@has_any_role_by_id(HEAD_ADT_TEAM, HEAD_DISCORD_ADMIN)
async def tweak_team_slash(
    inter: disnake.ApplicationCommandInteraction,
    user: disnake.Member = Option(name="user", description="Пользователь, которому меняем роль", required=True),
    old_role: disnake.Role = Option(name="old_role", description="Роль, которую нужно удалить", required=True),
    new_role: disnake.Role = Option(name="new_role", description="Роль, которую нужно добавить", required=True),
    reason: str = Option(name="reason", description="Причина изменения роли (не менее 5 символов)", required=True)
):
    """
    Изменение роли пользователя. Позволяет заменить одну роль на другую с указанием причины.
    """

    # Проверка канала для логирования
    admin_channel = bot.get_channel(ADMIN_TEAM)
    if not admin_channel:
        await inter.response.send_message("❌ Не удалось найти канал для логирования.")
        return

    # Проверка наличия старой роли у пользователя
    if old_role not in user.roles:
        await inter.response.send_message(
            f"❌ У {user.mention} нет роли **{old_role.name}**. Убедитесь, что роль указана верно.",
            ephemeral=True
        )
        return

    # Проверка на допустимость причины
    if len(reason.strip()) < 5:
        await inter.response.send_message(
            "❌ Причина должна содержать не менее 5 символов."
        )
        return

    try:
        # Удаление старой роли и добавление новой
        await user.remove_roles(old_role, reason=reason)
        await user.add_roles(new_role, reason=reason)

        # Определяем тип действия: повышение или понижение
        action = "Повышение в должности" if old_role < new_role else "Понижение в должности"
        action_description = (
            f"{inter.author.mention} ({inter.author.display_name}) "
            f"{'повысил(а)' if old_role < new_role else 'понизил(а)'} {user.mention} ({user.display_name})."
        )
        color = new_role.color  # Цвет Embed сообщения

        # Создаем Embed для лог-канала
        embed = disnake.Embed(
            title=action,
            description=action_description,
            color=color,
        )
        embed.add_field(name="Старая должность", value=f"**{old_role.name}**", inline=False)
        embed.add_field(name="Новая должность", value=f"**{new_role.name}**", inline=False)
        embed.add_field(name="Причина", value=f"**{reason}**", inline=False)
        embed.set_author(name=inter.author.name, icon_url=inter.author.avatar.url)
        embed.set_footer(
            text=f"Изменение роли произведено {inter.author}",
            icon_url=inter.guild.icon.url if inter.guild.icon else None,
        )

        # Отправляем Embed в лог-канал
        await admin_channel.send(embed=embed)

        # Ответ пользователю
        await inter.response.send_message(
            f"✅ Роль **{old_role.name}** была успешно заменена на **{new_role.name}** у {user.mention}. Причина: {reason}",
            ephemeral=True
        )

    except disnake.Forbidden:
        await inter.response.send_message(
            "⚠️ У бота нет прав для изменения ролей. Проверьте права бота."
        )
    except disnake.HTTPException as e:
        await inter.response.send_message(
            f"❌ Произошла ошибка при изменении ролей: {e}"
        )
        print(f"Ошибка при изменении ролей: {e}")
    except Exception as e:
        await inter.response.send_message(
            f"❌ Возникла ошибка: {e}"
        )
        print("Ошибка при выполнении команды tweak_team:", e)


async def get_log_channel():
    """ Проверяет наличие канала для логирования. """
    return bot.get_channel(ADMIN_TEAM)


async def check_reason(inter, reason):
    """ Проверяет, что причина указана и содержит хотя бы 5 символов. """
    if not reason or len(reason.strip()) < 5:
        await inter.response.send_message(
            "❌ Причина должна быть указана и содержать хотя бы 5 символов."
        )
        return False
    return True


async def remove_roles_from_user(user, roles):
    """ Удаляет указанные роли у пользователя. """
    removed_roles = []
    errors = []
    for role in roles:
        if role in user.roles:
            try:
                await user.remove_roles(role)
                removed_roles.append(role)
            except Exception as e:
                errors.append(f"❌ Ошибка при удалении роли **{role.name}**: {str(e)}")
        else:
            errors.append(f"❌ У {user.name} нет роли **{role.name}**.")
    return removed_roles, errors


async def send_results(inter, removed_roles, errors):
    """ Отправляет результаты удаления ролей или ошибки в канал. """
    messages = []
    if removed_roles:
        role_names = ", ".join([role.name for role in removed_roles])
        messages.append(f"✅ У {inter.author.mention} успешно сняты роли: **{role_names}**.")

    if errors:
        messages.extend(errors)

    await inter.response.send_message("\n".join(messages))


@bot.slash_command(
    name="team_remove",
    description="Снимает сотрудника с должности, удаляя две роли и логируя действие в админ состав."
)
@has_any_role_by_id(HEAD_ADT_TEAM, HEAD_DISCORD_ADMIN)
async def team_remove_slash(
    inter: disnake.ApplicationCommandInteraction,
    user: disnake.Member = Option(name="user", description="Пользователь, которого нужно снять с должности", required=True),
    role_dep: disnake.Role = Option(name="role_dep", description="Роль отдела, которую нужно удалить", required=True),
    role_job: disnake.Role = Option(name="role_job", description="Роль должности, которую нужно удалить", required=True),
    reason: str = Option(name="reason", description="Причина снятия с должности (не менее 5 символов)", required=True)
):
    """
    Команда для снятия сотрудника с должности. Удаляет роли отдела и должности.
    """

    # Проверяем канал для логирования
    channel_get = await get_log_channel()
    if not channel_get:
        await inter.response.send_message("❌ Не удалось найти канал для логирования действий.")
        return

    # Проверка причины
    if not await check_reason(inter, reason):
        return

    # Удаляем роли
    removed_roles, errors = await remove_roles_from_user(user, [role_dep, role_job])

    # Отправляем результаты
    await send_results(inter, removed_roles, errors)

    # Если обе роли успешно удалены, отправляем Embed в лог-канал
    if len(removed_roles) == 2:
        embed = disnake.Embed(
            title="Снятие с должности",
            description=f"{inter.author.mention} снял(а) с должности {user.mention}.",
            color=role_job.color,
        )
        embed.add_field(name="Отдел:", value=f"**{role_dep.name}**", inline=False)
        embed.add_field(name="Должность:", value=f"**{role_job.name}**", inline=False)
        embed.add_field(name="Причина:", value=f"**{reason}**", inline=False)
        embed.set_author(name=inter.author.name, icon_url=inter.author.avatar.url)

        await channel_get.send(embed=embed)


@bot.slash_command(
    name="new_team",
    description="Назначает пользователя на новую должность (требуется две роли: отдел и должность)."
)
@has_any_role_by_id(HEAD_ADT_TEAM, HEAD_DISCORD_ADMIN)
async def new_team(
    inter: disnake.ApplicationCommandInteraction,
    user: disnake.Member = Option(name="user", description="Пользователь, которого нужно назначить", required=True),
    role_department: disnake.Role = Option(name="role_dep", description="Роль отдела", required=True),
    role_position: disnake.Role = Option(name="role_job", description="Роль должности", required=True)
):
    """
    Команда для назначения пользователя на новую должность.
    Требуется передать две роли: <роль отдела> и <роль должности>.
    """

    assigned_roles = []

    # Проверяем и добавляем роли
    for role in [role_department, role_position]:
        if role in user.roles:
            await inter.response.send_message(
                f"❌ У {user.mention} уже есть роль **{role.name}**."
            )
        else:
            try:
                await user.add_roles(role)
                assigned_roles.append(role.name)
            except disnake.Forbidden:
                await inter.response.send_message(
                    f"⚠️ У бота нет прав для добавления роли **{role.name}**."
                )
                return
            except disnake.HTTPException as e:
                await inter.response.send_message(
                    f"❌ Ошибка при добавлении роли **{role.name}**: {str(e)}"
                )
                return
            except Exception as e:
                await inter.response.send_message(
                    f"❌ Произошла ошибка при добавлении роли **{role.name}**: {str(e)}"
                )
                return

    # Отправляем сообщение об успешных действиях
    if assigned_roles:
        await inter.response.send_message(
            f"✅ Роли успешно добавлены для {user.mention}: {', '.join(assigned_roles)}."
        )

    # Если обе роли успешно добавлены, отправляем Embed в лог-канал
    if len(assigned_roles) == 2:
        admin_channel = await get_log_channel()
        if admin_channel:
            embed = disnake.Embed(
                title="Назначение на должность",
                description=f"{inter.author.mention} назначает {user.mention} на новую должность.",
                color=role_position.color,
            )
            embed.add_field(name="Отдел", value=f"**{role_department.name}**", inline=False)
            embed.add_field(name="Должность", value=f"**{role_position.name}**", inline=False)
            embed.set_author(name=inter.author.name, icon_url=inter.author.avatar.url)

            await admin_channel.send(embed=embed)

@bot.slash_command(
    name="contribute",
    description="Добавляет роль контрибьютера указанному пользователю."
)
@has_any_role_by_id(HEAD_ADT_TEAM, HEAD_DISCORD_ADMIN)
async def contribution_add_slash(
    inter: disnake.ApplicationCommandInteraction,
    user: disnake.Member = Option(
        name="user",
        description="Пользователь, которому нужно выдать роль контрибьютера.",
        required=True
    ),
):
    """
        Команда для назначения пользователя на должность контрибьютера.
    """
    # Получаем роль отпуска
    role_contribute = inter.guild.get_role(1348226466227163176)
    if not role_contribute:
        await inter.response.send_message("❌ Ошибка: Роль Контрибьютера не найдена на сервере.")
        return

    # Проверяем, есть ли у пользователя уже роль отпуска
    if role_contribute in user.roles:
        await inter.response.send_message(
            f"❌ {user.mention} уже имеет роль {role_contribute.name}."
        )
        return

    try:
        # Добавляем роль контрибьюта пользователю
        await user.add_roles(role_contribute)
        await inter.response.send_message(
            f"✅ Роль {role_contribute.name} успешно добавлена {user.mention}."
        )

    except disnake.Forbidden:
        await inter.response.send_message(
            "⚠️ Ошибка: У бота недостаточно прав для добавления роли."
        )
    except disnake.HTTPException as e:
        await inter.response.send_message(f"❌ Ошибка: Не удалось добавить роль. Подробнее: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        await inter.response.send_message("❌ Произошла непредвиденная ошибка.")
