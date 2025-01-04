# Inactivity Timeout

The **Inactivity Timeout** feature ensures that **Dollar** will automatically leave a voice channel if it detects that no music is being played for a period of time. This is managed through **Lavalink** and its configuration settings.

## Purpose
- The **Inactivity Timeout** feature prevents **Dollar** from staying in voice channels unnecessarily when there is no active music playing.
- It helps manage resources and ensures that the bot does not remain connected to voice channels when no users are interacting with it.
- This is especially useful in large servers where voice channels may be frequently used for various activities, and you don’t want idle bots taking up space.

## How It Works
- **Dollar** connects to the Lavalink server with a specified **inactive_player_timeout** parameter, which determines how long the bot will wait before leaving a voice channel due to inactivity.
- The `inactive_player_timeout` is set to **600 seconds** (10 minutes), meaning that if no music has been played for 10 minutes, **Dollar** will automatically leave the voice channel.
- This is configured in the Lavalink node setup where the bot is instructed to disconnect after 10 minutes of inactivity.

### Configuration
- The Lavalink connection is set up as follows:

```python
nodes = [lib.wavelink.Node(uri="http://lavalink:2333", password=LAVALINK_TOKEN, identifier="MAIN", 
							retries=None, heartbeat=60, inactive_player_timeout=600)]
```

- The `inactive_player_timeout` parameter is set to **600 seconds** (10 minutes) in the Lavalink node configuration.

### Important Notes

- The **Inactivity Timeout** feature is essential for managing resources and ensuring that **Dollar** does not remain connected to voice channels when not in use.
- This feature helps maintain a clean and efficient server environment by automatically disconnecting the bot after a period of inactivity.
