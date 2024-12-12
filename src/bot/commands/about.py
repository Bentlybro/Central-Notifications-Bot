import discord
from discord import app_commands
from .base_cog import BaseServiceCog

class AboutCog(BaseServiceCog):
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

async def setup(bot):
    await bot.add_cog(AboutCog(bot)) 