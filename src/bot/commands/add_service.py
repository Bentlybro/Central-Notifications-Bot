import discord
from discord import app_commands
import os
import sqlite3
from .base_cog import BaseServiceCog

OWNER_ID = int(os.getenv("OWNER_ID", "353922987235213313"))

class AddServiceCog(BaseServiceCog):
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
                    
                    # Update bot status to reflect new service count
                    await self.bot.update_status()
                
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

async def setup(bot):
    await bot.add_cog(AddServiceCog(bot)) 