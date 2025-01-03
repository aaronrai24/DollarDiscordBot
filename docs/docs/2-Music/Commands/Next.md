# `!next`

The `!next` command allows users to view the **next song** in the music queue. It provides a preview of the song that is scheduled to play after the current track finishes, giving users an idea of what to expect next.

## Purpose

- The `!next` command is designed to show the **upcoming track** in the music queue without having to wait for the current song to finish playing.
- This command is useful for users who want to know what song is coming up next or if they are considering skipping to the next track.

## How It Works

When you issue the `!next` command, **Dollar** checks the music queue to identify the song that will play after the current song finishes. The bot then sends the title of the next song to the chat, so users can see what’s coming up next in the queue.

- **Dollar** examines the queue to find the next song that will be played.
- The bot sends a message containing the title of the next song to the chat, allowing users to preview the upcoming track.
- If there are no songs in the queue or the bot is at the end of the queue, **Dollar** will notify the user that there is no next song available.

### Usage

```bash
!next
```

If the current song is "Timeless" by The Weeknd and Playboi Carti and the next song in the queue is "Levitating" by Dua Lipa, typing `!next` will prompt **Dollar** to send the following message to the chat:

```bash
The next song in the queue is "Levitating" by Dua Lipa.
```

## Important Notes

- The `!next` command only works if there are additional songs in the queue after the current one. If the queue is empty or there is no next song, **Dollar** will inform you that there is no upcoming track.
- This command provides a helpful preview of the music queue, making it easier for users to decide whether to skip or wait for the next song.

The `!next` command enhances the music playback experience by allowing users to stay informed about what’s coming up next in the playlist, making it easier to manage the queue.
