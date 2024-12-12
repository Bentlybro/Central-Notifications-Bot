import discord
from discord import app_commands
import sqlite3
from .base_cog import BaseServiceCog

class RemoveServiceCog(BaseServiceCog):
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

async def setup(bot):
    await bot.add_cog(RemoveServiceCog(bot)) 