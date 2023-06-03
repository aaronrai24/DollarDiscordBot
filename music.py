# music.py
# dev: Aaron Rai

import discord
import os
import wavelink
import logging
import asyncio
import logging.handlers
import random
import pandas
import time
import psutil
import threading
import traceback
import sys
import spotipy
import requests
import json
import mysql.connector

from datetime import date
from pandas import *
from discord.ext import commands
from dotenv import load_dotenv
from lyricsgenius import Genius
from spotipy.oauth2 import SpotifyClientCredentials
from collections import defaultdict

# Global Variables
ADMIN = '⚡️'
MOD = '🌩️'
artist = ''
CREATEDCHANNELS = []
START_TIME = time.time()
user_usage = defaultdict(lambda: {'timestamp': 0, 'count': 0})



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
handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s'))
logger.addHandler(handler)
logging.getLogger('discord.gateway').setLevel(logging.WARNING)
logger.setLevel(logging.DEBUG)

# Get Discord, Genius, Spotify token from ENV
DISCORD_TOKEN = os.getenv('TOKEN')
genius = Genius('GENIUSTOKEN')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
TRACKER_GG = os.getenv('TRACKERGG')
RIOT_TOKEN = os.getenv('RIOTTOKEN')
GITHUB_TOKEN = os.getenv('GITHUBTOKEN')

# Initiatize connection to DB
mydb = mysql.connector.connect(
    host="localhost",
    user= os.getenv('DB_USER'),
    password= os.getenv('DB_PW'),
    database="cash")

# Authenticate your application with Spotify
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

@client.event
async def on_ready():
    client.loop.create_task(connect_nodes())
    try:
        synced = await client.tree.sync()
        logger.info(f'Synced {len(synced)} command(s)')
    except Exception as e:
        logger.error(f'{e}')

    for guild in client.guilds:
        logger.info(f'Dollar loaded in {guild.name}, owner: {guild.owner}')
        channel = guild.system_channel # Notify guild's default system channel set in Discord settings
        if channel is not None:
            try:
                file_path = os.path.join("markdown", "patch_notes.md")
                if os.path.isfile(file_path):
                    with open(file_path, "r") as file:
                        desc = file.read()

                embed = discord.Embed(
                    title='Patch: 1.1',
                    url='https://en.wikipedia.org/wiki/Dollar',
                    description=desc,
                    colour=discord.Color.green()
                )
                embed.set_author(name='Dollar')
                file_path = os.path.join("images", "dollar.png")
                img = discord.File(file_path, filename='dollar.png')
                embed.set_thumbnail(url="attachment://dollar.png")
                embed.set_footer(text='Feature request? Bug? Please report it by using /reportbug or /featurerequest')

                await channel.send(embed=embed, file=img)
                logger.info(f'Notified {guild.name} of dollar\'s latest update.')
            except discord.Forbidden:
                logger.warning(f"Could not send message to {channel.name} in {guild.name}. Missing permissions.")
            except discord.HTTPException:
                logger.error(f"Could not send message to {channel.name} in {guild.name}. HTTP exception occurred.")


async def connect_nodes():
    await client.wait_until_ready()
    await wavelink.NodePool.create_node(
        bot=client,
        host='127.0.0.1',
        port=2333,
        password='discordTest123'
    )

#------------------------------------------------------------------------------------------------

# App commands

# /ping App command, Make sure dollar is alive app command
@client.tree.command(name='ping', description='Make sure Dollar is alive')
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Yo {interaction.user.mention}, i'm alive thanks for checking", ephemeral=True)

# /status App command, Check dollar diagnostics, CPU, RAM, Uptime
@client.tree.command(name='status', description='Dollar server status, CPU usage, Memory usage, Uptime, etc.')
async def status(interaction: discord.Interaction):
    uptime = time.time() - START_TIME
    uptime_formatted = time.strftime("%H:%M:%S", time.gmtime(uptime))
    cpu_percent = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent
    response_message = f"Bot is currently online and running smoothly.\n\nUptime: {uptime_formatted}\nCPU Load: {cpu_percent}%\nRAM Usage: {ram_usage}%"
    await interaction.response.send_message(response_message)

# /setup App command, setup JOIN HERE and commands text channel automatically
@client.tree.command(name='setup', description='Automatically create all dependencies to use all of Dollar\'s features')
async def setup(interaction: discord.Interaction):
    guild = interaction.guild
    logger.info(f'/setup used in {guild}, creating dependencies')

    # Check if voice channel 'JOIN HERE' already exists
    voice_channel_exists = discord.utils.get(guild.voice_channels, name='JOIN HERE💎')
    if voice_channel_exists:
        logger.warning(f'JOIN HERE💎 already exists in {guild}')
    else:
        await guild.create_voice_channel('JOIN HERE💎')
        logger.info(f'Created JOIN HERE💎 in {guild}')

    # Check if text channel 'commands' already exists
    text_channel_exists = discord.utils.get(guild.text_channels, name='commands')
    if text_channel_exists:
        logger.warning(f'commands already exists in {guild}')
    else:
        await guild.create_text_channel('commands')
        logger.info(f'Created commands in {guild}')
  
    await interaction.response.send_message('Voice channel and text channels created successfully, use !help for more info.', ephemeral=True)

# /reportbug, Submit a bug
@client.tree.command(name='reportbug', description='Report a bug to the developer')
async def reportbug(interaction: discord.Interaction, bug_title: str, bug_description: str):
    author = interaction.user
    server = interaction.guild

    # Check if user has exceeded rate limit
    now = time.time()
    user_info = user_usage[author.id]
    if now - user_info['timestamp'] < 3600 and user_info['count'] >= 3:
        await interaction.response.send_message('You have exceeded the rate limit for this command. Please try again later.', ephemeral=True)
        return
    
    # Update user usage information
    user_info['timestamp'] = now
    user_info['count'] += 1
    
    # Proceed with command as normal
    embed = discord.Embed(title='Bug Report', description=f"AUTHOR: {author} DISCORD: {server}\n\nTitle: {bug_title}\n\nDescription: {bug_description}", color=discord.Color.green())
    logger.info(f'{author} submitted a bug in {server}')

    # Send the bug report to the developer
    user = await client.fetch_user('223947980309397506')
    message = await user.send(embed=embed)
    await interaction.response.send_message('Bug report submitted successfully!', ephemeral=True)

    # Add reactions for accepting and declining the bug report, as well as bug in progress and completion
    await message.add_reaction('✅')  # Accept Bug report
    await message.add_reaction('❌')  # Decline Bug report

    # Create a check function for the reactions
    def check(reaction, user):
        return user == user and str(reaction.emoji) in ["✅", "❌"]

    # Wait for a reaction from the developer
    try:
        reaction, user = await client.wait_for('reaction_add', check=check)
    except asyncio.TimeoutError:
        await message.reply("The bug report was not accepted or declined in time.", mention_author=False)
        logger.warning('Developer did not accept/decline bug report, timing out')
        return

    # Notify the user who submitted the bug report whether it was accepted or declined
    if str(reaction.emoji) == '✅':
        user_embed = discord.Embed(title='Bug Report', description=f"Your bug report regarding '{bug_title}' has been accepted!", color=discord.Color.green())
        # Create the issue payload
        issue_title = bug_title
        issue_body = f'Bug report: {bug_description}\n\nSubmitted by: {author}\nServer: {server}'
        payload = {'title': issue_title, 'body': issue_body, 'labels': ['bug']}

        # Define the necessary variables
        repository = 'DollarDiscordBot'
        owner = 'aaronrai24'
        access_token = GITHUB_TOKEN

        # Define the API endpoint for creating an issue
        url = f'https://api.github.com/repos/{owner}/{repository}/issues'

        # Add authentication using your access token
        headers = {'Authorization': f'token {access_token}'}

        # Send the POST request to create the issue
        response = requests.post(url, headers=headers, data=json.dumps(payload))

        # Check the response status code
        if response.status_code == 201:
            logger.info('Added bug report to GitHub issues')
        else:
            await message.reply("Failed to add bug report to GitHub issues.", mention_author=False)
            logger.error(f'Failed to add bug report to GitHub issues: {response.text}')

    else:
        user_embed = discord.Embed(title='Bug Report', description=f"Your bug report regarding '{bug_title}' has been declined.", color=discord.Color.red())
    
    try:
        user_message = await author.send(embed=user_embed)
        logger.info(f"Sent notification to {author}")
    except discord.errors.Forbidden:
        logger.warning(f"Failed to send notification to {author} (user has blocked the bot)")

# /featurerequest, Submit a feature request
@client.tree.command(name='featurerequest', description='Submit a feature request to the developer')
async def featurerequest(interaction: discord.Interaction, feature_title: str, feature_description: str):
    author = interaction.user
    server = interaction.guild
    
    # Check if user has exceeded rate limit
    now = time.time()
    user_info = user_usage[author.id]
    if now - user_info['timestamp'] < 3600 and user_info['count'] >= 3:
        await interaction.response.send_message('You have exceeded the rate limit for this command. Please try again later.', ephemeral=True)
        return
    
    # Update user usage information
    user_info['timestamp'] = now
    user_info['count'] += 1
    
    # Proceed with command as normal
    embed = discord.Embed(title='Feature Request', description=f"AUTHOR: {author} DISCORD: {server}\n\nTitle: {feature_title}\n\nDescription: {feature_description}", color=discord.Color.green())
    logger.info(f'{author} submitted a feature request in {server}')

    # Send the feature request to the developer
    user = await client.fetch_user('223947980309397506')
    message = await user.send(embed=embed)
    await interaction.response.send_message('Feature request submitted successfully!', ephemeral=True)

    # Add reactions for accepting and declining the feature request
    await message.add_reaction('✅')  # Accept feature request
    await message.add_reaction('❌')  # Decline feature request

    # Create a check function for the reactions
    def check(reaction, user):
        return user == user and str(reaction.emoji) in ['✅', '❌']

    # Wait for a reaction from the developer
    try:
        reaction, user = await client.wait_for('reaction_add', check=check)
    except asyncio.TimeoutError:
        await message.reply('The feature request was not accepted or declined in time.', mention_author=False)
        logger.warning('Developer did not accept/decline feature request, timing out')
        return
    
    # Notify the user who submitted the feature request whether it was accepted or declined
    if str(reaction.emoji) == '✅':
        user_embed = discord.Embed(title='Feature Request', description=f"Your feature request regarding '{feature_title}' has been accepted!", color=discord.Color.green())
        
        # Create the issue payload
        issue_title = feature_title
        issue_body = f'Feature request: {feature_description}\n\nSubmitted by: {author}\nServer: {server}'
        payload = {'title': issue_title, 'body': issue_body, 'labels': ['enhancement']}  # Add 'enhancement' label to the issue

        # Define the necessary variables
        repository = 'DollarDiscordBot'
        owner = 'aaronrai24'
        access_token = GITHUB_TOKEN

        # Define the API endpoint for creating an issue
        url = f'https://api.github.com/repos/{owner}/{repository}/issues'

        # Add authentication using your access token
        headers = {'Authorization': f'token {access_token}'}

        # Send the POST request to create the issue
        response = requests.post(url, headers=headers, data=json.dumps(payload))

        # Check the response status code
        if response.status_code == 201:
            logger.info('Added feature request to GitHub issues')
        else:
            await message.reply("Failed to add feature request to GitHub issues.", mention_author=False)
            logger.error(f'Failed to add feature request to GitHub issues: {response.text}')
    else:
        user_embed = discord.Embed(title='Feature Request', description=f"Your feature request regarding '{feature_title}' has been declined.", color=discord.Color.red())
    
    try:
        user_message = await author.send(embed=user_embed)
        logger.info(f"Sent notification to {author}")
    except discord.errors.Forbidden:
        logger.warning(f"Failed to send notification to {author} (user has blocked the bot)")

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
        await asyncio.sleep(.5)
        next_track = player.queue.get()
        await player.play(next_track)
        logger.info(f'Playing next track: {next_track}')
    else:
        logger.info('Queue is empty')

# Event was created
@client.event
async def on_scheduled_event_create(event):
    logger.info(f'The event [{event.name}] in was created in {event.guild}')

# Event was cancelled
@client.event
async def on_scheduled_event_delete(event):
    logger.info(f'The event [{event.name}] in was cancelled in {event.guild}')

# Event was modifed(changes made or status changed)
@client.event
async def on_scheduled_event_update(before, after):
    start = str(before.status)
    current = str(after.status)
    users = after.users()
    channel = after.channel

    if start == 'EventStatus.scheduled' and current == 'EventStatus.active':
        #Event has started
        logger.info(f'Event [{after.name}] in {after.guild} has started')
        mentioned_users = []
        async for user in users:
            await channel.set_permissions(user, connect=True)
            mentioned_users.append(user.mention)
            logger.info(f'{user} is interested, allowing them to connect to {channel}')
        mention_string = ' '.join(mentioned_users)
        await channel.send(f"The event has started! {mention_string}, you can now join the voice channel.")
    elif start == 'EventStatus.active' and current == 'EventStatus.completed':
        #Event has completed
        logger.info(f'Event [{after.name}] in {after.guild} has completed')
        async for user in users:
            await channel.set_permissions(user, connect=False)
            logger.info(f'No longer allowing {user} to connect to {channel}')

# Add interested users to connect to event channel
@client.event
async def on_scheduled_event_user_add(event, user):
    logger.info(f'{user} is interested in [{event.name}] in {event.guild}')

# If user loses interest in event, remove permissions to connect to channel
@client.event
async def on_scheduled_event_user_remove(event, user):
    logger.info(f'{user} is now uninterested in the event [{event.name}] in {event.guild}')

# Scan messages to ensure message was sent in #commands chat
@client.event
async def on_message(message):
    msg = message.content
    channel = str(message.channel)
    author = message.author

    if isinstance(message.channel, discord.channel.DMChannel) and message.author != client.user:
        logger.info(f'{author} sent a DM to Dollar')
        await message.author.send('Read the readme at this link: https://github.com/aaronrai24/DollarDiscordBot/blob/main/README.md, if you still')
        await message.author.send('If you still have questions, go to a discord I am in and use /featurerequest to submit a request and interact with my devs.')

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
        logger.warn(f'{guild} is not using auto-channel creation, JOIN HERE💎 channel does not exist')
    user = str(member).split("#")[0]

    if str(member) == 'Dollar#5869':
        dollar = member.id
    else:
        dollar = 0

    # Add/Remove DJ Role from users, if user joins JOIN HERE💎, create a voice channel and move them to that channel, remove created channel(s) when its empty
    if ctxbefore is None and ctxafter is not None:
        # Somebody joined a voice channel
        logger.info(f'{member} joined {ctxafter}')
        if str(ctxafter) == str(channel):
            await channel.set_permissions(guild.default_role, connect=False)
            logger.info(f'Locked {str(channel)}, beginning channel creation in {str(guild)}')
            category_channel = discord.utils.get(guild.categories, id=category)
            v_channel = await guild.create_voice_channel(f"{user}'s Channel", category=category_channel, position=2)
            CREATEDCHANNELS.append(v_channel.id)
            logger.info(f'Successfully created {v_channel} in {str(guild)}')
            await member.move_to(v_channel)
            while member.voice.channel != v_channel:
                await asyncio.sleep(1)
            await channel.set_permissions(guild.default_role, connect=True)
            logger.info(f'Unlocked {str(channel)}, channel creation finished in {str(guild)}')
    elif ctxbefore is not None and ctxafter is None:
        # Somebody left a voice channel
        logger.info(f'{member} left {ctxbefore}')
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
            while member.voice.channel != v_channel:
                await asyncio.sleep(1)
            await channel.set_permissions(guild.default_role, connect=True)
            logger.info(f'Unlocked {str(channel)}, channel creation finished in {str(guild)}')

    # Inactivity Checker, create a new thread to run idle_checker
    vc_lock = threading.Lock()
    comchannel_lock = threading.Lock()
    
    if member.id != dollar:
        return

    elif ctxbefore is None:
        vc = after.channel.guild.voice_client
        asyncio.create_task(idle_checker(vc, comchannel, guild))

#------------------------------------------------------------------------------------------------

# Functions

# Inactivity Checker, disconnect dollar after 10 minutes
async def idle_checker(vc, comchannel, guild):
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
            await comchannel.purge(limit=500)
            logger.info('Finished clearing #commands channel')
        if not vc.is_connected():
            break

# Check if the command sent comes from a user in the same voice channel(for most music commands)
def is_connected_to_same_voice():
    async def predicate(ctx):
        if not ctx.author.voice:
            # User is not connected to a voice channel
            raise commands.CheckFailure("You need to be in a voice channel to use this command")
        elif not ctx.voice_client or ctx.author.voice.channel != ctx.voice_client.channel:
            # User is connected to a different voice channel than the bot
            raise commands.CheckFailure("You need to be in the same voice channel as Dollar to use this command")
        return True
    return commands.check(predicate)

# Check if the command is coming from a user in a voice channel(for !join and !leave)
def is_connected_to_voice():
    async def predicate(ctx):
        if not ctx.author.voice:
            # User is not connected to a voice channel
            raise commands.CheckFailure("You need to be in a voice channel to use this command")
        return True
    return commands.check(predicate)

#Convert tags to Icons
def tag2Icons (tag):
    if tag == 'Anime':
        return '🇯🇵'
    elif tag == 'TV':
        return '📺'
    else:
        return '🎥'

#------------------------------------------------------------------------------------------------

# Dollar Music Commands

# Join authors voice channel
@client.command(aliases=['Join'])
@is_connected_to_voice()
async def join(ctx):
    custom_player = CustomPlayer()
    vc: CustomPlayer = await ctx.author.voice.channel.connect(cls=custom_player)
    await vc.set_volume(5)  # Set bot volume initially to 5

# Leave voice channel
@client.command(aliases=['Leave'])
@is_connected_to_same_voice()
async def leave(ctx):
    vc = ctx.voice_client
    if vc:
        await vc.disconnect()
        await ctx.channel.purge(limit=500)
    else:
        await ctx.send('The bot is not connected to a voice channel.')

# Play a song, ex: !play starboy the weeknd
@client.command(aliases=['Play'])
@is_connected_to_voice()
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
@is_connected_to_voice()
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
@is_connected_to_same_voice()
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
@is_connected_to_same_voice()
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
@is_connected_to_same_voice()
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
@is_connected_to_same_voice()
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
@is_connected_to_same_voice()
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
@is_connected_to_same_voice()
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
@is_connected_to_same_voice()
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
@is_connected_to_same_voice()
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
@is_connected_to_same_voice()
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

        embed = discord.Embed(title='Whats Queued?', description=desc, colour=discord.Colour.random())
        file_path = os.path.join("images", "dollar2.png")
        img = discord.File(file_path, filename='dollar2.png')
        embed.set_thumbnail(url="attachment://dollar2.png")
        await ctx.send(embed=embed, file=img)
    else:
        logger.info('Queue is already empty')
        await ctx.send("The queue is currently empty, add a song by using !play or !playsc")

# Clears queue, !empty
@client.command(aliases=['Empty', 'clearqueue', 'restart'])
@is_connected_to_same_voice()
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
@commands.check_any(commands.has_role(ADMIN), commands.has_role(MOD))
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
@is_connected_to_same_voice()
async def load(ctx):
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
        await queue(ctx)
        logger.info(f'Finished loading {count} songs into queue from playlist')
    else:
        await ctx.send('Please upload an Exportify Playlist to this channel and then use !load')
        logger.warning('ex.csv does not exist!')

@client.command(aliases=['generatePlaylist', 'GeneratePlaylist', 'genplay', 'genPlay'])
@is_connected_to_same_voice()
async def generateplaylist(ctx, playlist_type, artist=None, album=None):
    vc = ctx.voice_client
    count = 0
    offset = random.randint(0, 1000)

    query = f'genre:{playlist_type}'
    if artist:
        query += f' artist:{artist}'
    if album:
        query += f' album:{album}'

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
        await queue(ctx)
        logger.info(f'Finished loading {count} songs into the queue from the Spotify generated playlist')

# Print lyrics of current playing song, pulls from Genius.com
@client.command(aliases=['Lyrics'])
@is_connected_to_same_voice()
async def lyrics(ctx):
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

#------------------------------------------------------------------------------------------------

# Game Stat Commands

# Retreive CSGO Stats
@client.command(aliases=['cs'])
async def csgo(ctx, player_id):
    url = f'https://public-api.tracker.gg/v2/csgo/standard/profile/steam/{player_id}'
    headers = {'TRN-Api-Key': f'{TRACKER_GG}'}
    
    response = requests.get(url, headers=headers)
    logger.info(f'Retrieving CSGO stats from TrackerGG, player: {player_id}')
    if response.ok:
        data = response.json()
        logger.info('Stats retrieved, embedding')

        embed = discord.Embed(title=f"{data['data']['platformInfo']['platformUserHandle']}'s CSGO Stats", color=0xFFA500)
        avatar_url = data['data']['platformInfo']['avatarUrl']
        embed.set_thumbnail(url='attachment://output.png')
        embed.set_author(name=data['data']['platformInfo']['platformUserHandle'], icon_url=avatar_url)

        for segment in data['data']['segments']:
            segment_title = segment['metadata']['name']
            stats = segment['stats']

            for stat_key, stat_value in stats.items():
                stat_name = stat_value['displayName']
                stat_value = stat_value['displayValue']
                embed.add_field(name=stat_name, value=stat_value, inline=True)

            embed.add_field(name="Segment", value=segment_title, inline=False)
            file_path = os.path.join("images", "csgo.png")
            img = discord.File(file_path, filename='csgo.png')
            embed.set_thumbnail(url="attachment://csgo.png")
        # send the embed message
        await ctx.send(embed=embed, file=img)
    else:
        await ctx.send('Failed to retrieve CSGO stats, are you registered with TrackerGG? If yes, please submit a bug ticket using /reportbug')
        logger.error(f'Failed to retrieve CSGO stats for player: {player_id}')
        logger.warning(response)

# Retreive Specifc Apex Stats, filters can be weapon, gameMode, mapPool
@client.command(aliases=['Apex'])
async def apex(ctx,player_id):
    
    url = f'https://public-api.tracker.gg/v2/apex/standard/profile/origin/{player_id}'
    headers = {'TRN-Api-Key': f'{TRACKER_GG}'}
    
    response = requests.get(url, headers=headers)
    logger.info(f'Retrieving Apex stats from TrackerGG, player: {player_id}')
    if response.ok:
        data = response.json()
        logger.info('Stats retrieved, embedding')
        
        embed = discord.Embed(title=f"{data['data']['platformInfo']['platformUserHandle']}'s Apex Stats", color=0xA70000)
        player_info = data['data']['platformInfo']
        avatar_url = player_info['avatarUrl']
        handle = player_info['platformUserHandle']
        embed.set_author(name=handle, icon_url=avatar_url)

        lifetime_stats = data['data']['segments'][0]['stats']
        level = lifetime_stats['level']['displayValue']
        kills = lifetime_stats['kills']['displayValue']
        embed.add_field(name='Level', value=level, inline=True)
        embed.add_field(name='Lifetime Kills', value=kills, inline=True)

        rank_score = lifetime_stats['rankScore']
        rank_name = rank_score['metadata']['rankName']
        embed.add_field(name='Rank', value=rank_name, inline=True)
        
        active_legend_stats = data['data']['segments'][1]['stats']
        legend_name = data['data']['segments'][1]['metadata']['name']
        embed.add_field(name='Active Legend', value=legend_name, inline=False)

        file_path = os.path.join("images", "apex.png")
        img = discord.File(file_path, filename='apex.png')
        embed.set_thumbnail(url="attachment://apex.png")
        
        await ctx.send(embed=embed, file=img)
    else:
        await ctx.send('Failed to retrieve Apex stats, are you registered with TrackerGG? If yes, please submit a bug ticket using /reportbug')
        logger.error(f'Failed to retrieve Apex stats for player: {player_id}')
        logger.warning(response)

@client.command(aliases=['lol', 'league'])
async def leagueoflegends(ctx, player_id):
    region = 'na1'
    summoner_url = f'https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{player_id}'
    summoner_headers = {'X-Riot-Token': RIOT_TOKEN}

    # Get Account Data
    logger.info(f'Getting summoner data from RIOT API, player: {player_id}')
    summoner_response = requests.get(summoner_url, headers=summoner_headers)
    
    # Get Users last matches
    logger.info(f'Getting summoners last match from RIOT API, player: {player_id}')

    # Return all data collected into a discordEmbed
    if summoner_response.status_code == 200:
        logger.info(f'Obtained summoner data, player:{player_id}')
        summoner_data = summoner_response.json()
        summoner_id = summoner_data['id']

        # Get Summoner ranked data
        logger.info('Now obtaining summoner stats from RIOT API')
        stats_url = f'https://{region}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}'
        stats_response = requests.get(stats_url, headers=summoner_headers)

        logger.info('Obtained summoner stats from RIOT API, embedding')
        embed = discord.Embed(title=f'{player_id} Ranked Stats', color=0x9933FF)
        if stats_response.status_code == 200:
            stats = stats_response.json()
            profile_icon_id = summoner_data['profileIconId']
            level = summoner_data['summonerLevel']
            profile_icon_url = f'http://ddragon.leagueoflegends.com/cdn/11.11.1/img/profileicon/{profile_icon_id}.png'

            if not stats:
                embed.add_field(name='No Results Returned', value='Have you played ranked?')
            else:
                for stat in stats:
                    embed.add_field(name=stat['queueType'], value=f'{stat["tier"]} {stat["rank"]} ({stat["leaguePoints"]} LP)', inline=True)
                    embed.add_field(name='Wins', value=f'{stat["wins"]}', inline=True)
                    embed.add_field(name='Losses', value=f'{stat["losses"]}', inline=True)
            embed.set_author(name=f'{player_id} LVL: {level}', icon_url=profile_icon_url)
            file_path = os.path.join("images", "league.jpg")
            img = discord.File(file_path, filename='league.jpg')
            embed.set_thumbnail(url="attachment://league.jpg")
            await ctx.send(embed=embed, file=img)
        else:
            logger.info(f'Failed to get summoner stats, response: {stats_response}')
            await ctx.send('Error retrieving stats.')
    else:
        logger.info(f'Failed to get summoner, response: {summoner_response}')
        await ctx.send('Player not found.')

#------------------------------------------------------------------------------------------------

# WatchList Commands

# Query for userID and return Username with their watchlist if found
# else,  generate entry and initialization message
@client.command(aliases=['wl'])
async def watchlist(ctx):
    mycursor = mydb.cursor()
    try:
        mycursor.execute("SELECT * FROM userlist WHERE Username = \"%s\"" % str(ctx.author))
        logger.info(f'Executed query to return UserID for {ctx.author}')
    except (mysql.connector.Error, mysql.connector.Warning) as e:
        await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
        logger.warning(e)
        return None
    myresult = mycursor.fetchall()

    # Initialize entry for user
    if len(myresult) == 0:
        try:
            mycursor.execute("INSERT INTO userlist (Username) VALUES (\'%s\')" % str(ctx.author))
        except (mysql.connector.Error, mysql.connector.Warning) as e:
            await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
            logger.warning(e)
            return None
        mydb.commit()
        await ctx.send(f'{ctx.author.mention} Initialization complete! Created an entry for you!')
        logger.info(f'Entry created for {ctx.author}')
            

    #print watchlist for user
    else:
        logger.info(f'Entry already exists for {ctx.author}, printing their watchlist')
        userId = myresult[0][0]
        try:
            mycursor.execute("SELECT * FROM activelist WHERE UserID = \'%s\'" % userId)
            logger.info(f'Executed query to return entries in activelist for {ctx.author}')
        except (mysql.connector.Error, mysql.connector.Warning) as e:
            await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
            logger.warning(e)
            return None
        userresults = mycursor.fetchall()
        if not len(userresults):
            await ctx.send(f"{ctx.author.mention} Current list is empty. Please use !addshow to add to your WatchList")
            return
        
        # Embed response
        embed = discord.Embed(title="Current WatchList", colour=discord.Colour.random())
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
        embed.add_field(name='Title', value='', inline=True)
        embed.add_field(name='Tag', value='', inline=True)
        embed.add_field(name='Order', value='', inline=True)
        for x in userresults:
            embed.add_field(name='', value=x[1], inline=True)
            embed.add_field(name='', value=tag2Icons(x[3]), inline=True)
            embed.add_field(name='', value=x[4], inline=True)
        await ctx.send(embed=embed)
        

# Add entry to watchlist for user
@client.command(aliases=['AddShow', 'addShow', 'Addshow', 'as'])
async def addshow(ctx):
    # Get UserID from Username
    mycursor = mydb.cursor()
    try:
        mycursor.execute("SELECT * FROM userlist WHERE Username = \"%s\"" % str(ctx.author))
        logger.info(f'Executed query to return UserID for {ctx.author}')
    except (mysql.connector.Error, mysql.connector.Warning) as e:
        await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
        logger.warning(e)
        return None
    myresult = mycursor.fetchall()
    if len(myresult) == 0:
        await ctx.send(f'{ctx.author.mention} User does not exist. Try !watchlist to setup user.')
        return
    userId = myresult[0][0]

    # Check if 7 entries and get index for new entry.
    try:
        mycursor.execute("SELECT TableIndex FROM activelist WHERE UserID = %d ORDER BY TableIndex DESC LIMIT 1" % userId)
        logger.info(f'Executed query to return highest TableIndex for {ctx.author}')
    except (mysql.connector.Error, mysql.connector.Warning) as e:
        await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
        logger.warning(e)
        return None
    index = mycursor.fetchall()
    if index == []:
        index = 1
    else:
        index = index[0][0] + 1
    if index > 7:
        await ctx.send(f"{ctx.author.mention} Maximum size of WatchList reached (7).\nPlease use !removeshow to clear an entry")
        return

    # Prompt user for show title and sanitize input; timeout after 15 seconds
    await ctx.send(f"{ctx.author.mention} Enter the show name: ")
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    try:
        title = await client.wait_for('message', check=check, timeout=15)
    except asyncio.TimeoutError:
        await ctx.send(f"{ctx.author.mention} Timeout exceeded. Please try again.")
        return
    # Sanitize input for \'
    if title.content.find('\'') != -1:
        await ctx.send(f"{ctx.author.mention} Please ensure you do not include apostrophes or other invalid characters.\nTry !addshow again.")
        return

    # Prompt user for show tag
    msg = await ctx.send(f"{ctx.author.mention} Select the shows tag (TV 📺, Anime 🇯🇵, Movie 🎥): ")
    await msg.add_reaction('📺')  # TV entry
    await msg.add_reaction('🇯🇵')  # Anime entry
    await msg.add_reaction('🎥')  # Movie entry

    def reaction1check(reaction, user):
        name1 = str(ctx.author).split("#")[0]
        return  user.name == name1 and str(reaction.emoji) in ['🇯🇵', '📺', '🎥']

    try:
        reaction, user = await client.wait_for('reaction_add', timeout=15, check=reaction1check)
        if reaction.emoji == '📺':
            react = 'TV'
        elif reaction.emoji == '🇯🇵':
            react = 'Anime'
        else:
            react = 'Movie'
    except asyncio.TimeoutError:
        await ctx.send(f"{ctx.author.mention} Timeout exceeded. Please try again.")
        return
    # Prompt user to confirm details
    msg = await ctx.send(f"{ctx.author.mention} Is this correct (Select ✅ or ❌):\nTitle: {title.content} | Tag: {react}")
    await msg.add_reaction('✅')  # Acknowledge entry
    await msg.add_reaction('❌')  # Decline entry

    def reaction2check(reaction, user):
        name1 = str(ctx.author).split("#")[0]
        return  user.name == name1 and str(reaction.emoji) in ['✅','❌']
    try:
        reaction, user = await client.wait_for('reaction_add', timeout=15, check=reaction2check)
    except asyncio.TimeoutError:
        await ctx.send(f"{ctx.author.mention} Timeout exceeded. Please try again.")
        return

    #Verify confirmation
    if reaction.emoji == '✅':
        # Insert entry to user's watchlisttable
        imageUrl = 'x' # add query for image later (FR)
        try:
            mycursor.execute("INSERT INTO activelist (UserID, ShowName, Image, Tag, TableIndex) VALUES (%d, \'%s\', \'%s\', \'%s\', %d)" % (userId, title.content, imageUrl, react, index))
            mydb.commit()
            logger.info(f'Watchlist entry added for {ctx.author}')
            await ctx.send(f"{ctx.author.mention} Added {title.content} to your WatchList!")
        except (mysql.connector.Error, mysql.connector.Warning) as e:
            await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
            logger.warning(e)
            return None
        
    else:
        await ctx.send(f"{ctx.author.mention} Didn't confirm entry. Please try !addshow again to create an entry.")
        return
    
# Remove entry from watchlist for user
@client.command(aliases=['rs', 'Removeshow', 'RemoveShow'])
async def removeshow(ctx):
    # Get UserID from Username
    mycursor = mydb.cursor()
    try:
        mycursor.execute("SELECT * FROM userlist WHERE Username = \"%s\"" % str(ctx.author))
        logger.info(f'Executed query to return UserID for {ctx.author}')
    except (mysql.connector.Error, mysql.connector.Warning) as e:
        await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
        logger.warning(e)
        return None    
    myresult = mycursor.fetchall()
    if len(myresult) == 0:
        await ctx.send(f'{ctx.author.mention} User does not exist. Try !watchlist to setup user.')
        return
    userId = myresult[0][0]

    # Prompt user for show title; timeout after 15 seconds
    await ctx.send(f"{ctx.author.mention} Enter the name of the show to be removed: ")
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    try:
        title = await client.wait_for('message', check=check, timeout=15)
    except asyncio.TimeoutError:
        await ctx.send(f"{ctx.author.mention} Timeout exceeded. Please try again.")
        return

    # Check if show currently exists and get index
    try:
        mycursor.execute("SELECT * FROM activelist WHERE UserID = %d AND ShowName = \'%s\'" % (userId, title.content))
        logger.info(f'Executed query to return if show exists in activelist for {ctx.author}')
    except (mysql.connector.Error, mysql.connector.Warning) as e:
        await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
        logger.warning(e)
        return None
    userresults = mycursor.fetchall()
    if not len(userresults):
        await ctx.send(f"{ctx.author.mention} This show is not in your WatchList. Nothing to remove.")
        return
    showIndex = userresults[0][4]
    
    # Remove show from WatchList
    try:
        mycursor.execute("DELETE FROM activelist WHERE UserID = %d AND ShowName = \'%s\'" % (userId, title.content))
    except (mysql.connector.Error, mysql.connector.Warning) as e:
        await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
        logger.warning(e)
        return None
    mydb.commit()
    logger.info(f'{ctx.author}\'s Watchlist entry deleted for {title.content}')
    await ctx.send(f"{ctx.author.mention} Removed WatchList entry for {title.content}")

    # Get list of higher indexed shows to be updated
    try:
        mycursor.execute("SELECT * FROM activelist WHERE UserID = %d AND TableIndex > %d" % (userId, showIndex))
        logger.info(f'Executed query to return list of shows needing to update indices for {ctx.author}')
    except (mysql.connector.Error, mysql.connector.Warning) as e:
        await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
        logger.warning(e)
        return None
    higherResults = mycursor.fetchall()
    for x in higherResults:
        # Update indexes by decrementing
        try:
            mycursor.execute("UPDATE activelist SET TableIndex = %d WHERE UserID = %d AND TableIndex = %d" % (x[4] - 1, userId, x[4]))
        except (mysql.connector.Error, mysql.connector.Warning) as e:
            await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
            logger.warning(e)
            return None
    mydb.commit()
    logger.info(f'Executed query to update indexes for {ctx.author}')

# Query for userID and return Username with their watchhistory if found
# else, suggest !watchlist to generate entry
@client.command(aliases=['wh','History', 'WatchHistory', 'watchhistory', 'watchHistory'])
async def history(ctx):
    mycursor = mydb.cursor()
    try:
        mycursor.execute("SELECT * FROM userlist WHERE Username = \"%s\"" % str(ctx.author))
        logger.info(f'Executed query to return UserID for {ctx.author}')
    except (mysql.connector.Error, mysql.connector.Warning) as e:
        await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
        logger.warning(e)
        return None
    myresult = mycursor.fetchall()

    # Check if user exists
    if len(myresult) == 0:
        await ctx.send(f'{ctx.author.mention} User does not exist. Try !watchlist to setup user.')

    # Print WatchHistory for user
    else:
        logger.info(f'Printing {ctx.author}\'s WatchHistory')
        userId = myresult[0][0]
        try:
            mycursor.execute("SELECT * FROM watchhistory WHERE UserID = \'%s\' ORDER BY Rating DESC" % userId)
            logger.info(f'Executed query to return WatchHistory entries for {ctx.author}')
        except (mysql.connector.Error, mysql.connector.Warning) as e:
            await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
            logger.warning(e)
            return None
        userresults = mycursor.fetchall()
        if not len(userresults):
            await ctx.send(f"{ctx.author.mention} Current list is empty. Please use !addhistory to add to your WatchHistory")
            return
        # Embed response
        embed = discord.Embed(title="Watch History", colour=discord.Colour.random())
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
        embed.add_field(name='Title', value='', inline=True)
        embed.add_field(name='Rating', value='', inline=True)
        embed.add_field(name='Date', value='', inline=True)
        # NEEDS WORK
        count = 1
        for x in userresults:
            if count > 7:
                break
            embed.add_field(name='', value=x[1], inline=True)
            embed.add_field(name='', value=x[2], inline=True)
            embed.add_field(name='', value=x[4], inline=True)
            count += 1

        await ctx.send(embed=embed)

# Add entry for WatchHistory after completing a show
@client.command(aliases=['ah','Addhistory', 'AddHistory'])
async def addhistory(ctx):

    # Get UserID from Username
    mycursor = mydb.cursor()
    try:
        mycursor.execute("SELECT * FROM userlist WHERE Username = \"%s\"" % str(ctx.author))
        logger.info(f'Executed query to return UserID for {ctx.author}')
    except (mysql.connector.Error, mysql.connector.Warning) as e:
        await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
        logger.warning(e)
        return None
    myresult = mycursor.fetchall()
    if len(myresult) == 0:
        await ctx.send(f'{ctx.author.mention} User does not exist. Try !watchlist to setup user.')
        return
    userId = myresult[0][0]

    # Prompt user for show title and sanitize input; timeout after 15 seconds
    await ctx.send(f"{ctx.author.mention} Enter the show name: ")
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    try:
        title = await client.wait_for('message', check=check, timeout=15)
    except asyncio.TimeoutError:
        await ctx.send(f"{ctx.author.mention} Timeout exceeded. Please try again.")
        return
    # Sanitize input for \'
    if title.content.find('\'') != -1:
        await ctx.send("Please ensure you do not include apostrophes or other invalid characters.\nTry !addhistory again.")
        return

    # Prompt user for show tag
    msg = await ctx.send(f"{ctx.author.mention} Select the shows tag (TV 📺, Anime 🇯🇵, Movie 🎥): ")
    await msg.add_reaction('📺')  # TV entry
    await msg.add_reaction('🇯🇵')  # Anime entry
    await msg.add_reaction('🎥')  # Movie entry

    def reaction1check(reaction, user):
        name1 = str(ctx.author).split("#")[0]
        return  user.name == name1 and str(reaction.emoji) in ['🇯🇵', '📺', '🎥']

    try:
        reaction, user = await client.wait_for('reaction_add', timeout=15, check=reaction1check)
        if reaction.emoji == '📺':
            react = 'TV'
        elif reaction.emoji == '🇯🇵':
            react = 'Anime'
        else:
            react = 'Movie'
    except asyncio.TimeoutError:
        await ctx.send(f"{ctx.author.mention} Timeout exceeded. Please try again.")
        return

    # Prompt user for show rating 1-5; timeout after 15 seconds
    msg2 = await ctx.send(f"{ctx.author.mention} Enter your rating for {title.content} (1-5): ")
    await msg2.add_reaction('1️⃣')  # TV entry
    await msg2.add_reaction('2️⃣')  # Anime entry
    await msg2.add_reaction('3️⃣')  # Movie entry
    await msg2.add_reaction('4️⃣')  # TV entry
    await msg2.add_reaction('5️⃣')  # Anime entry

    def reaction3check(reaction, user):
        name1 = str(ctx.author).split("#")[0]
        return  user.name == name1 and str(reaction.emoji) in ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']
    try:
        reaction, user = await client.wait_for('reaction_add', timeout=15, check=reaction3check)
        if reaction.emoji == '1️⃣':
            rating = 1
        elif reaction.emoji == '2️⃣':
            rating = 2
        elif reaction.emoji == '3️⃣':
            rating = 3
        elif reaction.emoji == '4️⃣':
            rating = 4
        else:
            rating = 5
    except asyncio.TimeoutError:
        await ctx.send(f"{ctx.author.mention} Timeout exceeded. Please try again.")
        return
    
     # Prompt user to confirm details
    msg = await ctx.send(f"{ctx.author.mention} Is this correct (Select ✅ or ❌):\nTitle: {title.content} | Rating: {rating} | Tag: {react}")
    await msg.add_reaction('✅')  # Acknowledge entry
    await msg.add_reaction('❌')  # Decline entry

    def reaction2check(reaction, user):
        name1 = str(ctx.author).split("#")[0]
        return  user.name == name1 and str(reaction.emoji) in ['✅','❌']
    try:
        reaction, user = await client.wait_for('reaction_add', timeout=15, check=reaction2check)
    except asyncio.TimeoutError:
        await ctx.send(f"{ctx.author.mention} Timeout exceeded. Please try again.")
        return
    
    # Verify confirmation
    if reaction.emoji == '✅':
        # Add WatchHistory entry
        try:
            today = date.today().strftime("%B %d %y")
            mycursor.execute("INSERT INTO watchhistory (UserID, ShowName, Rating, Tag, CompletedDate) VALUES (%d, \'%s\', %d, \'%s', \'%s')" % (userId, title.content, rating, react, today))
            mydb.commit()
            logger.info(f'WatchHistory entry added for {ctx.author}')
            response = f"{ctx.author.mention} Added {title.content} to your WatchHistory!"
        except (mysql.connector.Error, mysql.connector.Warning) as e:
            await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
            logger.warning(e)
            return None
    else:
        await ctx.send(f"{ctx.author.mention} Didn't confirm entry. Please try !addhistory again to create an entry.")
        return
    
    # Remove entry from WatchList if exists
    try:
        mycursor.execute("SELECT * FROM activelist WHERE UserID = %d AND ShowName = \'%s\'" % (userId, title.content))
        logger.info(f'Executed query to return if entry exists in activelist for {ctx.author}')
    except (mysql.connector.Error, mysql.connector.Warning) as e:
        await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
        logger.warning(e)
        return None
    myresult = mycursor.fetchall()
    # Entry exists in WatchList if len != 0
    if len(myresult) != 0:
        myIndex = myresult[0][4]
        try:
            mycursor.execute("DELETE FROM activelist WHERE UserID = %d AND ShowName = \'%s\'" % (userId, title.content))
            response += f"\nSince you finished it, also removed {title.content} from your WatchList!"
        except (mysql.connector.Error, mysql.connector.Warning) as e:
            await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
            logger.warning(e)
            return None
        mydb.commit()

        logger.info(f'Removed {title.content} from user\'s WatchList')
        # Get shows in WatchList with a higher index
        try:
            mycursor.execute("SELECT * FROM activelist WHERE UserID = %d AND TableIndex > %d" % (userId, myIndex))
            logger.info(f'Executed query to return shows needing to update indices for {ctx.author}')
        except (mysql.connector.Error, mysql.connector.Warning) as e:
            await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
            logger.warning(e)
            return None
        higherResults = mycursor.fetchall()
        for x in higherResults:
            # Update indexes by decrementing
            try:
                mycursor.execute("UPDATE activelist SET TableIndex = %d WHERE UserID = %d AND TableIndex = %d" % (x[4] - 1, userId, x[4]))
            except (mysql.connector.Error, mysql.connector.Warning) as e:
                await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
                logger.warning(e)
                return None
        mydb.commit()
        logger.info(f'Executed query to update indices for {ctx.author}')
    await ctx.send(response)
    
# Remove entry from WatchHistory for user
@client.command(aliases=['rh', 'Removehistory', 'RemoveHistory'])
async def removehistory(ctx):
    # Get UserID from Username
    mycursor = mydb.cursor()
    try:
        mycursor.execute("SELECT * FROM userlist WHERE Username = \"%s\"" % str(ctx.author))
        logger.info(f'Executed query to return UserID for {ctx.author}')
    except (mysql.connector.Error, mysql.connector.Warning) as e:
        await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
        logger.warning(e)
        return None
    myresult = mycursor.fetchall()
    if len(myresult) == 0:
        await ctx.send(f'{ctx.author.mention} User does not exist. Try !watchlist to setup user.')
        return
    userId = myresult[0][0]

    # Prompt user for show title; timeout after 15 seconds
    await ctx.send(f"{ctx.author.mention} Enter the name of the show to be removed: ")
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    try:
        title = await client.wait_for('message', check=check, timeout=15)
    except asyncio.TimeoutError:
        await ctx.send(f"{ctx.author.mention} Timeout exceeded. Please try again.")
        return

    # Check if show currently exists
    try:
        mycursor.execute("SELECT * FROM watchhistory WHERE UserID = %d AND ShowName = \'%s\'" % (userId, title.content))
        logger.info(f'Executed query to check if show exists in WatchHistory for {ctx.author}')
    except (mysql.connector.Error, mysql.connector.Warning) as e:
        await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
        logger.warning(e)
        return None
    userresults = mycursor.fetchall()
    if not len(userresults):
        await ctx.send(f"{ctx.author.mention} This show is not in your WatchHistory. Nothing to remove.")
        return
    
    # Remove show from WatchHistory
    try:
        mycursor.execute("DELETE FROM watchhistory WHERE UserID = %d AND ShowName = \'%s\'" % (userId, title.content))
    except (mysql.connector.Error, mysql.connector.Warning) as e:
        await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
        logger.warning(e)
        return None
    mydb.commit()
    logger.info(f'{ctx.author}\'s WatchHistory entry deleted for {title.content}')
    await ctx.send(f"{ctx.author.mention} Removed WatchHistory entry for {title.content}")
                
#------------------------------------------------------------------------------------------------

# Dollar Diagnostic Commands

# See all of dollars commands
@client.command()
async def help(ctx, category=None):

    if category is None:
        desc = "Available categories: music, game. Use either !help music or !help game or !help mywatchlist"
        embed = discord.Embed(title='Which commands?', description=desc, colour=0x2ecc71)
        embed.set_author(name='Dollar')
        file_path = os.path.join("images", "dollar3.png")
        img = discord.File(file_path, filename='dollar3.png')
        embed.set_thumbnail(url="attachment://dollar3.png")
        embed.set_footer(text='Feature request? Bug? Please report it by using /reportbug or /featurerequest')
        await ctx.send(embed=embed, file=img)
    elif category.lower() == "music":
        file_path = os.path.join("markdown", "musicCommands.md")
        if os.path.isfile(file_path):
            with open(file_path, "r") as file:
                commands = file.read()

        embed = discord.Embed(title='Music Commands', description=commands, colour=0x2ecc71)
        embed.set_author(name='Dollar')
        file_path = os.path.join("images", "dollar3.png")
        img = discord.File(file_path, filename='dollar3.png')
        embed.set_thumbnail(url="attachment://dollar3.png")
        embed.set_footer(text='Feature request? Bug? Please report it by using /reportbug or /featurerequest')
        await ctx.send(embed=embed, file=img)
    elif category.lower() == "game":
        file_path = os.path.join("markdown", "gameCommands.md")
        if os.path.isfile(file_path):
            with open(file_path, "r") as file:
                commands = file.read()

        embed = discord.Embed(title='Game Commands', description=commands, colour=0x2ecc71)
        embed.set_author(name='Dollar')
        file_path = os.path.join("images", "dollar3.png")
        img = discord.File(file_path, filename='dollar3.png')
        embed.set_thumbnail(url="attachment://dollar3.png")
        embed.set_footer(text='Feature request? Bug? Please report it by using /reportbug or /featurerequest')
        await ctx.send(embed=embed, file=img)
    elif category.lower() == "mywatchlist":
        file_path = os.path.join("markdown", "watchlistCommands.md")
        if os.path.isfile(file_path):
            with open(file_path, "r") as file:
                commands = file.read()

        embed = discord.Embed(title='MyWatchList Commands', description=commands, colour=0x2ecc71)
        embed.set_author(name='Dollar')
        file_path = os.path.join("images", "dollar3.png")
        img = discord.File(file_path, filename='dollar3.png')
        embed.set_thumbnail(url="attachment://dollar3.png")
        embed.set_footer(text='Feature request? Bug? Please report it by using /reportbug or /featurerequest')
        await ctx.send(embed=embed, file=img)
    else:
        await ctx.send("Invalid category. Available categories: music, game, mywatchlist")

# Admin only, see Dollar's current threads
@client.command()
@commands.has_role(ADMIN)
async def threaddump(ctx):
    logger.info('START THREAD DUMP')
    thread_list = threading.enumerate()

    # Find the highest existing thread dump number
    existing_dumps = [file for file in os.listdir() if file.startswith('dollar-thread-dump-')]
    max_dump_number = 0
    for dump in existing_dumps:
        try:
            dump_number = int(dump.split('-')[-1].split('.')[0])
            max_dump_number = max(max_dump_number, dump_number)
        except ValueError:
            pass

    dump_number = max_dump_number + 1
    dump_file_name = f'dollar-thread-dump-{dump_number}.txt'

    # Check if the dump file with the same number already exists
    while dump_file_name in existing_dumps:
        dump_number += 1
        dump_file_name = f'dollar-thread-dump-{dump_number}.txt'

    with open(dump_file_name, 'w') as file:
        for thread in thread_list:
            file.write(f'Thread: {thread.name}\n')
            file.write(f'Thread ID: {thread.ident}\n')  # Add thread ID
            file.write('Thread Stack Trace:\n')
            traceback.print_stack(sys._current_frames()[thread.ident], file=file)
            file.write('\n')

    channel = ctx.channel
    with open(dump_file_name, 'rb') as file:
        dump_file = discord.File(file)
        await channel.send(file=dump_file)

    logger.info('FINISH THREAD DUMP')

#------------------------------------------------------------------------------------------------

# Error Handling
@play.error
async def play_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("Unable to find track :(")
        logger.error("Unable to find track")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please provide a song to play")
        logger.error('User did not provide a song when using !play')

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send('Insufficient Permissions to use this command')
        logger.error('User has insufficient permissions')
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send('Command not found')
        logger.error('User tried to use a command that does not exist')
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Missing required argument')
        logger.error('User did not provide a required argument')
    elif isinstance(error, commands.BadArgument):
        await ctx.send('Invalid argument')
        logger.error('User provided an invalid argument')
    elif isinstance(error, commands.CheckFailure):
        await ctx.send('You must be in the same channel as dollar to use that command')
        logger.error('User tried using command in a different channel than dollar')

# Run bot
client.run(DISCORD_TOKEN)