**New Features**:

**Spotify Playlist Generation:**
- `!spotify 'genre' 'artist' 'album'`, can now be used to generate a 25 song playlist automatically leveraging Spotify's API. Genre is a required field, while artist and album can be given to make playlists more specific. If you would like more filters to be added I suggest taking a look at [Spotipy documentation](https://spotipy.readthedocs.io/en/latest/#spotipy.client.Spotify.search) to see what other filters may be useful, and then submit a feature request using `/featurerequest`.

**Event Permissions:**
- By default, everyone will not have access to the Shows voice channel.
- Users interested in the event will be given permissions to join Shows when the event starts.
- When the event ends, permissions to join the Shows voice channel will get reset.

**New Game Commands:**
  - `!csgo (steamID)` - Grabs all CSGO stats like kills, deaths, wins, etc using TrackerGG API.
  - `!apex (originID)` - Grabs all Apex stats like kills, deaths, rank, etc using TrackerGG API.

**Application commands:**
- `/ping` - Diagnostic tool to check if Dollar's responding.
- `/status` - Diagnostic tool to check Dollar server CPU, memory usage, and Dollar's uptime.
- `/setup` - Used for first time setup when adding Dollar to your discord, the commands text channel, and the JOIN HERE voice channel to take advantage of all of Dollar's features.
- `/reportbug` - Submit a bug for Dollar. This gets sent directly to the Developer.
- `/featurerequest` - Submit a feature request for Dollar to get new features added.
  - Both `/reportbug` and `/featurerequest` will notify if the report/request was accepted or declined. This will notify the submitee.
- Also added rate limits for bug reports and feature requests to prevent users from spamming the devs.
- This also updates the public board found at [Issues](https://github.com/aaronrai24/DollarDiscordBot/issues)

**Multi-threading:**
- Beginning optimizations to Dollar, since Dollar now handles much more than music there are a lot of tasks that can happen simultaneously. Now Dollar's idle timeout operates in its own thread, this leads to increased responsiveness and better utilization of resources.

**Changes to DJ role:**
- Dollar used to add a DJ role when users join a voice channel, and removed that role when they left. This was a decent way of verifying the user was actually in a voice channel to interact with Dollar.
- Now Dollar knows if you are in the same voice channel, if you are, your command will get processed, if not, a message will be sent indicating you are not in the same voice channel to interact with Dollar.
- Dollar no longer needs to add/remove the dj role when user join and leave voice channels, this removes one dependancy for adding Dollar to discords.

**Fixes:**
- Fixes to DMing Dollar, help commands now get embedded plus instructions on adding Dollar to your discord.
- Fixes to `!clear` commands, now admins and mods will be able to use the command to clear messages.
- Removed `!stop` command, due to optimizations of `!queue` and `!load`, stopping playlist loading or queue printing is no longer necessary.
- Added logger for when a song starts playing to help debugging songs getting 'queued' but not playing.
- Fixes to auto channel creation, now Dollar will lock the JOIN HERE voice channel until the user has joined their created channel rather than simply locking the channel for 5 seconds.
- Fix to !load, now queries will be done in YouTubeMusic rather than just YouTube to give better chances of just music playing and not music videos.
- Additional fix to !load, now removes old CSV files uploaded once playlist has been loaded to prevent multiple CSVs being present on Dollar's drive.