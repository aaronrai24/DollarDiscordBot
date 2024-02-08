"""
DESCRIPTION: Common functions accessible by any class
All general functions should be written here.
"""

from ..common.libraries import(
	discord, logging, commands, wavelink, os, psycopg2,
	asyncio, pool
)

class CustomPlayer(wavelink.Player):
	"""
	DESCRIPTION: Creates CustomPlayer class for wavelink
	PARAMETERS: wavelink.Player - Player instance
	"""
	def __init__(self):
		super().__init__()
		self.queue = wavelink.Queue()

class GeneralFunctions():
	"""
	DESCRIPTION: Creates GeneralFunctions class
	"""
	def __init__(self):
		pass

	def setup_logger(logger_name):
		"""
		Set up and configure a rotating file logger for the specified logger name.

		Parameters:
		- logger_name (str): The name of the logger.

		Returns:
		- logging.Logger: The configured logger instance.
		"""
		#pylint: disable=redefined-outer-name
		logger = logging.getLogger(logger_name)
		if not logger.handlers:
			handler = logging.handlers.RotatingFileHandler(
				filename="discord.log",
				encoding="utf-8",
				maxBytes=1024*1024,  # 1mb
				backupCount=5,  # Rotate through 5 files
			)
			handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
			logger.addHandler(handler)
			logger.setLevel(logging.INFO)
		return logger

	def is_connected_to_same_voice():
		"""
		Check if the command invoker is connected to the same voice channel.

		Returns:
		- A check function that raises `commands.CheckFailure`
		"""
		async def predicate(ctx):
			if not ctx.author.voice:
				raise commands.CheckFailure("You need to be in a voice channel to use this command")
			elif not ctx.voice_client or ctx.author.voice.channel != ctx.voice_client.channel:
				raise commands.CheckFailure("You need to be in the same voice channel as Dollar to use this command")
			return True
		return commands.check(predicate)

	def is_connected_to_voice():
		"""
		Check if the command invoker is connected to a voice channel.

		Returns:
		- A check function that raises `commands.CheckFailure`
		"""
		async def predicate(ctx):
			if not ctx.author.voice:
				raise commands.CheckFailure("You need to be in a voice channel to use this command")
			return True
		return commands.check(predicate)

	def is_guild_owner():
		"""
		Check if the command invoker is the guild owner.

		Returns:
		- A check function that raises `commands.CheckFailure`
		"""
		async def predicate(ctx):
			if not ctx.author.id == ctx.guild.owner_id:
				raise commands.CheckFailure("You need to be the guild owner to use this command")
			return True
		return commands.check(predicate)

	def connect_to_database():
		"""
		Validate the connection to a PostgreSQL database by executing a simple query.

		Returns:
		- bool: True if the connection is valid, False otherwise.
		"""
		try:
			connection_pool = pool.SimpleConnectionPool(
				1,
				8,
				host="localhost",
				user=os.getenv("DB_USER"),
				password=os.getenv("DB_PW"),
				dbname=os.getenv("DB_SCHEMA")
			)
			mydb = connection_pool.getconn()
			logger.info("Connected to the database successfully.")
			logger.debug("Acquired a database connection from the connection pool.")
			return mydb
		except Exception as err:
			logger.error(f"Failed to connect to the database: {err}")
			return None

	async def validate_connection(mydb):
		"""
		Validate the connection to a PostgreSQL database by executing a simple query.

		Parameters:
		- mydb (psycopg2.extensions.connection): The PostgreSQL database connection object.

		Returns:
		- bool: True if the connection is valid, False otherwise.
		"""
		try:
			cursor = mydb.cursor()
			cursor.execute("SELECT 1")
			cursor.fetchall()
			cursor.close()
			logger.debug("Executed validation query")
			return True
		except Exception as error:
			logger.error(f"Error validating connection: {error}")
			return False

	async def send_patch_notes(client):
		"""
		Send the latest patch notes to the system channel of each guild the bot is a member of.

		Parameters:
		- client (discord.Client): The Discord client instance representing the bot.

		Returns:
		- None
		"""
		for guild in client.guilds:
			logger.debug(f"Dollar loaded in {guild.name}, owner: {guild.owner}")
			channel = guild.system_channel
			if channel is not None:
				try:
					file_path = os.path.join("markdown", "patch_notes.md")
					if os.path.isfile(file_path):
						with open(file_path, "r", encoding="utf-8") as file:
							desc = file.read()

					embed = discord.Embed(
						title="Patch: 1.1.4",
						url="https://en.wikipedia.org/wiki/Dollar",
						description=desc,
						colour=discord.Color.green()
					)
					embed.set_author(name="Dollar")
					file_path = os.path.join("images", "dollar.png")
					img = discord.File(file_path, filename="dollar.png")
					embed.set_thumbnail(url="attachment://dollar.png")
					embed.set_footer(text="Feature request? Bug? Please report it by using /reportbug or /featurerequest")

					await channel.send(embed=embed, file=img)
					logger.debug(f"Notified {guild.name} of dollar\"s latest update.")
				except discord.Forbidden:
					logger.warning(f"Could not send message to {channel.name} in {guild.name}. Missing permissions.")
				except discord.HTTPException:
					logger.error(f"Could not send message to {channel.name} in {guild.name}. HTTP exception occurred.")

	async def idle_checker(vc, comchannel, guild):
		"""
		Check for inactivity in the voice channel and disconnect the bot if idle for 10 minutes.

		Parameters:
		- vc: discord.VoiceClient
			The voice client representing the bot's connection to a voice channel.
		- comchannel: discord.TextChannel
			The text channel where the bot commands are typically sent.
		- guild: discord.Guild
			The guild (server) associated with the voice channel.

		Returns:
		- None
		"""
		time = 0
		while True:
			await asyncio.sleep(1)
			time = time + 1
			if time % 30 == 0:
				logger.debug(f"Dollar has been idle for {time} seconds in {str(guild)}")
			if vc.is_playing() and not vc.is_paused():
				time = 0
			if time == 600:
				logger.info(f"10 minutes reached, Dollar disconnecting from {str(guild)}")
				await vc.disconnect()
				await comchannel.purge(limit=500)
				logger.debug("Finished clearing #commands channel")
				msg = f"10 minutes reached, Dollar disconnecting from {str(guild)}"
				await GeneralFunctions.send_embed("Inactivity", "dollar4.png", msg, comchannel)
			if not vc.is_connected():
				break

	async def send_embed(title, image, msg, channel, footer=False):
		"""
		Send an embedded message with a title, image, and description to a specified channel.

		Parameters:
		- title (str): The title of the embed.
		- image (str): The filename of the image to be attached.
		- msg (str): The description or content of the embed.
		- channel (discord.TextChannel): The channel where the embed will be sent.
		- footer (bool): Flag to include a footer on embed.

		Returns:
		- None
		"""
		embed = discord.Embed(title=title, description=msg, colour=0x2ecc71)
		embed.set_author(name="Dollar")
		file_path = os.path.join("images", image)
		img = discord.File(file_path, filename=image)
		embed.set_thumbnail(url=f"attachment://{image}")
		if footer:
			embed.set_footer(text="Feature request? Bug? Please report it by using /reportbug or /featurerequest")
		await channel.send(embed=embed, file=img)

	async def send_embed_error(title, msg, channel, footer=False):
		"""
		Send an embedded error message with a title and description to a specified channel.

		Parameters:
		- title (str): The title of the error embed.
		- msg (str): The description or content of the error embed.
		- channel (discord.TextChannel): The channel where the error embed will be sent.
		- footer (bool): Flag to include a footer on embed.

		Returns:
		- None
		"""
		image = "error.png"
		embed = discord.Embed(title=title, description=msg, colour=0xe74c3c)
		embed.set_author(name="Dollar")
		file_path = os.path.join("images", image)
		img = discord.File(file_path, filename=image)
		embed.set_thumbnail(url=f"attachment://{image}")
		if footer:
			embed.set_footer(text="Feature request? Bug? Please report it by using /reportbug or /featurerequest")
		await channel.send(embed=embed, file=img)

logger = GeneralFunctions.setup_logger("core")
