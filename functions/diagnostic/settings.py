"""
Dollar Customization Settings
"""

import functions.common.libraries as lib
from ..common.generalfunctions import GeneralFunctions
from functions.queries.queries import Queries

logger = GeneralFunctions.setup_logger("settings")

async def is_owner(ctx):
	return ctx.author.id == ctx.guild.owner_id

class SettingsModal(lib.discord.ui.Modal, title="DollarSettings"):
	"""
	DESCRIPTION: Creates Settings Modal
	PARAMETERS: discord.ui.Modal - Discord Modal
	"""
	text_channel = lib.discord.ui.TextInput(label="Text Channel", placeholder="Enter Preferred Text Channel Name", required=True)
	voice_channel = lib.discord.ui.TextInput(label="Voice Channel", placeholder="Enter Preferred Voice Channel Name", required=True)
	shows_channel = lib.discord.ui.TextInput(label="Shows Channel", placeholder="Enter Preferred Shows Channel Name", required=True)
	
	async def on_submit(self, interaction: lib.discord.Interaction):
		"""
		DESCRIPTION: Fires on submit of Settings Modal
		PARAMETERS: discord.Interaction - Discord Interaction
		"""
		await interaction.response.send_message("Settings Saved! Creating your channels", ephemeral=True)

	async def on_error(self, interaction: lib.discord.Interaction, error: Exception) -> None:
		"""
		DESCRIPTION: Fires on error of Settings Modal
		PARAMETERS: discord.Interaction - Discord Interaction
		"""
		await interaction.response.send_message("Oops! Something went wrong.", ephemeral=True)
		logger.error(error)

class UserInfoModal(lib.discord.ui.Modal, title="UserInfo"):
	"""
	DESCRIPTION: Creates UserInfo Modal
	PARAMETERS: discord.ui.Modal - Discord Modal
	"""
	def __init__(self, mydb):
		super().__init__()
		self.mydb = mydb
	
	home_address = lib.discord.ui.TextInput(label="Home Address", placeholder="Enter Home Address", required=True)
	work_address = lib.discord.ui.TextInput(label="Work Address", placeholder="Enter Work Address", required=True)
	
	async def on_submit(self, interaction: lib.discord.Interaction):
		"""
		DESCRIPTION: Fires on submit of UserInfo Modal
		PARAMETERS: discord.Interaction - Discord Interaction
		"""
		user_name = interaction.user.name
		home_address_value = self.home_address.value
		work_address_value = self.work_address.value
		logger.debug(f"Username: {user_name}, Home Address: {home_address_value}, Work Address: {work_address_value}")

		user_exists = Queries.check_if_user_exists(self, str(user_name))
		if user_exists is None:
			logger.debug("User does not exist in database")
			Queries.add_user_to_db(self, user_name, home_address_value, work_address_value)
		else:
			logger.debug(f"User exists in database, updating home and work addresses for user {user_name}")
			Queries.update_users_home_address(self, user_name, home_address_value)
			Queries.update_users_work_address(self, user_name, work_address_value)
			logger.debug(f"Home and work addresses updated for user {user_name}")
		await interaction.response.send_message("Thanks! This data will never be shared and will be stored securely.", ephemeral=True)

	async def on_error(self, interaction: lib.discord.Interaction, error: Exception) -> None:
		"""
		DESCRIPTION: Fires on error of UserInfo Modal
		PARAMETERS: discord.Interaction - Discord Interaction
		"""
		await interaction.response.send_message("Oops! Something went wrong.", ephemeral=True)
		logger.error(error)

class Settings(lib.commands.Cog):
	"""
	DESCRIPTION: Creates Settings class and commands
	PARAMETERS: commands.Bot - Discord
	"""

	def __init__(self, bot):
		self.bot = bot
		self.mydb = bot.mydb

	@GeneralFunctions.is_guild_owner()
	@lib.discord.app_commands.command(name="dollarsettings", description="Change Dollar Settings")
	async def settings(self, interaction: lib.discord.Interaction):
		"""
		DESCRIPTION: Creates Settings command
		PARAMETERS: discord.Interaction - Discord Interaction
		"""
		logger.info(f"Creating Settings Modal for user: {interaction.user.name}")
		await interaction.response.send_modal(SettingsModal())

	@lib.discord.app_commands.command(name="updateuserinfo", description="Update user information")
	async def userinformation(self, interaction: lib.discord.Interaction):
		"""
		DESCRIPTION: Creates UserInfo command
		PARAMETERS: discord.Interaction - Discord Interaction
		"""
		logger.info(f"Creating UserInfo Modal for: {interaction.user.name}")
		await interaction.response.send_modal(UserInfoModal(self.mydb))

async def setup(bot):
	await bot.add_cog(Settings(bot))
