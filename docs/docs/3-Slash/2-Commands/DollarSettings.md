# `/dollarsettings`

The `/dollarsettings` command allows server administrators to customize and manage specific bot settings for their Discord server. By using this command, administrators can configure Dollar's behavior in terms of channel management, auto-channel creation, and the selection of a voice channel for media playback (like a show or movie channel). 

## Purpose
- The `/dollarsettings` command is designed to give server owners full control over how Dollar behaves within their server, particularly around the management of channels related to bot activities.
- This command ensures that the bot integrates smoothly with the server's layout and preferences, allowing users to optimize their experience.

## How It Works
When the command is invoked, Dollar opens a **modal** (a pop-up window) where server owners can configure several important settings:
- **Preferred command channels (text)**: The server owner can specify which text channels the bot should listen to for commands.
- **Auto-channel creation (voice)**: If enabled, Dollar can automatically create voice channels as needed for various activities, like playing music or hosting events.
- **Show/movie voice channel**: The server owner can designate a voice channel specifically for activities like watching movies or shows, ensuring that Dollar operates within the intended space.

These options are only available to the server owner, ensuring that they maintain control over how Dollar functions within the server.

### Usage
To use the `/dollarsettings` command:

```bash
/dollarsettings
```

### Important Notes
- This command is only available to the server owner.
- The settings configured through this command will affect how Dollar interacts with the server and its members.
- It is recommended to review and adjust these settings periodically to ensure they align with the server's needs and preferences.


#### Known Issue
- If the voice/text channel is deleted/renamed, Dollar does not automatically update the settings. The server owner will need to reconfigure the settings accordingly. We are working on a solution to address this issue in future updates.
