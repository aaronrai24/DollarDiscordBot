**New Features**:

**MyWatchList**:
- Keep track of shows you are currently watching, or shows you've finished! Shows that have been finshed can be give an rating(1-5). 
- Dollar now has a MySQL database for persistent data so that this data is always available to users, expect more features leveraging this database soon!
- Support for images + more commands(including editing history) coming soon, checkout the feature requests on the [Issues](https://github.com/aaronrai24/DollarDiscordBot/issues) board.
- Added: `!watchlist` `!addshow` `!removeshow` `!history` `!addhistory` `!removehistory`, please do `!help mywatchlist` for more info.

**Spotify Playlist Generation:**
- `!spotify 'genre' 'artist' 'album'`, can now be used to generate a 25 song playlist automatically leveraging Spotify's API. Genre is a required field, while artist and album can be given to make playlists more specific. If you would like more filters to be added I suggest taking a look at [Spotipy documentation](https://spotipy.readthedocs.io/en/latest/#spotipy.client.Spotify.search) to see what other filters may be useful, and then submit a feature request using `/featurerequest`.

**Event Permissions:**
- By default, everyone will not have access to the Shows voice channel.
- Users interested in the event will be given permissions to join Shows when the event starts.
- When the event ends, permissions to join the Shows voice channel will get reset.

**New Game Commands:**
  - `!csgo (steamID)` - Grabs all CSGO stats like kills, deaths, wins, etc using TrackerGG API.
  - `!apex (originID)` - Grabs all Apex stats like kills, deaths, rank, etc using TrackerGG API.
  - `!lol (riotID)` - Grabs your current ranked stats for this season, like wins, losses, rank etc using RIOT GAMES API.

**Application commands:**
- `/ping` - Diagnostic tool to check if Dollar's responding.
- `/status` - Diagnostic tool to check Dollar server CPU, memory usage, and Dollar's uptime.
- `/setup` - Used for first time setup when adding Dollar to your discord, the commands text channel, and the JOIN HERE voice channel to take advantage of all of Dollar's features.
- `/reportbug` - Submit a bug for Dollar. This gets sent directly to the Developer.
- `/featurerequest` - Submit a feature request for Dollar to get new features added.
  - Both `/reportbug` and `/featurerequest` will notify if the report/request was accepted or declined. This will notify the submitee.
- Also added rate limits for bug reports and feature requests to prevent users from spamming the devs.
- This also updates the public board found at [Issues](https://github.com/aaronrai24/DollarDiscordBot/issues)

**Changes to DJ role:**
- Dollar used to add a DJ role when users join a voice channel, and removed that role when they left. This was a decent way of verifying the user was actually in a voice channel to interact with Dollar.
- Now Dollar knows if you are in the same voice channel, if you are, your command will get processed, if not, a message will be sent indicating you are not in the same voice channel to interact with Dollar.
- Dollar no longer needs to add/remove the dj role when user join and leave voice channels, this removes one dependancy for adding Dollar to discords.

**Fixes:**
- `!clear` command: Admins and mods can use it to clear messages.
- Removed `!stop` command. Optimizations made to `!queue` and `!load`.
- Fixes to auto channel creation and CSV handling in `!load` command.