# `!nowplaying`

The `!nowplaying` command displays the **current song** that is playing in the voice channel. It provides users with the title and artist of the song that **Dollar** is playing, allowing everyone to stay informed about the track currently being played.

## Purpose
- The `!nowplaying` command is designed to show the **current song** being played by **Dollar** in the voice channel.
- This command is useful for users who want to know the title and artist of the song without needing to check the player directly.

## How It Works
When you issue the `!nowplaying` command, **Dollar** will send a message in the text channel with the title and artist of the song that is currently playing. If no song is currently playing, the bot will notify you that there is no active song.

- **Dollar** checks the currently playing song.
- The bot sends a message with the title and artist of the current song.
- If the bot is not currently playing a song, it will notify you that there is no active song.

### Usage

```bash
!nowplaying
```

If the current song playing is "Blinding Lights" by The Weeknd, typing `!nowplaying` will result in **Dollar** sending the following message to the chat:

```bash
Now playing: "Blinding Lights" by The Weeknd
```

## Important Notes

- The `!nowplaying` command only works when there is a song currently playing in the voice channel. If no song is playing, the bot will inform you that there is no active song.