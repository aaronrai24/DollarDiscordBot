"""
DESCRIPTION: Main class that creates UnfilteredBot
All client events should be written here.
"""
from functions import GeneralFunctions
from functions import AutoChannelCreation
from functions import Queries
from functions import PushNotifications
import functions.common.libraries as lib

lib.load_dotenv()

exts: list = [
		"functions.diagnostic.debugging", "functions.game.gamecommands", 
		"functions.music.musiccommands", "functions.admin.admin",
		"functions.queries.queries", "functions.diagnostic.settings",
		"functions.notifications.push_notifications"
	]

class UnfilteredBot(lib.commands.Bot):
	"""
	DESCRIPTION: Creates UnfilteredBot, loads exts, connects to db
	PARAMETERS: commands.Bot - Discord Commands
	"""
	async def process_commands(self, message):
		ctx = await self.get_context(message)
		await self.invoke(ctx)

	async def setup_hook(self):
		"""
		DESCRIPTION: Send patch notes, load cogs, and sync app commands
		"""
		logger.info("=== Starting Dollar ===")
		for cog in exts:
			try:
				logger.debug(f"Loading ext {cog}")
				await self.load_extension(cog)
				logger.debug(f"Loaded ext {cog}")
			except Exception as e:
				exc = f"{type(e).__name__}: {e}"
				logger.error(f"Failed to load ext {cog}\n{exc}")
		logger.info("Loaded Extensions!")
		try:
			logger.debug("Syncing commands...")
			synced = await self.tree.sync()
			logger.debug(f"Synced {len(synced)} command(s)")
		except Exception as e:
			logger.error(f"{e}")
		logger.info("Synced commands!")

	async def close(self):
		logger.info("=== Closing Dollar ===")
		await super().close()
		await self.session.close()

	mydb = GeneralFunctions.connect_to_database()

client = UnfilteredBot(command_prefix="!", intents=lib.discord.Intents.all(), help_command=None)

logger = GeneralFunctions.setup_logger("dollar")

DISCORD_TOKEN = lib.os.getenv("TOKEN")
LAVALINK_TOKEN = lib.os.getenv("LAVALINK_TOKEN")

#NOTE: Declarations
push_notifications = PushNotifications(UnfilteredBot)
queries = Queries(UnfilteredBot)

async def connect_nodes():
	"""
	DESCRIPTION: Connect to Wavelink Node
	"""
	await client.wait_until_ready()
	#NOTE: Connect to Wavelink
	nodes = [lib.wavelink.Node(uri="http://lavalink:2333", password=LAVALINK_TOKEN, identifier="MAIN", 
							retries=None, heartbeat=60, inactive_player_timeout=600)]
	await lib.wavelink.Pool.connect(nodes=nodes, client=client, cache_capacity=100)
	logger.info(f"Node: <{nodes}> is ready")
	await client.change_presence(activity=lib.discord.Game(name=" Music! | !help"))
	logger.info("=== Dollar is ready ===")

#------------------------------------------------------------------------------------------------
# Tasks
#------------------------------------------------------------------------------------------------
@lib.tasks.loop(seconds=60)
async def validate_db():
	"""
	DESCRIPTION: Periodically validate the connection
	"""
	await GeneralFunctions.validate_connection(UnfilteredBot.mydb)

#------------------------------------------------------------------------------------------------
# Client Events

@client.event
async def on_ready():
	"""
	DESCRIPTION: On Ready Event
	"""
	client.loop.create_task(connect_nodes())
	validate_db.start()
	await GeneralFunctions.send_patch_notes(client)
	for guild in client.guilds:
		lib.guild_text_channels[str(guild)] = queries.get_guilds_preferred_text_channel(str(guild))
		lib.guild_voice_channels[str(guild)] = queries.get_guilds_preferred_voice_channel(str(guild))
	logger.info(f"Cached text and voice channels, text: {lib.guild_text_channels}, voice: {lib.guild_voice_channels}")

# Event was created
@client.event
async def on_scheduled_event_create(event):
	"""
	DESCRIPTION: Event was created
	PARAMETERS: event - Event
	"""
	logger.info(f"The event [{event.name}] in was created in {event.guild}")

@client.event
async def on_scheduled_event_delete(event):
	"""
	DESCRIPTION: Event was cancelled
	PARAMETERS: event - Event
	"""
	logger.info(f"The event [{event.name}] in was cancelled in {event.guild}")

@client.event
async def on_scheduled_event_update(before, after):
	"""
	DESCRIPTION: Event was modified(changes made or status changed)
	PARAMETERS: before - Event
				after - Event
	"""
	start = str(before.status)
	current = str(after.status)
	users = after.users()
	channel = after.channel

	if start == "EventStatus.scheduled" and current == "EventStatus.active":
		#NOTE: Event has started
		logger.info(f"Event [{after.name}] in {after.guild} has started")
		mentioned_users = []
		async for user in users:
			await channel.set_permissions(user, connect=True)
			mentioned_users.append(user.mention)
			logger.info(f"{user} is interested, allowing them to connect to {channel}")
		mention_string = " ".join(mentioned_users)
		await channel.send(f'''The event, {after.name} has started!
						   {mention_string}, you can now join the voice channel.''')
		await channel.set_permissions(channel.guild.default_role, connect=False)
	elif start == "EventStatus.active" and current == "EventStatus.completed":
		#NOTE: Event has completed
		logger.info(f"Event [{after.name}] in {after.guild} has completed")
		await channel.edit(sync_permissions=True)
		await channel.set_permissions(channel.guild.default_role, connect=True)
		logger.info(f"Reset channel permissions and granted access to {channel} for all users")

@client.event
async def on_scheduled_event_user_add(event, user):
	"""
	DESCRIPTION: Add user to event channel
	PARAMETERS: event - Event
				user - Discord User
	"""
	logger.info(f"{user} is interested in [{event.name}] in {event.guild}")

@client.event
async def on_scheduled_event_user_remove(event, user):
	"""
	DESCRIPTION: Remove user from event channel
	PARAMETERS: event - Event
				user - Discord User
	"""
	logger.info(f"{user} is now uninterested in the event [{event.name}] in {event.guild}")

@client.event
async def on_guild_join(guild):
	"""
	DESCRIPTION: Create voice channel "JOIN HERE" and text channel "commands"
	PARAMETERS: guild - Discord Guild
	"""
	logger.info(f"Joined {guild.name} ({guild.id})")
	user_exists = queries.check_if_user_exists(str(guild.owner.name))
	if user_exists is None:
		queries.add_user_to_db(guild.owner.id, guild.owner.name)
	queries.add_guild_to_db(guild.name, guild.owner.name)
	await guild.owner.send("Thanks for adding me to your server! Please use `/dollarsettings`, to configure Dollar to your discord.")
	await guild.owner.send("Additionally use `/userinformation` to update your user information(not required).")

@client.event
async def on_guild_remove(guild):
	"""
	DESCRIPTION: Delete voice channel "JOIN HERE" and text channel "commands"
	PARAMETERS: guild - Discord Guild
	"""
	logger.info(f"Left guild: {guild.name} ({guild.id})")
	queries.remove_guild_from_db(guild.name)
	app_info = await client.application_info()
	owner = app_info.owner
	msg = f"""Damn, I got kicked from {guild.name}, was I not good enough? 😢 
		If im missing features please alert my devs using `/featurerequest`"""
	await owner.send(msg)

@client.event
async def on_member_join(member):
	"""
	DESCRIPTION: Send user a message when the join a server to the system channel
	PARAMETERS: member - Discord Member
	"""
	guild = member.guild
	channel = member.guild.system_channel
	user_id = member.id
	if channel is not None:
		try:
			await channel.send(f"Welcome {member.mention} to {guild.name}!")
			queries.add_user_to_db(user_id, str(member))
			logger.info(f"Sent welcome message to {member} in {guild}")
		except lib.discord.Forbidden:
			logger.warning(f"Could not send message to {channel.name} in {guild.name}. Missing permissions.")
		except lib.discord.HTTPException:
			logger.error(f"Could not send message to {channel.name} in {guild.name}. HTTP exception occurred.")

@client.event
async def on_member_remove(member):
	"""
	DESCRIPTION: Send user a message when they leave a server to the system channel
	PARAMETERS: member - Discord Member
	"""
	if member == client.user:
		return

	guild = member.guild
	channel = member.guild.system_channel
	if channel is not None:
		try:
			await channel.send(f"{member.mention} has left {guild.name}. Bye Felicia")
			queries.remove_user_from_db(str(member))
			logger.info(f"Sent leave message to {member} in {guild}")
		except lib.discord.Forbidden:
			logger.warning(f"Could not send message to {channel.name} in {guild.name}. Missing permissions.")
		except lib.discord.HTTPException:
			logger.error(f"Could not send message to {channel.name} in {guild.name}. HTTP exception occurred.")

@client.event
async def on_raw_reaction_add(payload):
	"""
	DESCRIPTION: Scan for reactions to messages
	PARAMETERS: payload - Discord Raw Reaction
	"""
	user_name = str(payload.member)
	user_id = payload.user_id
	reaction = payload.emoji.name
	channel_id = payload.channel_id
	message_id = payload.message_id
	message = await client.get_channel(channel_id).fetch_message(message_id)
	game_name = None
	if message.embeds:
		game_name = str(message.embeds[0].author.name)

	#NOTE: Add subscription to game
	if reaction == "🔔" and int(channel_id) == int(lib.PATCHES_CHANNEL):
		logger.debug(f"{user_name} reacted with {reaction} to {game_name}")
		game_result = queries.check_if_game_exists(game_name)

		if game_result is None:
			queries.add_game_to_db(game_name)
		user_result = queries.check_if_user_exists(user_name)

		if user_result is None:
			queries.add_user_to_db(user_id, user_name)
		queries.add_game_subscription(user_name, game_name)
		await payload.member.send(f"Subscribed to {game_name} notifications!")

	#NOTE: Remove subscription to game
	elif reaction == "🔕" and int(channel_id) == int(lib.PATCHES_CHANNEL):
		logger.info(f"{user_name} reacted with {reaction} to {game_name}")
		game_result = queries.check_if_game_exists(game_name)
		user_result = queries.check_if_user_exists(user_name)

		if game_result and user_result:
			queries.remove_game_subscription(user_name, game_name)
			await payload.member.send(f"Unsubscribed from {game_name} notifications!")
		else:
			await payload.member.send("An error occurred while unsubscribing from notifications. Please report this bug using /reportbug")
			logger.error(f"User {user_name} or game {game_name} does not exist in database")
	
@client.event
async def on_message(message):
	"""
	DESCRIPTION: Scan messages to ensure message was sent in #commands chat
	PARAMETERS: message - Discord Message
	"""
	msg = message.content
	channel = str(message.channel)
	author = message.author
	guild = message.guild
	guild_text_channel = lib.guild_text_channels.get(str(guild))

	#NOTE: DMs to Dollar
	if isinstance(message.channel, lib.discord.channel.DMChannel) and message.author != client.user:
		logger.info(f"{author} sent a DM to Dollar")
		msg = '''Checkout this readme:
		(https://github.com/aaronrai24/DollarDiscordBot/blob/main/README.md)'''
		await GeneralFunctions.send_embed("Welcome to Dollar", "dollar.png", msg, message.author)

	#NOTE: Game update notifications in #patches in mfDiscord 
	if str(message.channel.id) == str(lib.PATCHES_CHANNEL):
		try:
			embed_title = str(message.embeds[0].author.name)
			logger.info(f"Game update detected: {embed_title}, channel id: {message.channel.id}, message id: {message.id}")
			await push_notifications.notify_game_update(embed_title, message)
		except IndexError:
			pass

	#NOTE: Bot commands
	if channel in (guild_text_channel, "dollar-dev", "commands"):
		if msg.startswith("!"):
			logger.info(f"Bot command entered. Command: {msg} | Author: {author} Guild: {guild}")
			await client.process_commands(message)
	elif msg.startswith("!clear"):
		await client.process_commands(message)
		logger.info(f"{author} used !clear in Guild: {guild}")
	elif msg.startswith("!"):
		logger.info(f"Command entered in wrong channel, deleting: {msg} in Guild: {guild}")
		await author.send(f"Please use the {guild_text_channel} channel to enter commands in {guild}, thanks!")
		await message.delete(delay=1)

@client.event
async def on_voice_state_update(member, before, after):
	"""
	DESCRIPTION: Handles voice state update
	PARAMETERS: member - Discord Member
				before - Discord VoiceState
				after - Discord VoiceState
	"""
	guild = member.guild
	join_channel = AutoChannelCreation.get_join_channel(guild)
	
	if not join_channel:
		return
	
	if before.channel is None and after.channel:
		#NOTE: User joined channel
		logger.info(f"{member} joined {after.channel} in {guild}")

	if before.channel != after.channel:
		#NOTE: User moved channels
		if after.channel == join_channel:
			try:
				logger.debug("Checking for hanging channels...")
				await AutoChannelCreation.handle_channel_leave(before.channel)
			except AttributeError:
				pass
			finally:
				await AutoChannelCreation.create_personal_channel(member, join_channel)
		elif before.channel:
			logger.info(f"{member} left {before.channel} in {guild}")
			await AutoChannelCreation.handle_channel_leave(before.channel)

@client.event
async def on_command_error(ctx, error):
	"""
	DESCRIPTION: Error handling for commands
	PARAMETERS: ctx - Discord Context
				error - Exception
	"""
	error_type = type(error)
	
	if error_type in lib.ERROR_MAPPING:
		title, log_message = lib.ERROR_MAPPING[error_type]
		await GeneralFunctions.send_embed_error(title, str(error), ctx)
		logger.error(log_message.format(ctx=ctx))
	else:
		msg = "An unexpected error occurred while processing your command. Please use /reportbug."
		await GeneralFunctions.send_embed_error("Unexpected Error", msg, ctx)
		logger.exception("Unexpected error occurred", exc_info=error)

client.run(DISCORD_TOKEN)
