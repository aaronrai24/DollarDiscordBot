# `!playskip`

The `!playskip` command allows users to **skip the currently playing song** and immediately **start playing a new song** that is specified by the user. It combines the functions of skipping a song and playing a new one in a single command.

## Purpose
- The `!playskip` command is designed to **skip the current song** in the queue and **start a new song** immediately.
- This command is useful for users who want to quickly move on to a new track without having to wait for the current song to finish.

## How It Works
When you issue the `!playskip` command followed by a song name or URL, **Dollar** skips the current song and immediately starts playing the song specified in the command. If the song is found, it will be added to the queue and start playing right away.

- **Dollar** skips the song currently playing.
- The bot searches for the new song based on the user’s input (song name or URL).
- If the song is found, it is added to the queue and played immediately.

### Usage

```bash
!playskip <song_name_or_url>
```

- Replace `<song_name_or_url>` with the name of the song or the URL of the song you want to play.

### Example

```bash
!playskip Despacito
```

In this example, the bot will skip the current song and start playing the song "Despacito" immediately.

## Important Notes

- The `!playskip` command is a quick way to skip the current song and start playing a new one.
- This command is useful when you want to change the song without waiting for the current one to finish.
