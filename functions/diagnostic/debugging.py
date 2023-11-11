"""
DESCRIPTION: Debugging functions reside here
"""
from ..common.libraries import (
	discord, os, commands, threading, traceback, sys, time,
	psutil, asyncio, requests, json, logging, ADMIN, 
	MOD, START_TIME, user_usage, GITHUB_TOKEN
)
from ..common.generalfunctions import(
	setup_logger
)

logger = setup_logger("diagnostic")

class Debugging(commands.Cog):
	"""
	DESCRIPTION: Creates Debugging Class
	PARAMETERS: commands.Bot - Discord Commands
	"""
	def __init__(self, bot):
		self.bot = bot

	# /status App command, Check dollar diagnostics, CPU, RAM, Uptime
	@discord.app_commands.command(name="status", description="Dollar server status, CPU usage, Memory usage, Uptime, etc.")
	async def status(self, interaction: discord.Interaction):
		uptime = time.time() - START_TIME
		uptime_formatted = time.strftime("%H:%M:%S", time.gmtime(uptime))
		cpu_percent = psutil.cpu_percent()
		ram_usage = psutil.virtual_memory().percent
		response_message = f"Bot is currently online and running smoothly.\n\nUptime: {uptime_formatted}\nCPU Load: {cpu_percent}%\nRAM Usage: {ram_usage}%"
		await interaction.response.send_message(response_message)

	# /setup App command, setup JOIN HERE and commands text channel automatically
	@discord.app_commands.command(name="setup", description="Automatically create all requirements to use all of Dollar\"s features")
	async def setup(self, interaction: discord.Interaction):
		guild = interaction.guild
		logger.info(f"/setup used in {guild}, creating requirements")

		# Check if voice channel "JOIN HERE" already exists
		voice_channel_exists = discord.utils.get(guild.voice_channels, name="JOIN HERE💎")
		if voice_channel_exists:
			logger.warning(f"JOIN HERE💎 already exists in {guild}")
		else:
			await guild.create_voice_channel("JOIN HERE💎")
			logger.info(f"Created JOIN HERE💎 in {guild}")

		# Check if text channel "commands" already exists
		text_channel_exists = discord.utils.get(guild.text_channels, name="commands")
		if text_channel_exists:
			logger.warning(f"commands already exists in {guild}")
		else:
			await guild.create_text_channel("commands")
			logger.info(f"Created commands in {guild}")
		
		# Check if voice_channel "Shows" already exists
		show_channel_exists = discord.utils.get(guild.voice_channels, name="Shows📺")
		if show_channel_exists:
			logger.warning(f"Shows📺 already exists in {guild}")
		else:
			await guild.create_voice_channel("Shows📺")
			logger.info(f"Created Shows📺 in {guild}")
	
		await interaction.response.send_message("Voice channel and text channels created successfully, use !help in the #commands text channel for more info.", ephemeral=True)

	# /reportbug, Submit a bug
	@discord.app_commands.command(name="reportbug", description="Report a bug to the developer")
	async def reportbug(self, interaction: discord.Interaction, bug_title: str, bug_description: str):
		author = interaction.user
		server = interaction.guild

		# Check if user has exceeded rate limit
		now = time.time()
		user_info = user_usage[author.id]
		if now - user_info["timestamp"] < 3600 and user_info["count"] >= 3:
			await interaction.response.send_message("You have exceeded the rate limit for this command. Please try again later.", ephemeral=True)
			return
		
		# Update user usage information
		user_info["timestamp"] = now
		user_info["count"] += 1
		
		# Proceed with command as normal
		#pylint: disable=line-too-long
		embed = discord.Embed(title="Bug Report", description=f"AUTHOR: {author} DISCORD: {server}\n\nTitle: {bug_title}\n\nDescription: {bug_description}", color=discord.Color.green())
		logger.info(f"{author} submitted a bug in {server}")

		# Send the bug report to the developer
		user = await self.bot.fetch_user("223947980309397506")
		message = await user.send(embed=embed)
		await interaction.response.send_message("Bug report submitted successfully!", ephemeral=True)

		# Add reactions for accepting and declining the bug report, as well as bug in progress and completion
		await message.add_reaction("✅")  # Accept Bug report
		await message.add_reaction("❌")  # Decline Bug report

		# Create a check function for the reactions
		def check(reaction, user):
			return user and str(reaction.emoji) in ["✅", "❌"]

		# Wait for a reaction from the developer
		try:
			reaction, user = await self.bot.wait_for("reaction_add", check=check)
		except asyncio.TimeoutError:
			await message.reply("The bug report was not accepted or declined in time.", mention_author=False)
			logger.warning("Developer did not accept/decline bug report, timing out")
			return

		# Notify the user who submitted the bug report whether it was accepted or declined
		if str(reaction.emoji) == "✅":
			user_embed = discord.Embed(title="Bug Report", description=f"Your bug report regarding '{bug_title}' has been accepted!", color=discord.Color.green())
			# Create the issue payload
			issue_title = bug_title
			issue_body = f"Bug report: {bug_description}\n\nSubmitted by: {author}\nServer: {server}"
			payload = {"title": issue_title, "body": issue_body, "labels": ["bug"]}

			# Define the necessary variables
			repository = "DollarDiscordBot"
			owner = "aaronrai24"
			access_token = GITHUB_TOKEN

			# Define the API endpoint for creating an issue
			url = f"https://api.github.com/repos/{owner}/{repository}/issues"

			# Add authentication using your access token
			headers = {"Authorization": f"token {access_token}"}

			# Send the POST request to create the issue
			response = requests.post(url, headers=headers, data=json.dumps(payload))

			# Check the response status code
			if response.status_code == 201:
				logger.info("Added bug report to GitHub issues")
			else:
				await message.reply("Failed to add bug report to GitHub issues.", mention_author=False)
				logger.error(f"Failed to add bug report to GitHub issues: {response.text}")

		else:
			user_embed = discord.Embed(title="Bug Report", description=f"Your bug report regarding '{bug_title}' has been declined.", color=discord.Color.red())
		
		try:
			await author.send(embed=user_embed)
			logger.info(f"Sent notification to {author}")
		except discord.errors.Forbidden:
			logger.warning(f"Failed to send notification to {author} (user has blocked the bot)")

	# /featurerequest, Submit a feature request
	@discord.app_commands.command(name="featurerequest", description="Submit a feature request to the developer")
	async def featurerequest(self, interaction: discord.Interaction, feature_title: str, feature_description: str):
		author = interaction.user
		server = interaction.guild
		
		# Check if user has exceeded rate limit
		now = time.time()
		user_info = user_usage[author.id]
		if now - user_info["timestamp"] < 3600 and user_info["count"] >= 3:
			await interaction.response.send_message("You have exceeded the rate limit for this command. Please try again later.", ephemeral=True)
			return
		
		# Update user usage information
		user_info["timestamp"] = now
		user_info["count"] += 1
		
		# Proceed with command as normal
		#pylint: disable=line-too-long
		embed = discord.Embed(title="Feature Request", description=f"AUTHOR: {author} DISCORD: {server}\n\nTitle: {feature_title}\n\nDescription: {feature_description}", color=discord.Color.green())
		logger.info(f"{author} submitted a feature request in {server}")

		# Send the feature request to the developer
		user = await self.bot.fetch_user("223947980309397506")
		message = await user.send(embed=embed)
		await interaction.response.send_message("Feature request submitted successfully!", ephemeral=True)

		# Add reactions for accepting and declining the feature request
		await message.add_reaction("✅")  # Accept feature request
		await message.add_reaction("❌")  # Decline feature request

		# Create a check function for the reactions
		def check(reaction, user):
			return user and str(reaction.emoji) in ["✅", "❌"]

		# Wait for a reaction from the developer
		try:
			reaction, user = await self.bot.wait_for("reaction_add", check=check)
		except asyncio.TimeoutError:
			await message.reply("The feature request was not accepted or declined in time.", mention_author=False)
			logger.warning("Developer did not accept/decline feature request, timing out")
			return
		
		# Notify the user who submitted the feature request whether it was accepted or declined
		if str(reaction.emoji) == "✅":
			user_embed = discord.Embed(title="Feature Request", description=f"Your feature request regarding '{feature_title}' has been accepted!", color=discord.Color.green())
			
			# Create the issue payload
			issue_title = feature_title
			issue_body = f"Feature request: {feature_description}\n\nSubmitted by: {author}\nServer: {server}"
			payload = {"title": issue_title, "body": issue_body, "labels": ["enhancement"]}  # Add "enhancement" label to the issue

			# Define the necessary variables
			repository = "DollarDiscordBot"
			owner = "aaronrai24"
			access_token = GITHUB_TOKEN

			# Define the API endpoint for creating an issue
			url = f"https://api.github.com/repos/{owner}/{repository}/issues"

			# Add authentication using your access token
			headers = {"Authorization": f"token {access_token}"}

			# Send the POST request to create the issue
			response = requests.post(url, headers=headers, data=json.dumps(payload))

			# Check the response status code
			if response.status_code == 201:
				logger.info("Added feature request to GitHub issues")
			else:
				await message.reply("Failed to add feature request to GitHub issues.", mention_author=False)
				logger.error(f"Failed to add feature request to GitHub issues: {response.text}")
		else:
			user_embed = discord.Embed(title="Feature Request", description=f"Your feature request regarding '{feature_title}' has been declined.", color=discord.Color.red())
		
		try:
			await author.send(embed=user_embed)
			logger.info(f"Sent notification to {author}")
		except discord.errors.Forbidden:
			logger.warning(f"Failed to send notification to {author} (user has blocked the bot)")

	# /ticket, Open an issue in the mfDiscord(get access to the #issues channel)
	@discord.app_commands.command(name="ticket", description="Open a issue with the developers when you are having issues with Dollar")
	async def ticket(self, interaction: discord.Interaction):
		author = interaction.user
		server = interaction.guild
		
		# Check if user has exceeded rate limit
		now = time.time()
		user_info = user_usage[author.id]
		if now - user_info["timestamp"] < 3600 and user_info["count"] >= 3:
			await interaction.response.send_message("You have exceeded the rate limit for this command. Please try again later.", ephemeral=True)
			return
		
		# Update user usage information
		user_info["timestamp"] = now
		user_info["count"] += 1

		guild_id = 261351089864048645
		mf_discord = discord.utils.get(self.bot.guilds, id=guild_id)
		issues_channel = discord.utils.get(mf_discord.text_channels, name="issues")

		if not issues_channel:
			await interaction.response.send_message("The issues channel could not be found, please try again later.", ephemeral=True)
			return

		# Create an invite with a 30-minute expiration for the issues channel
		invite = await issues_channel.create_invite(max_age=1800, unique=True)

		channel = await self.bot.fetch_channel("1117217882070323291")
		dev_role_id = 1112192013903872100
		qa_role_id = 1097642643133051032

		dev_role_mention = f"<@&{dev_role_id}>"
		qa_role_mention = f"<@&{qa_role_id}>"

		await channel.send(f"Issue occurred while using Dollar for {author}. {dev_role_mention}{qa_role_mention} Please grant {author} access to view this channel.")
		# Send the invite as a direct message to the user
		try:
			await author.send(f"Here's your invite link to the #issues channel: {invite}")
			await interaction.response.send_message("An invite link has been sent to your DMs.", ephemeral=True)
			logger.info(f"Issue likely occured in {server}, author: {author}")
		except discord.Forbidden:
			await interaction.response.send_message("I cannot send you the invite link because you have disabled DMs.", ephemeral=True)
			logger.warning(f"{author} has likely disabled DMs" )

	@commands.command()
	async def help(self, ctx, category=None):

		if category is None:
			desc = "Available categories: music, game, mywatchlist. Use either !help music or !help game or !help mywatchlist"
			embed = discord.Embed(title="Which commands?", description=desc, colour=0x2ecc71)
			embed.set_author(name="Dollar")
			file_path = os.path.join("images", "dollar3.png")
			img = discord.File(file_path, filename="dollar3.png")
			embed.set_thumbnail(url="attachment://dollar3.png")
			embed.set_footer(text="Feature request? Bug? Please report it by using /reportbug or /featurerequest")
			await ctx.send(embed=embed, file=img)
		elif category.lower() == "music":
			file_path = os.path.join("markdown", "musicCommands.md")
			if os.path.isfile(file_path):
				with open(file_path, "r", encoding="utf-8") as file:
					bot_commands = file.read()

			embed = discord.Embed(title="Music Commands", description=bot_commands, colour=0x2ecc71)
			embed.set_author(name="Dollar")
			file_path = os.path.join("images", "dollar3.png")
			img = discord.File(file_path, filename="dollar3.png")
			embed.set_thumbnail(url="attachment://dollar3.png")
			embed.set_footer(text="Feature request? Bug? Please report it by using /reportbug or /featurerequest")
			await ctx.send(embed=embed, file=img)
		elif category.lower() == "game":
			file_path = os.path.join("markdown", "gameCommands.md")
			if os.path.isfile(file_path):
				with open(file_path, "r", encoding="utf-8") as file:
					game_commands = file.read()

			embed = discord.Embed(title="Game Commands", description=game_commands, colour=0x2ecc71)
			embed.set_author(name="Dollar")
			file_path = os.path.join("images", "dollar3.png")
			img = discord.File(file_path, filename="dollar3.png")
			embed.set_thumbnail(url="attachment://dollar3.png")
			embed.set_footer(text="Feature request? Bug? Please report it by using /reportbug or /featurerequest")
			await ctx.send(embed=embed, file=img)
		elif category.lower() == "mywatchlist":
			file_path = os.path.join("markdown", "watchlistCommands.md")
			if os.path.isfile(file_path):
				with open(file_path, "r", encoding="utf-8") as file:
					watchlist_commands = file.read()

			embed = discord.Embed(title="MyWatchList Commands", description=watchlist_commands, colour=0x2ecc71)
			embed.set_author(name="Dollar")
			file_path = os.path.join("images", "dollar3.png")
			img = discord.File(file_path, filename="dollar3.png")
			embed.set_thumbnail(url="attachment://dollar3.png")
			embed.set_footer(text="Feature request? Bug? Please report it by using /reportbug or /featurerequest")
			await ctx.send(embed=embed, file=img)
		else:
			await ctx.send("Invalid category. Available categories: music, game, mywatchlist")

	# Admin only, see Dollar"s current threads
	@commands.command()
	@commands.check_any(commands.has_role(ADMIN), commands.has_role(MOD))
	async def threaddump(self, ctx):
		logger.info("START THREAD DUMP")
		thread_list = threading.enumerate()

		# Find the highest existing thread dump number
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

		# Check if the dump file with the same number already exists
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

	# Admin and mod only, see Dollar"s current logs
	@commands.command()
	@commands.check_any(commands.has_role(ADMIN), commands.has_role(MOD))
	async def logs(self, ctx):
		log_file_name = "discord.log"
		log_file_path = os.path.join(os.getcwd(), log_file_name)

		if not os.path.isfile(log_file_path):
			await ctx.send(f"Log file '{log_file_name}' not found.")
			return

		channel = ctx.channel
		with open(log_file_path, "rb") as file:
			log_file = discord.File(file, filename=log_file_name)
			await channel.send(file=log_file)
	
	# Set logging to certain level
	@commands.command()
	@commands.check_any(commands.has_role(ADMIN), commands.has_role(MOD))
	async def logging(self, ctx, level):
		level = getattr(logging, level.upper(), None)
		if level == 20:
			logging.getLogger("discord.gateway").setLevel(logging.WARNING)
		if level is None:
			await ctx.send("Invalid logging level provided.")
			return

		for name in logging.root.manager.loggerDict.items():
			if isinstance(name, logging.Logger):
				logger.setLevel(level)

		await ctx.send(f"Logging level set to {level}.")

async def setup(bot):
	await bot.add_cog(Debugging(bot))
