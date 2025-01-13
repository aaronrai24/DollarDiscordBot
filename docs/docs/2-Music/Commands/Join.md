# `!join`

The `!join` command is used to have **Dollar** join the voice channel that the user is currently in. This command is essential for initiating music playback, as it allows the bot to connect to a voice channel where it can stream audio.

## Purpose

- **Dollar** needs to be in a voice channel to play music, and the `!join` command allows the bot to automatically join the voice channel that the user is connected to.
- This command ensures that **Dollar** can start interacting with the server’s audio system and play music directly in the voice channel.

## How It Works

When you use the `!join` command, **Dollar** will check if you are currently in a voice channel. If you are, the bot will join that voice channel and be ready to stream music.

### Usage

```bash
!join
```

If you are in a voice channel called **"Music"**, you can type `!join`, and **Dollar** will automatically join the **"Music"** voice channel.

## Important Notes

- **Dollar** will only join a voice channel if the user issuing the command is already connected to one. If the user is not in a voice channel, the bot will not join any channel.
- If **Dollar** is already in a voice channel, calling `!join` will simply keep the bot in that channel, ensuring continuous music playback.

The `!join` command is a fundamental part of the music functionality, as it sets the bot in the right context (a voice channel) to play and manage music.
