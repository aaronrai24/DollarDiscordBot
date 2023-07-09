Dollar 1.1.2 aims to eliminate additional pesky bugs to enhance the user experience and create a smoother software version. As we progress towards more stable iterations of 1.1, we encourage users to share their feature requests using `/featurerequest`. Your ideas are valuable to us!

*New Features*:
`!nowplaying` - Reworked command to display a prettier message to show the current playing song. Now we use the Genius API to show the current playing song, its artist and a thumbnail of the songs artwork.

**Fixes:**
- Fix to MySQL connection timing out, last attempt at a validation query would cause Dollar's terminal to freeze due to threads not being cleaned up. Refactored to use tasks.loop rather than manually creating a thread. Tasks.loop run in the background of the main event thread and is essentially the same creating a thread for this task.
- Fix to Event permissions, now users are granted access to Shows📺 by default. If you create and start an event, 'interested' users will be given access to join the channel when the event starts, while restricting access for everone who is 'uninterested'