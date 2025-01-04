# `!generateplaylist`

The `!generateplaylist` command allows **Dollar** to generate a playlist based on user-specified filters such as genre, artist, or album. This command utilizes **Spotify** to search for tracks that match the provided filters, leveraging the **Spotipy** library to interact with the Spotify API, and then adds those tracks to the music queue for playback.

## Purpose
- The `!generateplaylist` command gives users the ability to automatically generate a playlist based on specific criteria, like genre, artist, or album.
- It pulls relevant tracks from Spotify and adds them to the queue, allowing users to enjoy music tailored to their preferences.

## How It Works
When you issue the `!generateplaylist` command, **Dollar** will use the **Spotipy** library to interact with the Spotify API and search for tracks that match the provided filters (genre, artist, album). It then processes the results, retrieves playable tracks, and adds them to the music queue.

### Steps

1. **Query Formation**: 
   - The command constructs a query string based on the provided parameters (e.g., genre, artist, or album). If no parameters are provided, it sends a message asking for at least one filter.
   
2. **Spotify API Call**:
   - The query is used to search Spotify’s track database through the Spotipy library, retrieving up to 26 tracks matching the criteria.

3. **Track Search and Queueing**:
   - Once Spotify returns search results, the bot uses **Wavelink** to search for playable tracks on YouTube and adds them to the queue.

4. **Playback**:
   - If the bot is not currently playing music, it starts playing the first track from the generated playlist. The remaining tracks are added to the queue for playback after the first song finishes.

### Usage

To generate a playlist, use the following command format:

```bash
!generateplaylist [genre] [artist] [album]
```

- `genre`: Specify a genre (e.g., `rock`, `pop`, `jazz`).
- `artist`: Optionally, specify a particular artist.
- `album`: Optionally, specify a specific album by the artist.



This explanation details how **Dollar** generates a playlist using the **Spotipy** library to interface with Spotify, the track retrieval process, and how the playlist is added to the queue using **Wavelink**. It also includes an example of how to use the command and some code insights.
