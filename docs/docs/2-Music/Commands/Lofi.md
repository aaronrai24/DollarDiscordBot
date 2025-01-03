# `!lofi`

The `!lofi` command allows **Dollar** to generate a **lofi music playlist** and start playing it in the voice channel. The playlist consists of relaxing, chill, and calming music, ideal for background listening while working, studying, or just relaxing.

## Purpose
- The `!lofi` command provides users with an instant lofi music experience by generating a curated playlist of lofi tracks.
- It is useful for creating a calm atmosphere in the voice channel, especially in servers focused on relaxation or study.

## How It Works
When you issue the `!lofi` command, **Dollar** will automatically search for a curated playlist of lofi music and begin playing it. The playlist typically includes ambient, instrumental beats that are characteristic of lofi music. 

- **Dollar** will search for a lofi playlist on YouTube using **Wavelink** (via the YouTube API).
- Once the playlist is found, **Dollar** will add the tracks to the music queue and start playing them in the voice channel.

### Usage:

```bash
!lofi
```

Typing `!lofi` in the chat will prompt **Dollar** to generate a lofi music playlist and start playing it in the voice channel you're currently in.

## Important Notes

- The `!lofi` command automatically generates a playlist and adds it to the queue, so no additional song selection is required.
- The playlist will consist of chill, relaxing lofi beats that are suitable for background listening.
- The bot will only play the lofi music if it is connected to a voice channel. If **Dollar** is not in a voice channel, it will not be able to play the playlist until it joins one.
- If the bot is already playing music, the `!lofi` command will queue the lofi playlist after the current track finishes.

The `!lofi` command is a great way to enjoy relaxing background music without needing to search for tracks manually. It provides users with a seamless listening experience, perfect for creating a chill atmosphere in any server.
