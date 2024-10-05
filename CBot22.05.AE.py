#Чудо бот
import discord
import asyncio
from discord.ext import commands #только библиотека Discord.py
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

ticket_data_file = "C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/tickets.json"
rewards = {
    100: {"Tier 4": 0.5, "Tier 5": 0.5}, # Лотерейка
    50: {"Tier 3": 1.0}
}
presence_data = {} # похождения юзеров на сервере (жруны за 7 дней)
reaction_channel_id = 1179745995345645609  # ID канала
DATA_DIR = 'C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/'
BALANCE_FILE = 'C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/Jrun_balance.json'

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

class Jopnik: # Жопник, работа с файлами
    def __init__(self, filename):
        self.filename = os.path.join(DATA_DIR, filename)
        self.data = self.load_data()

    def load_data(self):
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            with open(self.filename, 'w') as f:
                json.dump({'balance': 0, 'commission': 5, 'event_active': False, 'event_start_balance': 0, 'event_end_time': None, 'top_list': []}, f)
            return {'balance': 0, 'commission': 5, 'event_active': False, 'event_start_balance': 0, 'event_end_time': None, 'top_list': []}
    def save_data(self):
        with open(self.filename, 'w') as f:
            print(f"Файл {self.filename} открыт для записи.")
            json.dump(self.data, f)
            print(f"Данные сохранены в файл {self.filename}.")

    def add_jopnik_commission(self, amount):
        self.data['balance'] += amount
        self.save_data()

    def get_jopnik_balance(self):
        return self.data['balance']

    def get_jopnik_commission(self):
        return self.data['commission']

    def start_jopnik_event(self):
        self.data['event_active'] = True
        self.data['event_start_balance'] = self.data['balance']
        self.save_data()

    def end_jopnik_event(self):
        if self.data['balance'] < 68:
            self.data['commission'] = 2
        self.data['event_active'] = False
        self.save_data()

    def get_jopnik_event_status(self):
        return self.data['event_active']

    def get_jopnik_top_list(self):
        return self.data['top_list']

    def add_to_jopnik_top_list(self, user_id):
        self.data['top_list'].append(user_id)
        self.save_data()

# Функции
def has_moderator_role(user): # роли модеров
    moderator_roles = ['Чудо', 'Влад', 'Сфера', 'роль1']
    for role in user.roles:
        if role.name in moderator_roles:
            return True

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
################################################################################################
################################################################################################
def add_jopnik_commission(amount):
    jopnik = Jopnik('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/jopnik.json')
    jopnik.data['balance'] += amount
    jopnik.save_data()

def check_jopnik_balance(): # проверка баланса жопника
    now = datetime.datetime.now()
    if now.weekday() == 6 and now.hour == 23 and now.minute == 59:
        jopnik = Jopnik('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/jopnik.json')
        if jopnik.data['balance'] >= 100:
            start_jopnik_event()

def start_jopnik_event(): # запуск ивента
    jopnik = Jopnik('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/jopnik.json')
    jopnik.data['event_active'] = True
    jopnik.data['event_start_balance'] = jopnik.data['balance']
    jopnik.save_data()
    enable_zadobrit_command()
    schedule.every().day.at("00:00").do(end_jopnik_event)

def end_jopnik_event(): # окончание ивента
    jopnik = Jopnik('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/jopnik.json')
    if jopnik.data['balance'] < 68:
        jopnik.data['commission'] = 2
    calculate_rewards(jopnik.data['event_start_balance'])
    disable_zadobrit_command()
    jopnik.data['event_active'] = False
    jopnik.save_data()

def calculate_rewards(initial_balance): # Топ 5 за ивент
    jopnik = Jopnik('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/jopnik.json')
    top_list = jopnik.data['top_list']
    rewards = []
    for i, user in enumerate(top_list[:5]):
        reward = int(initial_balance * (0.25 - i * 0.05))
        rewards.append((user, reward))
    save_rewards(rewards)

def save_rewards(rewards): # save наград
    with open(DATA_DIR + 'rewards.json', 'w') as f:
        json.dump(rewards, f)

def enable_zadobrit_command(): # функция для !задобрить
    @bot.command(name='задобрить')
    async def zadobrit(ctx):
        jopnik = Jopnik('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/jopnik.json')
        if ctx.author.id in zadobrit_cooldown:
            await ctx.send("Вы уже использовали команду '!задобрить' в этом часе.")
            return
        bank = Bank('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/Jrun_balance.json')
        balance = bank.get_balance(ctx.author.id)
        if balance < 3:
            await ctx.send("У вас не хватает жрунов для использования команды '!задобрить'.")
            return
        bank.decrement_balance(ctx.author.id, 3)
        reward = random.randint(0, 5)
        bank.increment_balance(ctx.author.id, reward)
        jopnik.data['top_list'].append(ctx.author.id)
        jopnik.save_data()

def disable_zadobrit_command(): # Для особо активных отключение команды !задобрить
    @bot.command(name='задобрить')
    async def zadobrit(ctx):
        await ctx.send("Команда '!задобрить' неактивна.")

def load_zadobrit_top():
    jopnik = Jopnik('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/jopnik.json')
    return jopnik.data['top_list']

def save_zadobrit_top(top_list): # топ Задобрителей
    jopnik = Jopnik('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/jopnik.json')
    jopnik.data['top_list'] = top_list

def get_commission():
    jopnik = Jopnik('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/jopnik.json')
    return jopnik.data['commission']

def update_commission():
    jopnik = Jopnik('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/jopnik.json')
    jopnik.data['commission'] = random.randint(1, 10)
    jopnik.save_data()

def check_requirements(user, role): 
    bank = Bank(BALANCE_FILE)
    balance = bank.get_balance(user.id)
    asses = get_user_asses(user.id)
    print(balance," - баланс 0 ", asses)
    if role == 'Продвинутый':
        print(balance," - баланс 1 ", asses)
        if balance < 30 + get_commission():
            print(balance," - баланс 2 ", asses)
            return False
    elif role == 'Опытный':
        print(balance," - баланс 1 ", asses)
        if balance < 70 + get_commission():
            print(balance," - баланс 2 ", asses)
            return False
    return True

def check_roles(): # проверка на наличие жопок
    jopnik = Jopnik('top_list.json')
    top_list = jopnik.data
    for user in bot.get_all_members():
        user_info = next((x for x in top_list if x.get('никнейм') == user.name), None)
        if user_info is not None:
            if user_info.get('жопки', 0) < 5 and 'Продвинутый' in [role.name for role in user.roles]:
                role = discord.utils.get(user.guild.roles, name='Продвинутый')
                user.remove_roles(role)
            if user_info.get('жопки', 0) < 10 and 'Опытный' in [role.name for role in user.roles]:
                role = discord.utils.get(user.guild.roles, name='Опытный')
                user.remove_roles(role)

def set_first_jrun_date(user): # дата получения первого жруна
    try:
        with open('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/first_jrun_date.json', 'r+') as f:
            first_jrun_dates = json.load(f)
    except FileNotFoundError:
        with open('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/first_jrun_date.json', 'w') as f:
            json.dump({}, f)
        first_jrun_dates = {}
    now = datetime.datetime.now(datetime.timezone.utc)
    first_jrun_dates[str(user.id)] = now.strftime('%Y-%m-%d %H:%M:%S.%f')
    with open('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/first_jrun_date.json', 'w') as f:
        json.dump(first_jrun_dates, f)

def give_jrun_for_all_members(): #Пополнения жрунов от роли
    for member in bot.get_all_members():
        if "Опытный" in [role.name for role in member.roles]:
            account = BankAccount('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/Jrun_balance.json', member.id)
            account.give_jrun(member.id, 4)
        elif "Продвинутый" in [role.name for role in member.roles]:
            account = BankAccount('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/Jrun_balance.json', member.id)
            account.give_jrun(member.id, 2)

def remove_roles_if_needed(user_id, new_asses_count): # удаление ролей при понижении жопок
    user = bot.get_user(user_id)
    if user:
        if new_asses_count < 30:
            role = discord.utils.get(user.guild.roles, name='Продвинутый')
            if role in user.roles:
                user.remove_roles(role)
        if new_asses_count < 70:
            role = discord.utils.get(user.guild.roles, name='Опытный')
            if role in user.roles:
                user.remove_roles(role)

async def handle_buy_advanced_interaction(interaction):
    if not check_requirements(interaction.user, 'Продвинутый'):
        await interaction.response.send_message('У вас не хватает жрунов или жопок для покупки этой роли!')
        return
async def handle_buy_experienced_interaction(interaction):
    if not check_requirements(interaction.user, 'Опытный'):
        await interaction.response.send_message('У вас не хватает жрунов или жопок для покупки этой роли!')
        return
################################################################################################
################################################################################################
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
################################################################################################
################################################################################################
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
################################################################################################

schedule.every().day.at("00:00").do(reset_last_message_time)  # 0:00 по времени Сахалину
schedule.every(1).day.at("00:00").do(give_jrun_for_all_members)  # вызывать функцию каждый день в 00:00 получение жрунов
schedule.every(1).day.at("00:00").do(check_roles)  # вызывать функцию каждый день в 00:00 чек на жопки
#schedule.every().week.at("23:59").do(check_jopnik_balance)
schedule.every().day.at("00:00").do(reset_message_count)
schedule.every().day.at("00:00").do(reset_reaction_count)
schedule.every().day.at("00:00").do(update_commission)

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
#convert_to_member
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
        give_jrun_for_message(message.author.id, message.guild.id, message)
    await bot.process_commands(message)

@bot.event
async def on_reaction_add(reaction, user):
    if user == bot.user:
        return
    give_jrun_for_reaction(reaction, user)
############################################################################################################
@bot.event # обработчик кнопок !для магазина и !для Жопника
async def on_interaction(interaction):
    if interaction.type == discord.InteractionType.component:
        await handle_component_interaction(interaction)

async def handle_component_interaction(interaction):
    if interaction.data.get('custom_id') == 'zadobrit':
        await handle_zadobrit_interaction(interaction)
    elif interaction.data.get('custom_id') == 'shop':
        await handle_shop_interaction(interaction)
    elif interaction.data.get('custom_id') == 'buy_advanced':
        await handle_buy_advanced_interaction(interaction)
    elif interaction.data.get('custom_id') == 'buy_experienced':
        await handle_buy_experienced_interaction(interaction)

async def zadobrit(interaction):
    bank = Bank('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/Jrun_balance.json')
    balance = bank.get_balance(interaction.user.id)
    if balance < 3:
        await interaction.response.send_message('У вас не хватает жрунов для задобрения жопника!')
        return
    bank.decrement_balance(interaction.user.id, 3)
    reward = random.randint(0, 5)
    bank.increment_balance(interaction.user.id, reward)
    await interaction.response.send_message(f'Вы задобрили жопника и получили {reward} жрунов!')

async def handle_shop_interaction(interaction):
    commission = get_commission()
    embed = discord.Embed(title='Магазин Жопника', description='Здесь вы можете купить роли и другие товары')
    embed.add_field(name='Продвинутый', value=f'30 жрунов + {commission} жрунов', inline=False)
    embed.add_field(name='Опытный', value=f'70 жрунов + {commission} жрунов', inline=False)
## ID покупка
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label='Купить Продвинутый', custom_id='buy_advanced'))
    view.add_item(discord.ui.Button(label='Купить Опытный', custom_id='buy_experienced'))

    await interaction.response.edit_message(embed=embed, view=view)

async def handle_buy_advanced_interaction(interaction):
    if not check_requirements(interaction.user, 'Продвинутый'):
        await interaction.response.send_message('У вас не хватает жрунов или жопок для покупки этой роли!')
        return
    bank = Bank('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/Jrun_balance.json')
    balance = bank.get_balance(interaction.user.id)
    bank.decrement_balance(interaction.user.id, 30 + get_commission())
    role = discord.utils.get(interaction.guild.roles, name='Продвинутый')
    await interaction.user.add_roles(role)
    await interaction.response.send_message('Вы успешно купили роль Продвинутый!')

async def handle_buy_experienced_interaction(interaction):
    if not check_requirements(interaction.user, 'Опытный'):
        await interaction.response.send_message('У вас не хватает жрунов или жопок для покупки этой роли!')
        return
    bank = Bank('C:/Users/APM_1/Documents/GitHub/ChudoBot/JavaS/Jrun_balance.json')
    balance = bank.get_balance(interaction.user.id)
    bank.decrement_balance(interaction.user.id, 70 + get_commission())
    role = discord.utils.get(interaction.guild.roles, name='Опытный')
    await interaction.user.add_roles(role)
    await interaction.response.send_message('Вы успешно купили роль Опытный!')

async def on_interaction(interaction):
    if interaction.type == discord.InteractionType.component:
        if interaction.data.get('custom_id') == 'shop':
            await handle_shop_interaction(interaction)
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

*Жопки**
`!Жопка` - Топ владельцев жопок

**Пнуть пользователя**
`!пнуть <@user>` - пинает пользователя в ЛС



**Жопник**
`!Жопник` - открывает функционал Жопника

**Магазин**
`!магаз` - открыть магазин для покупки ролей и других товаров

**Помощь по Жопнику**
`!help_jopnik` - получить информацию о Жопнике и его командах

"""
    await ctx.send(guide)

# HELP команды Жопника
@bot.command()
async def help_jopnik(ctx):
    guide = """
**Команды для работы с Жопником**

**Открыть меню Жопника**
`!жопник` - открыть меню Жопника и задобрить его во время ивента

**Задобрить Жопника**
`!задобрить` - задобрить Жопника во время ивента

**Получить информацию о Жопнике**
`!help_jopnik` - получить информацию о Жопнике и его командах

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

## Команда профиль - выводит стату пользователя (Жруны / жопки)


@bot.command(name='магаз')
async def shop(ctx):
    commission = get_commission()
    embed = discord.Embed(title='Магазин Жопника', description='Здесь вы можете купить роли и другие товары')
    embed.add_field(name='Продвинутый', value=f'30 жрунов + {commission} жрунов', inline=False)
    embed.add_field(name='Опытный', value=f'70 жрунов + {commission} жрунов', inline=False)
##Покупка через ID (user) --
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label='Купить Продвинутый', custom_id='buy_advanced'))
    view.add_item(discord.ui.Button(label='Купить Опытный', custom_id='buy_experienced'))

    await ctx.send(embed=embed, view=view)

@bot.command(name='жопник')
async def jopnik(ctx):
    jopnik = Jopnik('jopnik.json')
    embed = discord.Embed(title='Магнат Комиссионович Жопник, приветствует тебя!')
    embed.add_field(name='Баланс Жопника', value=f'{jopnik.data["balance"]} жрунов', inline=False)
    embed.add_field(name='Дневная комиссия', value=f'{jopnik.data["commission"]} жрунов', inline=False)
    embed.add_field(name='Активность ивента', value='Да' if jopnik.data['event_active'] else 'Нет', inline=False)

    view = discord.ui.View()
    if jopnik.data['event_active']:
        view.add_item(discord.ui.Button(label='Задобрить', custom_id='zadobrit'))
    view.add_item(discord.ui.Button(label='Магазин', custom_id='shop'))

    await ctx.send(embed=embed, view=view)


#Добавление новых команд для взаимодействия со счетом в процессе!
exit_while = 0
while exit_while == 0:
    schedule.run_pending()
    check_jopnik_balance()
    time.sleep(1)
    exit_while+=1

# Токен
bot.run("MTE2NjYzODE2NTY1ODk3NjI3Nw.Gi1Xt0.0xhlWdERtyKuWQSupLmmN_hJ8FPdFXK9RKdvjU")
#Лото MTE2NjYzODE2NTY1ODk3NjI3Nw.Gi1Xt0.0xhlWdERtyKuWQSupLmmN_hJ8FPdFXK9RKdvjU
#Чудо MTIzMzAyMTQ4NzE3MTEwODkwNQ.GJHW7F.XZRRzqVMFKD4MW0N5yVzjJIfwFZdXuVICmWcRw
