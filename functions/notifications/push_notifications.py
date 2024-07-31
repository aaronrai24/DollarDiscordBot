"""
This file contains the functions for the push notifications.
"""
from ..common.generalfunctions import GeneralFunctions
from ..queries.queries import Queries
from ..common import libraries as lib

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

	def get_commute_duration(self, member):
		"""
		DESCRIPTION: Gets the commute duration
		PARAMETERS: member (discord.Member) - Discord Member
		RETURN: duration (int) - Duration of commute
		"""
		home_address = Queries.get_users_home_address(self.mydb, member.id)
		work_address = Queries.get_users_work_address(self.mydb, member.id)

		google_maps_api_key = lib.os.getenv('GOOGLE_MAPS_API_KEY')
		gmaps = googlemaps.Client(key=google_maps_api_key)

		directions = gmaps.directions(home_address, work_address)
		first_leg = directions[0]['legs'][0]
		duration = first_leg['duration']['value']

		return duration
	
	async def notify_eta_to_work(self, member):
		"""
		DESCRIPTION: Notifies user of the time until work
		PARAMETERS: member (discord.Member) - Discord Member
		"""
		logger.debug(f"Notifying {member} of their ETA to work...")
		duration = get_commute_duration(member)
		now = lib.datetime.datetime.now()
		arrival_time = (now + duration).strftime("%I:%M %p")
		departure_time = (now - duration).strftime("%I:%M %p")

		message = f"""Good morning!\n\n
		Estimated commute time from home to work at 8am is {duration}.\n
		You should leave by {departure_time} to arrive at work by {arrival_time}.\n"""

		GeneralFunctions.send_discord_dm(member, message)

async def setup(bot):
	await bot.add_cog(PushNotifications(bot))
