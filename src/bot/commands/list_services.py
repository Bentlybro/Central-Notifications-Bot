import discord
from discord import app_commands
import os
import sqlite3
from .base_cog import BaseServiceCog

OWNER_ID = int(os.getenv("OWNER_ID", "353922987235213313"))

class ListServicesCog(BaseServiceCog):
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

async def setup(bot):
    await bot.add_cog(ListServicesCog(bot)) 