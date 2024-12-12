from fastapi import FastAPI, Request, HTTPException
import sqlite3
import discord
from discord.ext import commands
import os
import json
from typing import Optional
from datetime import datetime
import asyncio

app = FastAPI()

def get_bot() -> Optional[commands.Bot]:
    return app.state.bot

def get_service_channels(service_path: str) -> list[tuple[str, int, int]]:
    with sqlite3.connect("config/services.db") as conn:
        return conn.execute("""
            SELECT s.name, sc.channel_id, sc.guild_id
            FROM services s
            JOIN server_channels sc ON s.id = sc.service_id
            WHERE s.webhook_path = ?
        """, (service_path,)).fetchall()

def format_statuspage_notification(payload: dict, service_name: str) -> discord.Embed:
    embed = discord.Embed(
        title=f"{service_name} Status Update",
        timestamp=datetime.utcnow(),
        color=discord.Color.blue()
    )
    
    # Handle page status
    if "page" in payload:
        page = payload["page"]
        status_desc = page.get("status_description", "")
        indicator = page.get("status_indicator", "")
        
        # Set color based on status indicator
        if indicator in ["none", "operational"]:
            embed.color = discord.Color.green()
        elif indicator in ["minor", "degraded_performance"]:
            embed.color = discord.Color.orange()
        elif indicator in ["major", "critical"]:
            embed.color = discord.Color.red()
            
        if status_desc:
            embed.add_field(
                name="Overall Status",
                value=status_desc,
                inline=False
            )

    # Handle component updates
    if "component_update" in payload and "component" in payload:
        component = payload["component"]
        update = payload["component_update"]
        
        embed.add_field(
            name="Component",
            value=component.get("name", "Unknown Component"),
            inline=False
        )
        
        old_status = update.get("old_status", "unknown").replace("_", " ").title()
        new_status = update.get("new_status", "unknown").replace("_", " ").title()
        
        embed.add_field(
            name="Status Change",
            value=f"{old_status} → {new_status}",
            inline=False
        )
        
        if update.get("created_at"):
            embed.timestamp = datetime.fromisoformat(
                update["created_at"].replace("Z", "+00:00")
            )

    # Handle incident updates
    if "incident" in payload:
        incident = payload["incident"]
        
        if incident.get("name"):
            embed.add_field(
                name="Incident",
                value=incident["name"],
                inline=False
            )
        
        status = incident.get("status", "").replace("_", " ").title()
        impact = incident.get("impact", "").replace("_", " ").title()
        
        if status:
            embed.add_field(name="Status", value=status, inline=True)
        if impact:
            embed.add_field(name="Impact", value=impact, inline=True)
        
        if incident.get("incident_updates"):
            updates = incident["incident_updates"]
            if updates:
                latest_update = updates[0]
                embed.add_field(
                    name="Latest Update",
                    value=latest_update.get("body", "No details available"),
                    inline=False
                )
                
                if latest_update.get("created_at"):
                    embed.timestamp = datetime.fromisoformat(
                        latest_update["created_at"].replace("Z", "+00:00")
                    )

    return embed

@app.post("/webhook/{service_name}")
async def webhook_handler(service_name: str, request: Request):
    service_path = f"/webhook/{service_name}"
    try:
        payload = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    channels = get_service_channels(service_path)
    if not channels:
        raise HTTPException(
            status_code=400,
            detail="No channels configured for this service"
        )

    bot = get_bot()
    if not bot:
        raise HTTPException(
            status_code=500,
            detail="Bot not initialized"
        )

    # Format the notification
    embed = format_statuspage_notification(payload, service_name)

    # Send to all configured channels
    failed_channels = []
    for service_name, channel_id, guild_id in channels:
        channel = bot.get_channel(channel_id)
        if channel:
            try:
                future = asyncio.run_coroutine_threadsafe(
                    channel.send(embed=embed),
                    bot.loop
                )
                future.result(timeout=10)
            except Exception as e:
                print(f"Error sending to channel {channel_id} in guild {guild_id}: {e}")
                failed_channels.append(channel_id)

    if failed_channels:
        print(f"Failed to send to channels: {failed_channels}")
        if len(failed_channels) == len(channels):
            raise HTTPException(
                status_code=500,
                detail="Failed to send message to all Discord channels"
            )

    return {"status": "ok", "failed_channels": failed_channels} 