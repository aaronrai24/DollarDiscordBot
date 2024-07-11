Long awaited update to Dollar! Dollar 2.0.0 includes a deeper integration with the Spotipy API, allowing users to search for playlists on Spotify. In addition, we have added new features that DM users with an ETA to work, the weather forecast, and NFL scores while migrating to a containerized environment and leveraging CI/CD tools from GitHub. 

## New Features

### Docker Containerization
- Dollar is now containerized using Docker. This allows for easier deployment and scaling of the bot.
- Included in the Docker container are images for the bot, the database, and lavalink.
- Running in Docker will allow for easier deployment and scaling of the bot while maintaining a consistent environment and improving security.

### Embed Creator
- Added a new feature that allows users to create custom embeds using the `!embed` command.
- Users can create custom embeds by providing the title, description, color, and fields for the embed.
- The bot will then create an embed with the provided information and post it in the channel.

### Patch Note Notifications
- Added a new feature to get pinged for new patch notes for a game you are subscribed to.
- Simply add a 🔔 emoji as a reaction to a game you want to be notified for and Dollar will create a thread on subsequent patch note updates and @you in the thread.
- To unsubscribe, simple add a ❌ emoji as a reaction to the game you want to unsubscribe from.

### Deeper Integration with Spotipy API
- Added a new command, `!spotify_playlist (playlist name)`, that allows users to search for playlists on Spotify. This command will play the first result found on Spotify.
- Added a new command, `!lofi`, that plays lofi playlist on Spotify.

### ETA to Work Notifications
- Added a new feature that DMs users with an ETA to work based on their home address and work address. This feature is activated by setting the home and work addresses using the /setup command. The ETA is calculated using the Google Maps API.
- DMs are sent at 6:30 AM every weekday morning. This feature is disabled on weekends.
- Disclaimer: This feature stores home and work addresses in a database. The addresses are only used to calculate the ETA to work and are not used for any other purpose.

### Weather Notifications
- Added a new feature that DMs users with the weather forecast for the day. This feature is activated by setting the home address using the /setup command. The weather forecast is calculated using the OpenWeatherMap API.
- DMs are sent at 6:30 AM every morning. This feature is disabled on weekends.
- Disclaimer: This feature stores home addresses in a database. The addresses are only used to calculate the weather forecast and are not used for any other purpose.

### NFL Score Notifications
- Added a new feature that posts scores to the `#sports` channel.
- Scores are posted at 1:00 PM, 5:30 PM, and 9:30 PM every Sunday.


### Fixes and Enhancements
- Added more debug loggers `[#66](https://github.com/aaronrai24/DollarDiscordBot/issues/66)` to help with debugging codebase
- Added feature to notify of planned downtime/mainenance and newly discovered bugs. 
- Addressed java.lang.RuntimeException `[#60](https://github.com/aaronrai24/DollarDiscordBot/issues/60)` by updating Java on Dollar's server
- Cleaned up codebase and removed unused imports as well as corrected current methods to import libraries and classes.
- Migrated from MySQL to PostgreSQL for better performance and scalability.


#### Deprecated Features
- Removed all MyWatchList commands and features as the methods were outdated and no longer functional.