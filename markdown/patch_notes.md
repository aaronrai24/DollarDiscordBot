## New Features

### Dollar Settings

- Added a new feature that allows users to customize the bot's settings to your discord using the `/dollarsettings` command.
- Users can customize their preferred names for their text, voice and shows discord channels.
- This will set dollars trigger channels to respond to commands and for the auto-channel-creation feature to work.

### Music Improvements
- Added `!lofi` command that generates a lofi playlist of songs to play.
- Added `!remove (song number)` command to remove a song from the queue.
- Added `!swap (song number) (song number)` command to swap the position of two songs in the queue.
- Added `!shuffle` command to shuffle the queue.

### User Information
- Added a new feature that allows user to give information like home/work address using the `/updateuserinfo` command.
- This information is planned to be used for future featurs.
- **Note**: This information is stored in the database securely and is not shared with anyone.

### Docker Containerization

- Dollar is now containerized using Docker. This allows for easier deployment and scaling of the bot.
- Included in the Docker container are images for the bot, the database, and lavalink.

### Patch Note Notifications

- Added a new feature to get pinged for new patch notes for a game you are subscribed to.
- Simply add a 🔔 emoji as a reaction to a game you want to be notified for and Dollar will create a thread on subsequent patch note updates and @you in the thread.
- To unsubscribe, simple add a ❌ emoji as a reaction to the game you want to unsubscribe from.

### Context Menu Commands
- Added a new feature that allows users to interact with Dollar using context menus.
  - Users can now `Poke User` to send a message to a user to join a voice channel. Simply right-click on a user and navigate to `Apps > Poke User`, and Dollar will take care of the rest.
  - Also added a `User Information` context menu that allows users to view information about a user.

### Deeper Integration with Spotipy API

- Added a new command, `!spotify_playlist (playlist name)`, that allows users to search for playlists on Spotify. This command will play the first result found on Spotify.

### Embed Creator

- Added a new feature that allows users to create custom embeds using the `!embed` command.
- Users can create custom embeds by providing the title, description, color, and fields for the embed.
- The bot will then create an embed with the provided information and post it in the channel.

### Fixes and Enhancements

- Added more debug loggers ([#66](https://github.com/aaronrai24/DollarDiscordBot/issues/66)) to help with debugging codebase
- Added ability to reload dollars extensions without restarting the bot ([#113](https://github.com/aaronrai24/DollarDiscordBot/issues/113))
- Added feature to notify of planned downtime/mainenance and newly discovered bugs. 
- Added message reactions to reduce spam in the preferred text channel/commands channel
- Addressed java.lang.RuntimeException ([#60](https://github.com/aaronrai24/DollarDiscordBot/issues/60)) by switching to Docker
- Cleaned up codebase and removed unused imports as well as corrected current methods to import libraries and classes([#85](https://github.com/aaronrai24/DollarDiscordBot/issues/85)).
- Fixed an issue where dollar would not leave a voice channel after being idle for 10 minutes
- Fixed an issue where orphaned channels were getting created by Dollar's auto-channel-creation feature ([#112](https://github.com/aaronrai24/DollarDiscordBot/issues/112)).
- Fixed an issue where `!nowplaying` would not display the correct song playing
- Managed dollar settings for existing servers ([#106](https://github.com/aaronrai24/DollarDiscordBot/issues/106)) by adding an extra step when entering dollar settings to ensure the guild is in the database.
- Migrated from MySQL to PostgreSQL for better performance and scalability.

### Deprecated Features

- Removed all MyWatchList commands and features as the methods were outdated and no longer functional.
