import discord
from discord import app_commands
import os
from .base_cog import BaseServiceCog

OWNER_ID = int(os.getenv("OWNER_ID", "353922987235213313"))

class ServiceRequestCog(BaseServiceCog):
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

async def setup(bot):
    await bot.add_cog(ServiceRequestCog(bot)) 