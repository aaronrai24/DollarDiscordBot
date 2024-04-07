"""
DESCRIPTION: Debugging functions reside here
"""
from ..common.libraries import (
	discord, os, commands, threading, traceback, sys, time,
	psutil, asyncio, requests, json, logging, START_TIME, 
	user_usage, GITHUB_TOKEN
)
from ..common.generalfunctions import GeneralFunctions

logger = GeneralFunctions.setup_logger("diagnostic")

class ReportBugModel(discord.ui.modal, title="Report Bug"):
	"""
	DESCRIPTION: Creates Report Bug Model
	PARAMETERS: discord.ui.modal - Discord Modal
	"""

	def __init__(self, bot):
		self.bot = bot
	
	bug_title = discord.ui.TextInput(label="Bug Title", placeholder="Enter Bug Title", required=True)
	bug_description = discord.ui.TextArea(placeholder='Enter a detailed description of the bug', label='Bug Description', required=True)

	async def on_submit(self, interaction: discord.Interaction):
		"""
		DESCRIPTION: Fires on submit of Report Bug Model
		PARAMETERS: interaction - Discord Interaction
		"""
		bug_title = self.bug_title.value
		bug_description = self.bug_description.value
		author = interaction.user
		server = interaction.guild

		issue_body = f"Bug report: {bug_description}\n\nSubmitted by: {author}\nServer: {server}"
		payload = {"title": bug_title, "body": issue_body, "labels": ["bug"]}

		repository = "DollarDiscordBot"
		owner = "aaronrai24"
		access_token = GITHUB_TOKEN

		url = f"https://api.github.com/repos/{owner}/{repository}/issues"

		headers = {"Authorization": f"token {access_token}"}

		response = requests.post(url, headers=headers, data=json.dumps(payload))

		if response.status_code == 201:
			logger.info("Added bug report to GitHub issues")
		else:
			await interaction.response.send_message("Failed to add bug report to GitHub issues.", ephemeral=True)
			logger.error(f"Failed to add bug report to GitHub issues: {response.text}")

	async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
		"""
		DESCRIPTION: Fires on error of Settings Modal
		PARAMETERS: discord.Interaction - Discord Interaction
		"""
		if isinstance(error, discord.NotFound):
			message = "Oops! The item you were looking for was not found. Please report this bug using /reportbug."
		elif isinstance(error, discord.Forbidden):
			message = "Oops! I don't have permission to do that. Please report this bug using /reportbug."
		elif isinstance(error, discord.HTTPException):
			message = "Oops! Something went wrong with the Discord server. Please report this bug using /reportbug."
		else:
			message = "Oops! Something went wrong. Please report this bug using /reportbug."

		await interaction.response.send_message(message, ephemeral=True)
		logger.error(f"An error occurred: {error}")

class FeatureRequestModel(discord.ui.modal, title="Feature Request"):
	"""
	DESCRIPTION: Creates Feature Request Model
	PARAMETERS: discord.ui.modal - Discord Modal
	"""

	def __init__(self, bot):
		self.bot = bot

	feature_title = discord.ui.TextInput(label="Feature Title", placeholder="Enter Feature Title", required=True)
	feature_description = discord.ui.TextArea(placeholder='Enter a detailed description of the feature', label='Feature Description', required=True)

	async def on_submit(self, interaction: discord.Interaction):
		"""
		DESCRIPTION: Fires on submit of Feature Request Model
		PARAMETERS: interaction - Discord Interaction
		"""
		feature_title = self.feature_title.value
		feature_description = self.feature_description.value
		author = interaction.user
		server = interaction.guild
		
		issue_body = f"Feature request: {feature_description}\n\nSubmitted by: {author}\nServer: {server}"
		payload = {"title": feature_title, "body": issue_body, "labels": ["enhancement"]}

		repository = "DollarDiscordBot"
		owner = "aaronrai24"
		access_token = GITHUB_TOKEN

		url = f"https://api.github.com/repos/{owner}/{repository}/issues"

		headers = {"Authorization": f"token {access_token}"}

		response = requests.post(url, headers=headers, data=json.dumps(payload))

		if response.status_code == 201:
			logger.info("Added feature request to GitHub issues")
		else:
			await interaction.response.send_message("Failed to add feature request to GitHub issues.", ephemeral=True)
			logger.error(f"Failed to add feature request to GitHub issues: {response.text}")
	
	async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
		"""
		DESCRIPTION: Fires on error of Settings Modal
		PARAMETERS: discord.Interaction - Discord Interaction
		"""
		if isinstance(error, discord.NotFound):
			message = "Oops! The item you were looking for was not found. Please report this bug using /reportbug."
		elif isinstance(error, discord.Forbidden):
			message = "Oops! I don't have permission to do that. Please report this bug using /reportbug."
		elif isinstance(error, discord.HTTPException):
			message = "Oops! Something went wrong with the Discord server. Please report this bug using /reportbug."
		else:
			message = "Oops! Something went wrong. Please report this bug using /reportbug."

		await interaction.response.send_message(message, ephemeral=True)
		logger.error(f"An error occurred: {error}")

class Debugging(commands.Cog):
	"""
	DESCRIPTION: Creates Debugging Class
	PARAMETERS: commands.Bot - Discord Commands
	"""
	def __init__(self, bot):
		self.bot = bot

	@discord.app_commands.command(name="status", description="Dollar server status, CPU usage, Memory usage, Uptime, etc.")
	async def status(self, interaction: discord.Interaction):
		"""
		DESCRIPTION: Check dollar diagnostics, CPU, RAM, Uptime
		PARAMETERS: interaction - Discord interaction
		"""
		uptime = time.time() - START_TIME
		uptime_days = uptime // (24 * 3600)
		uptime = uptime % (24 * 3600)
		uptime_hours = uptime // 3600
		uptime_minutes = (uptime % 3600) // 60
		uptime_seconds = uptime % 60
		uptime_formatted = f"{int(uptime_days)}d {int(uptime_hours)}h {int(uptime_minutes)}m {int(uptime_seconds)}s"
		cpu_percent = psutil.cpu_percent()
		ram_usage = psutil.virtual_memory().percent
		response_message = f"Bot is currently online and running smoothly.\n\nUptime: {uptime_formatted}\nCPU Load: {cpu_percent}%\nRAM Usage: {ram_usage}%"
		await interaction.response.send_message(response_message)

	@discord.app_commands.command(name="reportbug", description="Report a bug to the developer")
	async def reportbug(self, interaction: discord.Interaction):
		"""
		DESCRIPTION: Submit a bug
		PARAMETERS: interaction - Discord interaction
		"""
		logger.info(f"Creating Report Bug Model for user {interaction.user.name}")
		await interaction.response.send_message("Please fill out the form to report a bug.", ephemeral=True)

	@discord.app_commands.command(name="featurerequest", description="Submit a feature request to the developer")
	async def featurerequest(self, interaction: discord.Interaction, feature_title: str, feature_description: str):
		"""
		DESCRIPTION: Submit a feature request
		PARAMETERS: interaction - Discord interaction
		"""
		logger.info(f"Creating Feature Request Model for user {interaction.user.name}")
		await interaction.response.send_message("Please fill out the form to submit a feature request.", ephemeral=True)

	@commands.command()
	async def help(self, ctx, category=None):
		"""
		DESCRIPTION: Help command for Dollar
		PARAMETERS: ctx - Discord Context, category - category of commands
		"""
		if category is None:
			desc = "Available categories: music, game, mywatchlist. Use either !help music or !help game or !help mywatchlist"
			await GeneralFunctions.send_embed("Which commands?", "dollar3.png", desc, ctx)
		elif category.lower() == "music":
			file_path = os.path.join("markdown", "musicCommands.md")
			if os.path.isfile(file_path):
				with open(file_path, "r", encoding="utf-8") as file:
					bot_commands = file.read()
			await GeneralFunctions.send_embed("Music Commands", "dollar3.png", bot_commands, ctx)
		elif category.lower() == "game":
			file_path = os.path.join("markdown", "gameCommands.md")
			if os.path.isfile(file_path):
				with open(file_path, "r", encoding="utf-8") as file:
					game_commands = file.read()
			await GeneralFunctions.send_embed("Game Commands", "dollar3.png", game_commands, ctx)
		else:
			await ctx.send("Invalid category. Available categories: music, game, mywatchlist")

	@commands.command()
	@commands.is_owner()
	async def threaddump(self, ctx):
		"""
		DESCRIPTION: See Dollar's current threads
		PARAMETERS: ctx - Discord Context
		"""
		logger.info("START THREAD DUMP")
		thread_list = threading.enumerate()

		existing_dumps = [file for file in os.listdir() if file.startswith("dollar-thread-dump-")]
		max_dump_number = 0
		for dump in existing_dumps:
			try:
				dump_number = int(dump.split("-")[-1].split(".")[0])
				max_dump_number = max(max_dump_number, dump_number)
			except ValueError:
				pass

		dump_number = max_dump_number + 1
		dump_file_name = f"dollar-thread-dump-{dump_number}.txt"

		while dump_file_name in existing_dumps:
			dump_number += 1
			dump_file_name = f"dollar-thread-dump-{dump_number}.txt"

		with open(dump_file_name, "w", encoding="utf-8") as file:
			for thread in thread_list:
				file.write(f"Thread: {thread.name}\n")
				file.write(f"Thread ID: {thread.ident}\n")  # Add thread ID
				file.write("Thread Stack Trace:\n")
				#pylint: disable=protected-access
				traceback.print_stack(sys._current_frames()[thread.ident], file=file)
				file.write("\n")

		channel = ctx.channel
		with open(dump_file_name, "rb") as file:
			dump_file = discord.File(file)
			await channel.send(file=dump_file)

		logger.info("FINISH THREAD DUMP")

	@commands.command()
	@commands.is_owner()
	async def logs(self, ctx):
		"""
		DESCRIPTION: See Dollar's current logs
		PARAMETERS: ctx - Discord Context
		"""
		log_file_name = "discord.log"
		log_file_path = os.path.join(os.getcwd(), log_file_name)

		if not os.path.isfile(log_file_path):
			await ctx.send(f"Log file '{log_file_name}' not found.")
			return

		channel = ctx.channel
		with open(log_file_path, "rb") as file:
			log_file = discord.File(file, filename=log_file_name)
			await channel.send(file=log_file)
	
	@commands.command()
	@commands.is_owner()
	async def logging(self, ctx, level):
		"""
		DESCRIPTION: Set logging to certain level
		PARAMETERS: ctx - Discord Context, level - logging level
		"""
		level = getattr(logging, level.upper(), None)
		if level is None:
			await ctx.send("Invalid logging level provided.")
			return
		#pylint: disable=redefined-outer-name
		for name, logger in logging.root.manager.loggerDict.items():
			if isinstance(logger, logging.Logger):
				logger.info(f"Setting {name} to {level}")
				logger.setLevel(level)

		await ctx.send(f"Logging level set to {level}.")

	@commands.command()
	@commands.is_owner()
	async def shutdown(self, ctx):
		"""
		DESCRIPTION: Shut down Dollar
		PARAMETERS: ctx - Discord Context
		"""
		try:
			logger.info("Starting shut down...")
			await ctx.send(f"{ctx.author.mention} Dollar is shutting down...")

			for task in asyncio.all_tasks():
				task.cancel()
				logger.debug(f"Shutdown task: {task}")
			logger.debug("Closing database connection...")
			self.bot.mydb.close()
			logger.info("Database connection closed")
			await self.bot.close()
		except Exception as e:
			logger.error(f"An error occured during shutdown {e}")

async def setup(bot):
	await bot.add_cog(Debugging(bot))
