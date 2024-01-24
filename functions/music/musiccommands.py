"""
DESCRIPTION: Music commands reside here
"""

from ..common.libraries import(
	discord, commands, genius, wavelink, os, read_csv, random, asyncio, sp, artist
)

from ..common.generalfunctions import GeneralFunctions
from ..common.generalfunctions import CustomPlayer

logger = GeneralFunctions.setup_logger("music")

class Music(commands.Cog):
	"""
	DESCRIPTION: Creates Music class
	PARAMETERS: commands.Bot - Discord Commands
	"""
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	#pylint: disable=unused-argument
	async def on_wavelink_track_start(self, player: CustomPlayer, track: wavelink.Track):
		global artist
		artist = track.author
		
	@commands.Cog.listener()
	#pylint: disable=unused-argument
	async def on_wavelink_track_end(self, player: CustomPlayer, track: wavelink.Track, reason):
		if not player.queue.is_empty:
			await asyncio.sleep(.5)
			next_track = player.queue.get()
			await player.play(next_track)
			logger.info(f"Playing next track: {next_track}")
		else:
			logger.info("Queue is empty")

	# Join authors voice channel
	@commands.command(aliases=["Join"])
	@GeneralFunctions.is_connected_to_voice()
	async def join(self, ctx):
		custom_player = CustomPlayer()
		vc: CustomPlayer = await ctx.author.voice.channel.connect(cls=custom_player)
		await vc.set_volume(5)  # Set bot volume initially to 5

	# Leave voice channel
	@commands.command(aliases=["Leave"])
	@GeneralFunctions.is_connected_to_same_voice()
	async def leave(self, ctx):
		vc = ctx.voice_client
		if vc:
			await vc.disconnect()
			await ctx.channel.purge(limit=500)
		else:
			raise commands.CheckFailure("The bot is not connected to a voice channel.")

	# Play a song, ex: !play starboy the weeknd
	@commands.command(aliases=["Play"])
	@GeneralFunctions.is_connected_to_voice()
	async def play(self, ctx, *, search: wavelink.YouTubeMusicTrack):
		vc = ctx.voice_client
		if not vc:
			custom_player = CustomPlayer()
			vc: CustomPlayer = await ctx.author.voice.channel.connect(cls=custom_player)
			await vc.set_volume(5)

		if vc.is_playing():
			vc.queue.put(item=search)
			embed = discord.Embed(title=search.title, url=search.uri, description=f"Added {search.title} to the Queue!", colour=discord.Colour.random())
			embed.set_author(name=f"{search.author}")
			embed.set_thumbnail(url=f"{search.thumbnail}")
			if vc.queue.is_empty:
				embed.set_footer(text="Queue is empty")
			else:
				nextitem = vc.queue.get()
				vc.queue.put_at_front(item=nextitem)
				embed.set_footer(text=f"Next song is: {nextitem}")
			await ctx.send(embed=embed)
			logger.info(f"Queued from YouTube: {search.title}")
		else:
			embed = discord.Embed(title=search.title, url=search.uri, description=f"Now Playing {search.title}!", colour=discord.Colour.random())
			embed.set_author(name=f"{search.author}")
			embed.set_thumbnail(url=f"{search.thumbnail}")
			await ctx.send(embed=embed)
			await vc.play(search)
			logger.info(f"Playing from YouTube: {search.title}")

	# Play a song from SoundCloud, ex: !play Jackboy Seduction
	@commands.command(aliases=["Playsc", "soundcloud", "sc"])
	@GeneralFunctions.is_connected_to_voice()
	async def playsc(self, ctx, *, search: wavelink.SoundCloudTrack):
		vc = ctx.voice_client
		if not vc:
			custom_player = CustomPlayer()
			vc: CustomPlayer = await ctx.author.voice.channel.connect(cls=custom_player)
			await vc.set_volume(5)  # initially set volume to 5

		if vc.is_playing():
			vc.queue.put(item=search)
			embed = discord.Embed(title=search.title, url=search.uri, description=f"Added {search.title} to the Queue!", colour=discord.Colour.random())
			embed.set_author(name=f"{search.author}")
			if vc.queue.is_empty:
				embed.set_footer(text="Queue is empty")
			else:
				nextitem = vc.queue.get()
				vc.queue.put_at_front(item=nextitem)
				embed.set_footer(text=f"Next song is: {nextitem}")
			await ctx.send(embed=embed)
			logger.info(f"Queued from SoundCloud: {search.title}")
		else:
			embed = discord.Embed(title=search.title, url=search.uri, description=f"Now Playing {search.title}!", colour=discord.Colour.random())
			embed.set_author(name=f"{search.author}")
			await ctx.send(embed=embed)
			await vc.play(search)
			logger.info(f"Playing from SoundCloud: {search.title}")

	# Skip current song and play next, ex !playskip blinding lights the weeknd
	@commands.command(aliases=["Playskip", "PlaySkip"])
	@GeneralFunctions.is_connected_to_same_voice()
	async def playskip(self, ctx, *, search: wavelink.YouTubeMusicTrack):
		vc = ctx.voice_client
		if vc:
			if vc.is_playing() and not vc.is_paused():
				vc.queue.put_at_front(item=search)
				await vc.seek(vc.track.length * 1000)
				await ctx.send("Playing the next song...")
				embed = discord.Embed(title=search.title, url=search.uri, description=f"Now Playing {search.title}!", colour=discord.Colour.random())
				embed.set_author(name=f"{search.author}")
				embed.set_thumbnail(url=f"{search.thumbnail}")
				await ctx.send(embed=embed)
				logger.info(f"Playskipping to: {search.title}")
			elif vc.is_paused():
				msg = "The bot is currently paused, to playskip, first resume music with !resume"
				await GeneralFunctions.send_embed_error("Dollar is Paused", msg, ctx)
			else:
				msg = "Nothing is currently playing."
				await GeneralFunctions.send_embed_error("No Song Playing", msg, ctx)
		else:
			raise commands.CheckFailure("The bot is not connected to a voice channel.")

	# Skip current song, ex: !skip
	@commands.command(aliases=["Skip"])
	@GeneralFunctions.is_connected_to_same_voice()
	async def skip(self, ctx):
		vc = ctx.voice_client
		if vc:
			if not vc.is_playing():
				msg = "Nothing is currently playing."
				return await GeneralFunctions.send_embed_error("No Song Playing", msg, ctx)
			if vc.queue.is_empty:
				return await vc.stop()

			await vc.seek(vc.track.length * 1000)
			search = vc.queue.get()
			vc.queue.put_at_front(item=search)
			msg = f"Skipping to next song: {search}"
			await GeneralFunctions.send_embed("Skipping Song", "dollarMusic.png", msg, ctx)
			logger.info("Skipping music")
			if vc.is_paused():
				await vc.resume()
		else:
			raise commands.CheckFailure("The bot is not connected to a voice channel.")

	# Pause current song, ex: !pause
	@commands.command(aliases=["Pause"])
	@GeneralFunctions.is_connected_to_same_voice()
	async def pause(self, ctx):
		vc = ctx.voice_client
		if vc:
			if vc.is_playing() and not vc.is_paused():
				await vc.pause()
				msg = "Pausing Music Player!"
				await GeneralFunctions.send_embed("Pausing...", "dollarMusic.png", msg, ctx)
				logger.info("Pausing music")
			else:
				msg = "Nothing is currently playing"
				await GeneralFunctions.send_embed_error("No Song Playing", msg, ctx)
		else:
			raise commands.CheckFailure("The bot is not connected to a voice channel.")

	# Resume current song, ex: !resume
	@commands.command(aliases=["Resume"])
	@GeneralFunctions.is_connected_to_same_voice()
	async def resume(self, ctx):
		vc = ctx.voice_client
		if vc:
			if vc.is_paused():
				await vc.resume()
				msg = "Resuming Music Player!"
				await GeneralFunctions.send_embed("Resuming...", "dollarMusic.png", msg, ctx)
				logger.info("Resuming music")
			else:
				msg = "Nothing is currently playing"
				await GeneralFunctions.send_embed_error("No Song Playing", msg, ctx)
		else:
			raise commands.CheckFailure("The bot is not connected to a voice channel.")

	# Show current playing song, ex: !nowplaying
	@commands.command(aliases=["Nowplaying", "NowPlaying", "np"])
	@GeneralFunctions.is_connected_to_same_voice()
	async def nowplaying(self, ctx):
		vc = ctx.voice_client
		track = str(vc.track)

		if vc.is_playing():
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

	# Show whats next in the queue
	@commands.command(aliases=["Next", "nextsong"])
	@GeneralFunctions.is_connected_to_same_voice()
	async def next(self, ctx):
		vc = ctx.voice_client
		if vc:
			try:
				search = vc.queue.get()
				vc.queue.put_at_front(item=search)
				msg = f"The next song is: {search}"
				await GeneralFunctions.send_embed("Next Song...", "dollarMusic.png", msg, ctx)
				logger.info("Printing next song in queue")
			except:
				msg = "The queue is currently empty, add a song by using !play or !playsc"
				await GeneralFunctions.send_embed_error("Empty Queue", msg, ctx)
		else:
			raise commands.CheckFailure("The bot is not connected to a voice channel")

	# Seeks to specifc second in song, ex: !seek 50(seeks to 50 seconds)
	@commands.command(aliases=["Seek"])
	@GeneralFunctions.is_connected_to_same_voice()
	async def seek(self, ctx, seek=0):
		vc = ctx.voice_client
		val = int(seek)
		if vc:
			if vc.is_playing() and not vc.is_paused():
				await vc.seek(vc.track.length * val)
				msg = f"Seeking {val} seconds."
				await GeneralFunctions.send_embed("Seeking...", "dollarMusic.png", msg, ctx)
				logger.info(f"Song seeked for {val} seconds")
			else:
				msg = "Nothing is currently playing"
				await GeneralFunctions.send_embed_error("No Song Playing", msg, ctx)
		else:
			raise commands.CheckFailure("The bot is not connected to a voice channel")

	# Set volume of bot, ex !volume 1(sets volume of bot to 1)
	@commands.command(aliases=["Volume"])
	@GeneralFunctions.is_connected_to_same_voice()
	async def volume(self, ctx, volume):
		vc = ctx.voice_client
		val = int(volume)
		if vc and (0 < val <= 100):
			await vc.set_volume(val)
			msg = f"Volume set to: {val}"
			await GeneralFunctions.send_embed("Setting Volume...", "dollarMusic.png", msg, ctx)
			logger.info(f"Bot volume set to: {val}")
		else:
			raise commands.CheckFailure("The bot is not connected to a voice channel")

	# Prints all items in queue, ex !queue
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
				desc += "\n\n"

			embed = discord.Embed(title="Whats Queued?", description=desc, colour=discord.Colour.random())
			file_path = os.path.join("images", "dollar2.png")
			img = discord.File(file_path, filename="dollar2.png")
			embed.set_thumbnail(url="attachment://dollar2.png")
			await ctx.send(embed=embed, file=img)
		else:
			logger.info("Queue is already empty")
			msg = "The queue is currently empty, add a song by using !play or !playsc"
			await GeneralFunctions.send_embed_error("Empty Queue", msg, ctx)

	# Clears queue, !empty
	@commands.command(aliases=["Empty", "clearqueue", "restart"])
	@GeneralFunctions.is_connected_to_same_voice()
	async def empty(self, ctx):
		vc = ctx.voice_client
		if vc.queue.is_empty is False:
			vc.queue.clear()
			logger.info("Emptying queue")
			msg = "All items from queue have been removed"
			await GeneralFunctions.send_embed("Queue Cleared", "dollarMusic.png", msg, ctx)
		else:
			logger.info("Queue is already empty")
			msg = "The queue is currently empty, add a song by using !play or !playsc"
			await GeneralFunctions.send_embed_error("Empty Queue", msg, ctx)

	# Load playlist from CSV, ex !load
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
				search = await wavelink.YouTubeMusicTrack.search(query=item[0] + " " + item[1], return_first=True)
				if vc.is_playing():
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
			tracks.append(f"{track['name']} {track['artists'][0]['name']}")

		if not tracks:
			msg = "Those filters returned zero tracks, try again."
			await GeneralFunctions.send_embed_error("Zero Tracks Returned", msg, ctx)
			logger.warning(f"{query} returned zero results")
		else:
			while tracks:
				item = str(random.choice(tracks))
				tracks.remove(item)
				search = await wavelink.YouTubeMusicTrack.search(query=item, return_first=True)
				if vc.is_playing():
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

	# Print lyrics of current playing song, pulls from Genius.com
	@commands.command(aliases=["Lyrics"])
	@GeneralFunctions.is_connected_to_same_voice()
	async def lyrics(self, ctx):
		vc = ctx.voice_client
		track = str(vc.track)

		if vc.is_playing():
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

async def setup(bot):
	await bot.add_cog(Music(bot))
