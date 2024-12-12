import discord
from discord.ext import commands
import os
import importlib
import pkgutil

class NotificationBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        
    async def setup_hook(self):
        # Load all command cogs
        commands_package = 'src.bot.commands'
        for _, name, _ in pkgutil.iter_modules([commands_package.replace('.', '/')]):
            if name != 'base_cog':  # Skip the base cog
                await self.load_extension(f"{commands_package}.{name}")
        await self.tree.sync()
        
    async def update_status(self):
        try:
            # Get the first cog that inherits from BaseServiceCog to access the database
            base_cog = next(
                (cog for cog in self.cogs.values() if hasattr(cog, 'db_path')),
                None
            )
            if base_cog:
                import sqlite3
                with sqlite3.connect(base_cog.db_path) as conn:
                    service_count = conn.execute("SELECT COUNT(*) FROM services").fetchone()[0]
                    
                activity = discord.Activity(
                    type=discord.ActivityType.watching,
                    name=f"{service_count} services in {len(self.guilds)} servers"
                )
                await self.change_presence(activity=activity)
        except Exception as e:
            print(f"Error updating status: {e}")
        
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        await self.update_status()
        print('------')
        
    async def on_guild_join(self, guild):
        await self.update_status()
        
    async def on_guild_remove(self, guild):
        await self.update_status() 