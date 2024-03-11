"""
DESCRIPTION: Main class that creates UnfilteredBot
All client events should be written here.
"""
import functions.common.libraries as lib
from functions.common.generalfunctions import GeneralFunctions
from functions.queries.queries import Queries
from functions.notifications.push_notifications import PushNotifications

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

	mydb = GeneralFunctions.connect_to_database()

	async def setup_hook(self):
		"""
		DESCRIPTION: Send patch notes, load cogs, and sync app commands
		"""
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
			synced = await self.tree.sync()
			logger.debug(f"Synced {len(synced)} command(s)")
		except Exception as e:
			logger.error(f"{e}")
		logger.info("Synced commands!")

	async def close(self):
		await super().close()
		await self.session.close()

client = UnfilteredBot(command_prefix="!", intents=lib.discord.Intents.all(), help_command=None)

logger = GeneralFunctions.setup_logger("dollar")

DISCORD_TOKEN = lib.os.getenv("TOKEN")

#NOTE: Declarations
push_notifications = PushNotifications(UnfilteredBot)
queries = Queries(UnfilteredBot)

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

async def connect_nodes():
	"""
	DESCRIPTION: Connect to Wavelink Node
	"""
	await client.wait_until_ready()
	#NOTE: Connect to Wavelink
	nodes = [wavelink.Node(uri="http://localhost:2333", password="discordTest123")]
	await wavelink.Pool.connect(nodes=nodes, client=client, cache_capacity=100)
	logger.info(f"Node: <{nodes}> is ready")
	await client.change_presence(activity=discord.Game(name=" Music! | !help"))

#------------------------------------------------------------------------------------------------
# Client Events

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
		#Event has started
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
		#Event has completed
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
	logger.debug(f"Reaction added: {payload}")
	user_name = str(payload.member)
	user_id = payload.user_id
	reaction = payload.emoji.name
	channel_id = payload.channel_id
	message_id = payload.message_id
	message = await client.get_channel(channel_id).fetch_message(message_id)
	if message.embeds:
		game_name = str(message.embeds[0].title)
	#NOTE: Add subscription to game
	if reaction == "🔔" and int(channel_id) == int(lib.PATCHES_CHANNEL):
		logger.info(f"{user_name} reacted with {reaction} to {game_name}")
		game_result = queries.check_if_game_exists(game_name)
		logger.info(f"Game result: {game_result}")
		if game_result is None:
			queries.add_game_to_db(game_name)
		user_result = queries.check_if_user_exists(user_name)
		logger.info(f"User result: {user_result}")
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

	if isinstance(message.channel, lib.discord.channel.DMChannel) and message.author != client.user:
		logger.info(f"{author} sent a DM to Dollar")
		msg = '''Checkout this readme:
		(https://github.com/aaronrai24/DollarDiscordBot/blob/main/README.md)'''
		await GeneralFunctions.send_embed("Welcome to Dollar", "dollar.png", msg, message.author)

	if str(message.channel.id) == str(lib.PATCHES_CHANNEL):
		try:
			embed_title = message.embeds[0].title
			logger.info(f"Game update detected: {embed_title}, channel id: {message.channel.id}, message id: {message.id}")
			await push_notifications.notify_game_update(embed_title, message)
		except IndexError:
			pass

	if channel in (guild_text_channel, "test"):
		if msg.startswith("!"):
			logger.info(f"Bot command entered. Command: {msg} | Author: {author}")
			await client.process_commands(message)
		elif str(message.attachments) == "[]":
			await client.process_commands(message)
			logger.info(f"User message entered. Message: {msg} | Author: {author}")
		else:
			if message.attachments and message.attachments[0].filename.endswith(".csv"):
				try:
					await message.attachments[0].save(fp="ex.csv")
					lib.pandas.read_csv("ex.csv")
					await message.channel.send("File downloaded. Use !load to load songs into queue.")
					logger.info(f"CSV successfully downloaded, author: {author}")
				except lib.pandas.errors.ParserError:
					logger.warning("File is not a valid CSV")
					await message.channel.send("File is not a valid CSV.")
				except Exception as e:
					logger.error(f"Error occurred while downloading file: {e}")
					await message.channel.send(f"Error occurred while downloading file: {e}")
	elif msg.startswith("!clear"):
		await client.process_commands(message)
		logger.info(f"{author} used !clear")
	elif msg.startswith("!"):
		logger.info(f"Command entered in wrong channel, deleting: {msg}")
		await message.delete(delay=1)

@client.event
async def on_voice_state_update(member, before, after):
	"""
	DESCRIPTION: Scan when users join/leave/move voice channels
	PARAMETERS: member - Discord Member
				before - Discord Voice State
				after - Discord Voice State
	"""
	ctxbefore = before.channel
	ctxafter = after.channel
	guild = client.get_guild(member.guild.id)
	user = str(member.display_name)
	voice_channel = lib.guild_voice_channels.get(str(guild))
	text_channel = lib.guild_text_channels.get(str(guild))
	channel = lib.discord.utils.get(guild.channels, name=voice_channel)
	comchannel = lib.discord.utils.get(guild.channels, name=text_channel)
	if channel is not None:
		category = channel.category_id
	if str(member) == "DollarTest#1851":
		dollar = member.id
	else:
		dollar = 0
	
	#NOTE: If they join JOIN HERE💎, create a new channel
	if ctxbefore is None and ctxafter is not None:
		#NOTE Somebody joined a voice channel
		logger.info(f"{member} joined {ctxafter}")
		if str(ctxafter) == str(channel):
			await channel.set_permissions(guild.default_role, connect=False)
			logger.info(f"Locked {str(channel)}, beginning channel creation in {str(guild)}")
			category_channel = lib.discord.utils.get(guild.categories, id=category)
			v_channel = await guild.create_voice_channel(f"{user}'s Channel", category=category_channel, position=0)
			await v_channel.set_permissions(member, manage_channels=True)
			lib.created_channels.append(v_channel.id)
			logger.info(f"Successfully created {v_channel} in {str(guild)}")
			await member.move_to(v_channel)
			while member.voice.channel != v_channel:
				await lib.asyncio.sleep(1)
			await channel.set_permissions(guild.default_role, connect=True)
			logger.info(f"Unlocked {str(channel)}, channel creation finished in {str(guild)}")
	elif ctxbefore is not None and ctxafter is None:
		#NOTE: Somebody left a voice channel
		logger.info(f"{member} left {ctxbefore}")
		for channel_id in lib.created_channels:
			if ctxbefore.id == channel_id:
				v_channel = lib.discord.utils.get(guild.channels, id=ctxbefore.id)
				if len(v_channel.members) == 0:
					await v_channel.delete()
					logger.info(f"{v_channel} empty, deleted channel in {str(guild)}")
					# pylint: disable=modified-iterating-list
					lib.created_channels.remove(ctxbefore.id)
	elif str(ctxbefore) != str(ctxafter):
		#NOTE: Somebody was already connected to a vc but moved to a different channel
		logger.info(f"{member} moved from {ctxbefore} to {ctxafter}")

		#NOTE: Prioritize removing empty channels
		for channel_id in lib.created_channels:
			if ctxbefore.id == channel_id:
				v_channel = lib.discord.utils.get(guild.channels, id=ctxbefore.id)
				if len(v_channel.members) == 0:
					await v_channel.delete()
					logger.info(f"{v_channel} empty, deleted channel in {str(guild)}")
					# pylint: disable=modified-iterating-list
					lib.created_channels.remove(ctxbefore.id)

		#NOTE: If they move to JOIN HERE💎 go through channel creation
		if str(ctxafter) == str(channel):
			await channel.set_permissions(guild.default_role, connect=False)
			logger.info(f"Locked {str(channel)}, beginning channel creation in {str(guild)}")
			category_channel = lib.discord.utils.get(guild.categories, id=category)
			v_channel = await guild.create_voice_channel(f"{user}'s Channel", category=category_channel, position=0)
			await v_channel.set_permissions(member, manage_channels=True)
			lib.created_channels.append(v_channel.id)
			logger.info(f"Successfully created {v_channel} in {str(guild)}")
			await member.move_to(v_channel)
			while member.voice.channel != v_channel:
				await lib.asyncio.sleep(1)
			await channel.set_permissions(guild.default_role, connect=True)
			logger.info(f"Unlocked {str(channel)}, channel creation finished in {str(guild)}")

	#NOTE: Inactivity Checker, create a new thread to run idle_checker
	# pylint: disable=unused-variable
	vc_lock = lib.threading.Lock()
	# pylint: disable=unused-variable
	comchannel_lock = lib.threading.Lock()
	
	if member.id != dollar:
		return

	elif ctxbefore is None:
		vc = after.channel.guild.voice_client
		lib.asyncio.create_task(GeneralFunctions.idle_checker(vc, comchannel, guild))

@client.event
async def on_command_error(ctx, error):
	"""
	DESCRIPTION: Error Handling
	PARAMETERS: ctx - Discord Context
				error - Error
	"""
	if isinstance(error, lib.commands.MissingRole):
		await GeneralFunctions.send_embed_error("Missing Required Role", error, ctx)
		logger.error("User has insufficient role")
	elif isinstance(error, lib.commands.CommandNotFound):
		await GeneralFunctions.send_embed_error("Command Not Found", error, ctx)
		logger.error("User tried to use a command that does not exist")
	elif isinstance(error, lib.commands.BadArgument):
		await GeneralFunctions.send_embed_error("Invalid argument", error, ctx)
		logger.error("User provided an invalid argument")
	elif isinstance(error, lib.commands.CheckFailure):
		await GeneralFunctions.send_embed_error("Incorrect Command Usage", error, ctx)
		logger.error("User used command incorrectly")
	elif isinstance(error, lib.discord.errors.PrivilegedIntentsRequired):
		await GeneralFunctions.send_embed_error("Missing Required Intent", error, ctx)
		logger.error("Bot is missing required intent")
	elif isinstance(error, lib.commands.CommandOnCooldown):
		await GeneralFunctions.send_embed_error("Command Cooldown", error, ctx)
		logger.warning(f"Command on cooldown for user {ctx.author}")
	else:
		msg = "An unexpected error occurred while processing your command. Please use /ticket."
		await GeneralFunctions.send_embed_error("Unexpected Error", msg, ctx)
		logger.exception("Unexpected error occurred", exc_info=error)

#------------------------------------------------------------------------------------------------
# Tasks
#------------------------------------------------------------------------------------------------
@lib.tasks.loop(seconds=60)
async def validate_db():
	"""
	DESCRIPTION: Periodically validate the connection
	"""
	await GeneralFunctions.validate_connection(UnfilteredBot.mydb)

client.run(DISCORD_TOKEN)
