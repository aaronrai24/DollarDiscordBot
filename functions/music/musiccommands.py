"""
DESCRIPTION: Music commands reside here
"""

from ..common.libraries import(
	discord, commands, genius, wavelink, random,
	sp, artist
)

from ..common.generalfunctions import GeneralFunctions
from ..common.generalfunctions import CustomPlayer
from ..queries.queries import Queries

logger = GeneralFunctions.setup_logger("music")

class Music(commands.Cog):
	"""
	DESCRIPTION: Creates Music class
	PARAMETERS: commands.Bot - Discord Commands
	"""
	def __init__(self, bot):
		self.bot = bot
		self.mydb = bot.mydb

#------------------------------------------------------------------------------------------------
# Listeners
	@commands.Cog.listener()
	async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload) -> None:
		track: wavelink.Playable = payload.track
		global artist
		artist = track.author
		
	@commands.Cog.listener()
	async def on_wavelink_track_end(self, payload: wavelink.TrackStartEventPayload) -> None:
		player: wavelink.Player = payload.player
		if not player.queue.is_empty:
			next_track = player.queue.get()
			await player.play(next_track)
			logger.info(f"Playing next track: {next_track}")
		else:
			logger.info("Queue is empty")
	
	@commands.Cog.listener()
	async def on_wavelink_inactive_player(self, player: wavelink.Player) -> None:
		logger.info(f"10 minutes reached, Dollar disconnecting from {str(player.guild)}")
		msg = f"10 minutes reached, Dollar disconnecting from {str(player.guild)}"
		guilds_text_channel = Queries.get_guilds_preferred_text_channel(self, player.guild.name)
		if guilds_text_channel:
			channel = discord.utils.get(player.guild.channels, name=guilds_text_channel)
		else:
			channel = discord.utils.get(player.guild.channels, name="commands")
		await channel.purge(limit=500)
		await GeneralFunctions.send_embed("Inactivity", "dollar4.png", msg, channel)
		await player.disconnect()

#------------------------------------------------------------------------------------------------
# Helper Functions
	async def ensure_voice_connection(self, ctx):
		"""
		DESCRIPTION: Ensures the bot is connected to a voice channel
		PARAMETERS: ctx - Discord Context
		RETURNS: vc - Voice Client
		"""
		vc = ctx.voice_client
		if not vc:
			custom_player = CustomPlayer()
			vc = await ctx.author.voice.channel.connect(cls=custom_player)
			await vc.set_volume(5)
		return vc

	async def create_embed(self, search, description):
		"""
		DESCRIPTION: Creates an embed for the song
		PARAMETERS: search - Search object, description - Description of the song
		RETURNS: embed - Discord Embed
		"""
		embed = discord.Embed(title=search.title, url=search.uri, description=description, color=discord.Color.random())
		embed.set_author(name=search.author)
		embed.set_thumbnail(url=search.artwork)
		return embed

	async def add_to_queue(self, vc, search):
		"""
		DESCRIPTION: Adds a song to the queue
		PARAMETERS: vc - Voice Client, search - Search object
		RETURNS: embed - Discord Embed
		"""
		vc.queue.put(search)
		embed = await self.create_embed(search, f"Added {search.title} to the Queue!")
		if vc.queue.is_empty:
			embed.set_footer(text="Queue is empty")
		else:
			nextitem = vc.queue.get()
			vc.queue.put_at(0, nextitem)
			embed.set_footer(text=f"Next song is: {nextitem}")
		return embed

	async def play_track(self, vc, search):
		"""
		DESCRIPTION: Plays a song
		PARAMETERS: vc - Voice Client, search - Search object
		RETURNS: embed - Discord Embed
		"""
		embed = await self.create_embed(search, f"Now Playing {search.title}!")
		await vc.play(search)
		return embed

#------------------------------------------------------------------------------------------------
# Commands
	@commands.command(aliases=["Join"])
	@GeneralFunctions.is_connected_to_voice()
	async def join(self, ctx):
		custom_player = CustomPlayer()
		vc: CustomPlayer = await ctx.author.voice.channel.connect(cls=custom_player)
		await vc.set_volume(5)  #NOTE: Set bot volume initially to 5

	@commands.command(aliases=["Leave", "Stop", "stop"])
	@GeneralFunctions.is_connected_to_same_voice()
	async def leave(self, ctx):
		vc = ctx.voice_client
		if vc:
			await vc.disconnect()
			await ctx.channel.purge(limit=500)
		else:
			raise commands.CheckFailure("The bot is not connected to a voice channel.")

	@commands.command(aliases=["Play", "p", "P"])
	@GeneralFunctions.is_connected_to_voice()
	async def play(self, ctx, *, query):
		tracks = await wavelink.Playable.search(query)
		search = tracks[0]
		vc = await self.ensure_voice_connection(ctx)

		if vc.playing:
			embed = await self.add_to_queue(vc, search)
			logger.info(f"Queued from YouTube: {search.title}")
		else:
			embed = await self.play_track(vc, search)
			logger.info(f"Playing from YouTube: {search.title}")

		await ctx.send(embed=embed)

	@commands.command(aliases=["Playskip", "PlaySkip"])
	@GeneralFunctions.is_connected_to_same_voice()
	async def playskip(self, ctx, *, query):
		tracks = await wavelink.Playable.search(query)
		search = tracks[0]
		vc = ctx.voice_client

		if vc:
			if vc.playing and not vc.paused:
				vc.queue.put_at(0, search)
				await vc.skip(force=False)
				embed = await self.create_embed(search, f"Now Playing {search.title}!")
				await ctx.send(embed=embed)
				logger.info(f"Playskipping to: {search.title}")
			elif vc.paused:
				msg = "The bot is currently paused, to playskip, first resume music with !resume"
				await GeneralFunctions.send_embed_error("Dollar is Paused", msg, ctx)
			else:
				msg = "Nothing is currently playing."
				await GeneralFunctions.send_embed_error("No Song Playing", msg, ctx)
		else:
			raise commands.CheckFailure("The bot is not connected to a voice channel.")

	@commands.command(aliases=["Lofi"])
	@GeneralFunctions.is_connected_to_same_voice()
	async def lofi(self, ctx):
		lofii_list = [
			"lofi hip hop radio - beats to relax/study to",
			"90's chill lofi study music lofi rain chillhop beats",
			"Autumn lofi vibes",
			"synthwave lofi",
			"chillhop radio - jazzy & lofi hip hop beats"
		]
		lofi = random.choice(lofii_list)
		all_tracks = await wavelink.Playable.search(lofi)
		logger.debug(f"Queried lofi tracks: {all_tracks}")

		if len(all_tracks) < 10:
			await ctx.send("Not enough lofi tracks found. Please try again.")
			return

		selected_tracks = random.sample(all_tracks, 10)
		
		vc = ctx.voice_client
		if not vc:
			raise commands.CheckFailure("The bot is not connected to a voice channel.")

		first_track = selected_tracks[0]
		embed = await self.play_track(vc, first_track)
		await ctx.send(embed=embed)
		logger.info(f"Playing from YouTube: {first_track.title}")

		for track in selected_tracks[1:]:
			await self.add_to_queue(vc, track)
			logger.info(f"Queued from YouTube: {track.title}")

	@commands.command(aliases=["Skip", "s", "S"])
	@GeneralFunctions.is_connected_to_same_voice()
	async def skip(self, ctx):
		vc = ctx.voice_client
		if vc:
			if not vc.playing:
				await ctx.message.add_reaction("\u274C")
				msg = "Nothing is currently playing."
				return await GeneralFunctions.send_embed_error("No Song Playing", msg, ctx)
			if vc.queue.is_empty:
				await ctx.message.add_reaction("\u2705")
				return await vc.stop()

			await ctx.message.add_reaction("\u2705")
			await vc.skip(force=False)
			logger.info("Skipping music")
			if vc.paused:
				await vc.pause(False)
		else:
			raise commands.CheckFailure("The bot is not connected to a voice channel.")

	@commands.command(aliases=["Replay"])
	@GeneralFunctions.is_connected_to_same_voice()
	async def replay(self, ctx):
		vc = ctx.voice_client
		if vc:
			if vc.playing:
				await vc.seek(0)
				await ctx.message.add_reaction("\u2705")
				logger.info("Replaying music")
			else:
				await ctx.message.add_reaction("\u274C")
				msg = "Nothing is currently playing"
				await GeneralFunctions.send_embed_error("No Song Playing", msg, ctx)
		else:
			raise commands.CheckFailure("The bot is not connected to a voice channel.")
	
	@commands.command(aliases=["Remove"])
	@GeneralFunctions.is_connected_to_same_voice()
	async def remove(self, ctx, index: int):
		vc = ctx.voice_client

		if vc:
			if vc.queue.is_empty:
				await ctx.message.add_reaction("\u274C")
				msg = "The queue is currently empty, add a song by using !play or !playsc"
				await GeneralFunctions.send_embed_error("Empty Queue", msg, ctx)
			else:
				try:
					vc.queue.delete(index - 1)
					await ctx.message.add_reaction("\u2705")
					logger.info(f"Removed song at index: {index} from queue")
				except IndexError:
					await ctx.message.add_reaction("\u274C")
					msg = "The index provided is out of range, please try again."
					await GeneralFunctions.send_embed_error("Index Out of Range", msg, ctx)
		else:
			raise commands.CheckFailure("The bot is not connected to a voice channel.")
	
	@commands.command(aliases=["Swap"])
	@GeneralFunctions.is_connected_to_same_voice()
	async def swap(self, ctx, song_one: int, song_two: int):
		vc = ctx.voice_client

		if vc:
			if vc.queue.is_empty:
				await ctx.message.add_reaction("\u274C")
				msg = "The queue is currently empty, add a song by using !play or !playsc"
				await GeneralFunctions.send_embed_error("Empty Queue", msg, ctx)
			else:
				try:
					vc.queue.swap(song_one - 1, song_two - 1)
					await ctx.message.add_reaction("\u2705")
					logger.info(f"Swapped song at index: {song_one} with song at index: {song_two}")
				except IndexError:
					await ctx.message.add_reaction("\u274C")
					msg = "The index provided is out of range, please try again."
					await GeneralFunctions.send_embed_error("Index Out of Range", msg, ctx)
		else:
			raise commands.CheckFailure("The bot is not connected to a voice channel.")
		
	@commands.command(aliases=["Shuffle"])
	@GeneralFunctions.is_connected_to_same_voice()
	async def shuffle(self, ctx):
		vc = ctx.voice_client

		if vc:
			if vc.queue.is_empty:
				await ctx.message.add_reaction("\u274C")
				msg = "The queue is currently empty, add a song by using !play or !playsc"
				await GeneralFunctions.send_embed_error("Empty Queue", msg, ctx)
			else:
				vc.queue.shuffle()
				await ctx.message.add_reaction("\u2705")
				logger.info("Shuffled queue")
		else:
			raise commands.CheckFailure("The bot is not connected to a voice channel.")

	@commands.command(aliases=["Resume", "Pause", "resume", "pause"])
	@GeneralFunctions.is_connected_to_same_voice()
	async def pause_resume(self, ctx):
		vc = ctx.voice_client
		if vc:
			if vc.paused:
				await vc.pause(False)
				await ctx.message.add_reaction("\u25B6")
				logger.info("Resuming music")
			else:
				await vc.pause(True)
				await ctx.message.add_reaction("\u23F8")
				logger.info("Pausing music")
		else:
			raise commands.CheckFailure("The bot is not connected to a voice channel.")

	@commands.command(aliases=["Nowplaying", "NowPlaying", "np"])
	@GeneralFunctions.is_connected_to_same_voice()
	async def nowplaying(self, ctx):
		vc = ctx.voice_client
		track = str(vc.current)

		if vc.playing:
			desc = "Currently playing: " + track
			await GeneralFunctions.send_embed("Currently Playing", "dollarMusic.png", desc, ctx)
		else:
			msg = "There are no songs currently playing, you can queue one by using !play or !playsc"
			raise commands.CheckFailure(msg)

	@commands.command(aliases=["Next", "nextsong"])
	@GeneralFunctions.is_connected_to_same_voice()
	async def next(self, ctx):
		vc = ctx.voice_client
		if vc:
			try:
				search = vc.queue.get()
				vc.queue.put_at(0, search)
				msg = f"The next song is: {search}"
				await GeneralFunctions.send_embed("Next Song...", "dollarMusic.png", msg, ctx)
				logger.info("Printing next song in queue")
			except:
				msg = "The queue is currently empty, add a song by using !play or !playsc"
				await GeneralFunctions.send_embed_error("Empty Queue", msg, ctx)
		else:
			raise commands.CheckFailure("The bot is not connected to a voice channel")

	@commands.command(aliases=["Seek"])
	@GeneralFunctions.is_connected_to_same_voice()
	async def seek(self, ctx, seek=0):
		vc = ctx.voice_client
		val = int(seek)
		if vc:
			if vc.playing and not vc.paused:
				await vc.seek(vc.current.length * val)
				await ctx.message.add_reaction("\u2705")
				logger.info(f"Song seeked for {val} seconds")
			else:
				await ctx.message.add_reaction("\u274C")
				msg = "Nothing is currently playing"
				await GeneralFunctions.send_embed_error("No Song Playing", msg, ctx)
		else:
			raise commands.CheckFailure("The bot is not connected to a voice channel")

	@commands.command(aliases=["Volume"])
	@GeneralFunctions.is_connected_to_same_voice()
	async def volume(self, ctx, volume):
		vc = ctx.voice_client
		val = int(volume)
		if vc and (0 < val <= 100):
			await vc.set_volume(val)
			await ctx.message.add_reaction("\u2705")
			logger.info(f"Bot volume set to: {val}")
		else:
			raise commands.CheckFailure("The bot is not connected to a voice channel")

	@commands.command(aliases=["Queue"])
	@GeneralFunctions.is_connected_to_same_voice()
	async def queue(self, ctx):
		vc = ctx.voice_client
		desc = ""
		if vc.queue.is_empty is False:
			logger.info("Embedding Queue")
			test = vc.queue.copy()
			li = list(test)
			for i in range(len(li)):
				desc += (f"{i+1}. {li[i]}")
				desc += "\n"
			await GeneralFunctions.send_embed("Current Queue", "dollarMusic.png", desc, ctx)
		else:
			logger.info("Queue is already empty")
			msg = "The queue is currently empty, add a song by using !play or !playsc"
			await GeneralFunctions.send_embed_error("Empty Queue", msg, ctx)

	@commands.command(aliases=["Empty", "clearqueue", "restart"])
	@GeneralFunctions.is_connected_to_same_voice()
	async def empty(self, ctx):
		vc = ctx.voice_client
		if vc.queue.is_empty is False:
			vc.queue.clear()
			logger.info("Emptying queue")
			await ctx.message.add_reaction("\u2705")
		else:
			logger.info("Queue is already empty")
			msg = "The queue is currently empty, add a song by using !play or !playsc"
			await GeneralFunctions.send_embed_error("Empty Queue", msg, ctx)

	@commands.command(aliases=["generatePlaylist", "GeneratePlaylist", "genplay", "genPlay"])
	@GeneralFunctions.is_connected_to_same_voice()
	async def generateplaylist(self, ctx, playlist_type=None, musician=None, album=None):
		vc = ctx.voice_client
		offset = random.randint(0, 1000)

		query = " ".join(filter(None, [
			f"genre:{playlist_type}" if playlist_type else None,
			f"artist:{musician}" if musician else None,
			f"album:{album}" if album else None
		]))

		if not query:
			await ctx.send("Please provide at least one parameter.")
			logger.warning("No filters entered, exiting method")
			return

		logger.info(f"Spotify Generating Playlist, Parameters: Genre: {playlist_type}, Artist: {musician}, Album: {album}")
		results = sp.search(q=query, type="track", limit=26, offset=offset)
		logger.info("Spotify Playlist Generation complete, queuing songs...")

		tracks = []
		for track in results["tracks"]["items"]:
			#pylint: disable=inconsistent-quotes
			query = f"{track['name']} {track['artists'][0]['name']}"
			search_result = await wavelink.Playable.search(query)
			if search_result:
				tracks.append(search_result[0])

		if not tracks:
			msg = "Those filters returned zero tracks, try again."
			await GeneralFunctions.send_embed_error("Zero Tracks Returned", msg, ctx)
			logger.warning(f"{query} returned zero results")
			return

		if not vc.playing and vc.queue.is_empty:
			await vc.play(tracks[0])
			logger.info(f"Playing {tracks[0].title} from Spotify generated playlist")
			tracks = tracks[1:]

		logger.debug(f"Queuing {len(tracks)} songs from the Spotify generated playlist")
		await vc.queue.put_wait(tracks)
		logger.info(f"Finished loading {len(tracks)} songs into the queue from the Spotify generated playlist")

		await ctx.send("Finished loading the Spotify playlist. Here are the queued songs:")
		await Music.queue(self, ctx)

	@commands.command(aliases=["Lyrics"])
	@GeneralFunctions.is_connected_to_same_voice()
	async def lyrics(self, ctx):
		vc = ctx.voice_client
		track = str(vc.current)

		if vc.playing:
			async with ctx.typing():
				while True:
					try:
						logger.info(f"Searching lyrics for {track} by {artist}")
						song = genius.search_song(track, artist)
						break
					except TimeoutError:
						logger.warning("GET request timed out, retrying...")
				if song is None:
					await ctx.send("Unable to find song lyrics, songs from playlists are less likely to return lyrics...")
				else:
					if len(song.lyrics) > 4096:
						msg = f"Lyrics can be found here: <{song.url}>"
						return await GeneralFunctions.send_embed("Lyrics", "dollarMusic.png", msg, ctx)
					embed = discord.Embed(title=song.title, url=song.url,
										description=song.lyrics, color=discord.Color.random())
					embed.set_author(name=f"{song.artist}")
					embed.set_thumbnail(url=f"{song.header_image_thumbnail_url}")
					embed.set_footer()
					logger.info("Lyrics loaded from Genius API")
					await ctx.send(embed=embed)
		else:
			msg = "Nothing is currently playing, add a song by using !play or !playsc"
			await GeneralFunctions.send_embed_error("No Song Playing", msg, ctx)

	@play.error
	async def play_error(self, ctx, error):
		if isinstance(error, commands.BadArgument):
			await GeneralFunctions.send_embed_error("Bad Argument", error, ctx)
			logger.error(f"Bad argument {error}")
		elif isinstance(error, commands.MissingRequiredArgument):
			await GeneralFunctions.send_embed_error("Missing Required Argument", error, ctx)
			logger.error("User did not provide a song when using !play")
		elif isinstance(error, wavelink.WavelinkException):
			await GeneralFunctions.send_embed_error("Wavelink Error", error, ctx)
			logger.error(f"Wavelink error: {error}")
		elif isinstance(error, wavelink.LavalinkLoadException):
			await GeneralFunctions.send_embed_error("Lavalink Load Error", error, ctx)
			logger.error(f"Lavalink Load error: {error}")
		
async def setup(bot):
	await bot.add_cog(Music(bot))
