## Patch: 2.0.1

### Docusarus
- Added Docusarus to the project, command documentation and user guide are now available at [Dollar Docs](https://aaronrai24.github.io/DollarDiscordBot/). This will be updated regularly with new features and changes to the bot and will be the primary source of information for users and developers. `/help` command will continue to be a quick reference for users to see all available commands but will also link to the documentation for more detailed information.

### Fixes and Enhancements
- Fixed an issue where user ids were not being stored in the database when adding a user to the database from `/updateuserinfo`
- Added user preffered timezone to the database, now when updating user info, you can set your timezone and any time based commands/info will be displayed in your timezone
