#Чудо бот
import discord
import asyncio
from discord.ext import commands
import pytz
from datetime import datetime, timedelta
import random
import schedule
import json
import time
import datetime
import os

# Необходимые переменные
message_count = {}
TOP_LIST_FILE = "C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/top_list.json"
prefix = "!"
random_responses=[
    "Неактуально"
    ]
# бот
bot = commands.Bot(intents=discord.Intents.all(), case_insensitive=True, command_prefix=prefix)

ticket_data_file = "C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/tickets.json"
rewards = {
    100: {"Tier 4": 0.5, "Tier 5": 0.5},
    50: {"Tier 3": 1.0}
}
reaction_channel_id = 951816149291659274  # ID канала
reaction_emoji = '👍'  # реакция, за которую начисляется жрун

def reset_message_count():
    message_count.clear()

#Классы
class Bank:
    def __init__(self, filename):
        self.filename = filename
        self.balances = self.load_json()
        self.saved = False

    def load_json(self):
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.create_file()
            return {}
        except json.JSONDecodeError:
            return {}

    def save_json(self):
        with open(self.filename, 'w') as f:
            json.dump(self.balances, f, indent=4)

    def create_file(self):
        with open(self.filename, 'w') as f:
            json.dump({}, f, indent=4)

    def get_balance(self, user_id):
        return self.balances.get(str(user_id), {'balance': 0, 'username': '', 'user_id': user_id})['balance']

    def set_balance(self, user_id, balance):
        user_data = self.get_user_data(user_id)
        if user_data:
            self.balances[str(user_id)] = {'balance': balance, 'username': user_data['username'], 'user_id': user_id}
        else:
            self.balances[str(user_id)] = {'balance': balance, 'username': '', 'user_id': user_id}
        self.save_json()

    def increment_balance(self, user_id, amount):
        balance = self.get_balance(user_id)
        self.set_balance(user_id, balance + amount)
        self.saved = False  # Сбрасываем флаг

    def decrement_balance(self, user_id, amount):
        balance = self.get_balance(user_id)
        if balance >= amount:
            self.set_balance(user_id, balance - amount)
        else:
            raise ValueError("Insufficient funds")

    def update_balance(self, user_id, amount):
        self.increment_balance(user_id, amount)

    def get_user_data(self, user_id):
        return self.balances.get(str(user_id), {'balance': 0, 'username': '', 'user_id': user_id})

    def set_user_data(self, user_id, data):
        self.balances[str(user_id)] = data
        self.save_json()

class BankAccount:
    def __init__(self, filename, owner, balance=0):
        self.filename = filename
        self.owner = owner
        self.balance = balance
        self.bank = Bank(filename)
        try:
            self.load_data()
        except Exception as e:
            print(f"Ошибка при загрузке данных: {e}")

    def load_data(self):
        user_data = self.bank.get_user_data(self.owner)
        if user_data['balance'] == 0 and user_data['username'] == '':
            self.create_account()
        else:
            self.balance = user_data['balance']

    def create_account(self):
        self.bank.set_user_data(self.owner, {'balance': 0, 'username': '', 'user_id': self.owner})
        self.bank.save_json()

    def deposit(self, amount):
        self.balance += amount
        self.bank.set_balance(self.owner, self.balance)
        self.bank.save_json()
        print("Трабл строка 4 депозит")
        return self.balance

    def withdraw(self, amount):
        if amount > self.balance:
            print("Трабл условие ведра")
            raise ValueError("Insufficient funds")
        self.balance -= amount
        self.bank.set_balance(self.owner, self.balance)
        self.bank.save_json()

        return self.balance

    def get_balance(self):
        return self.bank.get_balance(self.owner)

    def give_jrun(self, user_id, amount=1):
        print("Трабл гив жрун")
        self.bank.increment_balance(user_id, amount)
        self.bank.save_json()




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

def give_jrun_for_message(user_id):
    if user_id not in message_count:
        message_count[user_id] = 0
    message_count[user_id] += 1
    account = BankAccount('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/Jrun_balance.json', user_id)
    account.give_jrun(user_id, 1)
    return True

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

async def convert_to_member(ctx, argument):
    try:
        member = await commands.MemberConverter().convert(ctx, argument)
    except commands.MemberNotFound:
        member = ctx.guild.get_member_named(argument)
    if not member:
        raise commands.BadArgument(f'Пользователь "{argument}" не найден.')
    return member

def check_last_reward_time(user_id):
    if not os.path.exists('JavaS/rewards.json'):
        with open('JavaS/rewards.json', 'w') as f:
            json.dump({}, f, indent=4)
    try:
        with open('JavaS/rewards.json', 'r') as f:
            rewards = json.load(f)
    except json.JSONDecodeError:
        rewards = {}
        with open('JavaS/rewards.json', 'w') as f:
            json.dump(rewards, f, indent=4)
    if str(user_id) not in rewards:
        rewards[str(user_id)] = {'last_reward_time': 0}
        with open('JavaS/rewards.json', 'w') as f:
            json.dump(rewards, f, indent=4)
    return rewards[str(user_id)]['last_reward_time']

def update_last_reward_time(user_id):
    rewards = check_last_reward_time(user_id)
    rewards[str(user_id)] = {'last_reward_time': time.time()}
    with open('JavaS/rewards.json', 'w') as f:
        json.dump(rewards, f, indent=4)

def can_receive_reward(user_id):
    last_reward_time = check_last_reward_time(user_id)
    current_time = time.time()
    return current_time - last_reward_time >= 86400  # 86400 секунд = 24 часа

def give_jrun_for_reaction(reaction, user):
    if reaction.message.channel.id == reaction_channel_id and reaction.emoji == reaction_emoji:
        now = datetime.datetime.utcnow()
        user_id = user.id
        try:
            with open('reaction_data.json', 'r+') as f:
                reaction_data = json.load(f)
        except FileNotFoundError:
            with open('reaction_data.json', 'w') as f:
                json.dump({}, f)
            reaction_data = {}
        user_data = reaction_data.get(str(user_id), {'last_reaction': None})
        last_reaction_date = datetime.datetime.strptime(user_data['last_reaction'], '%Y-%m-%d %H:%M:%S.%f') if user_data['last_reaction'] else None
        if not last_reaction_date or now - last_reaction_date > datetime.timedelta(days=1):
            reaction_data[str(user_id)] = {'last_reaction': now.strftime('%Y-%m-%d %H:%M:%S.%f')}
            with open('reaction_data.json', 'w') as f:
                json.dump(reaction_data, f)
            account = BankAccount('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/Jrun_balance.json', user_id)
            account.give_jrun(user_id, 1)
            return True
    return False

def update_last_message_time(user_id):
    try:
        with open('last_messages.json', 'r+') as f:
            last_messages = json.load(f)
    except FileNotFoundError:
        with open('last_messages.json', 'w') as f:
            json.dump({}, f)
        last_messages = {}
    except json.JSONDecodeError:
        last_messages = {}
    user_id_str = str(user_id)
    now = datetime.datetime.now(datetime.timezone.utc)
    last_message_time = last_messages.get(user_id_str, {'last_message': None})['last_message']
    if last_message_time is not None:
        last_message_date = datetime.datetime.strptime(last_message_time, '%Y-%m-%d %H:%M:%S.%f').replace(tzinfo=datetime.timezone.utc)
    else:
        last_message_date = None
    if not last_message_date or now - last_message_date > datetime.timedelta(days=1):
        last_messages[user_id_str] = {'last_message': now.strftime('%Y-%m-%d %H:%M:%S.%f')}
        with open('last_messages.json', 'w') as f:
            json.dump(last_messages, f)
        return True
    return False

def reset_last_message_time():
    with open('last_messages.json', 'w') as f:
        json.dump({}, f)

schedule.every().day.at("00:00").do(reset_last_message_time)  # 0:00 по времени Сахалину

def get_today():
    return datetime.now().strftime('%Y-%m-%d')

def read_data():
    try:
        with open('JavaS/percentages.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"Произошла ошибка при чтении файла: {e}")
        return {}

def write_data(data):
    with open('JavaS/percentages.json', 'w') as file:
        json.dump(data, file, indent=4)

def update_last_reward_time(member_id):
    with open('JavaS/rewards.json', 'r+') as f:
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

def has_moderator_role(user):
    moderator_roles = ['Чудо', 'Влад', 'Сфера', 'роль1']
    for role in user.roles:
        if role.name in moderator_roles:
            return True

#запуск Бота
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

# Ошибка в написанни команды
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        response = random.choice(["Эта команда неактуальна"])
        await ctx.send(response)

# Ответ на любое сообщение
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if update_last_message_time(message.author.id):
        account = BankAccount('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/Jrun_balance.json', message.author.id)
        account.give_jrun(message.author.id, 1)
        await message.add_reaction('🔥')
    await bot.process_commands(message)
    
@bot.event
async def on_reaction_add(reaction, user):
    if user == bot.user:
        return
    give_jrun_for_reaction(reaction, user)

# Команда - Время
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


# пнуть
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


# Лотерейка - test version
@bot.command(name='add_tickets')
@commands.has_any_role("Чудо", "Сфера", "Влад", "Сержант апельсин", "Берсерк")
async def add_tickets_command(ctx, member: discord.Member, amount: int):
    if amount <= 0:
        await ctx.send("Количество билетов должно быть положительным.")
        return
    add_tickets(member.id, amount)
    await ctx.send(f"{amount} билетов добавлено пользователю {member.mention}.")

# Мои билетики
@bot.command(name='my_tickets')
async def my_tickets_command(ctx):
    tickets = get_user_tickets(ctx.author.id)
    await ctx.send(f"У вас {tickets} билетов.")

# крутка билетиков
@bot.command(name='lottery')
async def lottery_command(ctx):
    result = draw_lottery(ctx.author.id)
    await ctx.send(result)

# HELP команды жрунов
@bot.command()
async def help_jrun(ctx):
    guide = """
**Команды для работы с Жрунами**

**Выдать Жруны**
`!mod_выдать <пользователь> <количество>` - начислить Жруны пользователю

**Проверить баланс**
`!mod_баланс <пользователь>` - проверить баланс пользователя

**Положить Жруны**
`!mod_положить <пользователь> <количество>` - положить Жруны на счет пользователя

**Снять Жруны**
`!mod_снять <пользователь> <количество>` - снять Жруны с счета пользователя


"""
    await ctx.send(guide)

#Bank Sistem Жруны!

#@bot.command(name='выдать')
#async def give_jrun(ctx, user: discord.Member, amount: int):
#    print("Трабл Запуска")
#    try:
#        account = BankAccount('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/Jrun_balance.json', user.id)
#        print("Трабл строка 1")
#        if account.balance is not None:
#            account.give_jrun(user.id, amount)
#            print("Трабл строка 2")
#            await ctx.send(f'Начислено {amount} Жрунов пользователю {user.mention}!')
#        else:
#            await ctx.send(f'Пользователь {user.mention} не имеет счета!')
#    except Exception as e:
#        await ctx.send(f'Ошибка: {e}')

#@bot.command(name='снять')
#async def withdraw(ctx, user: discord.Member, amount: int):
#    print("Трабл запуска")
#    account = BankAccount('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/Jrun_balance.json', user.id)
#    print("Трабл строка 1")
#    try:
#        account.withdraw(amount)
#        print("Трабл строка 2")
#        await ctx.send(f'Снято {amount} Жрунов с счета пользователя {user.mention}!')
#        print("Трабл строка 3")
#    except ValueError:
#        print("Трабл финал")
#        await ctx.send('Недостаточно средств на счете!')

#@bot.command(name='баланс')
#async def balance(ctx, user: discord.Member):
#    bank = Bank('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/Jrun_balance.json')
#    balance = bank.get_balance(user.id)
#    await ctx.send(f'Баланс пользователя {user.mention}: {balance} Жрунов')

@bot.command(name='mod_выдать')
async def mod_give_jrun(ctx, user: discord.Member, amount: int):
    if not has_moderator_role(ctx.author):
        await ctx.send('У вас нет прав для использования этой команды!')
        return
    try:
        account = BankAccount('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/Jrun_balance.json', user.id)
        account.give_jrun(user.id, amount)
        await ctx.send(f'Начислено {amount} Жрунов пользователю {user.mention}!')
    except Exception as e:
        await ctx.send(f'Ошибка: {e}')

@bot.command(name='mod_положить')
async def mod_deposit(ctx, user: discord.Member, amount: int):
    if not has_moderator_role(ctx.author):
        await ctx.send('У вас нет прав для использования этой команды!')
        return
    try:
        account = BankAccount('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/Jrun_balance.json', user.id)
        account.deposit(amount)
        await ctx.send(f'Начислено {amount} Жрунов на счет пользователя {user.mention}!')
    except Exception as e:
        await ctx.send(f'Ошибка: {e}')

@bot.command(name='mod_снять')
async def mod_withdraw(ctx, user: discord.Member, amount: int):
    if not has_moderator_role(ctx.author):
        await ctx.send('У вас нет прав для использования этой команды!')
        return
    try:
        account = BankAccount('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/Jrun_balance.json', user.id)
        account.withdraw(amount)
        await ctx.send(f'Снято {amount} Жрунов с счета пользователя {user.mention}!')
    except ValueError:
        await ctx.send('Недостаточно средств на счете!')
    except Exception as e:
        await ctx.send(f'Ошибка: {e}')

@bot.command(name='mod_баланс')
async def mod_balance(ctx, user: discord.Member):
    if not has_moderator_role(ctx.author):
        await ctx.send('У вас нет прав для использования этой команды!')
        return
    bank = Bank('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/Jrun_balance.json')
    balance = bank.get_balance(user.id)
    await ctx.send(f'Баланс пользователя {user.mention}: {balance} Жрунов')

@bot.command(name='баланс')
async def balance(ctx):
    bank = Bank('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/Jrun_balance.json')
    balance = bank.get_balance(ctx.author.id)
    await ctx.send(f'Ваш баланс: {balance} Жрунов')

#Добавление новых команд для взаимодействия со счетом в процессе!
exit_while = 0
while exit_while == 0:
    schedule.run_pending()
    time.sleep(1)
    exit_while+=1

# Токен
bot.run("MTE2NjYzODE2NTY1ODk3NjI3Nw.Gi1Xt0.0xhlWdERtyKuWQSupLmmN_hJ8FPdFXK9RKdvjU")
#Лото MTE2NjYzODE2NTY1ODk3NjI3Nw.Gi1Xt0.0xhlWdERtyKuWQSupLmmN_hJ8FPdFXK9RKdvjU
#Чудо MTIzMzAyMTQ4NzE3MTEwODkwNQ.GJHW7F.XZRRzqVMFKD4MW0N5yVzjJIfwFZdXuVICmWcRw
