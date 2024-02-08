"""
DESCRIPTION: Queries for the database reside here
"""

from ..common.libraries import(
	commands, wraps, ProgrammingError, IntegrityError, 
	DatabaseError, Error
)

from ..common.generalfunctions import GeneralFunctions

logger = GeneralFunctions.setup_logger("postgres.queries")

class Queries(commands.Cog):
	"""
	DESCRIPTION: Creates GameCommands class
	PARAMETERS: commands.Bot - Discord Commands
	"""
	
	def __init__(self, bot):
		self.bot = bot
		self.mydb = bot.mydb

	def handle_exceptions(func):
		"""
		DESCRIPTION: Decorator to handle exceptions in database queries
		PARAMETERS: func (obj) - Function to be wrapped
		"""
		@wraps(func)
		def wrapper(*args, **kwargs):
			try:
				return func(*args, **kwargs)
			except ProgrammingError as err:
				logger.error(f"Programming error: {err}")
			except IntegrityError as err:
				logger.error(f"Integrity error: {err}")
			except DatabaseError as err:
				logger.error(f"Database error: {err}")
			except Error as err:
				logger.error(f"General error: {err}")
		return wrapper

	@handle_exceptions
	def add_user_to_db(self, user_id, user_name, home_address=None, work_address=None):
		"""
		DESCRIPTION: Adds a user to the database

		PARAMETERS: self.mydb (obj) - Database connection
					user_name (str) - Discord user name
					home_address (str, OPT) - Home address
					work_address (str, OPT) - Work address
		"""
		cursor = self.mydb.cursor()
		logger.debug("Executing query to add user")
		cursor.execute(
			"INSERT INTO users (discord_id, username, home_address, work_address) VALUES (%s, %s, %s, %s)",
			(user_id, user_name, home_address, work_address)
		)
		self.mydb.commit()
		logger.debug("Query to add user executed")
	
	@handle_exceptions
	def check_if_user_exists(self, user_name):
		"""
		DESCRIPTION: Checks if a user exists in the database

		PARAMETERS: self.mydb (obj) - Database connection
					user_name (str) - Discord user name
		"""
		cursor = self.mydb.cursor()
		logger.debug("Executing query to check if user exists")
		cursor.execute("SELECT username FROM users WHERE username = %s", (user_name,))
		result = cursor.fetchone()
		logger.debug("Query to check if user exists executed")
		return result

	@handle_exceptions
	def add_game_to_db(self, game_name):
		"""
		DESCRIPTION: Adds a game to the database

		PARAMETERS: self.mydb (obj) - Database connection
					game_name (str) - Game name
		"""
		cursor = self.mydb.cursor()
		logger.debug("Inserting game into database")
		cursor.execute("INSERT INTO games (game_name) VALUES (%s)", (game_name,))
		self.mydb.commit()
		logger.debug("Game inserted into database")
	
	@handle_exceptions
	def check_if_game_exists(self, game_name):
		"""
		DESCRIPTION: Checks if a game exists in the database

		PARAMETERS: self.mydb (obj) - Database connection
					game_name (str) - Game name
		"""
		cursor = self.mydb.cursor()
		logger.debug("Executing query to check if game exists")
		cursor.execute("SELECT game_name FROM games WHERE game_name = %s", (game_name,))
		result = cursor.fetchone()
		logger.debug("Query to check if game exists executed")
		return result
	
	@handle_exceptions
	def add_game_subscription(self, user_name, game_name):
		"""
		DESCRIPTION: Adds a game subscription to the database

		PARAMETERS: self.mydb (obj) - Database connection
					user_name (str) - Discord user name
					game_name (str) - Game name
		"""
		cursor = self.mydb.cursor()
		logger.debug("Executing query to add game subscription")
		query = """
			INSERT INTO game_subscriptions (user_id, game_id)
			VALUES ((SELECT user_id FROM users WHERE username = %s), (SELECT game_id FROM games WHERE game_name = %s))
		"""
		params = (user_name, game_name)
		cursor.execute(query, params)
		self.mydb.commit()
		logger.debug("Query to add game subscription executed")

	@handle_exceptions
	def get_game_subscriptions(self, game_name):
		"""
		DESCRIPTION: Gets all usernames from game_name

		PARAMETERS: self.mydb (obj) - Database connection
					game_name (str) - Game name
		"""
		cursor = self.cursor()
		logger.debug("Executing query to get game subscriptions")
		query = """
			SELECT discord_id FROM users WHERE user_id IN 
			(SELECT user_id FROM game_subscriptions 
			WHERE game_id = (SELECT game_id FROM games WHERE game_name = %s))
		"""
		params = (game_name,)
		cursor.execute(query, params)
		result = cursor.fetchall()
		logger.debug("Query to get game subscriptions executed")
		discord_ids = [row[0] for row in result]
		return discord_ids

	@handle_exceptions
	def remove_game_subscription(self, user_name, game_name):
		"""
		DESCRIPTION: Removes a game subscription from the database

		PARAMETERS: self.mydb (obj) - Database connection
					user_name (str) - Discord user name
					game_name (str) - Game name
		"""
		cursor = self.mydb.cursor()
		logger.debug("Executing query to remove game subscription")
		query = """
			DELETE FROM game_subscriptions 
			WHERE user_id = (SELECT user_id FROM users WHERE username = %s) 
			AND game_id = (SELECT game_id FROM games WHERE game_name = %s)
		"""
		params = (user_name, game_name)
		cursor.execute(query, params)
		self.mydb.commit()
		logger.debug("Query to remove game subscription executed")

	@handle_exceptions
	def update_users_home_address(self, user_name, home_address):
		"""
		DESCRIPTION: Updates a users home address in the database

		PARAMETERS: self.mydb (obj) - Database connection
					user_name (str) - Discord user name
					home_address (str) - Home address
		"""
		cursor = self.mydb.cursor()
		logger.debug("Executing query to update users home address")
		cursor.execute("UPDATE users SET home_address = %s WHERE username = %s", (home_address, user_name))
		self.mydb.commit()
		logger.debug("Query to update users home address executed")
	
	@handle_exceptions
	def update_users_work_address(self, user_name, work_address):
		"""
		DESCRIPTION: Updates a users work address in the database

		PARAMETERS: self.mydb (obj) - Database connection
					user_name (str) - Discord user name
					work_address (str) - Work address
		"""
		cursor = self.mydb.cursor()
		logger.debug("Executing query to update users work address")
		cursor.execute("UPDATE users SET work_address = %s WHERE username = %s", (work_address, user_name))
		self.mydb.commit()
		logger.debug("Query to update users work address executed")
	
	@handle_exceptions
	def get_users_home_address(self, user_name):
		"""
		DESCRIPTION: Gets a users home address from the database

		PARAMETERS: self.mydb (obj) - Database connection
					user_name (str) - Discord user name
		"""
		cursor = self.mydb.cursor()
		logger.debug("Executing query to get users home address")
		cursor.execute("SELECT home_address FROM users WHERE username = %s", (user_name,))
		result = cursor.fetchone()
		logger.debug("Query to get users home address executed")
		return result
	
	@handle_exceptions
	def get_users_work_address(self, user_name):
		"""
		DESCRIPTION: Gets a users work address from the database

		PARAMETERS: self.mydb (obj) - Database connection
					user_name (str) - Discord user name
		"""
		cursor = self.mydb.cursor()
		logger.debug("Executing query to get users work address")
		cursor.execute("SELECT work_address FROM users WHERE username = %s", (user_name,))
		result = cursor.fetchone()
		logger.debug("Query to get users work address executed")
		return result
	
	@handle_exceptions
	def remove_user_from_db(self, user_name):
		"""
		DESCRIPTION: Removes a user from the database

		PARAMETERS: self.mydb (obj) - Database connection
					user_name (str) - Discord user name
		"""
		cursor = self.mydb.cursor()
		logger.debug("Executing query to remove user")
		cursor.execute("DELETE FROM users WHERE username = %s", (user_name,))
		self.mydb.commit()
		logger.debug("Query to remove user executed")

	@handle_exceptions
	def add_guild_to_db(self, guild_name, user_name):
		"""
		DESCRIPTION: Adds a guild to the database

		PARAMETERS: self.mydb (obj) - Database connection
					guild_name (str) - Guild name
					user_name (str) - Discord user name
		"""
		cursor = self.mydb.cursor()
		logger.debug("Executing query to add guild")
		query = """
			INSERT INTO guilds (guild_name, owner_id) 
			VALUES (%s, (SELECT user_id FROM users WHERE username = %s))
			ON CONFLICT (guild_name) DO NOTHING
		"""
		params = (guild_name, user_name)
		cursor.execute(query, params)
		logger.debug("Query to add guild executed")
		self.mydb.commit()

	@handle_exceptions
	def check_if_guild_exists(self, guild_name):
		"""
		DESCRIPTION: Checks if a guild exists in the database

		PARAMETERS: self.mydb (obj) - Database connection
					guild_name (str) - Guild name
		"""
		cursor = self.mydb.cursor()
		logger.debug("Executing query to check if guild exists")
		cursor.execute("SELECT guild_name FROM guilds WHERE guild_name = %s", (guild_name,))
		result = cursor.fetchone()
		logger.debug("Query to check if guild exists executed")
		return result
	
	@handle_exceptions
	def remove_guild_from_db(self, guild_name):
		"""
		DESCRIPTION: Removes a guild from the database

		PARAMETERS: self.mydb (obj) - Database connection
					guild_name (str) - Guild name
		"""
		cursor = self.mydb.cursor()
		logger.debug("Executing query to remove guild")
		cursor.execute("DELETE FROM guild_preferences WHERE guild_id = (SELECT guild_id FROM guilds WHERE guild_name = %s)", (guild_name,))
		self.mydb.commit()
		logger.debug("Query to remove guild preferences executed")
		cursor.execute("DELETE FROM guilds WHERE guild_name = %s", (guild_name,))
		self.mydb.commit()
		logger.debug("Query to remove guild executed")
	
	@handle_exceptions
	def add_guild_preferences(self, text_channel, voice_channel, shows_channel, guild_name):
		"""
		DESCRIPTION: Adds guild preferences to the database

		PARAMETERS: self.mydb (obj) - Database connection
					text_channel (str) - Text channel name
					voice_channel (str) - Voice channel name
					shows_channel (str) - Shows channel name
					guild_name (str) - Guild name
		"""
		cursor = self.mydb.cursor()
		logger.debug("Executing query to add guild preferences")
		query = """
			INSERT INTO guild_preferences (text_channel, voice_channel, shows_channel, guild_id)
			VALUES (%s, %s, %s, (SELECT guild_id FROM guilds WHERE guild_name = %s))
			ON CONFLICT (guild_id) DO UPDATE SET text_channel = %s, voice_channel = %s, shows_channel = %s
			"""
		params = (text_channel, voice_channel, shows_channel, guild_name, text_channel, voice_channel, shows_channel)
		cursor.execute(query, params)
		self.mydb.commit()
		logger.debug("Query to add guild preferences executed")
	
	@handle_exceptions
	def get_guilds_preferred_text_channel(self, guild_name):
		"""
		DESCRIPTION: Gets the preferred text channel for a guild

		PARAMETERS: self.mydb (obj) - Database connection
					guild_name (str) - Guild name
		"""
		cursor = self.mydb.cursor()
		logger.debug("Executing query to get guilds preferred text channel")
		query = """
			SELECT text_channel FROM guild_preferences WHERE 
			guild_id = (SELECT guild_id FROM guilds WHERE guild_name = %s)
		"""
		params = (guild_name,)
		cursor.execute(query, params)
		result = cursor.fetchone()
		logger.debug("Query to get guilds preferred text channel executed")
		return result[0] if result else None
	
	@handle_exceptions
	def get_guilds_preferred_voice_channel(self, guild_name):
		"""
		DESCRIPTION: Gets the preferred voice channel for a guild

		PARAMETERS: self.mydb (obj) - Database connection
					guild_name (str) - Guild name
		"""
		cursor = self.mydb.cursor()
		logger.debug("Executing query to get guilds preferred voice channel")
		query = """
			SELECT voice_channel FROM guild_preferences WHERE 
			guild_id = (SELECT guild_id FROM guilds WHERE guild_name = %s)
		"""
		params = (guild_name,)
		cursor.execute(query, params)
		result = cursor.fetchone()
		logger.debug("Query to get guilds preferred voice channel executed")
		return result[0] if result else None
	
	@handle_exceptions
	def get_guilds_preferred_shows_channel(self, guild_name):
		"""
		DESCRIPTION: Gets the preferred shows channel for a guild

		PARAMETERS: self.mydb (obj) - Database connection
					guild_name (str) - Guild name
		"""
		cursor = self.mydb.cursor()
		logger.debug("Executing query to get guilds preferred shows channel")
		query = """
			SELECT shows_channel FROM guild_preferences WHERE 
			guild_id = (SELECT guild_id FROM guilds WHERE guild_name = %s)
		"""
		params = (guild_name,)
		cursor.execute(query, params)
		result = cursor.fetchone()
		logger.debug("Query to get guilds preferred shows channel executed")
		return result[0] if result else None

async def setup(bot):
	await bot.add_cog(Queries(bot))
