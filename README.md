# Central Notifications Bot

A Discord bot that manages service status notifications through webhooks. The bot allows you to subscribe to various service status pages and receive notifications directly in your Discord servers.

## Quick Start
You can use our hosted version of the bot:
1. [Invite the bot to your server](https://discord.com/oauth2/authorize?client_id=1316555696430387301)
2. Navigate to the category where you want status notifications to appear
3. Use `/addservice <service_name>` to set up your first service
4. Configure your status page to send notifications to the provided webhook URL
5. Done! You'll now receive status updates in your Discord server

## Self-Hosting
If you prefer to host the bot yourself, follow these setup instructions:

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with the following variables:
```
DISCORD_TOKEN=your_discord_bot_token
WEBHOOK_BASE_URL=your_public_webhook_url (e.g. https://your-domain.com - no trailing slash or api path at the end)
PORT=8000
```

3. Run the bot:
```bash
python main.py
```

## Features
- Create unique webhook URLs for different services
- Receive and forward status notifications to Discord channels
- Support for multiple Discord servers
- Automatic channel creation and management
- Smart channel reuse (uses existing channels if they exist)
- Support for Statuspage.io webhooks
    - Component status updates
    - Incident updates and monitoring
    - System status changes
- Easy service management through Discord commands

## Commands
- `/addservice <service_name>` - Generate a new webhook URL for a service and create a dedicated channel
    - Creates a new channel in the same category as the command (e.g., "openai-status")
    - Reuses existing channels if they have the same name
    - Can be used across multiple servers for the same service
- `/listservices` - List all registered services
- `/removeservice <service_name>` - Remove a service
- `/setchannel <service_name> <channel>` - To manually set the notification channel for a service

## Multi-Server Support
The bot can be added to multiple Discord servers and will:
- Maintain separate channel configurations for each server
- Allow the same service to send notifications to multiple servers
- Create server-specific status channels
- Use a single webhook URL for each service across all servers

## Webhook Format
The bot supports the Statuspage.io webhook format, which includes:
- Component status updates
- Incident reports and updates
- System status changes
- Impact assessments

Each notification is formatted into a clear Discord embed with:
- Service name and status
- Color coding based on severity
- Detailed updates and descriptions
- Timestamps for each event

## Screenshots 
Here are some screenshots to show how the messages look
![image](https://github.com/user-attachments/assets/e4e27608-5961-4b50-8904-0ab9d8db45c6)
![image](https://github.com/user-attachments/assets/8d681652-2b08-43f8-9e02-d59add6963c1)


