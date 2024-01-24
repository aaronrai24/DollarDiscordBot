"""
DESCRIPTION: Queries for the database reside here
"""

from ..common.libraries import(
	commands, mysql
)

from ..common.generalfunctions import GeneralFunctions

logger = GeneralFunctions.setup_logger("mysql-queries")

class Queries(commands.Cog):
	"""
	DESCRIPTION: Creates GameCommands class
	PARAMETERS: commands.Bot - Discord Commands
	"""
	
	def __init__(self, bot):
		self.bot = bot

	def add_user_to_db(mydb, user_name=None, home_address=None, work_address=None):
		"""
		DESCRIPTION: Adds a user to the database

		PARAMETERS: mydb (obj) - Database connection
					user_name (str, OPT) - Discord user name
					home_address (str, OPT) - Home address
					work_address (str, OPT) - Work address
		"""
		try:
			cursor = mydb.cursor()
			logger.debug("Executing query to add user")
			cursor.execute(f"INSERT INTO users (username, home_address, work_address) VALUES ('{user_name}', '{home_address}', '{work_address}')")
			mydb.commit()
			logger.debug("Query to add user executed")
		except mysql.Error as e:
			logger.error(f"Failed to execute query: {e}")
	
	def check_if_user_exists(mydb, user_name):
		"""
		DESCRIPTION: Checks if a user exists in the database

		PARAMETERS: mydb (obj) - Database connection
					user_name (str) - Discord user name
		"""
		try:
			cursor = mydb.cursor()
			logger.debug("Executing query to check if user exists")
			cursor.execute(f"SELECT username FROM users WHERE username = '{user_name}'")
			result = cursor.fetchone()
			logger.debug("Query to check if user exists executed")
			return result
		except mysql.err.Error as err:
			logger.error(f"Failed to execute query: {err}")

	def add_game_to_db(mydb, game_name):
		"""
		DESCRIPTION: Adds a game to the database

		PARAMETERS: mydb (obj) - Database connection
					game_name (str) - Game name
		"""
		try:
			cursor = mydb.cursor()
			logger.debug("Inserting game into database")
			cursor.execute(f"INSERT INTO games (game_name) VALUES ('{game_name}')")
			mydb.commit()
			logger.debug("Game inserted into database")
		except mysql.err.Error as err:
			logger.error(f"Failed to execute query: {err}")
		
	def check_if_game_exists(mydb, game_name):
		"""
		DESCRIPTION: Checks if a game exists in the database

		PARAMETERS: mydb (obj) - Database connection
					game_name (str) - Game name
		"""
		try:
			cursor = mydb.cursor()
			logger.debug("Executing query to check if game exists")
			cursor.execute(f"SELECT game_name FROM games WHERE game_name = '{game_name}'")
			result = cursor.fetchone()
			logger.debug("Query to check if game exists executed")
			return result
		except mysql.Error as err:
			logger.error(f"Failed to execute query: {err}")
	
	def add_game_subscription(mydb, user_name, game_name):
		"""
		DESCRIPTION: Adds a game subscription to the database

		PARAMETERS: mydb (obj) - Database connection
					user_name (str) - Discord user name
					game_name (str) - Game name
		"""
		try:
			cursor = mydb.cursor()
			logger.debug("Executing query to add game subscription")
			query = """
				INSERT INTO game_subscriptions (user_id, game_id)
				VALUES ((SELECT user_id FROM users WHERE username = %s), (SELECT game_id FROM games WHERE game_name = %s))
			"""
			params = (user_name, game_name)
			cursor.execute(query, params)
			mydb.commit()
			logger.debug("Query to add game subscription executed")
		except mysql.err.Error as err:
			logger.error(f"Failed to execute query: {err}")

	def get_game_subscriptions(mydb, game_name):
		"""
		DESCRIPTION: Gets all usernames from game_name

		PARAMETERS: mydb (obj) - Database connection
					game_name (str) - Game name
		"""
		try:
			cursor = mydb.cursor()
			logger.debug("Executing query to get game subscriptions")
			query = """
				SELECT username FROM users WHERE user_id IN 
				(SELECT user_id FROM game_subscriptions 
				WHERE game_id = (SELECT game_id FROM games WHERE game_name = %s))
			"""
			params = (game_name,)
			cursor.execute(query, params)
			result = cursor.fetchall()
			logger.debug("Query to get game subscriptions executed")
			return result
		except mysql.err.Error as err:
			logger.error(f"Failed to execute query: {err}")

	def remove_game_subscription(mydb, user_name, game_name):
		"""
		DESCRIPTION: Removes a game subscription from the database

		PARAMETERS: mydb (obj) - Database connection
					user_name (str) - Discord user name
					game_name (str) - Game name
		"""
		try:
			cursor = mydb.cursor()
			logger.debug("Executing query to remove game subscription")
			query = """
				DELETE FROM game_subscriptions 
				WHERE user_id = (SELECT user_id FROM users WHERE username = %s) 
				AND game_id = (SELECT game_id FROM games WHERE game_name = %s)
			"""
			params = (user_name, game_name)
			cursor.execute(query, params)
			mydb.commit()
			logger.debug("Query to remove game subscription executed")
		except mysql.err.Error as err:
			logger.error(f"Failed to execute query: {err}")

	def update_users_home_address(mydb, user_name, home_address):
		"""
		DESCRIPTION: Updates a users home address in the database

		PARAMETERS: mydb (obj) - Database connection
					user_name (str) - Discord user name
					home_address (str) - Home address
		"""
		try:
			cursor = mydb.cursor()
			logger.debug("Executing query to update users home address")
			cursor.execute(f"UPDATE users SET home_address = '{home_address}' WHERE username = '{user_name}'")
			mydb.commit()
			logger.debug("Query to update users home address executed")
		except mysql.err.Error as err:
			logger.error(f"Failed to execute query: {err}")
	
	def update_users_work_address(mydb, user_name, work_address):
		"""
		DESCRIPTION: Updates a users work address in the database

		PARAMETERS: mydb (obj) - Database connection
					user_name (str) - Discord user name
					work_address (str) - Work address
		"""
		try:
			cursor = mydb.cursor()
			logger.debug("Executing query to update users work address")
			cursor.execute(f"UPDATE users SET work_address = '{work_address}' WHERE username = '{user_name}'")
			mydb.commit()
			logger.debug("Query to update users work address executed")
		except mysql.err.Error as err:
			logger.error(f"Failed to execute query: {err}")
	
	def get_users_home_address(mydb, user_name):
		"""
		DESCRIPTION: Gets a users home address from the database

		PARAMETERS: mydb (obj) - Database connection
					user_name (str) - Discord user name
		"""
		try:
			cursor = mydb.cursor()
			logger.debug("Executing query to get users home address")
			cursor.execute(f"SELECT home_address FROM users WHERE username = '{user_name}'")
			result = cursor.fetchone()
			logger.debug("Query to get users home address executed")
			return result
		except mysql.err.Error as err:
			logger.error(f"Failed to execute query: {err}")
	
	def get_users_work_address(mydb, user_name):
		"""
		DESCRIPTION: Gets a users work address from the database

		PARAMETERS: mydb (obj) - Database connection
					user_name (str) - Discord user name
		"""
		try:
			cursor = mydb.cursor()
			logger.debug("Executing query to get users work address")
			cursor.execute(f"SELECT work_address FROM users WHERE username = '{user_name}'")
			result = cursor.fetchone()
			logger.debug("Query to get users work address executed")
			return result
		except mysql.err.Error as err:
			logger.error(f"Failed to execute query: {err}")
	
	def remove_user_from_db(mydb, user_name):
		"""
		DESCRIPTION: Removes a user from the database

		PARAMETERS: mydb (obj) - Database connection
					user_name (str) - Discord user name
		"""
		try:
			cursor = mydb.cursor()
			logger.debug("Executing query to remove user")
			cursor.execute(f"DELETE FROM users WHERE username = '{user_name}'")
			mydb.commit()
			logger.debug("Query to remove user executed")
		except mysql.err.Error as err:
			logger.error(f"Failed to execute query: {err}")

	def add_guild_to_db(mydb, guild_name, user_name):
		"""
		DESCRIPTION: Adds a guild to the database

		PARAMETERS: mydb (obj) - Database connection
					guild_name (str) - Guild name
					user_name (str) - Discord user name
		"""
		try:
			cursor = mydb.cursor()
			logger.debug("Executing query to add guild")
			query = """INSERT INTO guilds (guild_name, user_id) VALUES (%s, (SELECT user_id FROM users WHERE username = %s))"""
			params = (guild_name, user_name)
			cursor.execute(query, params)
			logger.debug("Query to add guild executed")
			mydb.commit()
		except mysql.err.Error as err:
			logger.error(f"Failed to execute query: {err}")

	def check_if_guild_exists(mydb, guild_name):
		"""
		DESCRIPTION: Checks if a guild exists in the database

		PARAMETERS: mydb (obj) - Database connection
					guild_name (str) - Guild name
		"""
		try:
			cursor = mydb.cursor()
			logger.debug("Executing query to check if guild exists")
			cursor.execute(f"SELECT guild_name FROM guilds WHERE guild_name = '{guild_name}'")
			result = cursor.fetchone()
			logger.debug("Query to check if guild exists executed")
			return result
		except mysql.Error as err:
			logger.error(f"Failed to execute query: {err}")
	
	def remove_guild_from_db(mydb, guild_name):
		"""
		DESCRIPTION: Removes a guild from the database

		PARAMETERS: mydb (obj) - Database connection
					guild_name (str) - Guild name
		"""
		try:
			cursor = mydb.cursor()
			logger.debug("Executing query to remove guild")
			# delete from guild preferences table first
			cursor.execute(f"DELETE FROM guild_preferences WHERE guild_id = (SELECT guild_id FROM guilds WHERE guild_name = '{guild_name}')")
			mydb.commit()
			logger.debug("Query to remove guild preferences executed")
			cursor.execute(f"DELETE FROM guilds WHERE guild_name = '{guild_name}'")
			mydb.commit()
			logger.debug("Query to remove guild executed")
		except mysql.err.Error as err:
			logger.error(f"Failed to execute query: {err}")

async def setup(bot):
	await bot.add_cog(Queries(bot))
