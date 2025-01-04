# Message Moderation

The **Message Moderation** feature helps ensure that users interact with **Dollar** in the correct channels and prevents misuse by enforcing channel-specific command usage. It also handles Direct Messages (DMs) to the bot and checks for unauthorized or misplaced commands.

## Purpose

- The **Message Moderation** feature makes sure that all bot commands are issued in the correct text channels.
- It prevents bot commands from being used outside of designated command channels, keeping the server organized.
- It also manages messages in Direct Messages (DMs) to Dollar, ensuring users are aware of how to use the bot.
- It provides notifications for game updates in specific channels to keep the community informed.

## How It Works

1. **Direct Messages (DMs)**: If a user sends a DM to **Dollar**, the bot responds with a welcome message and a link to the README, ensuring that users know how to interact with the bot.

2. **Game Update Notifications**: If a game update is posted in the designated **#patches** channel, **Dollar** will automatically detect the update and send notifications to users subscribed to game updates.

3. **Bot Commands in Correct Channels**:
   - **Dollar** checks whether the message is sent in the appropriate command channels (e.g., `#commands`, `dollar-dev`).
   - If a bot command is used in one of these channels, the bot processes the command as usual.
   
4. **Command Misuse**:
   - If a user enters a bot command in an incorrect channel (not the designated command channels), **Dollar** will delete the message and send the user a reminder to use the correct channel.
   - The bot will notify the user through DM about the mistake and request they use the correct channel for commands.
   
5. **Clear Command**: The `!clear` command is also processed even if it is used in an incorrect channel, but a warning is logged for the admin's reference.

### Usage

- **Dollar** monitors all incoming messages and determines whether they are bot commands or general chat.
- If a bot command is used, it is processed only if the message is sent in the correct channel. If it's misused, the message will be deleted, and the user will be warned via DM.

### Important Notes

- Direct Messages to **Dollar** are always responded to with a link to the README, providing users with necessary information about how to interact with the bot.
- **Dollar** checks each command's context to ensure it is being used in the appropriate channels, preventing clutter in non-command channels.
- Misplaced commands are deleted, and users are gently reminded to follow the rules of the server.

The **Message Moderation** feature helps maintain an organized environment where bot commands are used correctly, ensuring a smooth and streamlined experience for users and administrators alike.
