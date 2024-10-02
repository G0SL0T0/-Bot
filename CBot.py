#Чудо бот
import discord
import asyncio
from discord.ext import commands
import pytz
from datetime import datetime, timedelta
import random
import json
import time
import datetime

# Необходимые переменные
message_count = {}
TOP_LIST_FILE = "top_list.json"
prefix = "!"
random_responses=[
    "Неактуально"
    ]
allowed_users = ['708019826232262686', '303101350118555658']

bot = commands.Bot(intents=discord.Intents.all(), case_insensitive=True, command_prefix=prefix)

# Функции для работы с файлами
def load_top_list():
    try:
        with open(TOP_LIST_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []
def save_top_list(top_list):
    with open(TOP_LIST_FILE, "w") as file:
        json.dump(top_list, file)
def load_last_update_and_price():
    return datetime(2024, 4, 24), 50000
def save_last_update_and_price(date, price):
    pass
def load_balances():
    try:
        with open('Jrun_balance.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_balances(balances):
    with open('Jrun_balance.json', 'w') as file:
        json.dump(balances, file, indent=4)

def daily_balance_check(member_id, balances):
    member_data = balances.setdefault(str(member_id), {'balance': 0, 'last_message': ''})
    today = datetime.now(pytz.timezone('Asia/Sakhalin')).date().isoformat()
    if member_data['last_message'] != today:
        member_data['balance'] += 1
        member_data['last_message'] = today
        save_balances(balances)

async def convert_to_member(ctx, argument):
    try:
        member = await commands.MemberConverter().convert(ctx, argument)
    except commands.MemberNotFound:
        member = ctx.guild.get_member_named(argument)
    if not member:
        raise commands.BadArgument(f'Пользователь "{argument}" не найден.')
    return member
def check_last_reward_time(member_id):
    with open('rewards.json', 'r') as f:
        rewards = json.load(f)
    return rewards.get(str(member_id), {'last_reward': None})['last_reward']
def update_last_message_time(user_id):
    with open('last_messages.json', 'r+') as f:
        try:
            last_messages = json.load(f)
        except json.JSONDecodeError:
            last_messages = {}
        user_id_str = str(user_id)
        now = datetime.utcnow()
        last_message_time = last_messages.get(user_id_str, {'last_message': None})['last_message']
        last_message_date = datetime.strptime(last_message_time, '%Y-%m-%d %H:%M:%S') if last_message_time else None
        if not last_message_date or now - last_message_date > timedelta(days=1):
            last_messages[user_id_str] = {'last_message': now.strftime('%Y-%m-%d %H:%M:%S')}
            f.seek(0)
            json.dump(last_messages, f, indent=4)
            f.truncate()
            return True
        return False
def get_today():
    return datetime.now().strftime('%Y-%m-%d')
def read_data():
    try:
        with open('percentages.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"Произошла ошибка при чтении файла: {e}")
        return {}

def write_data(data):
    with open('percentages.json', 'w') as file:
        json.dump(data, file, indent=4)

# запуск        
@bot.event
async def on_ready():
    print(f"{bot.user.name} успешно запущен")

@bot.event
async def on_message(message):
    balances = load_balances()
    daily_balance_check(message.author.id, balances)
    if message.author == bot.user:
        return
    trigger_phrase = 'О великий код питона даруй мне силу игр'
    if message.content == trigger_phrase:
        if str(message.author.id) in allowed_users:
            games = ['EVE', 'GTFO', 'Tradesman', 'DoW 3', 'Hunt', 'Witcher']
            selected_game = random.choice(games)
            await message.channel.send(f"Дарую тебе силу на {selected_game}!")
        else:
            await message.channel.send("Ты не достоин силы игр от питона.")
    current_time = time.time()
    message_count.setdefault(message.author.id, {"count": 0, "last_message_time": 0})
    if current_time - message_count[message.author.id]["last_message_time"] > 1800:  # 1800 секунд = 30 минут
        message_count[message.author.id]["count"] = 0
    message_count[message.author.id]["last_message_time"] = current_time
    message_count[message.author.id]["count"] += 1
    if message_count[message.author.id]["count"] > 5:
        await message.channel.send(f"{message.author.mention}, вы отправили слишком много команд за последние 30 минут. Пожалуйста, подождите некоторое время перед отправкой новой команды.")
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        response = random.choice(["Эта команда неактуальна"])
        await ctx.send(response)
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Ошибка: необходимо указать аргумент '{error.param.name}'.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"Ошибка: неверный аргумент '{error.param.name}'. Укажите корректное значение.")
    else:
        await ctx.send(f"Произошла ошибка: {error}")


# Время
@bot.command(name='Время')
async def get_time(ctx):
    time1 = pytz.timezone('Asia/Sakhalin')
    time2 = datetime.datetime.now(time1)
    time3 = time2 + datetime.timedelta(hours=0)
    formatted_time = time3.strftime("%H:%M:%S")
    await ctx.send(f"Сейчас у Чудачки: {formatted_time}")
    print('Команда Время')
# Команда - Vk Play
@bot.command(name='Вкплей')
async def vk_play(ctx):
    await ctx.send("# [Чудачка - Выживание Vk Play Live](https://live.vkplay.ru/chudachkapw)")
# Команда - Twitch
@bot.command(name='Твич')
async def Twitch(ctx):
    await ctx.send("# [Чудачка - Выживание Twitch](https://www.twitch.tv/chudachkafun)")
# Команда - Дискорд
@bot.command(name='Дискорд')
async def discord_info(ctx):
    await ctx.send("# [Присоединяйтесь к нашему серверу Discord!](https://discord.com/invite/pQ9zfKzmCj)")
# Команда - ПК
@bot.command(name='ПК')
async def pc_info(ctx):
    await ctx.send("## Конфиг ПК Чудачки\n Intel(R) Core(TM) i7-4790 CPU @ 3.60GHz\n Motherboard — Gigabyte GA-Z97P-D3\n MSI GeForce RTX 4060 GAMING X")
# Команда - Мемы
@bot.command(name='мем')
async def memes(ctx):
    await ctx.send("# [Кинь мем Чудачке на трансляцию!](https://memealerts.com/643f478676d4d6f40e06de95)")
# Команда - Бусти
@bot.command(name='бусти')
async def memes(ctx):
    await ctx.send("# [Поддержи Чудачку на бусти!](https://boosty.to/chudachkapw/purchase/784395?share=subscription_link)")
# Команда - Где стриим
@bot.command(name='Гдестрим')
async def stream_info(ctx):
    excuses = [
        "Сегодня уже не успеем, ждем завтра.",
        "Стрим будет в следующий раз, ожидайте!",
        "Планируем стрим на ближайшее время, следите за обновлениями."
    ]
    excuse = random.choice(excuses)
    await ctx.send(f"{excuse}")
# Команда - Дота
@bot.command(name='Дота')
async def play_dota(ctx):
    last_update, base_price = load_last_update_and_price()
    today = datetime.now()
    days_passed = (today - last_update).days
    if days_passed > 0:
        new_price = base_price + days_passed * 11
        save_last_update_and_price(today, new_price)
    else:
        new_price = base_price
    message = f"```Чудо поиграет в доту за {new_price:.3f} рублей```"
    await ctx.send(message)
# Команда - Танки
@bot.command(name='Танки')
async def play_dota(ctx):
    message = "```Чудо не поиграет в Танки 🤡```"
    await ctx.send(message)


# !стрим
@bot.command()
@commands.has_permissions(administrator=True)
async def стрим(ctx, *, comment: str = ''):
    channel_id = 1179745995345645609
    channel = bot.get_channel(channel_id)
    if channel is not None:
        message = (
            f"## Начался стрим! Присоединяйтесь! {comment}\n"
            "## [Чудачка - Выживание Twitch](https://www.twitch.tv/chudachkafun)\n"
            "## [Чудачка - Выживание Vk Play Live](https://live.vkplay.ru/chudachkapw)"
        )
        await channel.send(message)
    else:
        await ctx.send("Канал не найден. Пожалуйста, убедитесь, что указан правильный ID канала.")


# жопки
@bot.command(name='НоваяЖопка')
async def new_user(ctx, nickname):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("Ошибка: У вас нет прав для выполнения этой команды.")
        return
    top_list = load_top_list()
    for user_info in top_list:
        if user_info['никнейм'] == nickname:
            await ctx.send("Ошибка: Пользователь с таким никнеймом уже существует.")
            return
    user_num = len(top_list) + 1
    top_list.append({'никнейм': nickname, 'жопки': 2})
    save_top_list(top_list)
    await ctx.send(f"Новый пользователь {nickname} успешно создан с порядковым номером {user_num}.")
@bot.command(name='Номеражопок')
async def list_users(ctx):
    top_list = load_top_list()
    users_info = "Список пользователей и их номеров:\n"
    for user_num, user_info in enumerate(top_list, start=1):
        users_info += f"{user_num}. {user_info['никнейм']} - ({user_info['жопки']} жопок)\n"  # Добавление количества жопок к выводу
    await ctx.send(users_info)
@bot.command(name='Жопка')
async def asses_leaderboard(ctx):
    top_list = load_top_list()
    leaderboard = "Топ-5 владельцев жопок:\n"
    for i, user_info in enumerate(sorted(top_list, key=lambda x: x['жопки'], reverse=True)[:5], start=1):
        leaderboard += f"{i}. {user_info['никнейм']} - ({user_info['жопки']} жопок)\n"
    await ctx.send(leaderboard)
@bot.command(name='Перевестижопки')
async def transfer_asses(ctx, from_user: int, to_user: int, amount: int):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("Ошибка: У вас нет прав для выполнения этой команды.")
        return
    top_list = load_top_list()
    if from_user < 1 or from_user > len(top_list) or to_user < 1 or to_user > len(top_list):
        await ctx.send("Ошибка: Один или оба указанных пользователей не существуют.")
        return
    top_list[from_user - 1]['жопки'] -= amount
    top_list[to_user - 1]['жопки'] += amount
    save_top_list(top_list)
    await ctx.send(f"Успешно переведено {amount} жопок от {top_list[from_user - 1]['никнейм']} к {top_list[to_user - 1]['никнейм']}.")
@bot.command(name='минус')
async def minus_asses(ctx, amount: int, user_number: int):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("Ошибка: У вас нет прав для выполнения этой команды.")
        return
    top_list = load_top_list()
    if user_number < 1 or user_number > len(top_list):
        await ctx.send("Ошибка: Указанный пользователь не существует.")
        return
    top_list[user_number - 1]['жопки'] -= amount
    save_top_list(top_list)
    await ctx.send(f"Успешно снято {amount} жопок у {top_list[user_number - 1]['никнейм']}. Теперь у него {top_list[user_number - 1]['жопки']} жопок.")
@bot.command(name='плюс')
async def plus_asses(ctx, amount: int, user_number: int):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("Ошибка: У вас нет прав для выполнения этой команды.")
        return
    top_list = load_top_list()
    if user_number < 1 or user_number > len(top_list):
        await ctx.send("Ошибка: Указанный пользователь не существует.")
        return
    top_list[user_number - 1]['жопки'] += amount
    save_top_list(top_list)
    await ctx.send(f"Успешно добавлено {amount} жопок к {top_list[user_number - 1]['никнейм']}.")


# Команда !Процент
#@bot.command(name='Процент')
#async def percent(ctx):
    #user_id = str(ctx.author.id)
    #data = read_data()
    #print('1')
    #user_data = data.get(user_id, {'date': None, 'percent': 0, 'nickname': ctx.author.display_name, 'uses': 0})
    #unique_roles = ['роль1', 'роль2']
    #has_unique_role = any(role.name in unique_roles for role in ctx.author.roles)
    #print('2')
    #print(f"user_data['date']: {user_data['date']}")
    #print(f"has_unique_role: {has_unique_role}")
    #print(f"get_today(): {get_today()}")
    #if user_data['date'] == get_today() and not has_unique_role:
        #print('3 - Уже использовали команду')
        #await ctx.send("Вы уже использовали команду сегодня!")
        #return

    #print('3 - Продолжаем')
    #user_data['uses'] += 1
    #if user_data['percent'] < 100:
        #if user_data['percent'] == 0:
            #print('4')
            #new_percent = random.randint(0, 100)
        #else:
            #new_percent = random.randint(0, 99)
            #print('5')
        #user_data['percent'] = max(user_data['percent'], new_percent)
    #user_data['date'] = get_today()
    #print('6')
    #data[user_id] = user_data
    #write_data(data)
    #print('Отправка')
    #await ctx.send(f"{user_data['nickname']} ваш процент: {user_data['percent']}% (использовано {user_data['uses']} раз)")
    #print('Конец')

@bot.command(name='Топ')
async def top_users(ctx):
    data = read_data()
    top_users = sorted(data.items(), key=lambda x: x[1]['percent'], reverse=True)
    message = "Топ пользователей:\n"
    for user_id, user_data in top_users[:10]:
        message += f"{user_data['nickname']} - {user_data['percent']}% (использовано {user_data['uses']} раз)\n"
    await ctx.send(message)


# Что же я сделаю с жрунами
@bot.command()
async def баланс(ctx, *, member: discord.Member = None):
    if member is None:
        member = ctx.author
    balances = load_balances()
    user_balance = balances.get(str(member.id), {'balance': 0})['balance']
    await ctx.send(f"Баланс Жрунов пользователя {member.mention} составляет: {user_balance}💵")

@bot.command(name='Бонус')
async def on_bonus_command(ctx):
    user_id = str(ctx.author.id)
    balances = load_balances()
    member_data = balances.setdefault(user_id, {'balance': 0, 'last_message': ''})
    today = datetime.now(pytz.timezone('Asia/Sakhalin')).date().isoformat()
    if member_data['last_message'] != today:
        member_data['balance'] += 1
        member_data['last_message'] = today
        save_balances(balances)
        await ctx.send(f'Вы получили свой ежедневный бонус! Ваш баланс теперь составляет {member_data["balance"]} жрунов.')
    else:
        next_bonus_time = datetime.strptime(member_data['last_message'], '%Y-%m-%d') + timedelta(days=1)
        time_remaining = next_bonus_time - datetime.now(pytz.timezone('Asia/Sakhalin'))
        hours, remainder = divmod(int(time_remaining.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        await ctx.send(f'Погуляйте! Следующий бонус через {hours} часов и {minutes} минут.')


@bot.command()
async def магазин(ctx):
    # магаз
    pass




#1 + ответочка

# Токен
bot.run("MTIzMzAyMTQ4NzE3MTEwODkwNQ.GJHW7F.XZRRzqVMFKD4MW0N5yVzjJIfwFZdXuVICmWcRw") 
