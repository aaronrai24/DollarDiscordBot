from ..common.libraries import(
    commands, ADMIN, MOD
)
from ..common.generalFunctions import(
    setup_logger
)

logger = setup_logger('administrative')

class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    # Clear Messages from channel, ex !clear 50
    @commands.command(aliases=['purge', 'delete'])
    @commands.check_any(commands.has_role(ADMIN), commands.has_role(MOD))
    async def clear(self, ctx, amount=None):
        if (amount is None):
            await ctx.send("You must enter a number after the !clear")
        else:
            val = int(amount)
            if (val <= 0):
                await ctx.send("You must enter a number greater than 0")
            else:
                await ctx.channel.purge(limit=val)
                logger.info(f'Removed {val} messages')

async def setup(bot):
    await bot.add_cog(Admin(bot))