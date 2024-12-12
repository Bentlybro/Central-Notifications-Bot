# Central Notifications Bot

A Discord bot that manages service status notifications through webhooks. The bot allows you to subscribe to various service status pages and receive notifications directly in your Discord servers.

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

## Setup
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

## Usage
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