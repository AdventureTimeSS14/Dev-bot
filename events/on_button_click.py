import disnake
from disnake.ui import Modal, TextInput

from bot_init import bot


class BugReportModal(Modal):
    """ 
    Клас обработки модального окна баг-репортов
    """
    def __init__(self):
        # Создаем текстовое поле для ввода сообщения с custom_id
        text_input = TextInput(
            label="Подробности о сообщении", 
            placeholder="Опишите баг, отзыв или предложение...", 
            style=disnake.TextInputStyle.long,
            custom_id="bug_report_details"
        )

        # Инициализация модального окна с компонентом text_input
        super().__init__(title="🚨 Сообщение о баге/отзыв/предложение", components=[text_input])

    async def callback(self, inter: disnake.MessageInteraction):
        """
        Обрабатывает отправку модального окна с баг-репортом.

        Аргументы:
            inter (disnake.MessageInteraction): Взаимодействие с модальным окном.
        """
        try:
            # Получаем введённый текст через text_inputs
            report_text = inter.text_values['bug_report_details']

            # Указание канала для отправки сообщения о репорте/отзыва
            target_channel_id = 1333381720996843551
            target_channel = inter.bot.get_channel(target_channel_id)

            if target_channel:
                # Создаем Embed для отправки
                embed = disnake.Embed(
                    title="📝 Новый отзыв/баг-репорт",
                    description= (
                        f"Сообщение от пользователя {inter.author.display_name} "
                        f"({inter.author.mention}) ({inter.author.id}):"
                    ),
                    color=disnake.Color.yellow()
                )
                embed.add_field(name="Текст сообщения:", value=report_text, inline=False)
                embed.set_footer(
                    text = (
                        f"Отправлено: {inter.created_at.strftime('%Y-%m-%d %H:%M:%S')} "
                        f"от {inter.author.display_name}"
                    ),
                    icon_url=inter.author.avatar.url
                )

                # Пересылаем сообщение в канал
                await target_channel.send(embed=embed)

            # Ответ пользователю с подтверждением
            await inter.response.send_message(
                "Спасибо за ваше сообщение! Мы внимательно его рассмотрим "
                "и постараемся улучшить сервис. 😊", 
                ephemeral=True
            )

        except Exception as e:
            # Логирование ошибки (если происходит ошибка)
            print(f"Произошла ошибка при отправке сообщения: {e}")
            try:
                await inter.response.send_message(
                    "Извините, произошла ошибка при обработке вашего сообщения. "
                    "Пожалуйста, попробуйте снова позже.",
                    ephemeral=True
                )
            except Exception as inner_error:
                print(f"Ошибка при отправке сообщения об ошибке: {inner_error}")


@bot.event
async def on_button_click(inter: disnake.MessageInteraction):
    """Обрабатывает нажатия на кнопки в сообщениях."""
    if inter.component.custom_id == "button_help_id":
        await bot.get_command("help").callback(inter)

    if inter.component.custom_id == "button_team_help_id":
        await bot.get_command("team_help").callback(inter)

    if inter.component.custom_id == "button_git_help_id":
        await bot.get_command("git_help").callback(inter)

    if inter.component.custom_id == "button_admin_help_id":
        await bot.get_command("admin_help").callback(inter)

    if inter.component.custom_id == "button_bug_report_id":
        await inter.response.send_modal(BugReportModal())
