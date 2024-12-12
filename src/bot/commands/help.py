import discord
from discord import app_commands
from .base_cog import BaseServiceCog

class HelpCog(BaseServiceCog):
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

async def setup(bot):
    await bot.add_cog(HelpCog(bot)) 