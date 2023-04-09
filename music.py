# This music bot uses wavelink instead of FFMPEG
# Current commands:
# join, leave, play, skip, pause, resume, nowplaying, seek, volume, playskip, next, load, lyrics, stop, help
import discord
import os
import wavelink
import logging
import asyncio
import logging.handlers
import random
import pandas

from pandas import *
from discord.ext import commands
from discord.utils import get
from dotenv import load_dotenv
from lyricsgenius import Genius

# Global Variables
ADMIN = '⚡️'
DJ = '🎧'
MOD = '🌩️'
run = True
artist = ''
CREATEDCHANNELS = []

# Create Unfiltered Bot to accept commands from other bots
class UnfilteredBot(commands.Bot):
    async def process_commands(self, message):
        ctx = await self.get_context(message)
        await self.invoke(ctx)

client = UnfilteredBot(command_prefix='!', intents=discord.Intents.all())
client.remove_command('help')

# Create an instance of bot(for each bot instance to have its own queue)
class CustomPlayer(wavelink.Player):
    def __init__(self):
        super().__init__()
        self.queue = wavelink.Queue()

# load environment
load_dotenv()

# Setup Logging
logger = logging.getLogger('discord')
handler = logging.handlers.RotatingFileHandler(
    filename='discord.log',
    encoding='utf-8',
    maxBytes=1024*1024,  # 1mb
    backupCount=5,  # Rotate through 5 files
)
handler.setFormatter(logging.Formatter(
    '%(asctime)s [%(levelname)s] %(name)s: %(message)s'))
logger.addHandler(handler)
logging.getLogger('discord.gateway').setLevel(logging.WARNING)
logger.setLevel(logging.DEBUG)

# Get Discord and Genius token from ENV
DISCORD_TOKEN = os.getenv('TOKEN')
genius = Genius('GENIUSTOKEN')

@client.event
async def on_ready():
    client.loop.create_task(connect_nodes())
    for guild in client.guilds:
        logger.info(f'Dollar loaded in {guild.name}, owner: {guild.owner}')


async def connect_nodes():
    await client.wait_until_ready()
    await wavelink.NodePool.create_node(
        bot=client,
        host='10.0.0.210',
        port=2333,
        password='discordTest123'
    )

# Events, load wavelink node, play next song in queue
@client.event
async def on_wavelink_node_ready(node: wavelink.Node):
    logger.info(f'Node: <{node.identifier}> is ready')
    logger.info(f'Logged in as {node.bot.user} ({node.bot.user.id})')
    await client.change_presence(activity=discord.Game(name=' Music! | !help'))

@client.event
async def on_wavelink_track_start(player: CustomPlayer, track: wavelink.Track):
    global artist
    artist = track.author

@client.event
async def on_wavelink_track_end(player: CustomPlayer, track: wavelink.Track, reason):
    if not player.queue.is_empty:
        next_track = player.queue.get()
        await player.play(next_track)
        logger.info(f'Playing next track: {next_track}')
    else:
        logger.info('Queue is empty')

#Patch 1.1
# # Event was created
# @client.event
# async def on_scheduled_event_create(event):
#     await event.channel.set_permissions(event.guild.default_role, connect=False)
#     logger.info(f'The event [{event.name}] in was created in {event.guild}')

# # Event was cancelled
# @client.event
# async def on_scheduled_event_delete(event):
#     await event.channel.set_permissions(event.guild.default_role, connect=False)
#     logger.info(f'The event [{event.name}] in was cancelled in {event.guild}')

# # Add interested users to connect to event channel
# @client.event
# async def on_scheduled_event_user_add(event, user):
#     channel = event.channel
#     await channel.set_permissions(user, connect=True)
#     logger.info(f'{user} is intereseted in the event [{event.name}] in {event.guild}, allowing them to connect to {channel}')

# # If user loses interest in event, remove permissions to connect to channel
# @client.event
# async def on_scheduled_event_user_remove(event, user):
#     channel = event.channel
#     await channel.set_permissions(user, connect=False)
#     logger.info(f'{user} is now uninterested in the event [{event.name}] in {event.guild}, no longer allowing them to connect to {channel}')

# Scan messages to ensure message was sent in #commands chat
@client.event
async def on_message(message):
    msg = message.content
    channel = str(message.channel)
    author = message.author

    if isinstance(message.channel, discord.channel.DMChannel) and message.author != client.user:
        text = 'All of my commands are listed in the #commands chat in the mfDiscord, too add me to your discord or to get a list of commands, DM Cash#8915!'
        await message.channel.send(text)
        logger.info(f'{author} sent a DM to Dollar')

    if channel.startswith('commands') or channel.startswith('test'):
        if msg.startswith('!'):
            logger.info(
                f'Bot command entered. Command: {msg} | Author: {author}')
            await client.process_commands(message)
        elif str(message.attachments) == "[]":
            await client.process_commands(message)
            logger.info(
                f'User message entered. Message: {msg} | Author: {author}')
        else:
            if message.attachments and message.attachments[0].filename.endswith(".csv"):
                try:
                    await message.attachments[0].save(fp='ex.csv')
                    pandas.read_csv('ex.csv')
                    await message.channel.send('File downloaded. Use !load to load songs into queue.')
                    logger.info(
                        f'CSV successfully downloaded, author: {author}')
                except pandas.errors.ParserError:
                    logger.warning('File is not a valid CSV')
                    await message.channel.send('File is not a valid CSV.')
                except Exception as e:
                    logger.error(f'Error occurred while downloading file: {e}')
                    await message.channel.send(f'Error occurred while downloading file: {e}')
    elif msg.startswith('!clear'):
        await client.process_commands(message)
        logger.info(f"{author} used !clear")
    elif msg.startswith('!'):
        logger.info(f'Command entered in wrong channel, deleting: {msg}')
        await message.delete(delay=1)

# Scan when users join/leave/move voice channels
@client.event
async def on_voice_state_update(member, before, after):
    ctxbefore = before.channel
    ctxafter = after.channel
    guild = client.get_guild(member.guild.id)
    channel = discord.utils.get(guild.channels, name='JOIN HERE💎')
    comchannel = discord.utils.get(guild.channels, name='commands')
    if channel is not None:
        category = channel.category_id
    else:
        logger.debug(f'{guild} is not using auto-channel creation, JOIN HERE💎 channel does not exist')
    role = get(member.guild.roles, name=DJ)
    user = str(member).split("#")[0]

    if str(member) == 'Dollar#5869':
        dollar = member.id
    else:
        dollar = 0

    # Add/Remove DJ Role from users, if user joins JOIN HERE💎, create a voice channel and move them to that channel, remove created channel(s) when its empty
    if ctxbefore is None and ctxafter is not None:
        # Somebody joined a voice channel
        await member.add_roles(role)
        logger.info(f'{member} joined {ctxafter} adding Dj role')
        if str(ctxafter) == str(channel):
            await channel.set_permissions(guild.default_role, connect=False)
            logger.info(f'Locked {str(channel)}, beginning channel creation in {str(guild)}')
            category_channel = discord.utils.get(guild.categories, id=category)
            v_channel = await guild.create_voice_channel(f"{user}'s Channel", category=category_channel, position=2)
            CREATEDCHANNELS.append(v_channel.id)
            logger.info(f'Successfully created {v_channel} in {str(guild)}')
            await member.move_to(v_channel)
            await asyncio.sleep(5)
            await channel.set_permissions(guild.default_role, connect=True)
            logger.info(f'Unlocked {str(channel)}, channel creation finished in {str(guild)}')
    elif ctxbefore is not None and ctxafter is None:
        # Somebody left a voice channel
        await member.remove_roles(role)
        logger.info(f"{member} left {ctxbefore} removing Dj role")
        for id in CREATEDCHANNELS:
            if ctxbefore.id == id:
                v_channel = discord.utils.get(guild.channels, id=ctxbefore.id)
                if len(v_channel.members) == 0:
                    await v_channel.delete()
                    logger.info(f'{v_channel} empty, deleted channel in {str(guild)}')
                    CREATEDCHANNELS.remove(ctxbefore.id)
    elif str(ctxbefore) != str(ctxafter):
        # Somebody was already connected to a vc but moved to a different channel
        logger.info(f'{member} moved from {ctxbefore} to {ctxafter}')

        # Prioritize removing empty channels
        for id in CREATEDCHANNELS:
            if ctxbefore.id == id:
                v_channel = discord.utils.get(guild.channels, id=ctxbefore.id)
                if len(v_channel.members) == 0:
                    await v_channel.delete()
                    logger.info(f'{v_channel} empty, deleted channel in {str(guild)}')
                    CREATEDCHANNELS.remove(ctxbefore.id)

        # If they move to JOIN HERE💎 go through channel creation
        if str(ctxafter) == str(channel):
            await channel.set_permissions(guild.default_role, connect=False)
            logger.info(f'Locked {str(channel)}, beginning channel creation in {str(guild)}')
            category_channel = discord.utils.get(guild.categories, id=category)
            v_channel = await guild.create_voice_channel(f"{user}'s Channel", category=category_channel, position=2)
            CREATEDCHANNELS.append(v_channel.id)
            logger.info(f'Successfully created {v_channel} in {str(guild)}')
            await member.move_to(v_channel)
            await asyncio.sleep(5)
            await channel.set_permissions(guild.default_role, connect=True)
            logger.info(f'Unlocked {str(channel)}, channel creation finished in {str(guild)}')

    # Inactivity Checker, if Dollar idle for 10 minutes disconnect
    if member.id != dollar:
        return

    elif ctxbefore is None:
        vc = after.channel.guild.voice_client
        time = 0
        while True:
            await asyncio.sleep(1)
            time = time + 1
            if time % 30 == 0:
                logger.info(f'Dollar has been idle for {time} seconds in {str(guild)}')
            if vc.is_playing() and not vc.is_paused():
                time = 0
            if time == 600:
                logger.info(f'10 minutes reached, Dollar disconnecting from {str(guild)}')
                await vc.disconnect()
                await comchannel.purge(limit=10000)
                logger.info('Finished clearing #commands channel')
            if not vc.is_connected():
                break

# Join authors voice channel
@client.command(aliases=['Join'])
@commands.has_role(DJ or ADMIN)
async def join(ctx):
    vc = ctx.voice_client
    try:
        channel = ctx.author.voice.channel
    except AttributeError:
        return await ctx.send('You must be in a voice channel for the bot to connect.')
    if not vc:
        custom_player = CustomPlayer()
        vc: CustomPlayer = await ctx.author.voice.channel.connect(cls=custom_player)
        await vc.set_volume(5)  # Set bot volume initially to 5
    else:
        await ctx.send('The bot is already connected to a voice channel')

# Leave voice channel
@client.command(aliases=['Leave'])
@commands.has_role(DJ)
async def leave(ctx):
    vc = ctx.voice_client
    if vc:
        await vc.disconnect()
        await ctx.channel.purge(limit=10000)
    else:
        await ctx.send('The bot is not connected to a voice channel.')

# Play a song, ex: !play starboy the weeknd
@client.command(aliases=['Play'])
@commands.has_role(DJ)
async def play(ctx, *, search: wavelink.YouTubeMusicTrack):
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
@client.command(aliases=['Playsc', 'soundcloud', 'sc'])
@commands.has_role(DJ)
async def playsc(ctx, *, search: wavelink.SoundCloudTrack):
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
@client.command(aliases=['Playskip', 'PlaySkip'])
@commands.has_role(DJ)
async def playskip(ctx, *, search: wavelink.YouTubeMusicTrack):
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
@client.command(aliases=['Skip'])
@commands.has_role(DJ)
async def skip(ctx):
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
@client.command(aliases=['Pause'])
@commands.has_role(DJ)
async def pause(ctx):
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
@client.command(aliases=['Resume'])
@commands.has_role(DJ)
async def resume(ctx):
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
@client.command(aliases=['Nowplaying', 'NowPlaying', 'np'])
@commands.has_role(DJ)
async def nowplaying(ctx):
    vc = ctx.voice_client
    if vc:
        try:
            track = str(vc.track)
            await ctx.send(f'Currently playing: {track}')
            logger.info(f'Current playing track: {track}')
        except:
            await ctx.send('Nothing is currently playing, add a song by using !play or !playsc')
    else:
        await ctx.send("The bot is not connected to a voice channel")

# Show whats next in the queue
@client.command(aliases=['Next', 'nextsong'])
@commands.has_role(DJ)
async def next(ctx):
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
@client.command(aliases=['Seek'])
@commands.has_role(DJ)
async def seek(ctx, seek=0):
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
@client.command(aliases=['Volume'])
@commands.has_role(DJ)
async def volume(ctx, volume):
    vc = ctx.voice_client
    val = int(volume)
    if vc and val > 0 and val <= 100:
        await vc.set_volume(val)
        await ctx.send(f"Volume set to: {val}")
        logger.info(f'Bot volume set to: {val}')
    else:
        await ctx.send("The bot is not connected to a voice channel.")

# Prints all items in queue, ex !queue
@client.command(aliases=['Queue'])
@commands.has_role(DJ)
async def queue(ctx):
    vc = ctx.voice_client
    desc = ""
    if vc.queue.is_empty is False:
        logger.info('Embedding Queue')
        test = vc.queue.copy()
        li = list(test)
        for i in range(len(li)):
            desc += (f"{i+1}. {li[i]}")
            desc += '\n\n'

        img = discord.File("dollar2.png", filename="output.png")
        embed = discord.Embed(title='Whats Queued?', description=desc, colour=discord.Colour.random())
        embed.set_thumbnail(url="attachment://output.png")
        await ctx.send(embed=embed, file=img)
    else:
        logger.info('Queue is already empty')
        await ctx.send("The queue is currently empty, add a song by using !play or !playsc")

# Clears queue, !empty
@client.command(aliases=['Empty', 'clearqueue', 'restart'])
@commands.has_role(DJ)
async def empty(ctx):
    vc = ctx.voice_client
    if vc.queue.is_empty is False:
        vc.queue.clear()
        logger.info('Emptying queue')
        await ctx.send("All items from queue have been removed")
    else:
        logger.info('Queue is already empty')
        await ctx.send("The queue is currently empty, add a song by using !play or !playsc")

# Clear Messages from channel, ex !clear 50
@client.command(aliases=['purge', 'delete'])
@commands.has_role(ADMIN or MOD)
async def clear(ctx, amount=None):
    if (amount is None):
        await ctx.send("You must enter a number after the !clear")
    else:
        val = int(amount)
        if (val <= 0):
            await ctx.send("You must enter a number greater than 0")
        else:
            await ctx.channel.purge(limit=val)
            logger.info(f'Removed {val} messages')

# Load playlist from CSV, ex !load
@client.command(aliases=['Load'])
@commands.has_role(DJ)
async def load(ctx):
    vc = ctx.voice_client
    global run
    run = True
    count = 0

    if not vc:
        custom_player = CustomPlayer()
        vc: CustomPlayer = await ctx.author.voice.channel.connect(cls=custom_player)
        await vc.set_volume(5)

    await ctx.send('Loading playlist!')
    logger.info('Loading Playlist')

    data = read_csv("ex.csv")
    tracks = data['Track Name'].tolist()
    artists = data['Artist Name(s)'].tolist()
    song = list(zip(tracks, artists))

    while song:
        if not run:
            break
        if count == 75:
            break
        item = random.choice(song)
        song.remove(item)
        search = await wavelink.YouTubeTrack.search(query=item[0] + " " + item[1], return_first=True)
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
    await queue(ctx)
    logger.info(f'Finished loading {count} songs into queue from playlist')

# Print lyrics of current playing song, pulls from Genius.com
@client.command(aliases=['Lyrics'])
@commands.has_role(DJ)
async def lyrics(ctx):
    vc = ctx.voice_client
    track = str(vc.track)

    if vc.is_playing():
        async with ctx.typing():
            while True:
                try:
                    logger.info(f'Searching lyrics for {track} by {artist}')
                    song = genius.search_song(track, artist)
                    logger.info('Lyrics loaded from Genius API')
                    break
                except TimeoutError:
                    logger.error('GET request timed out, retrying...')
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
                await ctx.send(embed=embed)
    else:
        await ctx.send('Nothing is currently playing, add a song by using !play or !playsc')

# Make a post of dollars latest features(ADMIN only)
@client.command()
@commands.has_role(ADMIN)
async def patch(ctx):
    desc = '''THIS WILL BE THE FINAL UPDATE TIL 1.1
    \n- 1.1 development has begun and will release most likely sometime in May, there will be no more small updates for a while as 1.0.9 should be dollar's most stable state(knock on wood)
    \nInternal Fixes to Dollar:
    \n- Fixed major bug with auto channel creation feature:
    \n- Dollar now prioritizes removing empty voice channels when users move to 'JOIN HERE💎', if there are no empty voice channels dollar creates a new voice channel for the users
    \n- Improvements to playlist loading:
    \n- No more message spam with songs being queued in the commands text chat, dollar will now log that your playlist is being loaded, when it finishes and then embed the queued songs
    \n- This improves dollars processing of commands and reduces overhead with querying the REST API and embedding results of that query at the same time
    \n- Fixed wavelink_track_end bug that would not allow queued songs to play after the current playing ended, aftermath of 1.0.8 :(
    '''

    img = discord.File("dollar.png", filename="output.png")

    channel = client.get_channel(1043712431265955910)  # patches channel
    embed = discord.Embed(title='Patch: 1.0.9', url='https://en.wikipedia.org/wiki/Dollar', description=desc, colour=0x2ecc71)
    embed.set_author(name='Dollar')
    embed.set_thumbnail(url="attachment://output.png")
    embed.set_footer(text='Please send feature requests/bugs to Cash#8915')
    await channel.send(embed=embed, file=img)


@client.command()
async def help(ctx):
    desc = '''  !join  - Bot joins voice channel you are currently in 
                \n!leave  - Bot leaves voice channel
                \n!play (Song)  - Plays desired song from YouTube Music
                \n!playsc (Song) - Plays desired song from SoundCloud
                \n!skip  - Skips current song
                \n!pause  - Pauses currently playing song
                \n!resume  - Resumes last played song 
                \n!seek (int value)  - Fast forward or backtrack current play song volume
                \n!playskip (Song)  - Skips current playing song and plays song you chose from YouTube Music
                \n!nowplaying - Shows current playing song
                \n!next  - Shows next song in queue
                \n!queue - Prints out all items in queue
                \n!empty - Clears Dollars queue
                \n!load - Loads last saved playlist for Dollar to play
                \n!lyrics - Loads lyrics from Genius.com for current playing song
                \n\nWanna play your own playlist(75 song limit)? Export your Spotify playlist at https://exportify.net/ and then upload it to this channel'''

    img = discord.File("dollar3.png", filename="output.png")

    embed = discord.Embed(title='Current Commands',
                          description=desc, colour=0x2ecc71)
    embed.set_author(name='Dollar')
    embed.set_thumbnail(url="attachment://output.png")
    embed.set_footer(text='Please send feature requests/bugs to Cash#8915')
    await ctx.send(embed=embed, file=img)

# Stop loading playlist or printing queue
@client.command()
@commands.has_role(ADMIN or MOD)
async def stop(ctx):
    global run
    run = False
    logger.info('Playlist/Queue loading interrupted')
    await ctx.send('Interrupting!')

# Error Handling if unable to find song, or user isn't in a voice channel
async def play_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("Unable to find track :(")
        logger.error("Unable to find track")
    else:
        await ctx.send("Please join a voice channel")
        logger.error("User not in voice channel, bot unable to join")

# Run bot
client.run(DISCORD_TOKEN)