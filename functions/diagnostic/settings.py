"""
Dollar Customization Settings
"""

from ..common.generalfunctions import GeneralFunctions
from ..queries.queries import Queries
from ..common import libraries as lib

logger = GeneralFunctions.setup_logger("settings")

class SettingsModal(lib.discord.ui.Modal, title="DollarSettings"):
	"""
	DESCRIPTION: Creates Settings Modal
	PARAMETERS: discord.ui.Modal - Discord Modal
	"""
	def __init__(self, mydb):
		super().__init__()
		self.mydb = mydb

	text_channel = lib.discord.ui.TextInput(label="Text Channel", placeholder="Enter Preferred Text Channel Name", required=True)
	voice_channel = lib.discord.ui.TextInput(label="Voice Channel", placeholder="Enter Preferred Voice Channel Name", required=True)
	shows_channel = lib.discord.ui.TextInput(label="Shows Channel", placeholder="Enter Preferred Shows Channel Name", required=True)

	async def create_channels(self, guild, text_channel_value, voice_channel_value, shows_channel_value):
		"""
		DESCRIPTION: Creates text, voice, and shows channels if they do not already exist
		PARAMETERS: discord.Guild - Discord Guild, str - Text Channel Name, str - Voice Channel Name, str - Shows Channel Name
		"""
		logger.debug(f"Checking for existing channels and creating text, voice, and shows channels for guild {guild}")

		existing_channels = {channel.name: channel for channel in guild.channels}
		
		if text_channel_value not in existing_channels:
			await guild.create_text_channel(text_channel_value)
			logger.debug(f"Text channel '{text_channel_value}' created for guild {guild}")
		else:
			logger.warning(f"Text channel '{text_channel_value}' already exists in guild {guild}")
		
		if voice_channel_value not in existing_channels:
			await guild.create_voice_channel(voice_channel_value)
			logger.debug(f"Voice channel '{voice_channel_value}' created for guild {guild}")
		else:
			logger.warning(f"Voice channel '{voice_channel_value}' already exists in guild {guild}")
		
		if shows_channel_value not in existing_channels:
			await guild.create_voice_channel(shows_channel_value)
			logger.debug(f"Shows channel '{shows_channel_value}' created for guild {guild}")
		else:
			logger.warning(f"Shows channel '{shows_channel_value}' already exists in guild {guild}")
	
	async def on_submit(self, interaction: lib.discord.Interaction):
		"""
		DESCRIPTION: Fires on submit of Settings Modal
		PARAMETERS: discord.Interaction - Discord Interaction
		"""
		guild_id = interaction.guild_id
		guild = interaction.guild
		guild_owner = interaction.guild.owner
		text_channel_value = self.text_channel.value.replace(" ", "-").lower()
		voice_channel_value = self.voice_channel.value
		shows_channel_value = self.shows_channel.value
		logger.debug(f"Guild ID: {guild_id}, Text Channel: {text_channel_value}, Voice Channel: {voice_channel_value}, Shows Channel: {shows_channel_value}")

		result = Queries.check_if_guild_exists(self, str(guild))
		if result:
			logger.debug(f"Guild {guild_id} exists in database, updating text, voice, and shows channels")
			Queries.add_guild_preferences(self, text_channel_value, voice_channel_value, shows_channel_value, str(guild))
		else:
			logger.debug(f"Guild {guild_id} does not exist in database, adding text, voice, and shows channels")
			owner_exists = Queries.check_if_user_exists(self, str(guild_owner))
			if owner_exists is None:
				Queries.add_user_to_db(self, guild.owner.id, guild.owner.name)
			Queries.add_guild_to_db(self, str(guild), str(guild_owner))
			Queries.add_guild_preferences(self, text_channel_value, voice_channel_value, shows_channel_value, str(guild))
		
		#NOTE: Update text, voice channel caches
		lib.guild_text_channels[str(guild)] = text_channel_value
		lib.guild_voice_channels[str(guild)] = voice_channel_value
		logger.debug(f"Text and voice channel caches updated for guild {guild_id}")

		await interaction.response.send_message("Settings Saved! Creating your channels", ephemeral=True)

		await self.create_channels(guild, text_channel_value, voice_channel_value, shows_channel_value)
		logger.info(f"Dollar Settings saved for guild {guild_id}")

	async def on_error(self, interaction: lib.discord.Interaction, error: Exception) -> None:
		"""
		DESCRIPTION: Fires on error of Settings Modal
		PARAMETERS: discord.Interaction - Discord Interaction
		"""
		if isinstance(error, lib.discord.NotFound):
			message = "Oops! The item you were looking for was not found. Please report this bug using /reportbug."
		elif isinstance(error, lib.discord.Forbidden):
			message = "Oops! I don't have permission to do that. Please report this bug using /reportbug."
		elif isinstance(error, lib.discord.HTTPException):
			message = "Oops! Something went wrong with the Discord server. Please report this bug using /reportbug."
		else:
			message = "Oops! Something went wrong. Please report this bug using /reportbug."

		await interaction.response.send_message(message, ephemeral=True)
		logger.error(f"An error occurred: {error}")

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
		DESCRIPTION: Fires on error of Settings Modal
		PARAMETERS: discord.Interaction - Discord Interaction
		"""
		if isinstance(error, lib.discord.NotFound):
			message = "Oops! The item you were looking for was not found. Please report this bug using /reportbug."
		elif isinstance(error, lib.discord.Forbidden):
			message = "Oops! I don't have permission to do that. Please report this bug using /reportbug."
		elif isinstance(error, lib.discord.HTTPException):
			message = "Oops! Something went wrong with the Discord server. Please report this bug using /reportbug."
		else:
			message = "Oops! Something went wrong. Please report this bug using /reportbug."

		await interaction.response.send_message(message, ephemeral=True)
		logger.error(f"An error occurred: {error}")

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
		await interaction.response.send_modal(SettingsModal(self.mydb))

	@lib.discord.app_commands.command(name="updateuserinfo", description="Update Your User Information")
	async def userinformation(self, interaction: lib.discord.Interaction):
		"""
		DESCRIPTION: Creates UserInfo command
		PARAMETERS: discord.Interaction - Discord Interaction
		"""
		logger.info(f"Creating UserInfo Modal for: {interaction.user.name}")
		await interaction.response.send_modal(UserInfoModal(self.mydb))

async def setup(bot):
	await bot.add_cog(Settings(bot))
