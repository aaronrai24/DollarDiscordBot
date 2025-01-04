# `!remove`

The `!remove` command allows users to **remove a song** from the **music queue**. It provides users the ability to manage the queue by removing unwanted or incorrectly added songs.

## Purpose
- The `!remove` command is designed to allow users to **remove a specific song** from the queue based on its position.
- This command is useful for users who want to adjust the music queue, either by removing a song that was added by mistake or by removing a song they no longer want to hear.

## How It Works
When you issue the `!remove` command followed by an **integer value** (representing the position of the song in the queue), **Dollar** will identify the song at that position and remove it from the queue. The bot will send a message confirming the removal.

- **Dollar** checks the queue for the song at the specified position.
- The bot removes the song from the queue.
- The bot notifies the user that the song has been removed.

### Usage

```bash
!remove <position>
```

- Replace `<position>` with the **integer value** representing the position of the song you want to remove.

### Example

```bash
!remove 3
```

In this example, the bot will remove the song at position 3 in the queue.

## Additional Notes

- The `!remove` command is a useful tool for managing the music queue.
- Users can remove songs from the queue based on their position in the list.
- This command helps users maintain control over the songs that are played by the bot.
