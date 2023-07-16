from ..common.libraries import(
    discord, commands, genius, wavelink, os, read_csv, random, asyncio, sp, artist
)
from ..common.generalFunctions import(
    setup_logger, is_connected_to_same_voice, is_connected_to_voice, CustomPlayer
)

logger = setup_logger('music')

class Music(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, player: CustomPlayer, track: wavelink.Track):
        global artist
        artist = track.author
        
    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: CustomPlayer, track: wavelink.Track, reason):
        if not player.queue.is_empty:
            await asyncio.sleep(.5)
            next_track = player.queue.get()
            await player.play(next_track)
            logger.info(f'Playing next track: {next_track}')
        else:
            logger.info('Queue is empty')

    # Join authors voice channel
    @commands.command(aliases=['Join'])
    @is_connected_to_voice()
    async def join(self, ctx):
        custom_player = CustomPlayer()
        vc: CustomPlayer = await ctx.author.voice.channel.connect(cls=custom_player)
        await vc.set_volume(5)  # Set bot volume initially to 5

    # Leave voice channel
    @commands.command(aliases=['Leave'])
    @is_connected_to_same_voice()
    async def leave(self, ctx):
        vc = ctx.voice_client
        if vc:
            await vc.disconnect()
            await ctx.channel.purge(limit=500)
        else:
            await ctx.send('The bot is not connected to a voice channel.')

    # Play a song, ex: !play starboy the weeknd
    @commands.command(aliases=['Play'])
    @is_connected_to_voice()
    async def play(self, ctx, *, search: wavelink.YouTubeMusicTrack):
        vc = ctx.voice_client
        if not vc:
            custom_player = CustomPlayer()
            vc: CustomPlayer = await ctx.author.voice.channel.connect(cls=custom_player)
            await vc.set_volume(5)

        if vc.is_playing():
            vc.queue.put(item=search)
            embed = discord.Embed(title=search.title, url=search.uri, description=f"Added {search.title} to the Queue!", colour=discord.Colour.random())
            embed.set_author(name=f"{search.author}")
            embed.set_thumbnail(url=f"{search.thumbnail}")
            if vc.queue.is_empty:
                embed.set_footer(text="Queue is empty")
            else:
                nextitem = vc.queue.get()
                vc.queue.put_at_front(item=nextitem)
                embed.set_footer(text=f"Next song is: {nextitem}")
            await ctx.send(embed=embed)
            logger.info(f'Queued from YouTube: {search.title}')
        else:
            embed = discord.Embed(title=search.title, url=search.uri, description=f"Now Playing {search.title}!", colour=discord.Colour.random())
            embed.set_author(name=f"{search.author}")
            embed.set_thumbnail(url=f"{search.thumbnail}")
            await ctx.send(embed=embed)
            await vc.play(search)
            logger.info(f'Playing from YouTube: {search.title}')

    # Play a song from SoundCloud, ex: !play Jackboy Seduction
    @commands.command(aliases=['Playsc', 'soundcloud', 'sc'])
    @is_connected_to_voice()
    async def playsc(self, ctx, *, search: wavelink.SoundCloudTrack):
        vc = ctx.voice_client
        if not vc:
            custom_player = CustomPlayer()
            vc: CustomPlayer = await ctx.author.voice.channel.connect(cls=custom_player)
            await vc.set_volume(5)  # initially set volume to 5

        if vc.is_playing():
            vc.queue.put(item=search)
            embed = discord.Embed(title=search.title, url=search.uri, description=f"Added {search.title} to the Queue!", colour=discord.Colour.random())
            embed.set_author(name=f"{search.author}")
            if vc.queue.is_empty:
                embed.set_footer(text="Queue is empty")
            else:
                nextitem = vc.queue.get()
                vc.queue.put_at_front(item=nextitem)
                embed.set_footer(text=f"Next song is: {nextitem}")
            await ctx.send(embed=embed)
            logger.info(f'Queued from SoundCloud: {search.title}')
        else:
            embed = discord.Embed(title=search.title, url=search.uri, description=f"Now Playing {search.title}!", colour=discord.Colour.random())
            embed.set_author(name=f"{search.author}")
            await ctx.send(embed=embed)
            await vc.play(search)
            logger.info(f'Playing from SoundCloud: {search.title}')

    # Skip current song and play next, ex !playskip blinding lights the weeknd
    @commands.command(aliases=['Playskip', 'PlaySkip'])
    @is_connected_to_same_voice()
    async def playskip(self, ctx, *, search: wavelink.YouTubeMusicTrack):
        vc = ctx.voice_client
        if vc:
            if vc.is_playing() and not vc.is_paused():
                vc.queue.put_at_front(item=search)
                await vc.seek(vc.track.length * 1000)
                await ctx.send("Playing the next song...")
                embed = discord.Embed(title=search.title, url=search.uri, description=f"Now Playing {search.title}!", colour=discord.Colour.random())
                embed.set_author(name=f"{search.author}")
                embed.set_thumbnail(url=f"{search.thumbnail}")
                await ctx.send(embed=embed)
                logger.info(f'Playskipping to: {search.title}')
            elif vc.is_paused():
                await ctx.send('The bot is currently paused, to playskip, first resume music with !resume')
            else:
                await ctx.send('The bot is not currently playing anything.')
        else:
            await ctx.send('The bot is not connected to a voice channel.')

    # Skip current song, ex: !skip
    @commands.command(aliases=['Skip'])
    @is_connected_to_same_voice()
    async def skip(self, ctx):
        vc = ctx.voice_client
        if vc:
            if not vc.is_playing():
                return await ctx.send('There are no songs currently playing')
            if vc.queue.is_empty:
                return await vc.stop()

            await vc.seek(vc.track.length * 1000)
            search = vc.queue.get()
            vc.queue.put_at_front(item=search)
            await ctx.send(f"Skipping to next song: {search}")
            logger.info('Skipping music')
            if vc.is_paused():
                await vc.resume()
        else:
            await ctx.send('The bot is not connected to a voice channel.')

    # Pause current song, ex: !pause
    @commands.command(aliases=['Pause'])
    @is_connected_to_same_voice()
    async def pause(self, ctx):
        vc = ctx.voice_client
        if vc:
            if vc.is_playing() and not vc.is_paused():
                await vc.pause()
                await ctx.send("Paused!")
                logger.info('Pausing music')
            else:
                await ctx.send("Nothing is currently playing")
        else:
            await ctx.send("The bot is not connect to a voice channel.")

    # Resume current song, ex: !resume
    @commands.command(aliases=['Resume'])
    @is_connected_to_same_voice()
    async def resume(self, ctx):
        vc = ctx.voice_client
        if vc:
            if vc.is_paused():
                await vc.resume()
                await ctx.send("Resuming!")
                logger.info('Resuming music')
            else:
                await ctx.send("Nothing is currently paused.")
        else:
            await ctx.send("The bot is not connected to a voice channel")

    # Show current playing song, ex: !nowplaying
    @commands.command(aliases=['Nowplaying', 'NowPlaying', 'np'])
    @is_connected_to_same_voice()
    async def nowplaying(self, ctx):
        vc = ctx.voice_client
        track = str(vc.track)

        if vc.is_playing():
            async with ctx.typing():
                while True:
                    try:
                        logger.info(f'Relaying current playing song: {track} by {artist}')
                        song = genius.search_song(track, artist)
                        break
                    except TimeoutError:
                        logger.warning('GET request timed out, retrying...')
                if song == None:
                    await ctx.send('Unable to find current playing song on Genius, please try again...')
                else:
                    embed = discord.Embed(title=song.title, url=song.url, description=f'Currently playing {song.full_title}', colour=discord.Colour.random())
                    embed.set_author(name=f"{song.artist}")
                    embed.set_thumbnail(url=f"{song.header_image_thumbnail_url}")
                    embed.set_footer()
                    logger.info('Current song information loaded from Genius API')
                    await ctx.send(embed=embed)
        else:
            await ctx.send('There are no songs currently play, you can queue one by using !play or !playsc')

    # Show whats next in the queue
    @commands.command(aliases=['Next', 'nextsong'])
    @is_connected_to_same_voice()
    async def next(self, ctx):
        vc = ctx.voice_client
        if vc:
            try:
                search = vc.queue.get()
                vc.queue.put_at_front(item=search)
                await ctx.send(f"The next song is: {search}")
                logger.info('Printing next song in queue')
            except:
                await ctx.send("The queue is empty, add a song by using !play or !playsc")
        else:
            await ctx.send("The bot is not connected to a voice channel")

    # Seeks to specifc second in song, ex: !seek 50(seeks to 50 seconds)
    @commands.command(aliases=['Seek'])
    @is_connected_to_same_voice()
    async def seek(self, ctx, seek=0):
        vc = ctx.voice_client
        val = int(seek)
        if vc:
            if vc.is_playing() and not vc.is_paused():
                await vc.seek(vc.track.length * val)
                await ctx.send(f"Seeking {val} seconds.")
                logger.info(f'Song seeked for {val} seconds')
            else:
                await ctx.send("Nothing is currently playing")
        else:
            await ctx.send("The bot is not connected to a voice channel.")

    # Set volume of bot, ex !volume 1(sets volume of bot to 1)
    @commands.command(aliases=['Volume'])
    @is_connected_to_same_voice()
    async def volume(self, ctx, volume):
        vc = ctx.voice_client
        val = int(volume)
        if vc and val > 0 and val <= 100:
            await vc.set_volume(val)
            await ctx.send(f"Volume set to: {val}")
            logger.info(f'Bot volume set to: {val}')
        else:
            await ctx.send("The bot is not connected to a voice channel.")

    # Prints all items in queue, ex !queue
    @commands.command(aliases=['Queue'])
    @is_connected_to_same_voice()
    async def queue(self, ctx):
        vc = ctx.voice_client
        desc = ""
        if vc.queue.is_empty is False:
            logger.info('Embedding Queue')
            test = vc.queue.copy()
            li = list(test)
            for i in range(len(li)):
                desc += (f"{i+1}. {li[i]}")
                desc += '\n\n'

            embed = discord.Embed(title='Whats Queued?', description=desc, colour=discord.Colour.random())
            file_path = os.path.join("images", "dollar2.png")
            img = discord.File(file_path, filename='dollar2.png')
            embed.set_thumbnail(url="attachment://dollar2.png")
            await ctx.send(embed=embed, file=img)
        else:
            logger.info('Queue is already empty')
            await ctx.send("The queue is currently empty, add a song by using !play or !playsc")

    # Clears queue, !empty
    @commands.command(aliases=['Empty', 'clearqueue', 'restart'])
    @is_connected_to_same_voice()
    async def empty(self, ctx):
        vc = ctx.voice_client
        if vc.queue.is_empty is False:
            vc.queue.clear()
            logger.info('Emptying queue')
            await ctx.send("All items from queue have been removed")
        else:
            logger.info('Queue is already empty')
            await ctx.send("The queue is currently empty, add a song by using !play or !playsc")

    # Load playlist from CSV, ex !load
    @commands.command(aliases=['Load'])
    @is_connected_to_same_voice()
    async def load(self, ctx):
        vc = ctx.voice_client
        count = 0

        fileexists = os.path.isfile('ex.csv')

        if fileexists:
            await ctx.send('Loading playlist!')
            logger.info('Loading Playlist')
            data = read_csv('ex.csv')
            os.remove('ex.csv')
            tracks = data['Track Name'].tolist()
            artists = data['Artist Name(s)'].tolist()
            song = list(zip(tracks, artists))

            while song:
                if count == 75:
                    break
                item = random.choice(song)
                song.remove(item)
                search = await wavelink.YouTubeMusicTrack.search(query=item[0] + " " + item[1], return_first=True)
                if vc.is_playing():
                    async with ctx.typing():
                        vc.queue.put(item=search)
                        logger.info(f'Added {search} to queue from playlist')
                elif vc.queue.is_empty:
                    await vc.play(search)
                    logger.info(f'Playing {search} from playlist')
                else:
                    logger.error('Error queuing/playing from playlist')
                count += 1

            await ctx.send('Finished loading playlist heres the queued songs')
            await Music.queue(self, ctx)
            logger.info(f'Finished loading {count} songs into queue from playlist')
        else:
            await ctx.send('Please upload an Exportify Playlist to this channel and then use !load')
            logger.warning('ex.csv does not exist!')

    @commands.command(aliases=['generatePlaylist', 'GeneratePlaylist', 'genplay', 'genPlay'])
    @is_connected_to_same_voice()
    async def generateplaylist(self, ctx, playlist_type=None, artist=None, album=None):
        vc = ctx.voice_client
        count = 0
        offset = random.randint(0, 1000)

        query = ''
        if playlist_type:
            query += f'genre:{playlist_type}'
        if artist:
            query += f' artist:{artist}'
        if album:
            query += f' album:{album}'

        if not query:
            await ctx.send('Please provide at least one parameter.')
            logger.warning('No filters entered, exiting method')
            return
        logger.info(f'Spotify Generating Playlist, Parameters: Genre: {playlist_type}, Artist: {artist}, Album: {album}')
        results = sp.search(q=query, type='track', limit=25, offset=offset)
        logger.info('Spotify Playlist Generation complete, querying songs...')

        tracks = []
        for track in results['tracks']['items']:
            tracks.append(f"{track['name']} {track['artists'][0]['name']}")

        if not tracks:
            await ctx.send('Those filters returned zero tracks, try again.')
            logger.warning(f'{query} returned zero results')
        else:
            while tracks:
                item = str(random.choice(tracks))
                tracks.remove(item)
                search = await wavelink.YouTubeMusicTrack.search(query=item, return_first=True)
                if vc.is_playing():
                    async with ctx.typing():
                        vc.queue.put(item=search)
                        logger.info(f'Added {search} to queue from Spotify generated playlist')
                elif vc.queue.is_empty:
                    await vc.play(search)
                    logger.info(f'Playing {search} from Spotify generated playlist')
                else:
                    logger.error('Error queuing/playing from Spotify generated playlist')
                count += 1

            await ctx.send('Finished loading the Spotify playlist. Here are the queued songs:')
            await Music.queue(self, ctx)
            logger.info(f'Finished loading {count} songs into the queue from the Spotify generated playlist')

    # Print lyrics of current playing song, pulls from Genius.com
    @commands.command(aliases=['Lyrics'])
    @is_connected_to_same_voice()
    async def lyrics(self, ctx):
        vc = ctx.voice_client
        track = str(vc.track)

        if vc.is_playing():
            async with ctx.typing():
                while True:
                    try:
                        logger.info(f'Searching lyrics for {track} by {artist}')
                        song = genius.search_song(track, artist)
                        break
                    except TimeoutError:
                        logger.warning('GET request timed out, retrying...')
                if song == None:
                    await ctx.send('Unable to find song lyrics, songs from playlists are less likely to return lyrics...')
                else:
                    if len(song.lyrics) > 4096:
                        return await ctx.send(f"Lyrics can be found here: <{song.url}>")
                    embed = discord.Embed(title=song.title, url=song.url,
                                        description=song.lyrics, colour=discord.Colour.random())
                    embed.set_author(name=f"{song.artist}")
                    embed.set_thumbnail(url=f"{song.header_image_thumbnail_url}")
                    embed.set_footer()
                    logger.info('Lyrics loaded from Genius API')
                    await ctx.send(embed=embed)
        else:
            await ctx.send('Nothing is currently playing, add a song by using !play or !playsc')

    @play.error
    async def play_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Bad Argument please create a /ticket.")
            logger.error(f"Bad argument {error}")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Missing required argument for this command.")
            logger.error('User did not provide a song when using !play')

async def setup(bot):
    await bot.add_cog(Music(bot))