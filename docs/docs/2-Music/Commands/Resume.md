# `!resume`

The `!resume` command allows users to **resume the song** that was previously paused. It restarts the playback from the point where the song was paused, ensuring a seamless listening experience.

## Purpose
- The `!resume` command is designed to **resume playback** of the song that was paused using the `!pause` command.
- This command is useful for users who want to continue listening to the current song after taking a break.

## How It Works
When you issue the `!resume` command, **Dollar** resumes the playback of the song from where it was paused. The song continues playing without skipping or restarting.

- **Dollar** retrieves the song from its paused position.
- The bot will confirm that the song has been resumed in the chat.

### Usage

```bash
!resume
```

If the song "Blinding Lights" by The Weeknd was paused using the `!pause` command, typing `!resume` will prompt **Dollar** to resume the song from where it was paused.

## Important Notes
- The `!resume` command only works when a song has been paused using the `!pause` command. If no song has been paused, the bot will notify you that there is no song to resume.
- **Dollar** will resume the song from where it was paused, ensuring a seamless listening experience for users.
