#Чудо бот
import discord
import asyncio
from discord.ext import commands #только библиотека Discord.py
from discord.ui import View, Button
import pytz
from datetime import datetime, timedelta
import random #рандом
import shutil 
import schedule
import json # JSON файлы (Можно использовать базы данных!)
import time
import datetime #дата тайм и тайм дельта и pytz
import os # Владение ПК - OS

# Необходимые переменные
message_count = {}
TOP_LIST_FILE = "C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/top_list.json" # топ лист жопок
prefix = "!"
random_responses=[
    "Неактуально" # рандомные фразы на ошибочную команду
    ]
# бот INTENTS 
bot = commands.Bot(intents=discord.Intents.all(), case_insensitive=True, command_prefix=prefix)
price_rad1=random.randint(1, 10)
price_rad2=random.randint(10, 20)
price_rad3=random.randint(15, 25)
ticket_data_file = "C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/tickets.json"
rewards = {
    100: {"Tier 4": 0.5, "Tier 5": 0.5}, # Лотерейка
    50: {"Tier 3": 1.0}
}
presence_data = {} # похождения юзеров на сервере (жруны за 7 дней)
reaction_channel_id = 1179745995345645609  # ID канала
DATA_DIR = 'C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/'
BALANCE_FILE = 'C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/Jrun_balance.json'
Rili1=1291219768032104460#1292412725632303125# 
Rili2=1292393218175930379#1292412752060481606#
Rili3=1282958916657086508#1292412753360715798#
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
        print("Трабл гив жрун ", {user_id})
        self.bank.increment_balance(user_id, amount)
        self.bank.save_json()

# Функции
def has_moderator_role(user): # роли модеров
    moderator_roles = ['Чудо', 'Влад', 'Сфера', 'роль1']
    for role in user.roles:
        if role.name in moderator_roles:
            return True

################################################################################################
################################################################################################
####### Комиссия 


################################################################################################
################################################################################################
####### ПОЛУЧЕНИЕ ЖРУНОВ для АЛЛ ЮЗЕРС
def give_jrun_for_message(user_id, guild_id, message):
    if user_id not in message_count:
        message_count[user_id] = 0
    message_count[user_id] += 1
    account = BankAccount('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/Jrun_balance.json', user_id)
    account.give_jrun(user_id, 1)
    member = bot.get_guild(guild_id).get_member(user_id)
    if "Огонь" in [role.name for role in member.roles]:
        account.give_jrun(user_id, 1) 
    async def add_reaction():
        await message.add_reaction('✅')
    bot.loop.create_task(add_reaction())
    return True

def give_jrun_for_reaction(reaction, user): 
    if reaction.message.channel.id == reaction_channel_id:
        now = datetime.datetime.now(datetime.timezone.utc)
        user_id = user.id
        try:
            with open(DATA_DIR + 'reaction_data.json', 'r+') as f:
                try:
                    reaction_data = json.load(f)
                except json.JSONDecodeError:
                    reaction_data = {}
        except FileNotFoundError:
            with open(DATA_DIR + 'reaction_data.json', 'w') as f:
                json.dump({}, f)
            reaction_data = {}
        user_data = reaction_data.get(str(user_id), {'last_reaction': None})
        last_reaction_date = datetime.datetime.strptime(user_data['last_reaction'], '%Y-%m-%d %H:%M:%S.%f').replace(tzinfo=datetime.timezone.utc) if user_data['last_reaction'] else None
        if not last_reaction_date or now - last_reaction_date > datetime.timedelta(days=1):
            reaction_data[str(user_id)] = {'last_reaction': now.strftime('%Y-%m-%d %H:%M:%S.%f')}
            with open(DATA_DIR + 'reaction_data.json', 'w') as f:
                json.dump(reaction_data, f)
            account = BankAccount(DATA_DIR + 'reaction_data.json', user_id)
            account.give_jrun(user_id, 1)
            print ("Выдача 1-ого жруна за реакцию")
            if "Огонь" in [role.name for role in user.roles]:
                account.give_jrun(user_id, 1)
                print ("Выдача 2-ого жруна за реакцию")
            return True
    return False

def give_jrun_for_all_members():
    for member in bot.get_all_members():
        if update_last_message_time(member.id):
            account = BankAccount(DATA_DIR + 'reaction_data.json', member.id)
            account.give_jrun(member.id, 1)
            if "Огонь" in [role.name for role in member.roles]:
                print("Получение жруна Алл мемберс")
                account.give_jrun(member.id, 1)
        give_jrun_for_presence(member)

def give_jrun_for_presence(user):
    bank = Bank('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/Jrun_balance.json')
    balance = bank.get_balance(user.id)
    if balance > 0:
        try:
            with open(DATA_DIR + 'reaction_data.json', 'r+') as f:
                first_jrun_dates = json.load(f)
        except FileNotFoundError:
            with open(DATA_DIR + 'reaction_data.json', 'w') as f:
                json.dump({}, f)
            first_jrun_dates = {}
        first_jrun_date = first_jrun_dates.get(str(user.id), None)
        if first_jrun_date:
            now = datetime.datetime.now(datetime.timezone.utc)
            first_jrun_date_obj = datetime.datetime.strptime(first_jrun_date, '%Y-%m-%d %H:%M:%S.%f').replace(tzinfo=datetime.timezone.utc)
            days_since_first_jrun = (now - first_jrun_date_obj).days
            if days_since_first_jrun >= 7:
                print("{user.id} получил еженедельные жруны!")
                bank.increment_balance(user.id, 2)
                if "Огонь" in [role.name for role in user.roles]:
                    bank.increment_balance(user.id, 2)
                first_jrun_dates[str(user.id)] = now.strftime('%Y-%m-%d %H:%M:%S.%f')
                with open(DATA_DIR + 'reaction_data.json', 'w') as f:
                    json.dump(first_jrun_dates, f)
                    
def set_first_jrun_date(user_id):
    with open('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/jrun_balance.json', 'r+') as f_balance:
        try:
            jrun_balance = json.load(f_balance)
        except json.JSONDecodeError:
            jrun_balance = {}
    print("Опа человечек")
    if str(user_id) not in jrun_balance:
        print("Человечка нет в списках")
        return  # если пользователя нет в jrun_balance, игнорируем запрос
    print("Человечек прошел условия")
    with open('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/first_jrun_date.json', 'r+') as f_date:
        try:
            first_jrun_dates = json.load(f_date)
        except json.JSONDecodeError:
            first_jrun_dates = {}

        if str(user_id) not in first_jrun_dates:
            current_date = datetime.datetime.now(datetime.timezone.utc)
            first_jrun_date = current_date.strftime('%Y-%m-%d %H:%M:%S.%f')
            first_jrun_dates[str(user_id)] = first_jrun_date
            f_date.seek(0)
            json.dump(first_jrun_dates, f_date)
            f_date.truncate()


################################################################################################
################################################################################################
###### Сброс файлов для получения жрунов
def reset_message_count():
    global message_count
    message_count = {}

def reset_last_message_time():
    with open('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/last_messages.json', 'w') as f:
        json.dump({}, f)

def reset_reaction_count():
    with open('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/reaction_data.json', 'w') as f:
        json.dump({}, f)

##############################################################################################
### Разнорабочие функции ###
def get_user_asses(user_id):
    try:
        with open(TOP_LIST_FILE, "r") as file:
            top_list = json.load(file)
            for user_info in top_list:
                if user_info['никнейм'] == bot.get_user(user_id).name:
                    return user_info['жопки']
    except FileNotFoundError:
        return 0
    return 0

def reset_balance_on_leave(user): # Очищение баланса при лива с сервера
    bank = Bank('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/Jrun_balance.json')
    bank.set_balance(user.id, 0)
    try:
        with open('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/first_jrun_date.json', 'r+') as f:
            first_jrun_dates = json.load(f)
        first_jrun_dates.pop(str(user.id), None)
        with open('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/first_jrun_date.json', 'w') as f:
            json.dump(first_jrun_dates, f)
    except FileNotFoundError:
        pass

def update_last_message_time(user_id): #Файл с последним сообщением
    try:
        with open('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/last_messages.json', 'r+') as f:
            last_messages = json.load(f)
    except FileNotFoundError:
        with open('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/last_messages.json', 'w') as f:
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
        with open('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/last_messages.json', 'w') as f:
            json.dump(last_messages, f)
        return True
    return False

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

def update_last_message_time(user_id):
    try:
        with open('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/last_messages.json', 'r+') as f:
            last_messages = json.load(f)
    except FileNotFoundError:
        with open('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/last_messages.json', 'w') as f:
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
        with open('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/last_messages.json', 'w') as f:
            json.dump(last_messages, f)
        return True
    return False

def reset_last_message_time():
    with open('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/last_messages.json', 'w') as f:
        json.dump({}, f)

def get_today():
    return datetime.now().strftime('%Y-%m-%d')

def read_data():
    try:
        with open('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/percentages.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"Произошла ошибка при чтении файла: {e}")
        return {}

def write_data(data):
    with open('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/percentages.json', 'w') as file:
        json.dump(data, file, indent=4)

def update_last_reward_time(member_id):
    with open('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/rewards.json', 'r+') as f:
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


#######

################################################################################################

schedule.every().day.at("00:00").do(reset_last_message_time)
schedule.every(1).day.at("00:00").do(give_jrun_for_all_members)
schedule.every().day.at("00:00").do(reset_message_count)
schedule.every().day.at("00:00").do(reset_reaction_count)


################################################################################################
#запуск Бота
@bot.event
async def on_ready():
    print(f"{bot.user.name} успешно запущен")

@bot.event #пришел юзер
async def on_member_join(member):
    give_jrun_for_presence(member)
@bot.event #ушел юзер
async def on_member_remove(member):
    reset_balance_on_leave(member)


#Евриван Сообщение
@bot.event
async def on_message(message):
    if not message.content.startswith('!'):
        return
    if message.author == bot.user:
        return

    user_id = message.author.id
    print("Это нам нужно")
    set_first_jrun_date(user_id)
    moderator_roles = ["Чудо", "Сфера", "Влад", "роль1", "Берсерк"]
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

@bot.event #отладчик ошибочных команд
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        response = random.choice(["Эта команда неактуальна"])
        await ctx.send(response)

@bot.event #выдача Жруна за сообщение
async def on_message(message):
    if message.author == bot.user:
        return
    if update_last_message_time(message.author.id):
        give_jrun_for_message(message.author.id, message.guild.id, message)
    await bot.process_commands(message)
    user_id = message.author.id
    print("Опа, книжечка")
    set_first_jrun_date(user_id)

@bot.event #Выдача жруна за реакцию
async def on_reaction_add(reaction, user):
    if user == bot.user:
        return
    give_jrun_for_reaction(reaction, user)
############################################################################################################
@bot.event # обработчик кнопок !для магазина и !для Жопника



############################################################################################################

@bot.event
async def on_member_remove(member):
    user_id = member.id
    try:
        with open('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/presence_data.json', 'r+') as f:
            presence_data = json.load(f)
    except FileNotFoundError:
        with open('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/presence_data.json', 'w') as f:
            json.dump({}, f)
        presence_data = {}
    user_data = presence_data.get(str(user_id), {'join_date': None})
    now = datetime.datetime.now(datetime.timezone.utc)
    presence_data[str(user_id)] = {'join_date': None}
    with open('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/presence_data.json', 'w') as f:
        json.dump(presence_data, f)

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
#@bot.command(name='add_tickets')
#@commands.has_any_role("Чудо", "Сфера", "Влад", "Сержант апельсин", "Берсерк")
#async def add_tickets_command(ctx, member: discord.Member, amount: int):
#    if amount <= 0:
#        await ctx.send("Количество билетов должно быть положительным.")
#        return
#    add_tickets(member.id, amount)
#    await ctx.send(f"{amount} билетов добавлено пользователю {member.mention}.")

# Мои билетики
#@bot.command(name='my_tickets')
#async def my_tickets_command(ctx):
#    tickets = get_user_tickets(ctx.author.id)
#    await ctx.send(f"У вас {tickets} билетов.")

# крутка билетиков
#@bot.command(name='lottery')
#async def lottery_command(ctx):
#    result = draw_lottery(ctx.author.id)
#    await ctx.send(result)

# HELP команды жрунов
@bot.command(name='помощь')
async def help_jrun(ctx):
    guide = """
**Команды бота**

**Базовые команды**
`!Время` - Команда времени у Чудачки
`!Вкплей` - ссылка на площадку Vk Play Live Чудачки
`!Твич` - ссылка на площадку Twitch
`!Дискорд` - ссылка на данный Discord сервер (Сервер Чудачки)
`!ПК` - конфигурация ПК Чудачки
`!Мемы` - ссылка на Мем Алертс Чудачки
`!Бусти` - ссылка на Бусти Чудачки
`!Гдестрим` - это вопрос? Бот ответит когда будет следующий стрим.
`!Дота` - стоимость за которую Чудо поиграет в доту
`!Танки` - стоимость игры в танки

**Жопки**
`!Жопка` - Топ владельцев жопок

**Пнуть пользователя**
`!пнуть <@user>` - пинает пользователя в ЛС

**Жопник**
`!Жопник` - открывает функционал Жопника

**Магазин**
`!магаз` - открыть магазин для покупки ролей и других товаров

"""
    await ctx.send(guide)

@bot.command(name='mod_help')
async def help_mod(ctx):
    moderator_roles = ["Чудо", "Сфера", "Влад", "Сержант апельсин", "Берсерк"]
    if not any(role.name in moderator_roles for role in ctx.author.roles):
        await ctx.send("Ошибка: У вас нет прав для использования этой команды.")
        return
    guide = """
**Команды для модераторов**

**Выдать Жруны**
`!mod_выдать <пользователь> <количество>` - начислить Жруны пользователю

**Проверить баланс**
`!mod_баланс <пользователь>` - проверить баланс пользователя

**Положить Жруны**
`!mod_положить <пользователь> <количество>` - положить Жруны на счет пользователя

**Снять Жруны**
`!mod_снять <пользователь> <количество>` - снять Жруны с счета пользователя

**Манипуляция жопок**
`!НоваяЖопка <@user>`- создание новой жопки у юзера. Базовое значение 2.
`!НомераЖопок`- список всех жопок, для удобности перевода.
`!ПеревестиЖопки <@user минус> <@user плюс>`- перевод жопок от одного пользователя к другому.
`!минус <@user>`- вычесть у <@user> кол-во жопок
`!плюс <@user>`- добавить <@user> жопки

"""
    await ctx.send(guide)

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

############# Магазин ###################
'''
@bot.command(name="магаз")
async def shop(ctx):
    print("Начала")
    embed = discord.Embed(title="Магазин", description="Выберите товар, который хотите купить")
    embed.add_field(name="Роль 1", value="100 Жрунов", inline=False)
    embed.add_field(name="Роль 2", value="200 Жрунов", inline=False)
    embed.add_field(name="Роль 3", value="300 Жрунов", inline=False)
    # Добавьте здесь свои товары

    view = View()
    button1 = Button(label="Роль 1", style=discord.ButtonStyle.green, custom_id="role1")
    button2 = Button(label="Роль 2", style=discord.ButtonStyle.green, custom_id="role2")
    button3 = Button(label="Роль 3", style=discord.ButtonStyle.green, custom_id="role3")
    # Добавьте здесь свои кнопки

    async def button_callback(interaction: discord.Interaction):
        print("насяла класс 1")
        if interaction.data.get("custom_id") == "role1":
            item = "Роль 1"
            price = 100
            role_id = Rili1  # ID роли 1
        elif interaction.data.get("custom_id") == "role2":
            item = "Роль 2"
            price = 200
            role_id = Rili2  # ID роли 2
        elif interaction.data.get("custom_id") == "role3":
            item = "Роль 3"
            price = 300
            role_id = Rili3  # ID роли 3
        # Добавьте здесь свои кнопки

        user_id = interaction.user.id
        bank = Bank('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/Jrun_balance.json')
        balance = bank.get_balance(user_id)
        print("перевирка баласа")
        if balance >= price:
            bank.decrement_balance(user_id, price)
            role = interaction.guild.get_role(role_id)
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"Вы успешно купили {item} за {price} Жрунов")
        else:
            await interaction.response.send_message("У вас недостаточно Жрунов для покупки этого товара")

    button1.callback = button_callback
    button2.callback = button_callback
    button3.callback = button_callback

    view.add_item(button1)
    view.add_item(button2)
    view.add_item(button3)

    await ctx.send(embed=embed, view=view)
'''
###########################################################
#######################  ЖОПНИК ###########################

@bot.command(name="меню")
async def menu(ctx):
    await menu1(ctx)
##############################################################
async def menu1(ctx):
    button1_1 = "Магазин"
    button1_2 = "Репутация"
    button1_3 = "Комиссия"

    embed = discord.Embed(title="Меню", description="Выберите пункт меню")
    embed.add_field(name="Пункт 1", value=button1_1, inline=False)
    embed.add_field(name="Пункт 2", value=button1_2, inline=False)
    embed.add_field(name="Пункт 3", value=button1_3, inline=False)

    view = View()
    button1 = Button(label=button1_1, style=discord.ButtonStyle.green, custom_id="menu1_1")
    button2 = Button(label=button1_2, style=discord.ButtonStyle.green, custom_id="menu1_2")
    button3 = Button(label=button1_3, style=discord.ButtonStyle.green, custom_id="menu1_3")

    async def button_callback(interaction: discord.Interaction):
        if interaction.data.get("custom_id") == "menu1_1":
            await menu2(interaction)
        elif interaction.data.get("custom_id") == "menu1_2":
            await menu3(interaction)
        elif interaction.data.get("custom_id") == "menu1_3":
            await menu4(interaction)

    button1.callback = button_callback
    button2.callback = button_callback
    button3.callback = button_callback

    view.add_item(button1)
    view.add_item(button2)
    view.add_item(button3)

    await ctx.send(embed=embed, view=view)

####################################################
async def menu2(interaction: discord.Interaction):
    button2_1 = "Начальный"
    button2_2 = "Опытный"
    button2_3 = "Продвинутый"
    button2_4 = "Назад"

    embed = discord.Embed(title="Меню 2", description="Выберите пункт меню")
    embed.add_field(name="Пункт 1", value=button2_1, inline=False)
    embed.add_field(name="Пункт 2", value=button2_2, inline=False)
    embed.add_field(name="Пункт 3", value=button2_3, inline=False)

    view = View()
    button1 = Button(label=button2_1, style=discord.ButtonStyle.green, custom_id="menu2_1")
    button2 = Button(label=button2_2, style=discord.ButtonStyle.green, custom_id="menu2_2")
    button3 = Button(label=button2_3, style=discord.ButtonStyle.green, custom_id="menu2_3")
    button4 = Button(label=button2_4, style=discord.ButtonStyle.red, custom_id="menu2_4")

    async def button_callback(interaction: discord.Interaction):
        if interaction.data.get("custom_id") == "menu2_1":
            await menu1(interaction)  # <--- Add this line
        elif interaction.data.get("custom_id") == "menu2_2":
            # логика для кнопки 2
            pass
        elif interaction.data.get("custom_id") == "menu2_3":
            # логика для кнопки 3
            pass
        elif interaction.data.get("custom_id") == "menu2_4":
            await menu1(interaction)

    button1.callback = button_callback
    button2.callback = button_callback
    button3.callback = button_callback
    button4.callback = button_callback

    view.add_item(button1)
    view.add_item(button2)
    view.add_item(button3)
    view.add_item(button4)

    await interaction.response.edit_message(embed=embed, view=view)

####################################################
async def menu3(interaction: discord.Interaction):
    button3_1 = "Пункт 1"
    button3_2 = "Пункт 2"
    button3_3 = "Пункт 3"
    button3_4 = "Назад"

    embed = discord.Embed(title="Меню 3", description="Выберите пункт меню")
    embed.add_field(name="Пункт 1", value=button3_1, inline=False)
    embed.add_field(name="Пункт 2", value=button3_2, inline=False)
    embed.add_field(name="Пункт 3", value=button3_3, inline=False)

    view = View()
    button1 = Button(label=button3_1, style=discord.ButtonStyle.green, custom_id="menu3_1")
    button2 = Button(label=button3_2, style=discord.ButtonStyle.green, custom_id="menu3_2")
    button3 = Button(label=button3_3, style=discord.ButtonStyle.green, custom_id="menu3_3")
    button4 = Button(label=button3_4, style=discord.ButtonStyle.red, custom_id="menu3_4")

    async def button_callback(interaction: discord.Interaction):
        if interaction.data.get("custom_id") == "menu3_1":
            # логика для кнопки 1
            pass
        elif interaction.data.get("custom_id") == "menu3_2":
            # логика для кнопки 2
            pass
        elif interaction.data.get("custom_id") == "menu3_3":
            # логика для кнопки 3
            pass
        elif interaction.data.get("custom_id") == "menu3_4":
            await menu1(interaction)

    button1.callback = button_callback
    button2.callback = button_callback
    button3.callback = button_callback
    button4.callback = button_callback

    view.add_item(button1)
    view.add_item(button2)
    view.add_item(button3)
    view.add_item(button4)

    await interaction.response.edit_message(embed=embed, view=view)

#####################################################
async def menu4(interaction: discord.Interaction):
    button4_1 = "Пункт 1"
    button4_2 = "Пункт 2"
    button4_3 = "Пункт 3"
    button4_4 = "Назад"

    embed = discord.Embed(title="Меню 4", description="Выберите пункт меню")
    embed.add_field(name="Пункт 1", value=button4_1, inline=False)
    embed.add_field(name="Пункт 2", value=button4_2, inline=False)
    embed.add_field(name="Пункт 3", value=button4_3, inline=False)

    view = View()
    button1 = Button(label=button4_1, style=discord.ButtonStyle.green, custom_id="menu4_1")
    button2 = Button(label=button4_2, style=discord.ButtonStyle.green, custom_id="menu4_2")
    button3 = Button(label=button4_3, style=discord.ButtonStyle.green, custom_id="menu4_3")
    button4 = Button(label=button4_4, style=discord.ButtonStyle.red, custom_id="menu4_4")

    async def button_callback(interaction: discord.Interaction):
        if interaction.data.get("custom_id") == "menu4_1":
            # логика для кнопки 1
            pass
        elif interaction.data.get("custom_id") == "menu4_2":
            # логика для кнопки 2
            pass
        elif interaction.data.get("custom_id") == "menu4_3":
            # логика для кнопки 3
            pass
        elif interaction.data.get("custom_id") == "menu4_4":
            await menu1(interaction)

    button1.callback = button_callback
    button2.callback = button_callback
    button3.callback = button_callback
    button4.callback = button_callback

    view.add_item(button1)
    view.add_item(button2)
    view.add_item(button3)
    view.add_item(button4)

    await interaction.response.edit_message(embed=embed, view=view)




def update_commission():
    try:
        with open('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/jopnik.json', 'r') as f:
            jopnik_data = json.load(f)
    except FileNotFoundError:
        with open('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/jopnik.json', 'w') as f:
            json.dump({'balance': 0, 'commission': 0}, f)
        jopnik_data = {'balance': 0, 'commission': 0}

    jopnik_data['commission'] = random.randint(3, 27)
    with open('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/jopnik.json', 'w') as f:
        json.dump(jopnik_data, f)

schedule.every().day.at("00:00").do(update_commission)

###########################################################
#################### PROFILE ##############################

@bot.command(name='профиль')
async def profile(ctx):
    user_id = ctx.author.id
    bank = Bank('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/Jrun_balance.json')
    balance = bank.get_balance(user_id)
    try:
        with open('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/first_jrun_date.json', 'r') as f:
            first_jrun_dates = json.load(f)
    except FileNotFoundError:
        with open('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/first_jrun_date.json', 'w') as f:
            json.dump({}, f)
        first_jrun_dates = {}
    first_jrun_date = first_jrun_dates.get(str(user_id), None)
    if first_jrun_date:
        now = datetime.datetime.now(datetime.timezone.utc)
        first_jrun_date_obj = datetime.datetime.strptime(first_jrun_date, '%Y-%m-%d %H:%M:%S.%f').replace(tzinfo=datetime.timezone.utc)
        days_since_first_jrun = (now - first_jrun_date_obj).days
    else:
        days_since_first_jrun = 0
    try:
        with open(TOP_LIST_FILE, "r") as file:
            top_list = json.load(file)
            for user_info in top_list:
                if user_info['никнейм'] == bot.get_user(user_id).name:
                    asses = user_info['жопки']
                    break
            else:
                asses = 0
    except FileNotFoundError:
        asses = 0
    embed = discord.Embed(title="Профиль", description=f"Профиль пользователя {ctx.author.mention}")
    embed.set_thumbnail(url=ctx.author.display_avatar.url)
    embed.add_field(name="Никнейм", value=ctx.author.name, inline=False)
    embed.add_field(name="Баланс Жрунов", value=balance, inline=False)
    embed.add_field(name="Баланс Жопок", value=asses, inline=False)
    embed.add_field(name="Дней с первого жруна", value=days_since_first_jrun, inline=False)
    await ctx.send(embed=embed)




###
'''
@bot.command(name="жопник")
async def jopnik(ctx):
    embed = discord.Embed(title="Магнат Комиссорионович Жопник, приветствует тебя!", description="Чего изволите?")
    embed.add_field(name="Магазин", value="Предлагаемые товары", inline=False)
    embed.add_field(name="Репутация", value="Отношение Жопника к тебе", inline=False)
    # Добавьте здесь свои действия

    view = View()
    button1 = Button(label="Магазин", style=discord.ButtonStyle.green, custom_id="shop")
    button2 = Button(label="Репутация", style=discord.ButtonStyle.green, custom_id="reputation")
    # Добавьте здесь свои кнопки

    async def button_callback(interaction: discord.Interaction):
        if interaction.data.get("custom_id") == "shop":
            await shop_callback(interaction)
        elif interaction.data.get("custom_id") == "reputation":
            await reputation_callback(interaction)

    async def shop_callback(interaction: discord.Interaction):
        shop_embed = discord.Embed(title="Магазин", description="Выберите товар, который хотите купить")
        shop_embed.add_field(name="Начальный", value="1 Жрун", inline=False)
        shop_embed.add_field(name="Роль 2", value="200 Жрунов", inline=False)
        shop_embed.add_field(name="Роль 3", value="300 Жрунов", inline=False)
        # Добавьте здесь свои товары

        shop_view = View()
        button1 = Button(label="Назад", style=discord.ButtonStyle.red, custom_id="back")
        button2 = Button(label="Начальный", style=discord.ButtonStyle.green, custom_id="role1")
        button3 = Button(label="Роль 2", style=discord.ButtonStyle.green, custom_id="role2")
        button4 = Button(label="Роль 3", style=discord.ButtonStyle.green, custom_id="role3")
        # Добавьте здесь свои кнопки

        async def shop_callback2(interaction: discord.Interaction):
            if interaction.data.get("custom_id") == "back":
                await interaction.response.edit_message(embed=jopnik_embed, view=jopnik_view)
            elif interaction.data.get("custom_id") in ["role1", "role2", "role3"]:
                if interaction.data.get("custom_id") == "role1":
                    item = "Роль 1"
                    price = 100
                    role_id = Rili1  # ID роли 1
                elif interaction.data.get("custom_id") == "role2":
                    item = "Роль 2"
                    price = 200
                    role_id = Rili2  # ID роли 2
                elif interaction.data.get("custom_id") == "role3":
                    item = "Роль 3"
                    price = 300
                    role_id = Rili3  # ID роли 3

                user_id = interaction.user.id
                bank = Bank('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/Jrun_balance.json')
                balance = bank.get_balance(user_id)
                print("перевирка баласа")
                if balance >= price:
                    bank.decrement_balance(user_id, price)
                    role = interaction.guild.get_role(role_id)
                    await interaction.user.add_roles(role)
                    embed = discord.Embed(title="Спасибо за покупку!", description=f"Вы успешно купили {item} за {price} Жрунов")
                    view = View()
                    button1 = Button(label="Назад", style=discord.ButtonStyle.green, custom_id="back")
                    async def back_callback(interaction: discord.Interaction):
                        await interaction.response.edit_message(embed=jopnik_embed, view=jopnik_view)
                    button1.callback = back_callback
                    view.add_item(button1)
                    await interaction.response.edit_message(embed=embed, view=view)
                else:
                    embed = discord.Embed(title="Недостаточно Жрунов", description="Вам не хватает Жрунов для покупки этого товара. Возвращайтесь когда накопите.")
                    view = View()
                    button1 = Button(label="Назад", style=discord.ButtonStyle.green, custom_id="back")
                    async def back_callback(interaction: discord.Interaction):
                        await interaction.response.edit_message(embed=jopnik_embed, view=jopnik_view)
                    button1.callback = back_callback
                    view.add_item(button1)
                    await interaction.response.edit_message(embed=embed, view=view)

        button1.callback = shop_callback2
        button2.callback = shop_callback2
        button3.callback = shop_callback2
        button4.callback = shop_callback2

        shop_view.add_item(button1)
        shop_view.add_item(button2)
        shop_view.add_item(button3)
        shop_view.add_item(button4)

        await interaction.response.edit_message(embed=shop_embed, view=shop_view)

    async def reputation_callback(interaction: discord.Interaction):
        user_id = interaction.user.id
        try:
            with open('rep.json', 'r') as f:
                reputation_data = json.load(f)
        except FileNotFoundError:
            with open('rep.json', 'w') as f:
                json.dump({}, f)
            reputation_data = {}
        reputation = reputation_data.get(str(user_id), 0)
        embed = discord.Embed(title="Репутация", description=f"Ваша репутация: {reputation}")
        view = View()
        button1 = Button(label="Назад", style=discord.ButtonStyle.green, custom_id="back")
        button2 = Button(label="{No Name}", style=discord.ButtonStyle.red, custom_id="delete")
        async def reputation_callback2(interaction: discord.Interaction):
            if interaction.data.get("custom_id") == "back":
                await interaction.response.edit_message(embed=jopnik_embed, view=jopnik_view)
            elif interaction.data.get("custom_id") == "delete":
                await interaction.response.defer()
                await interaction.delete_original_response()
        button1.callback = reputation_callback2
        button2.callback = reputation_callback2
        view.add_item(button1)
        view.add_item(button2)
        await interaction.response.edit_message(embed=embed, view=view)

    button1.callback = button_callback
    button2.callback = button_callback

    view.add_item(button1)
    view.add_item(button2)

    jopnik_embed = embed
    jopnik_view = view

    await ctx.send(embed=embed, view=view)
'''
###########





###############################################################
## Команда профиль - выводит стату пользователя (Жруны / жопки)

#Добавление новых команд для взаимодействия со счетом в процессе!
exit_while = 0
while exit_while == 0:
    
    schedule.run_pending()
    time.sleep(1)
    exit_while+=1

# Токен

