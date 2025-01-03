"""
This file contains the functions for the push notifications.
"""
from ..common.generalfunctions import GeneralFunctions
from ..queries.queries import Queries
from ..common import libraries as lib

logger = GeneralFunctions.setup_logger("notifications")

@lib.discord.app_commands.context_menu(name="Poke User")
async def poke_user(interaction: lib.discord.Interaction, user: lib.discord.Member):
	"""
	DESCRIPTION: Pokes a user and notifies them to join a voice channel
	PARAMETERS: discord.Interaction - Discord Interaction
	"""
	command_user = interaction.user
	
	if command_user.voice and command_user.voice.channel:
		await interaction.response.send_message(f"Poking {user.mention} to join your voice channel!", ephemeral=True)
		invite = await command_user.voice.channel.create_invite(max_uses=1, unique=True)
		await user.send(f"Yo, {interaction.user} wants you to join their voice channel in {interaction.guild.name}! {invite.url}")
	else:
		await interaction.response.send_message("You need to be in a voice channel before using this command.", ephemeral=True)

@lib.discord.app_commands.context_menu(name="User Information")
async def get_user_info(interaction: lib.discord.Interaction, user: lib.discord.Member):
	"""
	DESCRIPTION: Gets user information
	PARAMETERS: interaction - Discord Interaction, user - Discord Member
	"""
	created_at = user.created_at.strftime("%B %d, %Y at %I:%M %p")
	joined_at = user.joined_at.strftime("%B %d, %Y at %I:%M %p")
		
	time_zone = "pacific" #TODO: Get time zone from database
	if time_zone:
		created_at = GeneralFunctions.convert_time_zone(created_at, time_zone)
		joined_at = GeneralFunctions.convert_time_zone(joined_at, time_zone)

	#pylint: disable=inconsistent-quotes
	msg = (f"User: {user.name}\n"
		   f"Preferred Name: {user.display_name}\n"
		   f"Created Their Account: {created_at}\n"
		   f"Joined This Discord: {joined_at}\n"
		   f"Roles: {', '.join([role.name for role in user.roles])}")
	
	embed = GeneralFunctions.create_embed(
		title="User Information",
		description=msg,
		author=user,
		image=user.avatar.url if user.avatar else None,
		footer=f"Requested by {interaction.user}"
	)
	
	await interaction.response.send_message(embed=embed)

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
	bot.tree.add_command(poke_user)
	bot.tree.add_command(get_user_info)
