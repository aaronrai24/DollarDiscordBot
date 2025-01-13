# `!seek`

The `!seek` command allows users to **fast forward or rewind** the currently playing song to a specific **time position**. It provides users with control over the playback, allowing them to jump to any point in the song.

## Purpose
- The `!seek` command is designed to allow users to **change the current position** in the song.
- This command is useful for skipping intros, revisiting favorite parts of a song, or moving past sections they don't want to listen to.

## How It Works
When you issue the `!seek` command followed by a time value (in seconds), **Dollar** adjusts the playback of the current song to the specified time position.

- **Dollar** receives a time value in seconds, which indicates the new position in the song.
- The bot then **jumps** to that specific point in the song and resumes playback from there.
- If the time value is outside the range of the song (i.e., longer than the song's duration), **Dollar** will notify you that the seek time is invalid.

### Usage

```bash
!seek <time_in_seconds>
```

- Replace `<time_in_seconds>` with the desired time position in seconds.

### Example

```bash
!seek 120
```

In this example, the bot will jump to the 2-minute mark (120 seconds) in the currently playing song.

## Important Notes

- The `!seek` command allows users to navigate to specific points in a song quickly.
- This command is useful for skipping intros, revisiting favorite parts, or moving past sections of a song.
- Make sure to provide the time value in seconds to accurately seek to the desired position.
- If the seek time is invalid (outside the song's duration), **Dollar** will inform you that the seek time is not valid.