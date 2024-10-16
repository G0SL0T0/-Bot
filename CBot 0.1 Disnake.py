import disnake
import disnake.backoff
from disnake.ext import commands
import json
from datetime import datetime
import time
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler


command_prefix="!"
intents=disnake.Intents.all()
bot = commands.InteractionBot(intents=intents)

menu_message = "Добро пожаловать в главное меню! Выберите один из вариантов ниже:"
ROLE_PRICES = {
    "role1": {"price": 100, "role_id": 1291219768032104460},
    "role2": {"price": 200, "role_id": 1292393218175930379},
    "role3": {"price": 300, "role_id": 1282958916657086508},
}
menu_buttons = [
    disnake.ui.Button(label="Жопник", custom_id="option_jopnik"),
    disnake.ui.Button(label="Магазин", custom_id="option_shop"),
    disnake.ui.Button(label="Команды", custom_id="option_commands"),
]

#########################################################################
########################### Запуск бота #################################
@bot.event
async def on_ready():
    print(f"Бот {bot.user} готов к работе!")
#########################################################################
############################  ФУНКЦИИ  ##################################

########  Кнопки "назад"  ########
def back_to_main_button():
    return disnake.ui.Button(label="Назад", custom_id="back_to_main")

def back_to_jopnik_button():
    return disnake.ui.Button(label="Назад", custom_id="back_to_jopnik")

##################################


async def handle_role_purchase(interaction, role_name):
    with open('jopnik.json', 'r') as f:
        data = json.load(f)
    commission = data.get('commission', 0)

    role_info = ROLE_PRICES.get(role_name)
    if not role_info:
        await interaction.response.send_message("Ошибка: роль не найдена.", ephemeral=True)
        return

    total_price = role_info['price'] + commission 
    user_balance = data.get('balance', 0)

    if user_balance < total_price:
        await interaction.response.send_message("У вас недостаточно средств для покупки этой роли.", ephemeral=True)
        return

    member = interaction.author 
    current_roles = {role.id for role in member.roles}
    role_ids = [info['role_id'] for info in ROLE_PRICES.values()]

    if role_info['role_id'] in current_roles:
        await interaction.response.send_message("Вы уже имеете эту роль.", ephemeral=True)
        return

    if any(role_id in current_roles for role_id in role_ids if role_id < role_info['role_id']):
        await interaction.response.send_message("Вы не можете купить роль ниже текущего уровня.", ephemeral=True)
        return

    # Списание средств и добавление роли data['balance'] -= total_price
    with open('jopnik.json', 'w') as f:
        json.dump(data, f, indent=4)

    role = interaction.guild.get_role(role_info['role_id'])
    await member.add_roles(role)

    await interaction.response.send_message(f"Вы успешно купили роль {role_name.capitalize()}!", ephemeral=True)

def update_commission():
    with open('jopnik.json', 'r+') as f:
        data = json.load(f)
        data['commission'] = 0
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()
    print(f"Комиссия обновлена в {datetime.now()}")

def back_to_main_button():
    return disnake.ui.Button(label="Назад", custom_id="back_to_main")

def initialize_files():
    if not os.path.exists('jopnik.json'):
        with open('jopnik.json', 'w') as f:
            json.dump({'balance': 1000, 'commission': 0}, f, indent=4)  # Начальный баланс для теста

    if not os.path.exists('rep.json'):
        with open('rep.json', 'w') as f:
            json.dump({}, f, indent=4)
initialize_files()

async def show_shop(interaction):
    with open('jopnik.json', 'r') as f:
        data = json.load(f)
    commission = data.get('commission', 0)

    embed = disnake.Embed(title="Магазин Жопника", description="Добро по��аловать в магазин! Выберите роль для покупки.")
    view = disnake.ui.View()
    for role_name, role_info in ROLE_PRICES.items():
        total_price = role_info['price'] + commission
        view.add_item(disnake.ui.Button(label=f"{role_name.capitalize()} ({total_price})", custom_id=f"buy_{role_name}"))

    view.add_item(back_to_jopnik_button())
    await interaction.response.edit_message(embed=embed, view=view)

####################################################################
######################### BALANCE ##################################

def get_user_balance(user_id):
    with open('Jrun_balance.json', 'r') as f:
        balances = json.load(f)
    return balances.get(str(user_id), 0)

def update_user_balance(user_id, new_balance):
    with open('Jrun_balance.json', 'r') as f:
        balances = json.load(f)
    balances[str(user_id)] = new_balance 
    with open('Jrun_balance.json', 'w') as f:
        json.dump(balances, f)

####################################################################
##########################    ######################################


###########################################################################
#############  // команды для бота {для выборки в меню} ###################

@bot.slash_command(description="Показать меню")
async def меню(interaction: disnake.ApplicationCommandInteraction):
    embed = disnake.Embed(title="Главное меню", description=menu_message)
    view = disnake.ui.View()
    for button in menu_buttons:
        view.add_item(button)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

@bot.slash_command(description="Получить ежедневный жрун")
async def ежедневка(interaction: disnake.ApplicationCommandInteraction):
    user_id = str(interaction.author.id)
    with open('Jrun_balance.json', 'r') as f:
        balances = json.load(f)
    if user_id not in balances:
        balances[user_id] = 0
    balances[user_id] += 1
    with open('Jrun_balance.json', 'w') as f:
        json.dump(balances, f)
    await interaction.response.send_message("Вы получили 1 жрун!", ephemeral=True)

#########################################################################

@bot.listen("on_message_interaction")
async def on_message_interaction(interaction: disnake.MessageInteraction):
    user_id = interaction.author.id 
    if interaction.data.custom_id.startswith("buy_"):
        role_name = interaction.data.custom_id.split("_")[1]
        role_info = ROLE_PRICES.get(role_name)

        if not role_info:
            await interaction.response.send_message("Роль не найдена.", ephemeral=True)
            return

        user_balance = get_user_balance(user_id)
        total_price = role_info['price'] + data.get('commission', 0)

        if user_balance >= total_price:
            update_user_balance(user_id, user_balance - total_price)
            role = interaction.guild.get_role(role_info['role_id'])
            await interaction.author.add_roles(role)
            await interaction.response.send_message(f"Вы успешно купили роль {role_name.capitalize()}!", ephemeral=True)
        else:
            await interaction.response.send_message("У вас недостаточно средств для покупки этой роли.", ephemeral=True)

    elif interaction.data.custom_id == "option_shop":
        await show_shop(interaction)

@bot.listen("on_message_interaction")
async def on_message_interaction(interaction: disnake.MessageInteraction):
    embed = disnake.Embed()
    if interaction.data.custom_id == "back_to_main":
        embed.title = "Главное меню"
        embed.description = menu_message
        view = disnake.ui.View()
        for button in menu_buttons:
            view.add_item(button)
        await interaction.response.edit_message(embed=embed, view=view)
    elif interaction.data.custom_id == "back_to_jopnik":
        embed.title = "Жопник"
        embed.description = "Выберите действие: баланс Жопника, комиссия, твоя репутация у Жопника."
        view = disnake.ui.View()
        view.add_item(disnake.ui.Button(label="Магазин Жопника", custom_id="shop"))
        view.add_item(disnake.ui.Button(label="Баланс Жопника", custom_id="jopnik_balance"))
        view.add_item(disnake.ui.Button(label="Комиссия Жопника", custom_id="jopnik_commission"))
        view.add_item(disnake.ui.Button(label="Репутация у Жопника", custom_id="jopnik_reputation"))
        view.add_item(back_to_main_button())
        await interaction.response.edit_message(embed=embed, view=view)
    elif interaction.data.custom_id.startswith("option_"):
        if interaction.data.custom_id == "option_jopnik":
            embed.title = "Жопник"
            embed.description = "Выберите действие: управление балансом, комиссией и репутацией."
            view = disnake.ui.View()
            view.add_item(disnake.ui.Button(label="Магазин Жопника", custom_id="shop_jopnik"))
            view.add_item(disnake.ui.Button(label="Баланс Жопника", custom_id="jopnik_balance"))
            view.add_item(disnake.ui.Button(label="Комиссия Жопника", custom_id="jopnik_commission"))
            view.add_item(disnake.ui.Button(label="Репутация у Жопника", custom_id="jopnik_reputation"))
            view.add_item(back_to_main_button())
        elif interaction.data.custom_id == "option_shop":
            await show_shop(interaction, back_to_main_button())
        elif interaction.data.custom_id == "option_commands":
            embed.title = "Команды"
            embed.description = (
                "Список доступных команд:\n"
                "/меню - Показать главное меню\n"
                "Жопник - Управление вашим виртуальным кошельком и репутацией\n"
                "Магазин - Покупка товаров"
            )
            view = disnake.ui.View()
            view.add_item(back_to_main_button())
        await interaction.response.edit_message(embed=embed, view=view)

    elif interaction.data.custom_id.startswith("jopnik_"):
        embed.title = "Жопник"
        if interaction.data.custom_id == "jopnik_balance":
            with open('jopnik.json', 'r') as f:
                data = json.load(f)
            embed.description = f"Баланс Жопника: {data.get('balance', 0)}"
        elif interaction.data.custom_id == "jopnik_commission":
            with open('jopnik.json', 'r') as f:
                data = json.load(f)
            embed.description = f"Комиссия Жопника: {data.get('commission', 0)}%"
        elif interaction.data.custom_id == "jopnik_reputation":
            with open('rep.json', 'r') as f:
                data = json.load(f)
            user_id = str(interaction.author.id)
            reputation = data.get(user_id, 0)
            embed.description = f"Ваша репутация: {reputation}"

        view = disnake.ui.View()
        view.add_item(back_to_jopnik_button())
        await interaction.response.edit_message(embed=embed, view=view)

    elif interaction.data.custom_id == "shop":
        await show_shop(interaction)

    elif interaction.data.custom_id == "shop_jopnik":
        await show_shop(interaction)

@bot.listen("on_button_click")
async def on_button_click(interaction: disnake.MessageInteraction):
    if interaction.data.custom_id.startswith("buy_"):
        role_name = interaction.data.custom_id.split("_")[1]
        await handle_role_purchase(interaction, role_name)



# Настройка планировщика задач
scheduler = AsyncIOScheduler()
scheduler.add_job(update_commission, 'cron', hour=0, minute=0)
scheduler.start()

bot.run("MTE2NjYzODE2NTY1ODk3NjI3Nw.Gi1Xt0.0xhlWdERtyKuWQSupLmmN_hJ8FPdFXK9RKdvjU")
#Лото MTE2NjYzODE2NTY1ODk3NjI3Nw.Gi1Xt0.0xhlWdERtyKuWQSupLmmN_hJ8FPdFXK9RKdvjU
#Чудо MTIzMzAyMTQ4NzE3MTEwODkwNQ.GJHW7F.XZRRzqVMFKD4MW0N5yVzjJIfwFZdXuVICmWcRw

