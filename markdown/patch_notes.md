- After a slight rough start with the 2.0.0 release, 2.0.1 is here to fix some of the issues that were present in the previous release. 

### Dollar User Manual

- Added Docusarus to the project, command documentation and user guide are now available at our github([Dollar Docs](https://aaronrai24.github.io/DollarDiscordBot/)). This will be updated regularly with new features and changes to the bot and will be the primary source of information for users and developers. `/help` command will continue to be a quick reference for users to see all available commands but will also link to the documentation for more detailed information.

- The documentation will be a continued work in progress, so if you see any issues or have any suggestions, please feel free to open an issue on the github repository with your feedback.
- Developer documentation will be added soon to assist developers in setting up their own instances of the bot and creating their own commands to contribute to the bot.

### Fixes and Enhancements

- Fixed an issue where user ids were not being stored in the database when adding a user to the database from `/updateuserinfo`
- Fixed an issue where `/help` view was still being displayed after a button was clicked, now the help view will be removed after a button is clicked
- Fixed an issue where auto channel creation would create the voice channel above the trigger channel, now the voice channel will be created right below the trigger channel
- Added Context Menu Commands to `/help` command
- Added user prefered timezone to the database, now when updating user info, you can set your timezone and any time based commands/info will be displayed in your timezone([#135](https://github.com/aaronrai24/DollarDiscordBot/issues/135))
- Temporarily removed game commands, they will be re-released in a future update once APIs are available to get game information
