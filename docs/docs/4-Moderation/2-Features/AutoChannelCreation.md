# Auto Channel Creation

The **Auto Channel Creation** feature allows Dollar to automatically create personalized voice channels for users when they join a designated trigger channel. This helps maintain an organized and dynamic voice channel environment by giving users their own space while in a voice chat.

## Purpose

- The **Auto Channel Creation** feature ensures that every user who joins a specific trigger voice channel gets their own personal voice channel automatically created.
- The feature is especially useful for servers where users need individual channels for temporary conversations, such as for gaming or study groups.
- It ensures that users have their own space without the need for manual intervention, and it deletes empty channels to keep the server clean.

## How It Works

The process is triggered when a member joins a **trigger channel**. The trigger channel is set through the `/dollarsettings` command, where server owners can specify which voice channel will act as the trigger for creating personal channels.

1. **Trigger Channel**: When a user joins the designated **trigger channel**, Dollar automatically creates a new voice channel for that user.
   - The new channel is named after the user, such as `User's Channel`.
   - The user is granted special permissions to manage the channel.
   
2. **Channel Lock**: During the creation of the personal channel, Dollar locks the trigger channel to prevent unwanted interference while setting permissions.
   
3. **Channel Deletion**: If the user does not join the newly created personal channel, the channel is deleted after a short period to avoid orphaned channels.
   
4. **Empty Channel Cleanup**: If a personal channel is created and later becomes empty (when the user leaves), Dollar will automatically delete the empty channel.

### Usage

Once configured, the Auto Channel Creation feature works automatically when a user joins the designated trigger voice channel. The user will receive a personal voice channel named after them.

### Configuration

- The **trigger channel** for this feature is set by the server owner using the `/dollarsettings` command.
  - The owner can specify which voice channel will trigger the creation of personal channels for users joining that channel.

### Important Notes

- Only the server owner can configure the trigger channel through the `/dollarsettings` command.
- Personal channels are deleted if the user does not join them after a short delay to avoid clutter.
- This feature helps keep the server organized by automatically managing the creation and deletion of channels based on user activity.

The **Auto Channel Creation** feature ensures that users have their own personalized space in voice channels while keeping the server clean and organized by deleting unused channels.
