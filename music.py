#This music bot uses wavelink instead of FFMPEG
#Current commands:
#join, leave, play, skip, pause, resume, seek, volume, playskip, next
import discord
import os
import wavelink
import logging
import asyncio

from discord.ext import commands
from discord.utils import get
from dotenv import load_dotenv

# Role Constants
ADMIN = "⚡️"
DJ = "🎧"

#Create Unfiltered Bot to accept commands from other bots
class UnfilteredBot(commands.Bot):
    async def process_commands(self, message):
        ctx = await self.get_context(message)
        await self.invoke(ctx)

client = UnfilteredBot(command_prefix="!", intents=discord.Intents.all())

#Create an instance of bot(for each bot instance to have its own queue)
class CustomPlayer(wavelink.Player):
    def __init__(self):
        super().__init__()
        self.queue = wavelink.Queue()

#load environment
load_dotenv()

#Setup Logging
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

#Get Discord token
DISCORD_TOKEN = os.getenv("TOKEN")

#Wavelink setup
@client.event
async def on_ready():
    client.loop.create_task(connect_nodes())

async def connect_nodes():
    await client.wait_until_ready()
    await wavelink.NodePool.create_node(
        bot=client,
        host='127.0.0.1',#Update to IP
        port=2333,
        password='discordTest123'
    )

#Events, load wavelink node, play next song in queue
@client.event
async def on_wavelink_node_ready(node: wavelink.Node):
    logger.info(f'Node: <{node.identifier}> is ready')
    logger.info(f'Logged in as {node.bot.user} ({node.bot.user.id})')
    #await client.change_presence(activity=discord.Game(name="DM me to see my commands"))

@client.event
async def on_wavelink_track_start(player: CustomPlayer, track: wavelink.Track):
    next_track = player.source
    #await client.change_presence(activity=discord.Game(name=f"{next_track}"))
    
@client.event
async def on_wavelink_track_end(player: CustomPlayer, track: wavelink.Track, reason):
    if not player.queue.is_empty:
        next_track = player.queue.get()
        await player.play(next_track)
        logger.info(f'Playing next track: {next_track}')
    else:
        logger.info(f'Queue is empty')
        #await client.change_presence(activity=discord.Game(name="DM me to see my commands"))

#Scan messages to ensure message was sent in #commands chat
@client.event
async def on_message(message):
    msg = message.content
    channel = str(message.channel)
    author = message.author
    
    if isinstance(message.channel, discord.channel.DMChannel) and message.author != client.user:
        text = 'Current commands:\n\n!join  - Bot joins voice channel you are currently in \n!leave  - Bot leaves voice channel\n!play (Song)  - Plays desired song from YouTube Music\n!playsc (Song) - Plays desired song from SoundCloud\n!skip  - Skips current song\n!pause  - Pauses currently playing song\n!resume  - Resumes last played song \n!seek (int value)  - Fast forward or backtrack current play song volume\n!playskip (Song)  - Skips current playing song and plays song you chose from YouTube Music\n!next  - Shows next song in queue\n!queue - Prints out all items in queue'
        await message.channel.send(text)
        logger.info(f'{author} sent a DM to Dollar')
    
    if channel == 'commands' or channel == 'test':
        if msg.startswith('!'):
            logger.info(f'Bot command entered; command: {msg}, author: {author}')
            await client.process_commands(message)
        else:
            logger.info(f'User message entered; message: {msg}, author: {author}')
    elif msg.startswith('!'):
        logger.info(f'Command entered in wrong channel, deleting: {msg}')
        await message.delete(delay = 1)

#When user joins a voice channel assign DJ role, and remove when they leave
#This prevents users not in a voice channel from making commands
@client.event
async def on_voice_state_update(member, before, after):
    ctxbefore = before.channel
    ctxafter = after.channel
    role = get(member.guild.roles, name="🎧")
    if ctxbefore is None and ctxafter is not None:
        await member.add_roles(role)
        logger.info(f"{member} joined {ctxafter} adding Dj role")
    elif ctxbefore is not None and ctxafter is None:
        await member.remove_roles(role)
        logger.info(f"{member} left {ctxbefore} removing Dj role")

#Join authors voice channel
@client.command()
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
        await vc.set_volume(5)#Set bot volume initially to 5
    else:
        await ctx.send('The bot is already connected to a voice channel')

#Leave voice channel
@client.command()
@commands.has_role(DJ)
async def leave(ctx):
    vc = ctx.voice_client
    if vc:
        await vc.disconnect()
        await ctx.channel.purge(limit=10000)
    else:
        await ctx.send('The bot is not connected to a voice channel.')

#Play a song, ex: !play starboy the weeknd
@client.command()
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
    else:
        embed = discord.Embed(title=search.title, url=search.uri, description=f"Now Playing {search.title}!", colour=discord.Colour.random())
        embed.set_author(name=f"{search.author}")
        embed.set_thumbnail(url=f"{search.thumbnail}")
        await ctx.send(embed=embed)
        await vc.play(search)
        logger.info(f'Playing from YouTube: {search.title}')

#Play a song from SoundCloud, ex: !play Jackboy Seduction
@client.command(aliases=['soundcloud', 'sc'])
@commands.has_role(DJ)
async def playsc(ctx, *, search: wavelink.SoundCloudTrack):
    vc = ctx.voice_client
    if not vc:
        custom_player = CustomPlayer()
        vc: CustomPlayer = await ctx.author.voice.channel.connect(cls=custom_player)
        await vc.set_volume(5)#initially set volume to 5

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
    else:
        embed = discord.Embed(title=search.title, url=search.uri, description=f"Now Playing {search.title}!", colour=discord.Colour.random())
        embed.set_author(name=f"{search.author}") 
        await ctx.send(embed=embed)
        await vc.play(search)
        logger.info(f'Playing from SoundCloud: {search.title}')

#Skip current song and play next, ex !playskip blinding lights the weeknd
@client.command()
@commands.has_role(DJ)
async def playskip(ctx, *, search: wavelink.YouTubeMusicTrack):
    vc = ctx.voice_client
    if vc:
        if vc.is_playing() and not vc.is_paused():
            vc.queue.put_at_front(item = search)
            await vc.seek(vc.track.length * 1000)
            await ctx.send("Playing the next song...")
            embed = discord.Embed(title=search.title, url=search.uri, description=f"Now Playing {search.title}!", colour=discord.Colour.random())
            embed.set_author(name=f"{search.author}")
            embed.set_thumbnail(url=f"{search.thumbnail}")
            await ctx.send(embed=embed)
            logger.info(f'Playskipping to: {search.title}')
        elif vc.is_paused():
            await ctx.send('The bot is currently paused, to playskip, first resume playing music with !resume')
        else:
            await ctx.send('The bot is not currently playing anything.')
    else:
        await ctx.send('The bot is not connected to a voice channel.')

#Skip current song, ex: !skip
@client.command()
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
        logger.info(f'Skipping music')
        if vc.is_paused():
            await vc.resume()
    else:
        await ctx.send('The bot is not connected to a voice channel.')

#Pause current song, ex: !pause
@client.command()
@commands.has_role(DJ)
async def pause(ctx):
    vc = ctx.voice_client
    if vc:
        if vc.is_playing() and not vc.is_paused():
            await vc.pause()
            await ctx.send("Paused!")
            logger.info(f'Pausing music')
        else:
            await ctx.send("Nothing is currently playing")
    else:
        await ctx.send("The bot is not connect to a voice channel.")
        
#Resume current song, ex: !resume
@client.command()
@commands.has_role(DJ)
async def resume(ctx):
    vc = ctx.voice_client
    if vc:
        if vc.is_paused():
            await vc.resume()
            await ctx.send("Resuming!")
            logger.info(f'Resuming music')
        else:
            await ctx.send("Nothing is currently paused.")
    else:
        await ctx.send("The bot is not connected to a voice channel")

#Show whats next in the queue
@client.command(aliases=['nextsong'])
@commands.has_role(DJ)
async def next(ctx):
    vc = ctx.voice_client
    if vc:
        try:
            search = vc.queue.get()
            vc.queue.put_at_front(item=search)
            await ctx.send(f"The next song is: {search}")
        except:    
            await ctx.send("The queue is empty, add a song by using !play or !playsc")
    else:
        await ctx.send("The bot is not connected to a voice channel")

#Seeks to specifc second in song, ex: !seek 50(seeks to 50 seconds)
@client.command()
@commands.has_role(DJ)
async def seek(ctx, seek = 0):
    vc = ctx.voice_client
    val = int(seek)
    if vc:
        if vc.is_playing() and not vc.is_paused():
            await vc.seek(vc.track.length * val)
            await ctx.send(f"Seeking!")
        else:
            await ctx.send("Nothing is currently playing")
    else:
        await ctx.send("The bot is not connected to a voice channel.")

#Set volume of bot, ex !volume 1(sets volume of bot to 1)
@client.command()
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

#Make copy of queue, get items and print to showcase all items
@client.command()
@commands.has_role(DJ)
async def queue(ctx):
    vc = ctx.voice_client
    if vc.queue.is_empty is False:
        logger.info(f'Printing Queue')    
        await ctx.send("Current Songs in queue: ")
        count = 1
        test = vc.queue.copy()
        while not test.is_empty:
            item = test.get()
            await ctx.send(f"{count}: {item}")
            await asyncio.sleep(0.5)
            count += 1
    else:
        logger.info(f'Queue is already empty')
        await ctx.send(f"The queue is currently empty, add a song by using !play or !playsc")

#Make copy of queue, get items and print to showcase all items
@client.command(aliases=['clearqueue, restart'])
@commands.has_role(DJ)
async def empty(ctx):
    vc = ctx.voice_client
    if vc.queue.is_empty is False:    
        vc.queue.clear()
        logger.info(f'Emptying queue')
        await ctx.send(f"All items from queue have been removed.")
    else:
        logger.info(f'Queue is already empty')
        await ctx.send(f"The queue is currently empty, add a song by using !play or !playsc")

#Clear Messages from channel, ex !clear 50
@client.command(aliases=['purge', 'delete'])
@commands.has_role(ADMIN or "MOD")
async def clear(ctx, amount=None):

    if (amount is None):
        await ctx.send("You must enter a number after the !clear")
    else:
        val = int(amount)
        if(val <= 0):
            await ctx.send("You must enter a number greater than 0")
        else:
            await ctx.channel.purge(limit=val)

#Error Handling if unable to find song, or user isn't in a voice channel
async def play_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("Unable to find track :(")
        logger.error("Unable to find track")
    else:
        await ctx.send("Please join a voice channel")
        logger.error("User not in voice channel, bot unable to join")

#Run bot
client.run(DISCORD_TOKEN)