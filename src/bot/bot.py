import discord
from discord import app_commands
from discord.ext import commands
import os
import sqlite3
from typing import Optional

class NotificationBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        
    async def setup_hook(self):
        await self.tree.sync()
        
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

class ServiceCommands(commands.Cog):
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

    @app_commands.command(name="addservice", description="Add a new service webhook")
    async def add_service(self, interaction: discord.Interaction, service_name: str):
        webhook_path = f"/webhook/{service_name.lower().replace(' ', '_')}"
        webhook_url = f"{os.getenv('WEBHOOK_BASE_URL')}{webhook_path}"
        
        # Get the category of the current channel
        category = interaction.channel.category
        channel_name = f"{service_name.lower().replace(' ', '-')}-status"
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # First try to get existing service
                service = conn.execute(
                    "SELECT id FROM services WHERE name = ?",
                    (service_name,)
                ).fetchone()
                
                if service:
                    service_id = service[0]
                else:
                    # Create new service if it doesn't exist
                    cursor = conn.execute(
                        "INSERT INTO services (name, webhook_path) VALUES (?, ?)",
                        (service_name, webhook_path)
                    )
                    service_id = cursor.lastrowid
                
                # Try to find existing channel with the same name in the category
                existing_channel = None
                if category:
                    for channel in category.text_channels:
                        if channel.name == channel_name:
                            existing_channel = channel
                            break
                
                if existing_channel:
                    new_channel = existing_channel
                else:
                    # Create a new channel if none exists
                    new_channel = await interaction.guild.create_text_channel(
                        name=channel_name,
                        category=category,
                        topic=f"Status updates for {service_name}"
                    )
                
                # Add or update server channel mapping
                conn.execute("""
                    INSERT OR REPLACE INTO server_channels 
                    (service_id, guild_id, channel_id) VALUES (?, ?, ?)
                """, (service_id, interaction.guild_id, new_channel.id))
                
                embed = discord.Embed(
                    title="Service Added Successfully",
                    color=discord.Color.green()
                )
                embed.add_field(name="Service Name", value=service_name, inline=False)
                embed.add_field(name="Webhook URL", value=webhook_url, inline=False)
                embed.add_field(name="Channel", value=new_channel.mention, inline=False)
                
                if service:
                    embed.add_field(
                        name="Note",
                        value="This service already exists. Notifications will now be sent to this server as well.",
                        inline=False
                    )
                
                if existing_channel:
                    embed.add_field(
                        name="Channel Note",
                        value="Using existing channel with matching name.",
                        inline=False
                    )
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
                
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            await interaction.response.send_message(
                "An error occurred while setting up the service.",
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "I don't have permission to create channels!",
                ephemeral=True
            )

    @app_commands.command(name="removeservice", description="Remove a service webhook")
    async def remove_service(self, interaction: discord.Interaction, service_name: str):
        with sqlite3.connect(self.db_path) as conn:
            # First check if the service exists
            service = conn.execute(
                "SELECT webhook_path FROM services WHERE name = ?",
                (service_name,)
            ).fetchone()
            
            if not service:
                await interaction.response.send_message(
                    f"Service '{service_name}' not found!",
                    ephemeral=True
                )
                return
                
            # Delete the service
            conn.execute("DELETE FROM services WHERE name = ?", (service_name,))
            
            embed = discord.Embed(
                title="Service Removed Successfully",
                description=f"Service '{service_name}' has been removed. The webhook URL will no longer accept notifications.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="listservices", description="List all registered services")
    async def list_services(self, interaction: discord.Interaction):
        with sqlite3.connect(self.db_path) as conn:
            services = conn.execute("SELECT name, webhook_path FROM services").fetchall()
        
        if not services:
            await interaction.response.send_message("No services registered yet!", ephemeral=True)
            return
            
        embed = discord.Embed(
            title="Registered Services",
            color=discord.Color.blue()
        )
        
        for name, path in services:
            webhook_url = f"{os.getenv('WEBHOOK_BASE_URL')}{path}"
            embed.add_field(name=name, value=webhook_url, inline=False)
            
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="setchannel", description="Set the notification channel for a service")
    async def set_channel(
        self,
        interaction: discord.Interaction,
        service_name: str,
        channel: discord.TextChannel
    ):
        with sqlite3.connect(self.db_path) as conn:
            result = conn.execute(
                "UPDATE services SET channel_id = ? WHERE name = ?",
                (channel.id, service_name)
            )
            
        if result.rowcount == 0:
            await interaction.response.send_message(
                f"Service '{service_name}' not found!",
                ephemeral=True
            )
            return
            
        await interaction.response.send_message(
            f"Notifications for '{service_name}' will now be sent to {channel.mention}",
            ephemeral=True
        )

async def setup(bot: NotificationBot):
    await bot.add_cog(ServiceCommands(bot)) 