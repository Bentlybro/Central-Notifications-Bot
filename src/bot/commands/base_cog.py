import sqlite3
import os
from discord.ext import commands
from ..bot import NotificationBot

class BaseServiceCog(commands.Cog):
    def __init__(self, bot: NotificationBot):
        self.bot = bot
        self.db_path = "config/services.db"
        self._init_db()

    def _init_db(self):
        os.makedirs("config", exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            # Create services table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS services (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE,
                    webhook_path TEXT UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create server_channels table for mapping services to channels in different servers
            conn.execute("""
                CREATE TABLE IF NOT EXISTS server_channels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    service_id INTEGER,
                    guild_id INTEGER,
                    channel_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(service_id, guild_id),
                    FOREIGN KEY(service_id) REFERENCES services(id)
                )
            """) 