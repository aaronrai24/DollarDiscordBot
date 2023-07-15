# This python file Runs Dollar, logger: dollar
# All client.events should be written here

from functions.common.libraries import(
    discord, os, wavelink, logging, pandas, threading, 
    asyncio, commands, tasks, load_dotenv, CREATEDCHANNELS
)
from functions.common.generalFunctions import(
    setup_logger, send_patch_notes, connect_to_database, 
    validate_connection, idle_checker
)

# load environment
load_dotenv()

# Get all commands from Cogs
exts: list = ['functions.diagnostic.debugging', 'functions.game.gameCommands', 'functions.music.musicCommands',
              'functions.admin.admin', 'functions.watchlist.myWatchList']

# Create Unfiltered Bot to accept commands from other bots
class UnfilteredBot(commands.Bot):
    async def process_commands(self, message):
        ctx = await self.get_context(message)
        await self.invoke(ctx)

    # Connect to MySQL database
    mydb = connect_to_database()

    # Send patch notes, load cogs, and sync app commands
    async def setup_hook(self):
        await send_patch_notes(self)
        for cog in exts:
            try:
                logger.debug(f"Loading ext {cog}")
                await self.load_extension(cog)
                logger.debug(f"Loaded ext {cog}")
            except Exception as e:
                exc = "{}: {}".format(type(e).__name__, e)
                logger.error("Failed to load ext {}\n{}".format(cog, exc))
        logger.info('Loaded Extensions!')
        try:
            synced = await self.tree.sync()
            logger.debug(f'Synced {len(synced)} command(s)')
        except Exception as e:
            logger.error(f'{e}')
        logger.info('Synced commands!')
    
    async def close(self):
        await super().close()
        await self.session.close()

client = UnfilteredBot(command_prefix='!', intents=discord.Intents.all(), help_command=None)

# Setup Logging
logger = setup_logger('dollar')
logging.getLogger('discord.gateway').setLevel(logging.WARNING)

# Get Discord, GitHub tokens from ENV
DISCORD_TOKEN = os.getenv('TOKEN')

@client.event
async def on_ready():
    client.loop.create_task(connect_nodes())
    validate_db.start()

async def connect_nodes():
    await client.wait_until_ready()
    await wavelink.NodePool.create_node(
        bot=client,
        host='127.0.0.1',
        port=2333,
        password='discordTest123'
    )

#------------------------------------------------------------------------------------------------
# Client Events

# Connected to Wavelink Node
@client.event
async def on_wavelink_node_ready(node: wavelink.Node):
    logger.info(f'Node: <{node.identifier}> is ready')
    logger.info(f'Logged in as {node.bot.user} ({node.bot.user.id})')
    await client.change_presence(activity=discord.Game(name=' Music! | !help'))

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
        await channel.send(f"The event, {after.name} has started! {mention_string}, you can now join the voice channel.")
        await channel.set_permissions(channel.guild.default_role, connect=False)
    elif start == 'EventStatus.active' and current == 'EventStatus.completed':
        #Event has completed
        logger.info(f'Event [{after.name}] in {after.guild} has completed')
        await channel.edit(sync_permissions=True)
        await channel.set_permissions(channel.guild.default_role, connect=True)
        logger.info(f'Reset channel permissions and granted access to {channel} for all users')

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
        await message.author.send('If you still have questions, go to a discord I am in and use /ticket to submit a request and interact with my devs.')

    if channel.startswith('commands') or channel.startswith('test'):
        if msg.startswith('!'):
            logger.info(f'Bot command entered. Command: {msg} | Author: {author}')
            await client.process_commands(message)
        elif str(message.attachments) == "[]":
            await client.process_commands(message)
            logger.info(f'User message entered. Message: {msg} | Author: {author}')
        else:
            if message.attachments and message.attachments[0].filename.endswith(".csv"):
                try:
                    await message.attachments[0].save(fp='ex.csv')
                    pandas.read_csv('ex.csv')
                    await message.channel.send('File downloaded. Use !load to load songs into queue.')
                    logger.info(f'CSV successfully downloaded, author: {author}')
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
    channel = discord.utils.get(guild.channels, name='JOIN HERE💎')
    comchannel = discord.utils.get(guild.channels, name='commands')
    if channel is not None:
        category = channel.category_id    
    if str(member) == 'DollarTest#1851':
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

# Periodically validate the connection
@tasks.loop(seconds=60)
async def validate_db():
    await validate_connection(UnfilteredBot.mydb)

# Error Handling
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send('Missing required role to use this command.')
        logger.error('User has insufficient role')
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send('Command not found.')
        logger.error('User tried to use a command that does not exist')
    elif isinstance(error, commands.BadArgument):
        await ctx.send('Invalid argument.')
        logger.error('User provided an invalid argument')
    elif isinstance(error, commands.CheckFailure):
        await ctx.send('Insufficient Permissions to use this command.')
        logger.error('User has insufficient permissions')

# Run bot
client.run(DISCORD_TOKEN)