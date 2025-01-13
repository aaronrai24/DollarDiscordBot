- 2.0.2 fixes some minor annoyances and updates some documentation, if you notice any issues please report them or missing documentation please report it using the `/reportbug` command as we are trying to make Dollar as stable as possible.


### Fixes and Enhancements

- Added deployment status to the deployment page in github
- Added documentation for game/software update notifiations[Dollar Docs](https://aaronrai24.github.io/DollarDiscordBot/docs/Notifications/overview)
- Added auto channel creation persistence by storing the channel id in the database. This was added in case a deployment is made and the bot is restarted, the bot will not lose the channel id and will allow the feature to work as intended.
- Fixed an issue with `Poke User`, now Dollar checks if the poked user was already in the same voice channel as the user who poked them. If they were, the bot will not send a message to the user who was poked.
