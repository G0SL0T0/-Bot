import json
import discord
from discord.ext import commands

class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount
        return self.balance

    def withdraw(self, amount):
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount
        return self.balance

    def get_balance(self):
        return self.balance

class Bank:
    def __init__(self, filename='bank.json'):
        self.filename = filename
        self.accounts = {}
        self.load_accounts()

    def load_accounts(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                data = json.load(f)
                for owner, account_data in data.items():
                    account = BankAccount(owner, account_data['balance'])
                    self.accounts[owner] = account

    def save_accounts(self):
        data = {}
        for owner, account in self.accounts.items():
            data[owner] = {'balance': account.get_balance()}
        with open(self.filename, 'w') as f:
            json.dump(data, f)

    def create_account(self, owner):
        if owner not in self.accounts:
            self.accounts[owner] = BankAccount(owner)
            self.save_accounts()
        return self.accounts[owner]

    def get_account(self, owner):
        return self.accounts.get(owner)

    def delete_account(self, owner):
        if owner in self.accounts:
            del self.accounts[owner]
            self.save_accounts()


@bot.command(name='create-account')
async def create_account(ctx, owner: str):
    account = bank.create_account(owner)
    await ctx.send(f'Account created for {owner} with balance {account.get_balance()}')

@bot.command(name='deposit')
async def deposit(ctx, owner: str, amount: int):
    account = bank.get_account(owner)
    if account:
        account.deposit(amount)
        await ctx.send(f'Deposited {amount} into {owner}\'s account. New balance: {account.get_balance()}')
    else:
        await ctx.send(f'Account for {owner} does not exist')

@bot.command(name='withdraw')
async def withdraw(ctx, owner: str, amount: int):
    account = bank.get_account(owner)
    if account:
        try:
            account.withdraw(amount)
            await ctx.send(f'Withdrew {amount} from {owner}\'s account. New balance: {account.get_balance()}')
        except ValueError as e:
            await ctx.send(str(e))
    else:
        await ctx.send(f'Account for {owner} does not exist')

@bot.command(name='balance')
async def balance(ctx, owner: str):
    account = bank.get_account(owner)
    if account:
        await ctx.send(f'Balance for {owner}: {account.get_balance()}')
    else:
        await ctx.send(f'Account for {owner} does not exist')
