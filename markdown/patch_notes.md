Dollar 1.1.5 updates the built in Lavalink player and Wavelink libraries to address a bug that caused the bot to fail to play music from Youtube and SoundCloud. Dollar 2.0 is also in development and will be released soon, with exciting new features and improvements. We plan to release a beta version of Dollar 2.0 in the coming weeks to test out new infrastructure(Docker) and features, to gather feedback from the community. If you would like to participate in the beta, please reach out to __mfcash__ on Discord.

## Fixes and Enhancements

- Updated Lavalink to 4.0.4 to address `java.io.IOException: Invalid status code for video page response: 400` error
- Updated DiscordPY to 2.3.2
- Updated Wavelink to 3.2.0 and updated music commands to reflect new Wavelink features
- Updated Server Python version to 3.12.2
- Added `!replay` command to restart current playing song
- Removed `!playsc` command as Wavelink 3.0 no longer supports searching SoundCloud directly, all searches are now down through `!play` and search Youtube, Youtube Music, and SoundCloud.


### Bugs and Issues
- If you encounter any issues with the bot, please report them using `/reportbug`, updating these dependencies may have introduced new bugs or issues that we are not aware of, or missed during testing, and we appreciate your help in identifying and resolving them. 
- If you have any feedback or suggestions for Dollar 2.0, please use `/featurerequest` to submit your ideas and suggestions. The update to Wavelink 3.0 and Lavalink 4.0.4 has introduced new features and improvements that we would like to incorporate into Dollar 2.0, and we would like to hear from you about what you would like to see in the next version of Dollar. Please checkout this [link](https://wavelink.dev/en/latest/migrating.html) for more information on the new features and improvements in Wavelink 3.0 and Lavalink 4.0.4.