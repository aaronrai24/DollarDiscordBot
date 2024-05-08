# DollarDiscordBot
---

Introducing Dollar Bot: Your all-in-one Discord companion! Powered by Lavalink, Dollar not only lets you play music from popular websites, but goes above and beyond. Dollar acts as a versatile moderator, creating personal voice channels and enforcing proper command usage.

With Dollar, you'll enjoy a seamless music experience. It intelligently responds to commands entered in the designated text channel and plays music exclusively when users are in the same voice channel. No more juggling multiple music platforms!

But that's not all! Dollar harnesses various APIs to elevate your experience. Dive into your lifetime stats for beloved video games, thanks to TrackerGG integration. Dollar keeps you connected, letting you and your friends listen to the same music simultaneously.

Stay tuned for weekly updates and exciting new features as Dollar continually evolves. Add Dollar and unleash the true potential of your Discord server!

## To add Dollar to your Discord:
Click the following [link](https://discord.com/api/oauth2/authorize?client_id=1044813990473257081&permissions=8&scope=applications.commands%20bot) to add to your Discord!
- Dollar will DM you with a welcome message and what to do next! 
- For a list of commands, type `!help` in the designated text channel.

## Issues/Feature Requests

We are also tracking numerous bugs and feature requests on our public [issues board](https://github.com/aaronrai24/DollarDiscordBot/issues). We'd appreciate any bugs/features requests be submitted by using Dollar's `/featurerequest` and `/reportbug` commands.

## For Developers

### Docker Setup
- To run the bot in a docker container, you must first build the image using the following command:
```bash
docker build -t dollar .
```
- Once the image is built, you can run the container using the following command:
```bash
docker compose up
```
- This will run the bot, lavalink, and the database in separate containers. The bot will be connected to the database and lavalink automatically.
- After making code changes, you can rebuild the image and restart the container using the following commands:
```bash
docker-compose up --build -d
```

### API Auth Keys
- Numerous Keys are required to take advantage of Dollars Spotify, Game and GitHub commands. Here is a list of API keys that are used:
1. DISCORD_TOKEN - Discord bot token
2. GENIUSTOKEN - Genius lyrics token
3. LAVALINK_TOKEN - Lavalink password
4. LAVALINK_EMAIL - Lavalink youtube email
5. LAVALINK_PASSWORD - Lavalink youtube password
6. CLIENT_ID - Spotify
7. CLIENT_SECRET - Spotify
8. TRACKER_GG - TrackerGG
9. RIOT_TOKEN - RIOT API
10. GITHUB_TOKEN - Github
11. DB_USER - Database username
12. DB_PASS - Database password
13. DB_SCHEMA - Database schema
- Store these tokens in a `.env` file following that syntax

### Logging
We have begun to develop a standard for logging. For debugging purposes do not rely on the console output, and turn to the `discord.log` instead. 
Summary of loggers:
- music: Relates to music related commands and functions
- game-commands: Relates to game commands
- watchlist: Relates to watchlist commands
- core: General logger that is used in Dollar's core functions that are used repeatedly
- dollar: General logger that is used in Dollar's core functions that are used repeatedly
- diagnostic: Relates to Dollar diagnostic commands that are ADMIN only. Ensures diagnostic commands are working properly
- administrative: Relates to administrative commands
- queries: Relates to database queries
- settings: Relates to settings commands