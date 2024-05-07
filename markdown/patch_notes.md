Dollar 1.1.6 updates the built in Lavalink player and uses the youtube-source plugin to search for songs. This fixes this major [bug](https://github.com/aaronrai24/DollarDiscordBot/issues/101), where the bot would be able to search for songs but not play them. The bot now uses the youtube plugin to search for songs and play them. 

## Fixes and Enhancements

- Updated Lavalink to version 4.0.5
- Added [youtube-source plugin](https://github.com/lavalink-devs/youtube-source#plugin) to search for songs
- Fixed bug where the bot would not play songs

### Known Issue
- Currently Dollar's idle-timeout feature is not working as intended, this is due to an update with the wavelink library. We have disabled this feature and it is currently being worked on along with Dollar 2.0.
