# `!lyrics`

The `!lyrics` command allows **Dollar** to fetch the **lyrics** for the currently playing song by searching on **Genius.com**. This command provides users with the ability to view the lyrics of a song directly within the Discord server while the song is playing, enhancing the listening experience.

## Purpose
- The `!lyrics` command is designed to retrieve and display the lyrics for the currently playing song.
- It uses **Genius.com**, a popular website for song lyrics, to search for the lyrics and display them in the chat.
- This command is useful for those who want to follow along with the lyrics while listening to a song.

## How It Works
When you issue the `!lyrics` command, **Dollar** will perform a search on **Genius.com** for the lyrics of the song that is currently playing in the voice channel. If the song is found on Genius, the bot will return the lyrics and display them in the chat.

- The bot extracts the song’s title and artist information.
- **Dollar** uses the Genius API to search for the lyrics associated with the song.
- Once the lyrics are found, the bot sends them to the Discord chat in a neatly formatted message.
- If the song’s lyrics are not found, the bot will inform the user that it couldn't retrieve the lyrics.

### Usage:

```bash
!lyrics
```

If the song currently playing is "Blinding Lights" by The Weeknd, typing `!lyrics` will result in **Dollar** sending the lyrics of "Blinding Lights" from Genius to the chat.

## Important Notes

- The `!lyrics` command only works when there is a song currently playing in the voice channel. If no song is playing, the bot will notify you that there are no lyrics available.
- **Dollar** relies on the Genius API to retrieve lyrics, so the quality and availability of lyrics depend on the data provided by Genius.com. Some songs might not have lyrics available.
- The command will display the lyrics in a formatted manner for easy reading. In cases where the lyrics are too long, **Dollar** may provide a preview and link to the full lyrics on Genius.com.

The `!lyrics` command enriches the music listening experience by providing an easy way to view song lyrics, allowing users to follow along with the song’s words in real-time.
