from disnake import ButtonStyle
from disnake.ui import ActionRow, Button

# Создание кнопок
button_help = Button(label="&help", style=ButtonStyle.green, custom_id="button_help_id")
button_team_help = Button(label="&team_help", style=ButtonStyle.blurple, custom_id="button_team_help_id")
button_git_help = Button(label="&git_help", style=ButtonStyle.gray, custom_id="button_git_help_id")
button_admin_help = Button(label="&admin_help", style=ButtonStyle.red, custom_id="button_admin_help_id")

button_bug_report = Button(
    label="🔧 Оставить отзыв / Сообщить о баге",
    style=ButtonStyle.danger,
    custom_id="button_bug_report_id"
)

action_row_button_help = ActionRow(
    button_help,
    button_team_help,
    button_git_help,
    button_admin_help
)

action_row_bug_report = ActionRow(
    button_bug_report
)