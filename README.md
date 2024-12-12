# Central Notifications Bot

A Discord bot that manages service status notifications through webhooks. The bot allows you to subscribe to various service status pages and receive notifications directly in your Discord servers.

## Quick Start
You can use our hosted version of the bot:
1. [Invite the bot to your server](https://discord.com/oauth2/authorize?client_id=1316555696430387301)
2. Navigate to the category where you want status notifications to appear
3. Choose one of these methods to set up services:
   
   **Option 1: Quick Setup (Recommended)**
   - Use `/setup [category_name]` to automatically create a category with channels for all available services
   - This will set up all services at once in a new category
   
   **Option 2: Manual Setup**
   - Use `/addservice <service_name>` for each service you want to add
   - Available services:
     - `openai` - OpenAI Status Updates
     - `github` - GitHub Status Updates
     - `discord` - Discord Status Updates
   - Example: `/addservice github` to add GitHub status notifications

4. Configure your status page to send notifications to the provided webhook URL (if you're adding your own service)
5. Done! You'll now receive status updates in your Discord server

Want to add a new service? Use `/servicerequest` to request additional services to be added to the bot.

## Project Structure
```
Central-Notifications-Bot/
├── src/
│   ├── bot/
│   │   ├── commands/
│   │   │   ├── __init__.py
│   │   │   ├── base_cog.py        # Base cog with shared functionality
│   │   │   ├── add_service.py     # Add service command
│   │   │   ├── remove_service.py  # Remove service command
│   │   │   ├── delete_service.py  # Delete service command
│   │   │   ├── list_services.py   # List services command
│   │   │   ├── help.py           # Help command
│   │   │   ├── about.py          # About command
│   │   │   ├── service_request.py # Service request command
│   │   │   └── setup.py          # Setup command
│   │   └── bot.py                # Main bot class
│   └── webhook/
│       └── server.py             # FastAPI webhook server
├── main.py                       # Entry point
├── requirements.txt              # Python dependencies
├── .env                         # Environment variables
└── README.md                    # This file
```

## Self-Hosting Setup
1. Clone the repository:
```bash
git clone https://github.com/Bentlybro/Central-Notifications-Bot.git
cd Central-Notifications-Bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with the following variables:
```env
DISCORD_TOKEN=your_discord_bot_token
WEBHOOK_BASE_URL=your_public_webhook_url (e.g. https://your-domain.com - no trailing slash or api path at the end)
PORT=8000
OWNER_ID=your_discord_user_id  # Required for owner-only commands
```

4. Set up the database:
- The bot will automatically create a SQLite database at `config/services.db`
- The database schema includes tables for services and server channels
- No manual setup required

5. Run the bot:
```bash
python main.py
```

The bot will:
- Initialize the database
- Start the FastAPI webhook server
- Connect to Discord
- Load all command cogs
- Begin listening for commands and webhooks

## Commands
### User Commands
- `/addservice <service_name>` - Add an existing service to your server
- `/removeservice <service_name>` - Remove a service from your server
- `/help` - Display help information
- `/about` - Learn about the bot
- `/setup [category_name]` - Create a new category with channels for all services

### Owner Commands
- `/addservice <service_name>` - Create a new service (when it doesn't exist)
- `/deleteservice <service_name>` - Completely delete a service
- `/listservices` - List all registered services

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

## Development
To add new features or modify existing ones:
1. Commands are organized in separate files in `src/bot/commands/`
2. Each command extends the `BaseServiceCog` class
3. Database operations are handled through the base cog
4. Webhook handling is in `src/webhook/server.py`

## Screenshots 
Here are some screenshots to show how the messages look
![image](https://github.com/user-attachments/assets/e4e27608-5961-4b50-8904-0ab9d8db45c6)
![image](https://github.com/user-attachments/assets/8d681652-2b08-43f8-9e02-d59add6963c1)


