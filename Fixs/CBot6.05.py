#Чудо бот
import discord
import asyncio
from discord.ext import commands
import pytz
import datetime
import random
import json
import time

# Необходимые переменные
message_count = {}
TOP_LIST_FILE = "top_list.json"
prefix = "!"
random_responses=[
    "Неактуально"
    ]

# Создание бота
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

# Обработчик события при успешном запуске бота
@bot.event
async def on_ready():
    print(f"{bot.user.name} успешно запущен")

# Время
@bot.command(name='Время')
async def get_time(ctx):
    ny_timezone = pytz.timezone('Asia/Sakhalin')
    current_time = datetime.datetime.now(ny_timezone).strftime("%H:%M:%S")
    await ctx.send(f"Сейчас у Чудачки: {current_time}")
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
    message = "```Чудо поиграет в доту за 50.044 рублей```"
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
    if top_list[from_user - 1]['жопки'] < amount:
        await ctx.send("Ошибка: У пользователя недостаточно жопок для передачи.")
        return
    top_list[from_user - 1]['жопки'] -= amount
    top_list[to_user - 1]['жопки'] += amount
    save_top_list(top_list)

    await ctx.send(f"Успешно переведено {amount} жопок от {top_list[from_user - 1]['никнейм']} к {top_list[to_user - 1]['никнейм']}.")

#1
@bot.event
async def on_message(message):
    if not message.content.startswith(prefix):
        return
    if message.author == bot.user:
        return
    user_id = message.author.id
    moderator_roles = ["Чудо", "Сфера", "Влад","Сержант апельсин"]
    is_moderator = False
    for role in message.author.roles:
        if role.name in moderator_roles:
            is_moderator = True
            break
    if is_moderator:
        await bot.process_commands(message)
        return
    current_time = time.time()
    message_count.setdefault(user_id, {"count": 0, "last_message_time": 0})
    if current_time - message_count[user_id]["last_message_time"] > 1800:  # 1800 секунд = 30 минут
        message_count[user_id]["count"] = 0
    message_count[user_id]["last_message_time"] = current_time
    message_count[user_id]["count"] += 1
    if message_count[user_id]["count"] > 5:
        await message.channel.send(f"{message.author.mention}, вы отправили слишком много команд за последние 30 минут. Пожалуйста, подождите некоторое время перед отправкой новой команды.")
    else:
        await bot.process_commands(message)
#2
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        response = random.choice(["Эта команда неактуальна"])
        await ctx.send(response)

#Ответочка
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        response = random.choice(random_responses)
        await ctx.send(response)
    else:
        
        pass
# Токен

