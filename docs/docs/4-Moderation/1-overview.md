# Overview of Key Features

## Auto Channel Creation

The **Auto Channel Creation** feature allows **Dollar** to dynamically create temporary personal voice channels for users. When a user joins a designated "trigger channel," **Dollar** creates a private voice channel for the user within the same category, granting them full control over the channel's permissions. Once the user leaves the created channel and it becomes empty, the bot automatically deletes the channel to keep the server tidy.

### Highlights

- Trigger channels are set via the [/dollarsettings](../3-Slash/2-Commands/DollarSettings.md) slash command.
- Temporary channels are automatically named after the user (e.g., "John's Channel").
- Users are granted management permissions for their channel.
- Unused channels are deleted when the user does not join or when they leave.

## Message Moderation

**Dollar** enforces message moderation by ensuring that bot commands are only issued in designated channels. This helps maintain a clear structure in the server, keeping bot-related interactions separate from general conversations.

### Highlights

- Moderation ensures bot commands are sent only in the specified commands channel (set using [/dollarsettings](../3-Slash/2-Commands/DollarSettings.md) or `#commands`).
- Commands sent in the wrong channel are deleted, and the user is notified privately.
- Supports direct messages (DMs) to the bot, providing helpful resources in response.
- Handles specialized notifications, such as game updates in predefined channels like `#patches`.

## Inactivity Timeout

The **Inactivity Timeout** feature prevents **Dollar** from remaining idle in voice channels for extended periods. If no music is being played for 10 minutes, the bot automatically disconnects from the voice channel, ensuring resources are not wasted.

### Highlights

- Configured with a 10-minute timeout using Lavalink's `inactive_player_timeout` setting.
- Ensures the bot disconnects when no music is playing or no activity is detected.
- Keeps server voice channels available for active use.

## Why These Features Matter

These features enhance the server experience by:
- Keeping the server organized and free of unused channels or idle bots.
- Ensuring efficient use of bot resources with automatic disconnection during inactivity.
- Providing a seamless and user-friendly experience with clear moderation rules and dynamic voice channel management.

Together, these features make **Dollar** an efficient and user-focused bot for managing voice and text interactions in your server.
