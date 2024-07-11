"""
DESCRIPTION: Creates Auto Channel Creation Class
"""
import functions.common.libraries as lib
from ..common.generalfunctions import GeneralFunctions

logger = GeneralFunctions.setup_logger("auto-channel-creation")

class AutoChannelCreation():
	"""
	DESCRIPTION: Creates Auto Channel Creation Class
	"""
	def __init__(self):
		pass
	
	async def create_personal_channel(member, join_channel):
		"""
		DESCRIPTION: Creates a personal channel for a member
		PARAMETERS: member - discord.Member
					join_channel - discord
		RETURNS: None
		"""
		logger.debug(f"Starting channel creation for {member.display_name} in {member.guild.name}")

		@lib.asynccontextmanager
		async def lock_channel(channel):
			"""
			DESCRIPTION: Locks a channel
			PARAMETERS: channel - discord.VoiceChannel
			RETURNS: None
			"""
			try:
				await channel.set_permissions(channel.guild.default_role, connect=False)
				yield
			finally:
				await channel.set_permissions(channel.guild.default_role, connect=True)

		guild = member.guild
		category = join_channel.category

		async with lock_channel(join_channel):
			new_channel = await guild.create_voice_channel(
				f"{member.display_name}'s Channel",
				category=category,
				position=0
			)
			await new_channel.set_permissions(member, manage_channels=True)
			lib.created_channels.add(new_channel.id)
			
			await member.move_to(new_channel)
			await lib.asyncio.sleep(1)  # Short delay to ensure move completes

		logger.info(f"Created channel {new_channel.name} for {member.display_name} in {guild.name}")

	async def handle_channel_leave(channel):
		"""
		DESCRIPTION: Handles channel leave event
		PARAMETERS: channel - discord.VoiceChannel
		RETURNS: None
		"""
		if channel.id in lib.created_channels and len(channel.members) == 0:
			await channel.delete()
			lib.created_channels.remove(channel.id)
			logger.info(f"Deleted empty channel {channel.name} in {channel.guild.name}")

	async def manage_idle_task(member, guild, channel):
		"""
		DESCRIPTION: Manages idle task for Dollar
		PARAMETERS: member - discord.Member
					guild - discord.Guild
					channel - discord.VoiceChannel
		RETURNS: None
		"""
		if str(member) == lib.DOLLAR_BOT_ID:
			if channel is None and guild.id in lib.idle_tasks:
				lib.idle_tasks[guild.id].cancel()
				del lib.idle_tasks[guild.id]
				logger.info(f"Cancelled idle task for Dollar in {guild.name}")
			elif channel is not None and guild.id not in lib.idle_tasks:
				lib.idle_tasks[guild.id] = lib.asyncio.create_task(
					GeneralFunctions.idle_checker(channel.guild.voice_client, guild)
				)
				logger.info(f"Created idle task for Dollar in {guild.name}")

	def get_join_channel(guild):
		"""
		DESCRIPTION: Gets trigger join channel for a guild
		PARAMETERS: guild - discord.Guild
		RETURNS: discord.VoiceChannel
		"""
		return lib.discord.utils.get(guild.voice_channels, name=lib.guild_voice_channels.get(str(guild)))
