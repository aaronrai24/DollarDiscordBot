# Music Commands Overview

Dollar uses advanced tools to provide a seamless music experience on your server. The bot leverages **Lavalink**, a high-performance audio streaming server for Discord bots, to serve music. Lavalink allows Dollar to play music reliably with low latency and minimal server load, even in large servers.

To interact with Lavalink, Dollar uses **Wavelink**, a Python wrapper around Lavalink that provides a simple and easy-to-use interface for controlling music playback.

## Lavalink: High-Performance Music Streaming

Lavalink is an audio streaming server designed specifically for Discord bots. It offloads the heavy lifting of audio playback from the bot to a separate server, ensuring smooth playback and less strain on your bot’s resources. By using Lavalink, Dollar can handle music in a way that scales well with high server usage and multiple concurrent users.

### Key Features of Lavalink:

- **Low latency streaming**: Lavalink streams music to Discord with minimal delay, ensuring a responsive listening experience.
- **High-quality audio**: It supports high-quality audio, including 320kbps streaming.
- **Scalable**: Lavalink is designed to handle large amounts of concurrent audio sessions, making it ideal for large Discord servers.

## Wavelink: Interfacing with Lavalink

**Wavelink** is a Python wrapper that simplifies interaction with Lavalink. It abstracts away the complexity of Lavalink's raw WebSocket API and provides a more Pythonic interface for controlling music playback. Wavelink is integral to how Dollar communicates with Lavalink, handling everything from song queue management to track retrieval.

### Key Features of Wavelink:

- **Track management**: Easily add, remove, and reorder tracks in the queue.
- **Playback control**: Simple methods to play, pause, skip, and resume music.
- **Player state management**: Retrieve and manage the state of the music player (e.g., current track, volume, etc.).
- **Integration with Lavalink**: Wavelink takes care of managing connections to Lavalink, making the bot’s music control effortless.

## Music Experience with Dollar

With Lavalink serving the music and Wavelink controlling the playback, Dollar offers a smooth and responsive music experience on your Discord server. Users can play songs, create playlists, shuffle the queue, and get real-time information like current track, next song, and lyrics—all through intuitive commands.

---

By using Lavalink for audio streaming and Wavelink for interacting with Lavalink, Dollar ensures high-quality, low-latency music playback for all users. This setup allows Dollar to efficiently handle music playback and scale across large servers with minimal resource usage.
