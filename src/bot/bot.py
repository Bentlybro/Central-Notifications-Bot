import discord
from discord import app_commands
from discord.ext import commands
import os
import sqlite3
from typing import Optional

OWNER_ID = int(os.getenv("OWNER_ID", "353922987235213313"))

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

    @app_commands.command(name="addservice", description="Add a service webhook to your server")
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
                    # Only bot owner can create new services
                    if interaction.user.id != OWNER_ID:
                        await interaction.response.send_message(
                            f"Service '{service_name}' doesn't exist yet. Please contact the bot owner to add new services.",
                            ephemeral=True
                        )
                        return
                        
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
                        value="Using existing service. Notifications will now be sent to this server.",
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

    @app_commands.command(name="removeservice", description="Remove a service from your server")
    async def remove_service(self, interaction: discord.Interaction, service_name: str):
        try:
            with sqlite3.connect(self.db_path) as conn:
                # First check if the service exists
                service = conn.execute(
                    "SELECT id FROM services WHERE name = ?",
                    (service_name,)
                ).fetchone()
                
                if not service:
                    await interaction.response.send_message(
                        f"Service '{service_name}' not found!",
                        ephemeral=True
                    )
                    return
                    
                # Remove the server-specific channel mapping
                conn.execute("""
                    DELETE FROM server_channels 
                    WHERE service_id = ? AND guild_id = ?
                """, (service[0], interaction.guild_id))
                
                # Try to find and delete the channel
                channel_name = f"{service_name.lower().replace(' ', '-')}-status"
                for channel in interaction.guild.channels:
                    if channel.name == channel_name:
                        await channel.delete()
                        break
                
                embed = discord.Embed(
                    title="Service Removed from Server",
                    description=f"Service '{service_name}' has been removed from this server. The channel has been deleted and you will no longer receive notifications.",
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            await interaction.response.send_message(
                "An error occurred while removing the service.",
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "I don't have permission to delete channels!",
                ephemeral=True
            )

    @app_commands.command(name="deleteservice", description="[Owner Only] Completely delete a service")
    async def delete_service(self, interaction: discord.Interaction, service_name: str):
        # Check if the user is the bot owner
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message(
                "Only the bot owner can delete services completely.",
                ephemeral=True
            )
            return

        try:
            with sqlite3.connect(self.db_path) as conn:
                # First check if the service exists
                service = conn.execute(
                    "SELECT id FROM services WHERE name = ?",
                    (service_name,)
                ).fetchone()
                
                if not service:
                    await interaction.response.send_message(
                        f"Service '{service_name}' not found!",
                        ephemeral=True
                    )
                    return
                
                # Get all servers using this service
                channels = conn.execute("""
                    SELECT guild_id, channel_id FROM server_channels
                    WHERE service_id = ?
                """, (service[0],)).fetchall()
                
                # Delete the service and all its channel mappings
                conn.execute("DELETE FROM server_channels WHERE service_id = ?", (service[0],))
                conn.execute("DELETE FROM services WHERE id = ?", (service[0],))
                
                # Notify and delete channels in all servers
                deleted_count = 0
                for guild_id, channel_id in channels:
                    guild = self.bot.get_guild(guild_id)
                    if guild:
                        channel = guild.get_channel(channel_id)
                        if channel:
                            try:
                                # Send notification message
                                await channel.send(
                                    f"The service '{service_name}' has been removed. This channel needs to be deleted."
                                )
                                deleted_count += 1
                            except discord.Forbidden:
                                continue
                
                embed = discord.Embed(
                    title="Service Deleted",
                    description=f"Service '{service_name}' has been completely deleted. The webhook URL will no longer accept notifications.",
                    color=discord.Color.red()
                )
                embed.add_field(
                    name="Cleanup",
                    value=f"Deleted {deleted_count} channels across {len(channels)} servers.",
                    inline=False
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            await interaction.response.send_message(
                "An error occurred while deleting the service.",
                ephemeral=True
            )

    @app_commands.command(name="listservices", description="List all registered services")
    async def list_services(self, interaction: discord.Interaction):
        # Check if the user is the bot owner
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message(
                "Only the bot owner can list all services.",
                ephemeral=True
            )
            return

        with sqlite3.connect(self.db_path) as conn:
            services = conn.execute("""
                SELECT s.name, s.webhook_path, COUNT(sc.channel_id) as server_count
                FROM services s
                LEFT JOIN server_channels sc ON s.id = sc.service_id
                GROUP BY s.id
            """).fetchall()
        
        if not services:
            await interaction.response.send_message(
                "No services registered yet.",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="Registered Services",
            color=discord.Color.blue()
        )
        
        for name, webhook_path, server_count in services:
            webhook_url = f"{os.getenv('WEBHOOK_BASE_URL')}{webhook_path}"
            value = f"Webhook: {webhook_url}\nActive in {server_count} servers"
            embed.add_field(name=name, value=value, inline=False)
        
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

    @app_commands.command(name="help", description="Learn how to use the bot and manage services")
    async def help_command(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📚 Notification Bot Help",
            description="A bot to manage service notifications across Discord servers.",
            color=discord.Color.blue()
        )
        
        # Regular User Commands
        embed.add_field(
            name="🔧 Regular User Commands",
            value=(
                "**`/addservice <service_name>`**\n"
                "➜ Add an existing service to your server\n"
                "➜ Creates a dedicated channel for notifications\n"
                "➜ Uses existing channel if one with matching name exists\n\n"
                "**`/removeservice <service_name>`**\n"
                "➜ Remove a service from your server\n"
                "➜ Deletes the associated notification channel\n"
                "➜ Stops all notifications for that service\n\n"
                "**`/about`**\n"
                "➜ Learn about the bot and its creator\n\n"
                "**`/help`**\n"
                "➜ Display this help message"
            ),
            inline=False
        )
        
        # Owner Only Commands
        embed.add_field(
            name="👑 Owner Only Commands",
            value=(
                "**`/addservice <service_name>`**\n"
                "➜ Create a new service (when service doesn't exist)\n"
                "➜ Generates a unique webhook URL\n\n"
            ),
            inline=False
        )
        
        # Additional Information
        embed.add_field(
            name="ℹ️ Additional Information",
            value=(
                "• Services are managed globally by the bot owner\n"
                "• Each server can subscribe to existing services\n"
                "• Channels are automatically created in the same category as the command\n"
                "• Webhook URLs are unique and permanent until service deletion"
            ),
            inline=False
        )

        embed.set_footer(
            text=f"Bot Owner: @bentlybro • Use these commands in any channel where the bot has access"
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="about", description="Learn about the bot and its creator")
    async def about_command(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📢 Central Notifications Bot",
            description=(
                "A powerful Discord bot that manages service status notifications through webhooks. "
                "Perfect for monitoring status pages and receiving real-time updates across multiple Discord servers."
            ),
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🔑 Key Features",
            value=(
                "• Centralized service status monitoring\n"
                "• Support for multiple Discord servers\n"
                "• Automatic channel management\n"
                "• Statuspage.io webhook integration\n"
                "• Real-time status updates and incidents"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🛠️ Created By",
            value="This bot was created by @bentlybro",
            inline=False
        )
        
        embed.add_field(
            name="📚 Need Help?",
            value="Use `/help` to see all available commands",
            inline=False
        )
        
        embed.set_footer(text="Made with ❤️ for the Discord community")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="servicerequest", description="Request a new service to be added")
    async def service_request(
        self, 
        interaction: discord.Interaction, 
        service_name: str, 
        service_url: str, 
        reason: str
    ):
        owner = self.bot.get_user(OWNER_ID)
        
        # Create a nice looking embed
        embed = discord.Embed(
            title="🔔 New Service Request",
            color=discord.Color.blue(),
            timestamp=interaction.created_at
        )
        
        embed.add_field(
            name="📋 Service Details",
            value=f"**Name:** {service_name}\n**URL:** {service_url}",
            inline=False
        )
        
        embed.add_field(
            name="📝 Reason",
            value=reason,
            inline=False
        )
        
        embed.add_field(
            name="👤 Requested By",
            value=f"{interaction.user} (ID: {interaction.user.id})",
            inline=False
        )
        
        embed.add_field(
            name="🏢 Server",
            value=f"{interaction.guild.name} (ID: {interaction.guild.id})",
            inline=False
        )

        try:
            # Send DM to owner
            if owner:
                await owner.send(embed=embed)

            # Send to the designated channel
            channel = self.bot.get_channel(1316865549363314808)
            if channel:
                await channel.send(embed=embed)

            # Respond to the user
            await interaction.response.send_message(
                "Your service request has been sent to the bot owner. Thank you!",
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "Unable to send your request. Please ensure the bot has permissions to send messages to the owner or the designated channel.",
                ephemeral=True
            )
        except Exception as e:
            print(f"Error sending service request: {e}")
            await interaction.response.send_message(
                "An error occurred while sending your request. Please try again later.",
                ephemeral=True
            )


async def setup(bot: NotificationBot):
    await bot.add_cog(ServiceCommands(bot)) 