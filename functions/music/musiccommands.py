"""
DESCRIPTION: Music commands reside here
"""

from ..common.libraries import(
	discord, commands, genius, wavelink, os,
	read_csv, random, sp, artist
)

from ..common.generalfunctions import GeneralFunctions
from ..common.generalfunctions import CustomPlayer
from functions.queries.queries import Queries

logger = GeneralFunctions.setup_logger("music")

class Music(commands.Cog):
	"""
	DESCRIPTION: Creates Music class
	PARAMETERS: commands.Bot - Discord Commands
	"""
	def __init__(self, bot):
		self.bot = bot
		self.mydb = bot.mydb

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

	@commands.command(aliases=["Join"])
	@GeneralFunctions.is_connected_to_voice()
	async def join(self, ctx):
		custom_player = CustomPlayer()
		vc: CustomPlayer = await ctx.author.voice.channel.connect(cls=custom_player)
		await vc.set_volume(5)  #NOTE: Set bot volume initially to 5

	@commands.command(aliases=["Leave"])
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
		tracks: wavelink.Search = await wavelink.Playable.search(query)
		search: wavelink.Playable = tracks[0]
		vc = ctx.voice_client
		if not vc:
			custom_player = CustomPlayer()
			vc: CustomPlayer = await ctx.author.voice.channel.connect(cls=custom_player)
			await vc.set_volume(5)

		if vc.playing:
			vc.queue.put(search)
			embed = discord.Embed(title=search.title, url=search.uri, description=f"Added {search.title} to the Queue!", colour=discord.Colour.random())
			embed.set_author(name=f"{search.author}")
			embed.set_thumbnail(url=f"{search.artwork}")
			if vc.queue.is_empty:
				embed.set_footer(text="Queue is empty")
			else:
				nextitem = vc.queue.get()
				vc.queue.put_at(0, nextitem)
				embed.set_footer(text=f"Next song is: {nextitem}")
			await ctx.send(embed=embed)
			logger.info(f"Queued from YouTube: {search.title}")
		else:
			embed = discord.Embed(title=search.title, url=search.uri, description=f"Now Playing {search.title}!", colour=discord.Colour.random())
			embed.set_author(name=f"{search.author}")
			embed.set_thumbnail(url=f"{search.artwork}")
			await ctx.send(embed=embed)
			await vc.play(search)
			logger.info(f"Playing from YouTube: {search.title}")

	@commands.command(aliases=["Playskip", "PlaySkip"])
	@GeneralFunctions.is_connected_to_same_voice()
	async def playskip(self, ctx, *, query):
		tracks: wavelink.Search = await wavelink.Playable.search(query)
		search: wavelink.Playable = tracks[0]
		vc = ctx.voice_client
		
		if vc:
			if vc.playing and not vc.paused:
				vc.queue.put_at(0, search)
				await vc.seek(vc.current.length * 1000)
				await ctx.send("Playing the next song...")
				embed = discord.Embed(title=search.title, url=search.uri, description=f"Now Playing {search.title}!", colour=discord.Colour.random())
				embed.set_author(name=f"{search.author}")
				embed.set_thumbnail(url=f"{search.artwork}")
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
			async with ctx.typing():
				while True:
					try:
						logger.info(f"Relaying current playing song: {track} by {artist}")
						song = genius.search_song(track, artist)
						break
					except TimeoutError:
						logger.warning("GET request timed out, retrying...")
				if song is None:
					msg = "Unable to find current playing song on Genius, please try again..."
					await GeneralFunctions.send_embed_error("Error Finding Song", msg, ctx)
				else:
					embed = discord.Embed(title=song.title, url=song.url, description=f"Currently playing {song.full_title}", colour=discord.Colour.random())
					embed.set_author(name=f"{song.artist}")
					embed.set_thumbnail(url=f"{song.header_image_thumbnail_url}")
					embed.set_footer()
					logger.info("Current song information loaded from Genius API")
					await ctx.send(embed=embed)
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

	@commands.command(aliases=["Load"])
	@GeneralFunctions.is_connected_to_same_voice()
	async def load(self, ctx):
		vc = ctx.voice_client
		count = 0

		fileexists = os.path.isfile("ex.csv")

		if fileexists:
			await ctx.send("Loading playlist!")
			logger.info("Loading Playlist")
			data = read_csv("ex.csv")
			os.remove("ex.csv")
			tracks = data["Track Name"].tolist()
			artists = data["Artist Name(s)"].tolist()
			song = list(zip(tracks, artists))

			while song:
				if count == 75:
					break
				item = random.choice(song)
				song.remove(item)
				search = await wavelink.Playable.search(query=item[0] + " " + item[1], return_first=True)
				if vc.playing:
					async with ctx.typing():
						vc.queue.put(item=search)
						logger.info(f"Added {search} to queue from playlist")
				elif vc.queue.is_empty:
					await vc.play(search)
					logger.info(f"Playing {search} from playlist")
				else:
					logger.error("Error queuing/playing from playlist")
				count += 1

			await ctx.send("Finished loading playlist heres the queued songs")
			await Music.queue(self, ctx)
			logger.info(f"Finished loading {count} songs into queue from playlist")
		else:
			logger.warning("ex.csv does not exist!")
			raise commands.CheckFailure("Please upload an Exportify Playlist to this channel and then use !load")

	@commands.command(aliases=["generatePlaylist", "GeneratePlaylist", "genplay", "genPlay"])
	@GeneralFunctions.is_connected_to_same_voice()
	async def generateplaylist(self, ctx, playlist_type=None, musician=None, album=None):
		vc = ctx.voice_client
		count = 0
		offset = random.randint(0, 1000)

		query = ""
		if playlist_type:
			query += f"genre:{playlist_type}"
		if musician:
			query += f" artist:{musician}"
		if album:
			query += f" album:{album}"

		if not query:
			await ctx.send("Please provide at least one parameter.")
			logger.warning("No filters entered, exiting method")
			return
		logger.info(f"Spotify Generating Playlist, Parameters: Genre: {playlist_type}, Artist: {musician}, Album: {album}")
		results = sp.search(q=query, type="track", limit=25, offset=offset)
		logger.info("Spotify Playlist Generation complete, querying songs...")

		tracks = []
		for track in results["tracks"]["items"]:
			#pylint: disable=inconsistent-quotes
			tracks.append(f"{track['name']} {track['artists'][0]['name']}")

		if not tracks:
			msg = "Those filters returned zero tracks, try again."
			await GeneralFunctions.send_embed_error("Zero Tracks Returned", msg, ctx)
			logger.warning(f"{query} returned zero results")
		else:
			while tracks:
				item = str(random.choice(tracks))
				tracks.remove(item)
				search = await wavelink.Playable.search(query=item, return_first=True)
				if vc.playing:
					async with ctx.typing():
						vc.queue.put(item=search)
						logger.info(f"Added {search} to queue from Spotify generated playlist")
				elif vc.queue.is_empty:
					await vc.play(search)
					logger.info(f"Playing {search} from Spotify generated playlist")
				else:
					logger.error("Error queuing/playing from Spotify generated playlist")
				count += 1

			await ctx.send("Finished loading the Spotify playlist. Here are the queued songs:")
			await Music.queue(self, ctx)
			logger.info(f"Finished loading {count} songs into the queue from the Spotify generated playlist")

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
										description=song.lyrics, colour=discord.Colour.random())
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
