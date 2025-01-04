# `Poke User`

The **Poke User** context menu command allows users to send a quick notification to another user, inviting them to join their current voice channel. This feature is ideal for bringing friends or teammates into a conversation or gaming session without needing to type out an invite message manually.

## Purpose

- Quickly notify a user to join your voice channel.
- Automatically generates a one-time invite link for the channel to make joining easy.

## How It Works

When you use the **Poke User** command:
1. **Dollar** checks if you are in a voice channel.
2. If you are in a voice channel:
   - The bot sends an ephemeral confirmation message to you.
   - It generates a one-time invite link for your voice channel.
   - The target user receives a direct message with your request and the invite link.
3. If you are not in a voice channel:
   - The bot sends an ephemeral message informing you that you need to join a voice channel first.

## Usage

1. **Right-Click on a User**: Find the user you want to poke.
2. **Navigate to Apps > Poke User**: Access the context menu command.
3. **Result**: The target user receives a direct message with an invite to your voice channel.

### Example

- **Scenario**: User "Alex" is in a voice channel and wants to invite "Jordan."
- **Action**: Alex right-clicks on Jordan's name, selects **Apps > Poke User**.
- **Outcome**:
  - Alex sees a confirmation: *"Poking Jordan to join your voice channel!"*
  - Jordan receives a DM: *"Yo, Alex wants you to join their voice channel in MyServer! [Invite Link]"*

## Important Notes

- The command can only be used if you are currently in a voice channel.
- The invite link is a **one-time use** and expires after it is used.
- Users who are poked receive a clear, friendly message that includes the server name and channel invite.

The **Poke User** command is a convenient way to connect with others in your server, ensuring seamless collaboration and communication in voice channels.
