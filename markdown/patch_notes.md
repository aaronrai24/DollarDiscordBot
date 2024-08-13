Long awaited update to Dollar! Here is each new feature broken down, followed by a list of fixes and enhancements. 

## New Features

### Dollar Settings

- Added a new feature that allows users to customize the bot's settings to your discord using the `/dollarsettings` command.
- Users can customize their preferred names for their text, voice and shows discord channels.
- This will set dollars trigger channels to respond to commands and for the auto-channel-creation feature to work.

### Docker Containerization

- Dollar is now containerized using Docker. This allows for easier deployment and scaling of the bot.
- Included in the Docker container are images for the bot, the database, and lavalink.

### Patch Note Notifications

- Added a new feature to get pinged for new patch notes for a game you are subscribed to.
- Simply add a 🔔 emoji as a reaction to a game you want to be notified for and Dollar will create a thread on subsequent patch note updates and @you in the thread.
- To unsubscribe, simple add a ❌ emoji as a reaction to the game you want to unsubscribe from.

### Deeper Integration with Spotipy API

- Added a new command, `!spotify_playlist (playlist name)`, that allows users to search for playlists on Spotify. This command will play the first result found on Spotify.
- Added a new command, `!lofi`, that plays lofi playlist on Spotify.

### ETA to Work Notifications

- Added a new feature that DMs users with an ETA to work based on their home address and work address. This feature is activated by setting the home and work addresses using the `/updateuserinfo` command. The ETA is calculated using the Google Maps API.
- DMs are sent at 6:30 AM every weekday morning. This feature is disabled on weekends.

### Weather Notifications

- Added a new feature that DMs users with the weather forecast for the day. This feature is activated by setting the home address using the `/updateuserinfo` command. The weather forecast is calculated using the OpenWeatherMap API.
- DMs are sent at 6:30 AM every morning. This feature is disabled on weekends.

### Embed Creator

- Added a new feature that allows users to create custom embeds using the `!embed` command.
- Users can create custom embeds by providing the title, description, color, and fields for the embed.
- The bot will then create an embed with the provided information and post it in the channel.

### Fixes and Enhancements

- Added more debug loggers ([#66](https://github.com/aaronrai24/DollarDiscordBot/issues/66)) to help with debugging codebase
- Added feature to notify of planned downtime/mainenance and newly discovered bugs. 
- Added message reactions to reduce spam in the preferred text channel/commands channel
- Addressed java.lang.RuntimeException ([#60](https://github.com/aaronrai24/DollarDiscordBot/issues/60)) by updating Java on Dollar's server
- Cleaned up codebase and removed unused imports as well as corrected current methods to import libraries and classes([#85](https://github.com/aaronrai24/DollarDiscordBot/issues/85)).
- Fixed an issue where dollar would not leave a voice channel after being idle for 10 minutes
- Fixed an issue where orphaned channels were getting created by Dollar's auto-channel-creation feature ([#112](https://github.com/aaronrai24/DollarDiscordBot/issues/112)).
- Fixed an issue where `!nowplaying` would not display the correct song playing
- Manged dollar settings for existing servers ([#106](https://github.com/aaronrai24/DollarDiscordBot/issues/106)) by adding an extra step when entering dollar settings to ensure the guild is in the database.
- Migrated from MySQL to PostgreSQL for better performance and scalability.

### Deprecated Features

- Removed all MyWatchList commands and features as the methods were outdated and no longer functional.
