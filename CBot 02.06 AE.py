import json
import discord
from discord.ext import commands

@bot.command(name='help')
async def help(ctx):
    guide = """
**Команды для работы с Жрунами**

**Выдать Жруны**
`!выдать <пользователь> <количество>` - начислить Жруны пользователю

**Проверить баланс**
`!баланс <пользователь>` - проверить баланс пользователя

**Положить Жруны**
`!положить <пользователь> <количество>` - положить Жруны на счет пользователя

**Снять Жруны**
`!снять <пользователь> <количество>` - снять Жруны с счета пользователя

**Примеры**
`!выдать @user 10` - начислить 10 Жрунов пользователю @user
`!баланс @user` - проверить баланс пользователя @user
`!положить @user 5` - положить 5 Жрунов на счет пользователя @user
`!снять @user 3` - снять 3 Жруны с счета пользователя @user
"""
    await ctx.send(guide)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Неправильный формат команды! Используйте `!help` для справки.")
    else:
        await ctx.send("Ошибка при выполнении команды! Используйте `!help` для справки.")

# Your commands here...

@bot.command(name='выдать')
async def give_jrun(ctx, user: discord.Member, amount: int = 1):
    jrun.give_jrun(user.id, amount)
    await ctx.send(f'Начислено {amount} Жрунов пользователю {user.mention}!')

@bot.command(name='баланс')
async def balance(ctx, user: discord.Member):
    bank = Bank('JavaS/Jrun_balance.json')
    balance = bank.get_balance(user.id)
    await ctx.send(f'Баланс пользователя {user.mention}: {balance} Жрунов')

@bot.command(name='положить')
async def deposit(ctx, user: discord.Member, amount: int):
    account = BankAccount('JavaS/Jrun_balance.json', user.id)
    account.deposit(amount)
    await ctx.send(f'Начислено {amount} Жрунов на счет пользователя {user.mention}!')

@bot.command(name='снять')
async def withdraw(ctx, user: discord.Member, amount: int):
    account = BankAccount('JavaS/Jrun_balance.json', user.id)
    try:
        account.withdraw(amount)
        await ctx.send(f'Снято {amount} Жрунов с счета пользователя {user.mention}!')
    except ValueError:
        await ctx.send('Недостаточно средств на счете!')
