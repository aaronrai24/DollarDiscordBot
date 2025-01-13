# `!pause`

The `!pause` command allows users to **pause the current song** that is playing in the voice channel. It temporarily stops the playback, allowing users to resume later without losing the song's progress.

## Purpose
- The `!pause` command is designed to **pause the music** that is currently playing in the voice channel.
- This command is useful for users who need a break from the music or want to temporarily stop playback without skipping or losing the current song.

## How It Works
When you issue the `!pause` command, **Dollar** pauses the current song that is playing. The song remains in the same position, and users can resume it later with the `!resume` command.

- **Dollar** stops the playback of the current song but keeps it in the same position.
- The bot will confirm that the song has been paused in the chat.
- To resume the song, users can use the `!resume` command.

### Usage

```bash
!pause
```

If the current song playing is "Blinding Lights" by The Weeknd, typing `!pause` will result in **Dollar** pausing the song will make dollar react with the pause emoji.

## Important Notes

- The `!pause` command only works when there is a song currently playing in the voice channel. If no song is playing, the bot will notify you that there is no active song to pause.
- **Dollar** will pause the song at its current position, allowing users to resume playback from where they left off.
- Users can use the [!resume](./Resume.md) command to continue playing the paused song without restarting it.