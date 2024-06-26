"""
This file contains the functions for the push notifications.
"""
import functions.common.libraries as lib
from ..common.generalfunctions import GeneralFunctions
from functions.queries.queries import Queries

logger = GeneralFunctions.setup_logger("notifications")

class PushNotifications(lib.commands.Cog):
	"""
	DESCRIPTION: Creates Push_Notifications class
	PARAMETERS: commands.Bot - Discord Commands
	"""
	
	def __init__(self, bot):
		self.bot = bot
		self.mydb = bot.mydb

	async def notify_game_update(self, game_name, message):
		"""
		DESCRIPTION: Notifies users of game updates
		PARAMETERS: game_name (str) - Game name
					channel_id (int) - Channel ID
					message_id (int) - Message ID
		"""
		logger.debug("Notifying users of game update...")
		users = Queries.get_game_subscriptions(self.mydb, game_name)
		logger.debug(f"Users: {users} that are subscribed to {game_name}")

		thread = await message.create_thread(name=f"{game_name} Update Subscriptions")
		for user in users:
			logger.info(f"Sending patch note notification for user: {user}")
			await thread.send(f"<@{user}>, {game_name} has had a new update, check it out!")

async def setup(bot):
	await bot.add_cog(PushNotifications(bot))