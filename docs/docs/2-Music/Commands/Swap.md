# `!swap`

The `!swap` command allows users to **swap the positions** of two songs in the music queue. This command is useful for users who want to change the order of the songs in the queue, allowing them to reorder songs without removing or adding new ones.

## Purpose
- The `!swap` command is designed to **swap the positions** of two songs in the current music queue.
- This command is helpful for users who want to rearrange the order of songs in the queue, such as moving a song higher up or lower down without affecting the rest of the queue.

## How It Works
When you issue the `!swap` command, **Dollar** swaps the positions of two specified songs in the queue. The bot identifies the songs by their positions in the queue (using their index), and then changes their order based on the user's input.

- **Dollar** takes the two song positions provided by the user.
- The bot swaps their positions in the queue.
- The queue is updated with the new song order, and the playback continues as normal.

### Usage

```bash
!swap (int value) (int value)
```

- `(int value)`: The position of the first song in the queue that you want to swap.
- `(int value)`: The position of the second song in the queue that you want to swap.

### Example

```bash
!swap 2 5
```

- This command will swap the songs at positions 2 and 5 in the queue.
- The song at position 2 will move to position 5, and the song at position 5 will move to position 2.
- The rest of the queue remains unchanged.

## Important Notes

- The `!swap` command is useful for users who want to rearrange the order of songs in the queue without adding or removing songs.
- This command can be used to customize the playback order based on the user's preferences.
- The `!swap` command is a convenient way to manage the queue and create a personalized listening experience.
- If you want to change the order of songs in the queue, the `!swap` command is a quick and easy
    way to do so without disrupting the playback flow.
