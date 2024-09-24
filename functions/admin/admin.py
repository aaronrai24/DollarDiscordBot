"""
DESCRIPTION: Admin/Mod only commands reside here
"""
from ..common.generalfunctions import GeneralFunctions
from ..common import libraries as lib

logger = GeneralFunctions.setup_logger("administrative")

class EmbedCreatorModal(lib.discord.ui.Modal, title="Embed Creator"):
	"""
	DESCRIPTION: Creates EmbedCreatorModal class
	PARAMETERS: lib.discord.ui.Modal - Discord UI Modal
	"""

	def __init__(self):
		super().__init__()
	
	embed_title = lib.discord.ui.TextInput(label="Embed Title", required=True)
	embed_description = lib.discord.ui.TextInput(label="Embed Description", required=True)
	embed_image_url = lib.discord.ui.TextInput(label="Embed Image URL", required=False)
	embed_footer = lib.discord.ui.TextInput(label="Embed Footer", required=False)

	async def on_submit(self, interaction: lib.discord.Interaction):
		"""
		DESCRIPTION: Creates Embed
		PARAMETERS: interaction - Discord Interaction
		"""
		embed = GeneralFunctions.create_embed(
			title=self.embed_title.value,
			author=interaction.user,
			image=self.embed_image_url.value,
			description=self.embed_description.value,
			footer=self.embed_footer.value
		)
		await interaction.response.send_message(embed=embed)
	
	async def on_error(self, interaction: lib.discord.Interaction, error: Exception) -> None:
		"""
		DESCRIPTION: Fires on error of Settings Modal
		PARAMETERS: discord.Interaction - Discord Interaction
		"""
		message = GeneralFunctions.modal_error_check(error)
		await interaction.response.send_message(message, ephemeral=True)
		logger.error(f"An error occurred: {error}")

class Admin(lib.commands.Cog):
	"""
	DESCRIPTION: Creates Admin class
	PARAMETERS: commands.Bot - Discord Commands
	"""
	def __init__(self, bot):
		self.bot = bot
		self.general_functions = GeneralFunctions()

	# Clear Messages from channel, ex !clear 50
	@lib.commands.command(aliases=["purge", "delete"])
	@lib.commands.is_owner()
	async def clear(self, ctx, amount=None):
		"""
		DESCRIPTION: Clears messages from channel
		PARAMETERS: ctx - context of message
					amount - number of messages to delete
		RETURNS: None
		"""
		if amount is None:
			await ctx.send("You must enter a number after the !clear")
		else:
			val = int(amount)
			if val <= 0:
				await ctx.send("You must enter a number greater than 0")
			else:
				await ctx.channel.purge(limit=val)
				logger.info(f"Removed {val} messages")

	@lib.commands.command()
	@lib.commands.is_owner()
	async def reload(self, ctx, extension):
		"""
		DESCRIPTION: Reloads a cog
		PARAMETERS: ctx - context of message
					extension - name of cog to reload
		RETURNS: None
		"""
		try:
			await self.bot.unload_extension(extension)
			await self.bot.load_extension(extension)
			await ctx.send(f"Reloaded {extension}")
			logger.info(f"Reloaded {extension}")
		except Exception as e: # pylint: disable=broad-except
			await ctx.send(f"Error reloading {extension}, Cause: {e}")
			logger.error(f"Error reloading {extension}: {e}")

	@lib.discord.app_commands.command(name="embedcreator", description="Create an Embed")
	async def embed_creator(self, interaction: lib.discord.Interaction):
		"""
		DESCRIPTION: Creates an Embed
		PARAMETERS: interaction - Discord Interaction
		"""
		logger.info(f"Creating Embed creator modal for user: {interaction.user.name}")
		await interaction.response.send_modal(EmbedCreatorModal())

async def setup(bot):
	await bot.add_cog(Admin(bot))
