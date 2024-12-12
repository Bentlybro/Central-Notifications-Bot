import discord
from discord import app_commands
import os
import sqlite3
from .base_cog import BaseServiceCog

OWNER_ID = int(os.getenv("OWNER_ID", "353922987235213313"))

class DeleteServiceCog(BaseServiceCog):
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
                
                # Update bot status to reflect the removed service
                await self.bot.update_status()
                
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

async def setup(bot):
    await bot.add_cog(DeleteServiceCog(bot)) 