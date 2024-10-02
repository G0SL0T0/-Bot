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
# бот
bot = commands.Bot(intents=discord.Intents.all(), case_insensitive=True, command_prefix=prefix)

ticket_data_file = "tickets.json"
rewards = {
    100: {"Tier 4": 0.5, "Tier 5": 0.5},
    50: {"Tier 3": 1.0}
}
# Функции
def load_top_list():
    try:
        with open(TOP_LIST_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_top_list(top_list):
    with open(TOP_LIST_FILE, "w") as file:
        json.dump(top_list, file)

def get_current_date():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def calculate_price():
    print('1.0');
    start_date = datetime(2024, 4, 24)
    print('1');
    today = datetime.now()
    print('2');
    delta = today - start_date
    print('3');
    price_increment = delta.days * 11
    print('4');
    return 50000 + price_increment

def check_balance_file(user_id):
    try:
        with open('Jrun_balance.json', 'r') as f:
            balances = json.load(f)
    except FileNotFoundError:
        balances = {}
    except json.JSONDecodeError:
        balances = {}
        with open('Jrun_balance.json', 'w') as f:
            json.dump(balances, f, indent=4)
    if str(user_id) not in balances:
        balances[str(user_id)] = {'balance': 0, 'username': '', 'user_id': user_id}
        with open('Jrun_balance.json', 'w') as f:
            json.dump(balances, f, indent=4)
    return balances

async def convert_to_member(ctx, argument):
    try:
        member = await commands.MemberConverter().convert(ctx, argument)
    except commands.MemberNotFound:
        member = ctx.guild.get_member_named(argument)
    if not member:
        raise commands.BadArgument(f'Пользователь "{argument}" не найден.')
    return member

def check_last_reward_time(user_id):
    if not os.path.exists('rewards.json'):
        with open('rewards.json', 'w') as f:
            json.dump({}, f, indent=4)
    try:
        with open('rewards.json', 'r') as f:
            rewards = json.load(f)
    except json.JSONDecodeError:
        rewards = {}
        with open('rewards.json', 'w') as f:
            json.dump(rewards, f, indent=4)
    if str(user_id) not in rewards:
        rewards[str(user_id)] = {'last_reward_time': 0}
        with open('rewards.json', 'w') as f:
            json.dump(rewards, f, indent=4)
    return rewards[str(user_id)]['last_reward_time']

def update_last_reward_time(user_id):
    rewards = check_last_reward_time(user_id)
    rewards[str(user_id)] = {'last_reward_time': time.time()}
    with open('rewards.json', 'w') as f:
        json.dump(rewards, f, indent=4)

def can_receive_reward(user_id):
    last_reward_time = check_last_reward_time(user_id)
    current_time = time.time()
    return current_time - last_reward_time >= 86400  # 86400 секунд = 24 часа

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

async def give_jrun(ctx, member, amount=1):
    print('Кто-то получил жрун')
    balances = check_balance_file(member.id)
    if str(member.id) in balances:
        user_balance = balances[str(member.id)]
        user_balance['balance'] += amount
        balances[str(member.id)] = user_balance
        with open('Jrun_balance.json', 'w') as f:
            json.dump(balances, f, indent=4)
        await ctx.send(f"Пользователю {member.mention} начислено {amount} Жрунов.")
        print(f"{member.mention} получил {amount} Жрунов.")
    else:
        await ctx.send("У пользователя нет баланса.")

def update_last_reward_time(member_id):
    with open('rewards.json', 'r+') as f:
        try:
            rewards = json.load(f)
        except json.JSONDecodeError:
            rewards = {}
        rewards[str(member_id)] = {'last_reward': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}
        f.seek(0)
        json.dump(rewards, f, indent=4)
        f.truncate()

async def send_private_message(member, content):
    try:
        await member.send(content)
    except discord.Forbidden:
        await ctx.send(f"Невозможно отправить личное сообщение пользователю {member.display_name}.")

def load_ticket_data():
    try:
        with open(ticket_data_file, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_ticket_data(ticket_data):
    with open(ticket_data_file, "w") as file:
        json.dump(ticket_data, file, indent=4)

def add_tickets(user_id, amount):
    ticket_data = load_ticket_data()
    user_id_str = str(user_id)
    if user_id_str in ticket_data:
        ticket_data[user_id_str]['tickets'] += amount
    else:
        ticket_data[user_id_str] = {'tickets': amount}
    save_ticket_data(ticket_data)

def get_user_tickets(user_id):
    ticket_data = load_ticket_data()
    return ticket_data.get(str(user_id), {'tickets': 0})['tickets']

def draw_lottery(user_id):
    user_tickets = get_user_tickets(user_id)
    if user_tickets == 0:
        return "У вас нет билетов."
    for ticket_threshold, prize_dict in rewards.items():
        if user_tickets >= ticket_threshold:
            prize = random.choices(list(prize_dict.keys()), list(prize_dict.values()))[0]
            return f"Поздравляем! Вы выиграли {prize}!"

    return "К сожалению, вы ничего не выиграли."

def update_balance_and_react(message):
    balances = check_balance_file(message.author.id)
    role_names = [role.name for role in message.author.roles]
    if "Огонь" in role_names:
        balances[str(message.author.id)]['balance'] += 2
    else:
        balances[str(message.author.id)]['balance'] += 1

    if "сфера" in role_names or "берсерк" in role_names:
        balances[str(message.author.id)]['balance'] += 1

    with open('Jrun_balance.json', 'w') as f:
        json.dump(balances, f, indent=4)

    return balances


@bot.event
async def on_ready():
    print(f"{bot.user.name} успешно запущен")

#Евриван Сообщение
@bot.event
async def on_message(message):
    if not message.content.startswith('!'):
        return
    if message.author == bot.user:
        return

    user_id = message.author.id
    moderator_roles = ["Чудо", "Сфера", "Влад", "Сержант апельсин", "Берсерк"]
    is_moderator = any(role.name in moderator_roles for role in message.author.roles)

    if is_moderator:
        await bot.process_commands(message)
        return

    current_time = time.time()
    message_count.setdefault(user_id, {"count": 0, "last_message_time": 0})
    if current_time - message_count[user_id]["last_message_time"] > 1800:  # 1800 секунд = 30 минут
        message_count[user_id]["count"] = 0
    message_count[user_id]["last_message_time"] = current_time
    message_count[user_id]["count"] += 1

#2
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        response = random.choice(["Эта команда неактуальна"])
        await ctx.send(response)

# Жрун (Евриыван)
@bot.event
async def on_raw_reaction_add(payload):
    channel_id = 951816149291659274
    if payload.channel_id == channel_id:
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        if "Огонь" in [role.name for role in member.roles]:
            await give_jrun(member, amount=2)
        else:
            if check_last_reward_time(member.id) is None or (
                    datetime.utcnow() - check_last_reward_time(member.id)).days >= 1:
                await give_jrun(member)
                update_last_reward_time(member.id)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if can_receive_reward(message.author.id):
        balances = update_balance_and_react(message)
        await message.add_reaction('🔥')
        update_last_reward_time(message.author.id)

    await bot.process_commands(message)

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
async def bysti(ctx):
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
@bot.command(name='дота')
async def play_dota(ctx):
    await ctx.send(f"Чудачка поиграет в доту за много-много рублей.")

# Команда - Танки
@bot.command(name='танки')
async def play_tanki(ctx):
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
    await ctx.send(f"Успешно добавлено {amount} жопок к {top_list[user_number - 1]['никнейм']}. Теперь у него {top_list[user_number - 1]['жопки']} жопок.")

#пнуть
@bot.command()
async def пнуть(ctx, *, user: discord.Member):
    if user == ctx.author:
        await ctx.send("Вы не можете пнуть сами себя!")
        return

    role_names = [role.name for role in ctx.author.roles]
    if "Сфера" in role_names or "Чудо" in role_names:
        await send_private_message(user, f"Вас пнули!")
        await ctx.send(f"{user.display_name} успешно пнут!")
    else:
        current_time = time.time()
        message_count.setdefault(ctx.author.id, {"count": 0, "last_message_time": 0})
        if current_time - message_count[ctx.author.id]["last_message_time"] > 3600:  # Ограничение на 2 пинка в час
            message_count[ctx.author.id]["count"] = 0
        message_count[ctx.author.id]["last_message_time"] = current_time
        message_count[ctx.author.id]["count"] += 1
        if message_count[ctx.author.id]["count"] > 2:
            await ctx.send("Вы уже пнули слишком много раз за последний час!")
            return
        else:
            await send_private_message(user, f"Вас пнули!")
            await ctx.send(f"{user.display_name} пнут!")

@bot.command(name='add_tickets')
@commands.has_any_role("Чудо", "Сфера", "Влад", "Сержант апельсин", "Берсерк")
async def add_tickets_command(ctx, member: discord.Member, amount: int):
    if amount <= 0:
        await ctx.send("Количество билетов должно быть положительным.")
        return
    add_tickets(member.id, amount)
    await ctx.send(f"{amount} билетов добавлено пользователю {member.mention}.")

@bot.command(name='my_tickets')
async def my_tickets_command(ctx):
    tickets = get_user_tickets(ctx.author.id)
    await ctx.send(f"У вас {tickets} билетов.")

@bot.command(name='lottery')
async def lottery_command(ctx):
    result = draw_lottery(ctx.author.id)
    await ctx.send(result)

# Команда баланса
@bot.command()
async def баланс(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    try:
        balances = check_balance_file(member.id)
        balance = balances[str(member.id)]['balance']
        await ctx.send(f"Баланс {member.display_name}: {balance} жрунов")
    except Exception as e:
        await ctx.send(f"Произошла ошибка при выполнении команды: {e}")

@баланс.error
async def баланс_error(ctx, error):
    await ctx.send(f"Произошла ошибка при выполнении команды: {error}")

@bot.command()
@commands.has_any_role("Чудо", "Сфера", "Влад", "Сержант апельсин", "Берсерк")
async def получение_жрунов(ctx, member: discord.Member, amount: int = 1):
    await give_jrun(ctx, member, amount)
@получение_жрунов.error
async def получение_жрунов_error(ctx, error):
    if isinstance(error, commands.MissingAnyRole):
        await ctx.send("У вас нет прав для использования этой команды.")

#

# Токен
bot.run("MTE2NjYzODE2NTY1ODk3NjI3Nw.Gi1Xt0.0xhlWdERtyKuWQSupLmmN_hJ8FPdFXK9RKdvjU")
#Лото MTE2NjYzODE2NTY1ODk3NjI3Nw.Gi1Xt0.0xhlWdERtyKuWQSupLmmN_hJ8FPdFXK9RKdvjU
#Чудо MTIzMzAyMTQ4NzE3MTEwODkwNQ.GJHW7F.XZRRzqVMFKD4MW0N5yVzjJIfwFZdXuVICmWcRw
