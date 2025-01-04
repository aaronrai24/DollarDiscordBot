# `!queue`

The `!queue` command allows users to **view the current music queue**. It displays all the songs that are waiting to be played after the current song finishes, providing users with an overview of upcoming tracks.

## Purpose
- The `!queue` command is designed to **display the list of songs** currently in the music queue.
- This command is useful for users who want to see what songs are queued up next, helping them manage and keep track of the playlist.

## How It Works
When you issue the `!queue` command, **Dollar** retrieves the songs that are queued up for playback after the current song finishes. The bot then sends the list of queued songs to the chat so users can see what's next in line.

- **Dollar** checks the queue for any songs waiting to be played.
- The bot formats the queue and sends it to the chat, displaying the titles and artists of the upcoming tracks.
- If the queue is empty, **Dollar** will inform users that there are no songs in the queue.

### Usage

```bash
!queue
```

- This command has no additional parameters or options.

### Example

```bash
!queue
```

#### Output

```
1. Song Title - Artist
2. Song Title - Artist
3. Song Title - Artist
...
```

- This command will display the list of songs currently in the queue, showing the titles and artists of the upcoming tracks.

## Important Notes

- The `!queue` command provides a quick way to see what songs are lined up for playback after the current song.
- If the queue is empty, **Dollar** will notify users that there are no songs in the queue.
