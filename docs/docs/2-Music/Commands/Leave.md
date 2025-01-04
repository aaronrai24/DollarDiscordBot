# `!leave`

The `!leave` command allows **Dollar** to **leave the voice channel** that it is currently connected to. This command is typically used when you no longer want the bot to stay in the voice channel after the music playback has finished or if you want to disconnect the bot for any other reason.

## Purpose
- The main purpose of the `!leave` command is to disconnect **Dollar** from the voice channel it is currently in.
- After executing the command, the bot will leave the voice channel, and no further music will be played unless it is called back into the channel with the `!join` command.

## How It Works
When you issue the `!leave` command, **Dollar** checks if it is currently connected to a voice channel. If it is, the bot will leave that channel. If **Dollar** is not in a voice channel, the bot will not take any action.

### Usage

```
!leave
```

If **Dollar** is currently in a voice channel named **"Music"**, typing `!leave` will cause the bot to disconnect from the **"Music"** channel and stop any ongoing playback.

## Important Notes

- The `!leave` command does not stop the current song from playing; it simply disconnects the bot from the voice channel. The song will continue playing until it finishes, but no new songs will be played.
- **Dollar** will only leave the channel if it is currently connected. If the bot is not in a voice channel, calling `!leave` will not produce any effect.
- After **Dollar** leaves the channel, it will not automatically join a new channel until the `!join` command is used again.

The `!leave` command is essential for managing **Dollar**’s presence in voice channels, allowing you to disconnect the bot when it is no longer needed, freeing up server resources and improving server management.
