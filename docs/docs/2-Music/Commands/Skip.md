# `!skip`

The `!skip` command allows users to **skip the current song** that is playing and move on to the next song in the queue. It is useful for users who no longer want to listen to the current track and want to jump directly to the next one.

## Purpose
- The `!skip` command is designed to **immediately skip** the current song and start playing the next song in the queue.
- This command is useful for users who want to skip a song they don't enjoy or want to move on to the next track quickly.

## How It Works
When you issue the `!skip` command, **Dollar** stops the current song and starts playing the next song in the queue. If there are no songs left in the queue, **Dollar** will notify you that there is no song to skip to.

- **Dollar** stops the current song that is playing.
- The bot checks the queue for any upcoming songs.
- If there is a song in the queue, **Dollar** starts playing the next song.
- If there are no songs in the queue, the bot will inform the user that there are no more songs to skip to.

### Usage

```bash
!skip
```


In this example, the user issues the `!skip` command to skip the current song and move on to the next song in the queue.

### Important Notes

- The `!skip` command is only available to users who are in the same voice channel as the bot.
- If there are no songs in the queue, the bot will inform the user that there are no more songs to skip to.
- The `!skip` command is useful for users who want to skip a song they don't enjoy or want to move on to the next track quickly.
