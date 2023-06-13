Dollar 1.1 had a successful launch and now we're back fixing the mayhem that was introduced in 1.1 as well as enhancing the new features as well. Thanks for the support as we continue to patch and improve Dollar's usabillity. Again if you encounter any issues or think of features that would be nice please use `/reportbug` and `/featurerequest` to let us know!

*New Features*:

**MyWatchList Improvements**
- Added `!clearhistory`, this command will clear you watch history in one shot.

**Spotify Playlist Generation Improvement**
- `!generateplaylist "Genre" "Artist" "Album"` - Now Genre is an optional parameter so you can generate playlists based off just a artist or album. Commands that do not include a genre should be executed exactly like this: `!generateplaylist "" "Drake"`, where "" represents an empty string. 

**New Application Command**
- Added `/ticket`, this command will give users an invite to a text channel in the mfDiscord for a ticket to be created with their issue. This will be a way for users to explain an issue they are having with Dollar and be a way to troubleshoot issues.

**Fixes:**
- Fix to MyWatchList `!addhistory` and `!addshow` will now check for duplicate show name to avoid entering duplicate shows into the database and using up limited space.
- Fix to auto channel creation, due to new discord name changes channels were being created using your actual discord name. We've update this to use your server name rather than your actual discord name as we believe the server name is what users would like their name to be.
- Removed 'X Discord is not using auto channel creation logger'.
- Fix to MySQL connection timing out, added validation query that runs in its own thread constantly keeping connection to the MySQL database valid. This should result in zero downtime with the database.
- Fix to event notifications, event notification message will now include the event title in the message.
- Fix to events, upon revoking access to Shows, users will still be given permission to create events.