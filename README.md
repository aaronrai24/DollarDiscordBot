# DollarDiscordBot
---

Introducing Dollar Bot: Your all-in-one Discord companion! Powered by Lavalink, Dollar not only lets you play music from popular websites, but goes above and beyond. Dollar acts as a versatile moderator, creating personal voice channels and enforcing proper command usage.

With Dollar, you'll enjoy a seamless music experience. It intelligently responds to commands entered in the designated text channel and plays music exclusively when users are in the same voice channel. No more juggling multiple music platforms!

But that's not all! Dollar harnesses various APIs to elevate your experience. Dive into your lifetime stats for beloved video games, thanks to TrackerGG integration. Dollar keeps you connected, letting you and your friends listen to the same music simultaneously.

Stay tuned for weekly updates and exciting new features as Dollar continually evolves. Add Dollar and unleash the true potential of your Discord server!

## To add Dollar to your Discord:
Click the following [link](https://discord.com/api/oauth2/authorize?client_id=1044813990473257081&permissions=8&scope=applications.commands%20bot) to add to your Discord!
- Be sure to run `/setup` upon first loading Dollar into your Discord to automatically setup the requirements.

## Requirements to be able to use Dollar in your discord:

1. You must have a text channel that starts with `commands`. It is recommended to use `commands` as the channel name, but having emojis after the `commands` string is also acceptable.

To use auto channel creation feature:

2. You must have a voice channel titled `JOIN HERE💎`. When users join this voice channel, Dollar recognizes them and automatically creates a channel for each user, moving them to their respective channels. Once a created channel becomes empty, Dollar removes it.

## Issues/Feature Requests

We are also tracking numerous bugs and feature requests on our public [issues board](https://github.com/aaronrai24/DollarDiscordBot/issues). We'd appreciate any bugs/features requests be submitted by using Dollar's `/featurerequest` and `/reportBug` commands.

## For Developers

### Install Dependencies
To install the required dependencies, run the following command:
`pip install -r rquirements.txt`

or use the setup.bat to run this code automatically

### Install Lavalink
- To install Lavalink see this [repository](https://github.com/lavalink-devs/Lavalink)
- Recommended Java Version is `Java 17.0.1`

### Install PostgreSQL database
- To install PostgreSQL see this [link](https://www.postgresql.org/download/)
- Dollar currently uses a Postgres database for notification features, for schema export please contact a contributor of Dollar

### API Auth Keys
- Numerous Keys are required to take advantage of Dollars Spotify, Game and GitHub commands. Here is a list of API keys that are used:
1. DISCORD_TOKEN - Discord bot token
2. genius - Genius lyrics token
3. CLIENT_ID - Spotify
4. CLIENT_SECRET - Spotify
5. TRACKER_GG - TrackerGG
6. RIOT_TOKEN - RIOT API
7. GITHUB_TOKEN - Github
- Store these tokens in a `.env` file following that syntax

### Logging
We have begun to develop a standard for logging. For debugging purposes do not rely on the console output, and turn to the `discord.log` instead. 
Summary of loggers:
- music: Relates to music related commands and functions
- game-commands: Relates to game commands
- watchlist: Relates to watchlist commands
- dollar: General logger that is used in Dollar's core functions that are used repeatedly
- diagnostic: Relates to Dollar diagnostic commands that are ADMIN only. Ensures diagnostic commands are working properly
- administrative: Relates to administrative commands
- queries: Relates to database queries
- settings: Relates to settings commands