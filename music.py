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

from bs4 import BeautifulSoup
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
    database=os.getenv('DB_SCHEMA'))

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
                    title='Patch: 1.1.1',
                    url='https://en.wikipedia.org/wiki/Dollar',
                    description=desc,
                    colour=discord.Color.green()
                )
                embed.set_author(name='Dollar')
                file_path = os.path.join("images", "dollar.png")
                img = discord.File(file_path, filename='dollar.png')
                embed.set_thumbnail(url="attachment://dollar.png")
                embed.set_footer(text='Feature request? Bug? Please report it by using /reportbug or /featurerequest')

                #await channel.send(embed=embed, file=img)
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

# /ticket, Open an issue in the mfDiscord(get access to the #issues channel)
@client.tree.command(name='ticket', description='Open a issue with the developers when you are having issues with Dollar')
async def ticket(interaction: discord.Interaction):
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

    guild_id = 261351089864048645
    mfDiscord = discord.utils.get(client.guilds, id=guild_id)
    issues_channel = discord.utils.get(mfDiscord.text_channels, name='issues')

    if not issues_channel:
        await interaction.response.send_message('The issues channel could not be found, please try again later.', ephemeral=True)
        return

    # Create an invite with a 30-minute expiration for the issues channel
    invite = await issues_channel.create_invite(max_age=1800, unique=True)

    # Send the invite as a direct message to the user
    try:
        await author.send(f"Here's your invite link to the #issues channel: {invite}")
        await interaction.response.send_message('An invite link has been sent to your DMs.', ephemeral=True)
        logger.info(f'Issue likely occured in {server}, author: {author}')
    except discord.Forbidden:
        await interaction.response.send_message('I cannot send you the invite link because you have disabled DMs.', ephemeral=True)
        logger.warning(f'{author} has likely disabled DMs' )

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
        await channel.send(f"The event [{after.name}] has started! {mention_string}, you can now join the voice channel.")
    elif start == 'EventStatus.active' and current == 'EventStatus.completed':
        #Event has completed
        logger.info(f'Event [{after.name}] in {after.guild} has completed')
        await channel.edit(sync_permissions=True)
        await channel.set_permissions(channel.guild.default_role, connect=False)
        logger.info(f'Revoked access to {channel} for all users')

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
    user = str(member.display_name)
    print(member.nick)
    channel = discord.utils.get(guild.channels, name='JOIN HERE💎')
    comchannel = discord.utils.get(guild.channels, name='commands')
    if channel is not None:
        category = channel.category_id    
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

# Function to execute the validation query
def validate_connection():
    try:
        cursor = mydb.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchall()
        cursor.close()
        logger.debug('Executed validation query')
        return True
    except mysql.connector.Error as error:
        # Handle the error appropriately (e.g., logging, error message)
        logger.error("Error validating connection: %s", error)
        return False

# Periodically validate the connection
def keep_alive():
    while True:
        if not validate_connection():
            # Re-establish the connection
            logger.info("Reconnecting to MySQL database")
            mydb.reconnect()
        # Wait for a certain interval before validating again
        time.sleep(60)  # 60 seconds

# Keep MySQL connection open buy run in its own thread
keep_alive_thread = threading.Thread(target=keep_alive)
keep_alive_thread.start()

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

# Convert tags to Icons
def tag2Icons(tag):
    if tag == 'Anime':
        return '🇯🇵'
    elif tag == 'TV':
        return '📺'
    else:
        return '🎥'
    
# Get UserID from userlist table
async def getUserId(ctx):
    mycursor = mydb.cursor()
    try:
        logger.info(f'Executing query to return UserID for {ctx.author}')
        mycursor.execute("SELECT * FROM userlist WHERE Username = \"%s\"" % str(ctx.author))
    except (mysql.connector.Error, mysql.connector.Warning) as e:
        await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
        logger.warning(e)
        return None
    myresult = mycursor.fetchall()
    # Return UserID or -1 if user does not exist
    if len(myresult) == 0:
        return -1
    return myresult[0][0]

# Get show title and sanitize inputs
async def getShowTitle(ctx):
    await ctx.send(f"{ctx.author.mention} Enter the show name: ")
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    try:
        title = await client.wait_for('message', check=check, timeout=15)
    except asyncio.TimeoutError:
        await ctx.send(f"{ctx.author.mention} Timeout exceeded. Please try again.")
        return -1
    # Sanitize input for \'
    if title.content.find('\'') != -1:
        await ctx.send(f"{ctx.author.mention} Please ensure you do not include apostrophes or other invalid characters.\nTry !addshow again.")
        return -2
    return title.content

# Get show tag
async def getShowTag(ctx):
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
        return -1
    return react

# Prompt user to confirm details
async def getEntryConfirmation(ctx, showTitle, showTag, rating):
    if rating == None:
        msg = await ctx.send(f"{ctx.author.mention} Is this correct (Select ✅ or ❌):\nTitle: {showTitle} | Tag: {showTag}")
    else:
        msg = await ctx.send(f"{ctx.author.mention} Is this correct (Select ✅ or ❌):\nTitle: {showTitle} | Rating: {rating} | Tag: {showTag}")
    await msg.add_reaction('✅')  # Acknowledge entry
    await msg.add_reaction('❌')  # Decline entry

    def reaction2check(reaction, user):
        name1 = str(ctx.author).split("#")[0]
        return  user.name == name1 and str(reaction.emoji) in ['✅','❌']
    try:
        reaction, user = await client.wait_for('reaction_add', timeout=15, check=reaction2check)
    except asyncio.TimeoutError:
        await ctx.send(f"{ctx.author.mention} Timeout exceeded. Please try again.")
        return -1
    return reaction

# Check if show currently exists in table and return index if exists
async def checkExists(ctx, userid, showTitle, table):
    mycursor = mydb.cursor()
    try:
        logger.info(f'Executing query to return if show exists in {table} for {ctx.author}')
        mycursor.execute("SELECT * FROM %s WHERE UserID = %d AND ShowName = \'%s\'" % (table, userid, showTitle))
    except (mysql.connector.Error, mysql.connector.Warning) as e:
        await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
        logger.warning(e)
        return None
    userresults = mycursor.fetchall()
    # Entry does not exist
    if not len(userresults):
        return -1
    # Entry exists
    logger.info(f'{showTitle} already exists in {ctx.author}\'s {table}.')
    return userresults[0][4]

# Remove entry in table
async def removeEntry(ctx, userid, showTitle, table):
    mycursor = mydb.cursor()
    try:
        logger.info(f'Executing query to delete {showTitle} in {table} for {ctx.author}')
        mycursor.execute("DELETE FROM %s WHERE UserID = %d AND ShowName = \'%s\'" % (table, userid, showTitle))
    except (mysql.connector.Error, mysql.connector.Warning) as e:
        await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
        logger.warning(e)
        return -1
    mydb.commit()
    return 1

# Get list of either higher or lower indexed shows and update indices
async def getIndicesAndUpdate(ctx, userid, showIndex1, showIndex2, direction1, direction2):
    mycursor = mydb.cursor()
    try:
        logger.info(f'Executing query to return list of shows needing to update indices for {ctx.author}')
        if showIndex2 == -1: # Normal remove
            mycursor.execute("SELECT * FROM activelist WHERE UserID = %d AND TableIndex %s %d" % (userid, direction1, showIndex1))
        else: # editing table
            mycursor.execute("SELECT * FROM activelist WHERE UserID = %d AND TableIndex %s %d AND TableIndex %s %d" % (userid, direction1, showIndex1, direction2, showIndex2))
    except (mysql.connector.Error, mysql.connector.Warning) as e:
        await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
        logger.warning(e)
        return None
    results = mycursor.fetchall()
    for x in results:
        # Update indexes by decrementing or incrementing based on the change being made
        try:
            logger.info(f'Executing query to update indices for {ctx.author}')
            if showIndex1 < showIndex2 or showIndex2 == -1: # Decrease other indices
                mycursor.execute("UPDATE activelist SET TableIndex = %d WHERE UserID = %d AND ShowName = \'%s\'" % (x[4] - 1, userid, x[1]))
            else: # Increase other indices
                mycursor.execute("UPDATE activelist SET TableIndex = %d WHERE UserID = %d AND ShowName = \'%s\'" % (x[4] + 1, userid, x[1]))
        except (mysql.connector.Error, mysql.connector.Warning) as e:
            await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
            logger.warning(e)
            return None
    mydb.commit()

# Get show rating 1-5 from user; timeout after 15 seconds
async def getShowRating(ctx, showTitle):
    msg2 = await ctx.send(f"{ctx.author.mention} Enter your rating for {showTitle} (1-5): ")
    await msg2.add_reaction('1️⃣')
    await msg2.add_reaction('2️⃣')
    await msg2.add_reaction('3️⃣')
    await msg2.add_reaction('4️⃣')
    await msg2.add_reaction('5️⃣')

    def reaction3check(reaction, user):
        name1 = str(ctx.author).split("#")[0]
        return  user.name == name1 and str(reaction.emoji) in ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']
    try:
        reaction, user = await client.wait_for('reaction_add', timeout=15, check=reaction3check)
        if reaction.emoji == '1️⃣':
            return 1
        elif reaction.emoji == '2️⃣':
            return 2
        elif reaction.emoji == '3️⃣':
            return 3
        elif reaction.emoji == '4️⃣':
            return 4
        else:
            return 5
    except asyncio.TimeoutError:
        await ctx.send(f"{ctx.author.mention} Timeout exceeded. Please try again.")
        return -1

# Get image result URL from the show's title
def getShowUrl(res, tag):
    searchName = res.replace(" ", "+")
    url = f'https://www.google.com/search?q={searchName}+{tag}&tbm=isch'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    image_results = soup.find_all('img')
    return image_results[1]['src']

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
async def generateplaylist(ctx, playlist_type=None, artist=None, album=None):
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

# Print user's WatchList if found, else generate entry and initialization message
@client.command(aliases=['wl'])
async def watchlist(ctx):
    # Get User ID
    userid = await getUserId(ctx)

    # Initialize entry for user
    mycursor = mydb.cursor()
    if userid == -1:
        try:
            logger.info(f'Executing query to create entry in userlist for {ctx.author}')
            mycursor.execute("INSERT INTO userlist (Username) VALUES (\'%s\')" % str(ctx.author))
        except (mysql.connector.Error, mysql.connector.Warning) as e:
            await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
            logger.warning(e)
            return None
        mydb.commit()
        await ctx.send(f'{ctx.author.mention} Initialization complete! Created an entry for you!')
        logger.info(f'Entry created for {ctx.author}')
        return
            
    # Print WatchList for user
    logger.info(f'Entry already exists for {ctx.author}, printing their watchlist')
    try:
        logger.info(f'Executing query to return entries in activelist for {ctx.author}')
        mycursor.execute("SELECT * FROM activelist WHERE UserID = \'%s\' ORDER BY TableIndex ASC" % userid)
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
    embed.set_thumbnail(url=getShowUrl(userresults[0][1], userresults[0][3]))
    embed.add_field(name='Title', value='', inline=True)
    embed.add_field(name='Tag', value='', inline=True)
    embed.add_field(name='Order', value='', inline=True)
    for x in userresults:
        embed.add_field(name='', value=x[1], inline=True)
        embed.add_field(name='', value=tag2Icons(x[3]), inline=True)
        embed.add_field(name='', value=x[4], inline=True)
    await ctx.send(embed=embed)

# Add entry to WatchList for user
@client.command(aliases=['AddShow', 'addShow', 'Addshow', 'as'])
async def addshow(ctx):
    # Get User ID
    userid = await getUserId(ctx)
    if userid == -1:
        await ctx.send(f'{ctx.author.mention} User does not exist. Try !watchlist to setup user.')
        return

    # Check if 5 entries and get index for new entry
    mycursor = mydb.cursor()
    try:
        logger.info(f'Executing query to return highest TableIndex for {ctx.author}')
        mycursor.execute("SELECT TableIndex FROM activelist WHERE UserID = %d ORDER BY TableIndex DESC LIMIT 1" % userid)
    except (mysql.connector.Error, mysql.connector.Warning) as e:
        await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
        logger.warning(e)
        return None
    index = mycursor.fetchall()
    if index == []:
        index = 1
    else:
        index = index[0][0] + 1
    if index > 5:
        await ctx.send(f"{ctx.author.mention} Maximum size of WatchList reached (5).\nPlease use !removeshow to clear an entry")
        return

    # Get show title
    showTitle = await getShowTitle(ctx)
    if showTitle == -1 or showTitle == -2: # timeout / invalid input
        return
    
    # Check if entry already exists
    if (await checkExists(ctx, userid, showTitle, 'activelist')) != -1:
        await ctx.send(f"{ctx.author.mention} {showTitle} already exists in your WatchList. Please use !removeshow to re-create this entry.")
        return

    # Get show tag
    showTag = await getShowTag(ctx)
    if showTag == -1: # timeout
        return

    # Confirm entry
    reaction = await getEntryConfirmation(ctx, showTitle, showTag, None)
    if reaction == -1: # timeout
        return

    # Verify confirmation
    if reaction.emoji == '✅':
        # Insert entry to user's activelist
        imageUrl = 'x' # add query for image later (FR)
        try:
            logger.info(f'Executing query to add {showTitle} to WatchList for {ctx.author}')
            mycursor.execute("INSERT INTO activelist (UserID, ShowName, Image, Tag, TableIndex) VALUES (%d, \'%s\', \'%s\', \'%s\', %d)" % (userid, showTitle, imageUrl, showTag, index))
            mydb.commit()
            logger.info(f'Watchlist entry added for {ctx.author}')
            await ctx.send(f"{ctx.author.mention} Added {showTitle} to your WatchList!")
        except (mysql.connector.Error, mysql.connector.Warning) as e:
            await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
            logger.warning(e)
            return None
    else:
        await ctx.send(f"{ctx.author.mention} Didn't confirm entry. Please try !addshow again to create an entry.")
    
# Remove entry from WatchList for user
@client.command(aliases=['rs', 'Removeshow', 'RemoveShow'])
async def removeshow(ctx):
    # Get User ID
    userid = await getUserId(ctx)
    if userid == -1:
        await ctx.send(f'{ctx.author.mention} User does not exist. Try !watchlist to setup user.')
        return

    # Get show title
    showTitle = await getShowTitle(ctx)
    if showTitle == -1 or showTitle == -2: # timeout or invalid input
        return
    # Remove entry from WatchList if exists
    showIndex = await checkExists(ctx, userid, showTitle, 'activelist')
    if showIndex < 0: # -1: Nothing to remove, -2: DELETE query error
        await ctx.send(f"{ctx.author.mention} This show is not in your WatchList. Nothing to remove.")
        return
    elif showIndex == None: # SELECT Query error
        return
    if (await removeEntry(ctx, userid, showTitle, 'activelist')) < 0: # Error
        return
    logger.info(f'{ctx.author}\'s WatchList entry deleted for {showTitle}')
    await ctx.send(f"{ctx.author.mention} Removed WatchList entry for {showTitle}")

    # Update indices for affected shows
    await getIndicesAndUpdate(ctx, userid, showIndex, -1, '>', None)

# Edit order of WatchList queue for user
@client.command(aliases=['eo', 'edit', 'editOrder', 'EditOrder', 'Editorder', 'editshow'])
async def editorder(ctx):
    # Get User ID
    userid = await getUserId(ctx)
    if userid == -1:
        await ctx.send(f'{ctx.author.mention} User does not exist. Try !watchlist to setup user.')
        return

    # Get show title
    showTitle = await getShowTitle(ctx)
    if showTitle == -1 or showTitle == -2: # timeout or invalid input
        return
    
    # Check if entry exists in WatchList
    showIndex = await checkExists(ctx, userid, showTitle, 'activelist')
    if showIndex < 0: # -1: Nothing to remove, -2: DELETE query error
        await ctx.send(f"{ctx.author.mention} This show is not in your WatchList. Use !addshow to add it to your WatchList.")
        return
    elif showIndex == None: # SELECT Query error
        return

    # Get current highest Order Index to verify input
    mycursor = mydb.cursor()
    try:
        logger.info(f'Executing query to get count of entries in WatchList for {ctx.author}')
        mycursor.execute("SELECT COUNT(*) FROM activelist WHERE UserID = %d" % (userid))
    except (mysql.connector.Error, mysql.connector.Warning) as e:
        await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
        logger.warning(e)
        return None
    wlCount = mycursor.fetchall()

    # Prompt user for new Index in WatchList table
    indices = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']
    msg = await ctx.send(f"{ctx.author.mention} Select the new Order value for {showTitle}: ")
    for x in range (0, wlCount[0][0]):
        await msg.add_reaction(indices[x])

    def reaction3check(reaction, user):
        name1 = str(ctx.author).split("#")[0]
        return user.name == name1 and str(reaction.emoji) in indices
    try:
        reaction, user = await client.wait_for('reaction_add', timeout=15, check=reaction3check)
        if reaction.emoji == '1️⃣':
            newIndex = 1
        elif reaction.emoji == '2️⃣':
            newIndex = 2
        elif reaction.emoji == '3️⃣':
            newIndex = 3
        elif reaction.emoji == '4️⃣':
            newIndex = 4
        elif reaction.emoji == '5️⃣':
            newIndex = 5
        else:
            newIndex = -1
    except asyncio.TimeoutError:
        await ctx.send(f"{ctx.author.mention} Timeout exceeded. Please try again.")
        newIndex = -1
    if newIndex > wlCount[0][0]: # Reacted with higher than current count
        await ctx.send(f"{ctx.author.mention} Invalid input. Please try !editorder again.")
        return
    if newIndex == showIndex: # No change
        await ctx.send(f"{ctx.author.mention} Inputted current Order value for {showTitle}. Please try !editorder again with a new Order value.")
        return
    
    # Execute changes on requested and affected entries
    if showIndex > newIndex:
        await getIndicesAndUpdate(ctx, userid, showIndex, newIndex, '<', '>=')
    else:
        await getIndicesAndUpdate(ctx, userid, showIndex, newIndex, '>', '<=')
    try:
        logger.info(f'Executing query to update {showTitle} index for {ctx.author}')
        mycursor.execute("UPDATE activelist SET TableIndex = %d WHERE UserID = %d AND ShowName = \'%s\'" % (newIndex, userid, showTitle))
    except (mysql.connector.Error, mysql.connector.Warning) as e:
        await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
        logger.warning(e)
        return None
    mydb.commit()
    await ctx.send(f"{ctx.author.mention} Updated your WatchList order!")
    await watchlist(ctx)

# Print user's WatchHistory if found, else suggest !watchlist to generate entry
@client.command(aliases=['wh','History', 'WatchHistory', 'watchhistory', 'watchHistory'])
async def history(ctx, filter=None):
    # Get User ID
    userid = await getUserId(ctx)
    if userid == -1:
        await ctx.send(f'{ctx.author.mention} User does not exist. Try !watchlist to setup user.')
        return
    
    # Apply filters
    if filter == None:
        queryFilter = 'ORDER BY Rating DESC'
    elif filter.lower() == "name":
        queryFilter = "ORDER BY ShowName ASC"
    elif filter.lower() in ['anime', 'movie', 'tv']:
        queryFilter = 'AND Tag = \'%s\' ORDER BY Rating DESC' % filter.lower()
    elif filter.lower() == 'date':
        queryFilter = 'ORDER BY Date DESC'
    else:
        queryFilter = 'ORDER BY Rating DESC'

    # Get WatchHistory results for user
    mycursor = mydb.cursor()
    logger.info(f'Printing {ctx.author}\'s WatchHistory')
    try:
        logger.info(f'Executing query to return WatchHistory entries for {ctx.author}')
        mycursor.execute("SELECT * FROM watchhistory WHERE UserID = \'%s\' %s" % (userid, queryFilter))
    except (mysql.connector.Error, mysql.connector.Warning) as e:
        await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
        logger.warning(e)
        return None
    userresults = mycursor.fetchall()
    if not len(userresults):
        await ctx.send(f"{ctx.author.mention} Current list is empty. Please use !addhistory to add to your WatchHistory")
        return
    
    # Embed response
    count = 0
    colour1 = discord.Colour.random()
    embed = discord.Embed(title="Watch History", colour=colour1)
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
    embed.set_thumbnail(url=getShowUrl(userresults[0][1], userresults[0][3]))
    embed.add_field(name='Title', value='', inline=True)
    embed.add_field(name='Rating', value='', inline=True)
    embed.add_field(name='Date', value='', inline=True)
    while count < len(userresults) and count < 7:
        print(f'Count={count}')
        embed.add_field(name='', value=userresults[count][1], inline=True)
        embed.add_field(name='', value=userresults[count][2], inline=True)
        embed.add_field(name='', value=userresults[count][4], inline=True)
        count += 1
    await ctx.send(embed=embed)
    # New embeds if WatchHistory contains > 7
    while count < len(userresults):
        embed2 = discord.Embed(title="", colour=colour1)
        innercount = 0
        while ((count + innercount) < len(userresults)) and ((innercount + 1) % 8 != 0):
            embed2.add_field(name='', value=userresults[(count + innercount)][1], inline=True)
            embed2.add_field(name='', value=userresults[(count + innercount)][2], inline=True)
            embed2.add_field(name='', value=userresults[(count + innercount)][4], inline=True)
            innercount += 1
        count += innercount
        await ctx.send(embed=embed2)
    

# Add entry for WatchHistory after completing a show
@client.command(aliases=['ah','Addhistory', 'AddHistory'])
async def addhistory(ctx):
    # Get User ID
    userid = await getUserId(ctx)
    if userid == -1:
        await ctx.send(f'{ctx.author.mention} User does not exist. Try !watchlist to setup user.')
        return

    # Get show title
    showTitle = await getShowTitle(ctx)
    if showTitle == -1 or showTitle == -2: # timeout or invalid input
        return
    
    # Check if entry already exists in WatchHistory
    if (await checkExists(ctx, userid, showTitle, 'watchhistory')) != -1:
        await ctx.send(f"{ctx.author.mention} {showTitle} already exists in your WatchHistory. Please use !removehistory to re-create this entry.")
        return

    # Get show tag
    showTag = await getShowTag(ctx)
    if showTag == -1: # timeout
        return

    # Get show rating
    rating = await getShowRating(ctx, showTitle)
    if rating == -1: # timeout
        return
    
     # Prompt user to confirm details
    reaction = await getEntryConfirmation(ctx, showTitle, showTag, rating)
    if reaction == -1: # timeout
        return
    
    # Verify confirmation
    if reaction.emoji == '✅':
        # Add WatchHistory entry
        mycursor = mydb.cursor()
        try:
            today = date.today().strftime("%B %d %y")
            logger.info(f'Executing query to add {showTitle} in WatchHistory for {ctx.author}')
            mycursor.execute("INSERT INTO watchhistory (UserID, ShowName, Rating, Tag, CompletedDate) VALUES (%d, \'%s\', %d, \'%s', \'%s')" % (userid, showTitle, rating, showTag, today))
            mydb.commit()
            logger.info(f'WatchHistory entry added for {ctx.author}')
            response = f"{ctx.author.mention} Added {showTitle} to your WatchHistory!"
        except (mysql.connector.Error, mysql.connector.Warning) as e:
            await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
            logger.warning(e)
            return None
    else:
        await ctx.send(f"{ctx.author.mention} Didn't confirm entry. Please try !addhistory again to create an entry.")
        return
    
    # Remove entry from WatchList if exists
    showIndex = await checkExists(ctx, userid, showTitle, 'activelist')
    if showIndex < 0: # -1: Nothing to remove, -2: DELETE query error
        await ctx.send(response)
        return
    elif showIndex == None: # SELECT query error
        return
    if (await removeEntry(ctx, userid, showTitle, 'activelist')) < 0: # Error
        return
    response += f"\nSince you finished it, also removed {showTitle} from your WatchList!"
    logger.info(f'{ctx.author}\'s Watchlist entry deleted for {showTitle}')
    
    # Update indices for affected shows
    await getIndicesAndUpdate(ctx, userid, showIndex, -1, '>', None)

    await ctx.send(response)
    
# Remove entry from WatchHistory for user
@client.command(aliases=['rh', 'Removehistory', 'RemoveHistory', 'removeHistory'])
async def removehistory(ctx):
    # Get User ID
    userid = await getUserId(ctx)
    if userid == -1:
        await ctx.send(f'{ctx.author.mention} User does not exist. Try !watchlist to setup user.')
        return

    # Get show title
    showTitle = await getShowTitle(ctx)
    if showTitle == -1 or showTitle == -2: # timeout or invalid input
        return

    # Remove entry from WatchHistory if exists
    showIndex = await checkExists(ctx, userid, showTitle, 'watchhistory')
    if showIndex == -1 or showIndex == -2: # -1: Nothing to remove, -2: DELETE query error
        await ctx.send(f"{ctx.author.mention} This show is not in your WatchHistory. Nothing to remove.")
        return
    elif showIndex == None: # SELECT query error
        return
    if (await removeEntry(ctx, userid, showTitle, 'watchhistory')) < 0: # Error
        return
    logger.info(f'{ctx.author}\'s WatchHistory entry deleted for {showTitle}')
    await ctx.send(f"{ctx.author.mention} Removed WatchHistory entry for {showTitle}")

# Edit the rating for an entry in WatchHistory
@client.command(aliases=['er','eh', 'EditRating', 'editRating', 'Editrating', 'edithistory'])
async def editrating(ctx):
    # Get User ID
    userid = await getUserId(ctx)
    if userid == -1:
        await ctx.send(f'{ctx.author.mention} User does not exist. Try !watchlist to setup user.')
        return

    # Get show title
    showTitle = await getShowTitle(ctx)
    if showTitle == -1 or showTitle == -2: # timeout or invalid input
        return
    
    # Confirm if entry exists in WatchHistory
    showIndex = await checkExists(ctx, userid, showTitle, 'watchhistory')
    if not isinstance(showIndex, str): # -1: Nothing to remove, -2: DELETE query error
        await ctx.send(f"{ctx.author.mention} This show is not in your WatchHistory. Use !addhistory to add it to your WatchHistory.")
        return
    elif showIndex == None: # SELECT Query error
        return
    
    # Get show rating
    rating = await getShowRating(ctx, showTitle)
    if rating == -1: # timeout
        return
    
    # Get current show's rating
    mycursor = mydb.cursor()
    try:
        logger.info(f'Executing query to return {showTitle} current rating for {ctx.author}')
        mycursor.execute("SELECT * FROM watchhistory WHERE UserID = \'%s\' AND ShowName = \'%s\'" % (userid, showTitle))
    except (mysql.connector.Error, mysql.connector.Warning) as e:
        await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
        logger.warning(e)
        return
    userresults = mycursor.fetchall()
    oldrating = userresults[0][2]
    if oldrating == rating: # No change
        await ctx.send(f"{ctx.author.mention} Inputted current rating for {showTitle}. Please try !editrating again with a different rating.")
        return
    
     # Prompt user to confirm details
    msg = await ctx.send(f"{ctx.author.mention} Is this correct (Select ✅ or ❌):\nTitle: {showTitle} | Rating: {oldrating} -> {rating}")
    await msg.add_reaction('✅')  # Acknowledge entry
    await msg.add_reaction('❌')  # Decline entry

    def reaction2check(reaction, user):
        name1 = str(ctx.author).split("#")[0]
        return  user.name == name1 and str(reaction.emoji) in ['✅','❌']
    try:
        reaction, user = await client.wait_for('reaction_add', timeout=15, check=reaction2check)
    except asyncio.TimeoutError:
        await ctx.send(f"{ctx.author.mention} Timeout exceeded. Please try again.")
        return -1
    
    # Verify confirmation
    if reaction.emoji == '✅':
        # Edit WatchHistory entry
        mycursor = mydb.cursor()
        try:
            logger.info(f'Executing query to edit {showTitle} in WatchHistory for {ctx.author}')
            mycursor.execute("UPDATE watchhistory SET Rating = %d WHERE UserID = %d AND ShowName = \'%s\'" % (rating, userid, showTitle))
            mydb.commit()
            logger.info(f'WatchHistory entry for {showTitle} updated for {ctx.author}')
        except (mysql.connector.Error, mysql.connector.Warning) as e:
            await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
            logger.warning(e)
            return None
        await ctx.send(f"{ctx.author.mention} WatchHistory entry for {showTitle} updated!")
    else:
        await ctx.send(f"{ctx.author.mention} Didn't confirm entry. Please try !addhistory again to create an entry.")
        return

# Clear all WatchHistory for user
@client.command(aliases=['ch', 'Clearhistory', 'ClearHistory', 'clearHistory'])
async def clearhistory(ctx):
    # Get User ID
    userid = await getUserId(ctx)
    if userid == -1:
        await ctx.send(f'{ctx.author.mention} User does not exist. Try !watchlist to setup user.')
        return
    
    # Request user to confirm deletion
    msg = await ctx.send(f"{ctx.author.mention} Please confirm you would like clear all entries in your WatchHistory (Select ✅ or ❌)")
    await msg.add_reaction('✅')  # Acknowledge entry
    await msg.add_reaction('❌')  # Decline entry

    def reaction2check(reaction, user):
        name1 = str(ctx.author).split("#")[0]
        return  user.name == name1 and str(reaction.emoji) in ['✅','❌']
    try:
        reaction, user = await client.wait_for('reaction_add', timeout=15, check=reaction2check)
    except asyncio.TimeoutError:
        await ctx.send(f"{ctx.author.mention} Timeout exceeded. Please try again.")
        return -1
    
    # Verify confirmation
    if reaction.emoji == '✅':
        # Get current WatchHistory entries for user
        mycursor = mydb.cursor()
        try:
            logger.info(f'Executing query to return WatchHistory entries for {ctx.author}')
            mycursor.execute("SELECT * FROM watchhistory WHERE UserID = \'%s\'" % userid)
        except (mysql.connector.Error, mysql.connector.Warning) as e:
            await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
            logger.warning(e)
            return
        userresults = mycursor.fetchall()
        if not len(userresults): # Empty WatchHistory list
            await ctx.send(f"{ctx.author.mention} Current list is empty. Please use !addhistory to add to your WatchHistory.")
            return
        
        # Remove all entries from WatchHistory table for user
        for x in userresults:
            if (await removeEntry(ctx, userid, x[1], 'watchhistory')) < 0: # Error
                return
        await ctx.send(f"{ctx.author.mention} Deleted all entries in your WatchHistory!")
    else:
        await ctx.send(f"{ctx.author.mention} Didn't confirm deletion. Please try !clearhistory again to delete all WatchHistory entries.")
                
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
@commands.check_any(commands.has_role(ADMIN), commands.has_role(MOD))
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

# Admin and mod only, see Dollar's current logs
@client.command()
@commands.check_any(commands.has_role(ADMIN), commands.has_role(MOD))
async def logs(ctx):
    logger.info('START LOG DOWNLOAD')

    log_file_name = 'discord.log'
    log_file_path = os.path.join(os.getcwd(), log_file_name)

    if not os.path.isfile(log_file_path):
        await ctx.send(f"Log file '{log_file_name}' not found.")
        return

    channel = ctx.channel
    with open(log_file_path, 'rb') as file:
        log_file = discord.File(file, filename=log_file_name)
        await channel.send(file=log_file)

    logger.info('FINISH LOG DOWNLOAD')

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