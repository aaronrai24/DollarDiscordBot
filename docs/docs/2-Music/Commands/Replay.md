# `!replay`

The `!replay` command allows users to **restart the currently playing song**. It enables users to replay the song from the beginning without needing to manually skip to it or search for it again.

## Purpose
- The `!replay` command is designed to **replay the current song** that is currently playing.
- This command is useful for users who want to listen to the current song again from the start, without having to wait for it to finish or find it in the queue.

## How It Works
When you issue the `!replay` command, **Dollar** stops the current song (if it's still playing) and restarts it from the beginning. The bot will ensure the song starts playing again from the start of the track.

- **Dollar** checks if a song is currently playing.
- If a song is playing, the bot restarts it from the beginning and plays it again.
- If no song is currently playing, **Dollar** will notify the user that there is nothing to replay.

### Usage

```bash
!replay
```

- The `!replay` command does not require any additional parameters. It simply restarts the currently playing song from the beginning.

### Important Notes

- The `!replay` command is useful for replaying the current song without having to skip to it manually.
- This command is handy when you want to listen to a song again without searching for it or waiting for it to come up in the queue.
