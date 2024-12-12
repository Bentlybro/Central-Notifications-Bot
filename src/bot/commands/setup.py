import discord
from discord import app_commands
import sqlite3
from .base_cog import BaseServiceCog

class SetupCog(BaseServiceCog):
    @app_commands.command(name="setup", description="Create a new category with channels for all services")
    async def setup_command(self, interaction: discord.Interaction, category_name: str = "Service Status"):
        try:
            # Create new category
            category = await interaction.guild.create_category(category_name)
            
            # Get all existing services
            with sqlite3.connect(self.db_path) as conn:
                services = conn.execute("SELECT id, name FROM services").fetchall()
            
            if not services:
                await interaction.response.send_message(
                    "No services found to set up channels for.",
                    ephemeral=True
                )
                return
            
            # Send initial response
            await interaction.response.send_message(
                "Setting up channels... Please wait.",
                ephemeral=True
            )
            
            created_channels = []
            for service_id, service_name in services:
                channel_name = f"{service_name.lower().replace(' ', '-')}-status"
                
                # Create channel in the new category
                channel = await interaction.guild.create_text_channel(
                    name=channel_name,
                    category=category,
                    topic=f"Status updates for {service_name}"
                )
                
                # Add channel mapping to database
                conn.execute("""
                    INSERT OR REPLACE INTO server_channels 
                    (service_id, guild_id, channel_id) VALUES (?, ?, ?)
                """, (service_id, interaction.guild_id, channel.id))
                
                created_channels.append((service_name, channel))
            
            # Create summary embed
            embed = discord.Embed(
                title="Setup Complete",
                description=f"Created category '{category_name}' with channels for all services",
                color=discord.Color.green()
            )
            
            channels_text = "\n".join([f"• {name}: {channel.mention}" for name, channel in created_channels])
            embed.add_field(
                name=f"Created Channels ({len(created_channels)})",
                value=channels_text or "No channels created",
                inline=False
            )
            
            # Edit the original response with the summary
            await interaction.edit_original_response(content="", embed=embed)
            
        except discord.Forbidden:
            await interaction.response.send_message(
                "I don't have permission to create categories or channels!",
                ephemeral=True
            )
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            await interaction.response.send_message(
                "An error occurred while setting up the channels.",
                ephemeral=True
            )
        except Exception as e:
            print(f"Error during setup: {e}")
            await interaction.response.send_message(
                "An unexpected error occurred during setup.",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(SetupCog(bot)) 