# `User Information`

The **User Information** context menu command allows users to view detailed information about another member in the Discord server. It provides insights into the user's account, server activity, and roles in an easy-to-read embed format.

## Purpose

- Quickly retrieve key information about a server member.
- Useful for moderators or members looking to learn more about others in the community.

## How It Works

When you use the **User Information** command:
1. **Dollar** collects the following details about the selected user:
   - **Username and Preferred Name**: Their username and display name in the server.
   - **Account Creation Date**: When their Discord account was created.
   - **Server Join Date**: When they joined the current Discord server.
   - **Roles**: A list of all roles assigned to the user.
2. **Dollar** compiles this information into a visually appealing embed.
3. The bot sends the embed as a response to your command.

## Usage

1. **Right-Click on a User**: Locate the user whose information you want to view.
2. **Navigate to Apps > User Information**: Select the context menu command.
3. **Result**: Dollar sends an embed message with the user’s details.

### Example Output

If you request information for a user named "Jordan," the bot might generate the following embed:

#### Embed Content:

- **User**: Jordan#1234  
- **Preferred Name**: J-Dawg  
- **Created Their Account**: January 10, 2020, at 3:15 PM  
- **Joined This Discord**: June 5, 2021, at 2:30 PM  
- **Roles**: Admin, Moderator, Verified

The embed will also include:
- The user's avatar (if available).
- A footer showing who requested the information.

## Important Notes

- The command provides **read-only information**—no changes can be made to the user's account or roles using this feature.
- The information is retrieved from Discord's servers, ensuring accuracy and up-to-date details.
- Only roles visible to you or allowed by server permissions are shown.

The **User Information** command enhances community management by offering an efficient way to access member details, promoting transparency and collaboration within the server.
