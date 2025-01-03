# `!play`

The `!play` command allows users to **play a song** from YouTube Music by providing the song's name or a URL. This command initiates playback of the requested song in the voice channel where **Dollar** is connected.

## Purpose
- The `!play` command is designed to **start playing a song** based on the user's input, either from a search query or a direct link.
- This command is useful for users who want to listen to a specific song by name or URL, making it a convenient way to add music to the queue and play it immediately.

## How It Works
When you issue the `!play` command with a song name or URL, **Dollar** searches YouTube Music for the track and plays it in the voice channel. If there is already a song playing, the new song will be added to the queue, and the current song will continue until it finishes.

- **Dollar** receives the song name or URL and searches for it on YouTube Music.
- If the song is found, it is added to the queue or played immediately if the queue is empty.
- If a song is already playing, the requested song is queued for the next available spot.

### Usage

```bash
!play <song_name_or_url>
```

- `song_name_or_url`: The name of the song or a YouTube Music URL that you want to play.

### Example

```bash
!play Never Gonna Give You Up
```

- This command will search for the song "Never Gonna Give You Up" on YouTube Music and play it in the voice channel.

## Important Notes

- If you provide a YouTube Music URL, **Dollar** will play the song directly from the URL.
- The `!play` command is a quick way to play a specific song without having to manually search for it on YouTube Music.
