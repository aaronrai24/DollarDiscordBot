"""
DESCRIPTION: Debugging functions reside here
"""
#pylint: disable=useless-parent-delegation
from ..common.libraries import (
	discord, os, commands, threading, traceback, sys, time,
	psutil, asyncio, requests, json, logging, START_TIME, 
	GITHUB_TOKEN
)
from ..common.generalfunctions import GeneralFunctions

logger = GeneralFunctions.setup_logger("diagnostic")

class ReportBugModel(discord.ui.Modal, title="Report Bug"):
	"""
	DESCRIPTION: Creates Report Bug Model
	PARAMETERS: discord.ui.modal - Discord Modal
	"""

	def __init__(self):
		super().__init__()
	
	bug_title = discord.ui.TextInput(label="Bug Title", placeholder="Enter Bug Title", required=True)
	bug_description = discord.ui.TextInput(placeholder="Enter a detailed description of the bug", label="Bug Description", required=True)

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
			await interaction.response.send_message("Bug report submitted successfully.", ephemeral=True)
		else:
			await interaction.response.send_message("Failed to add bug report to GitHub issues.", ephemeral=True)
			logger.error(f"Failed to add bug report to GitHub issues: {response.text}")

	async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
		"""
		DESCRIPTION: Fires on error of Settings Modal
		PARAMETERS: discord.Interaction - Discord Interaction
		"""
		message = GeneralFunctions.modal_error_check(error)
		await interaction.response.send_message(message, ephemeral=True)
		logger.error(f"An error occurred: {error}")

class FeatureRequestModel(discord.ui.Modal, title="Feature Request"):
	"""
	DESCRIPTION: Creates Feature Request Model
	PARAMETERS: discord.ui.modal - Discord Modal
	"""

	def __init__(self):
		super().__init__()

	feature_title = discord.ui.TextInput(label="Feature Title", placeholder="Enter Feature Title", required=True)
	feature_description = discord.ui.TextInput(placeholder="Enter a detailed description of the feature", label="Feature Description", required=True)
 
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
			await interaction.response.send_message("Feature request submitted successfully.", ephemeral=True)
		else:
			await interaction.response.send_message("Failed to add feature request to GitHub issues.", ephemeral=True)
			logger.error(f"Failed to add feature request to GitHub issues: {response.text}")
	
	async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
		"""
		DESCRIPTION: Fires on error of Settings Modal
		PARAMETERS: discord.Interaction - Discord Interaction
		"""
		message = GeneralFunctions.modal_error_check(error)
		await interaction.response.send_message(message, ephemeral=True)
		logger.error(f"An error occurred: {error}")

class HelpView(discord.ui.View):
	"""
	DESCRIPTION: Creates Help View
	PARAMETERS: discord.ui.View - Discord View
	"""
	def __init__(self):
		super().__init__()
		self.add_item(MyButton(label="Music", style=discord.ButtonStyle.green, custom_id="music"))
		self.add_item(MyButton(label="Game", style=discord.ButtonStyle.blurple, custom_id="game"))
		self.add_item(MyButton(label="Slash", style=discord.ButtonStyle.red, custom_id="slash"))

class MyButton(discord.ui.Button):
	"""
	DESCRIPTION: Creates Button for Help View
	PARAMETERS: discord.ui.Button - Discord Button
	"""

	async def callback(self, interaction: discord.Interaction):
		"""
		DESCRIPTION: Fires on button click
		PARAMETERS: interaction - Discord Interaction
		"""
		dollar = await GeneralFunctions.get_bot_member(interaction.guild, interaction.client)
		command_type = str(self.custom_id)

		if command_type:
			await self.send_commands(interaction, command_type, dollar)

	async def send_commands(self, interaction, command_type, dollar):
		"""
		DESCRIPTION: Send commands based on command type
		PARAMETERS: interaction - Discord Interaction, command_type - Command Type, dollar - Dollar Bot
		"""
		logger.debug(f"Sending {command_type} commands for user {interaction.user.name}")
		file_path = os.path.join("markdown", f"{command_type}Commands.md")
		try:
			with open(file_path, "r", encoding="utf-8") as file:
				dollar_commands = file.read()
				embed = GeneralFunctions.create_embed(f"{command_type.capitalize()} Commands", dollar_commands, dollar)
				await interaction.response.send_message(embed=embed)
		except FileNotFoundError:
			logger.error(f"File {file_path} not found")
		except Exception as e:
			logger.error(f"Failed to send commands: {e}")

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
		await interaction.response.send_modal(ReportBugModel())

	@discord.app_commands.command(name="featurerequest", description="Submit a feature request to the developer")
	async def featurerequest(self, interaction: discord.Interaction):
		"""
		DESCRIPTION: Submit a feature request
		PARAMETERS: interaction - Discord interaction
		"""
		logger.info(f"Creating Feature Request Model for user {interaction.user.name}")
		await interaction.response.send_modal(FeatureRequestModel())

	@discord.app_commands.command(name="help", description="See available commands for Dollar")
	async def help(self, interaction: discord.Interaction):
		"""
		DESCRIPTION: Show available commands
		PARAMETERS: interaction - Discord interaction
		"""
		logger.info(f"Creating Help View for user {interaction.user.name}")
		await interaction.response.send_message("Which commands?", view=HelpView())

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
