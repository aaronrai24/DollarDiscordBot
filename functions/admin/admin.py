"""
DESCRIPTION: Admin/Mod only commands reside here
"""
import functions.common.libraries as lib
from ..common.generalfunctions import GeneralFunctions

logger = GeneralFunctions.setup_logger("administrative")

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

async def setup(bot):
	await bot.add_cog(Admin(bot))
