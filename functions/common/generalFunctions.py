from ..common.libraries import(
    discord, logging, commands, wavelink, os, mysql,
    asyncio, pooling
)

class CustomPlayer(wavelink.Player):
    def __init__(self):
        super().__init__()
        self.queue = wavelink.Queue()

def setup_logger(logger_name):
    logger = logging.getLogger(logger_name)
    handler = logging.handlers.RotatingFileHandler(
        filename='discord.log',
        encoding='utf-8',
        maxBytes=1024*1024,  # 1mb
        backupCount=5,  # Rotate through 5 files
    )
    handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger

logger = setup_logger('core')

# Check if the command sent comes from a user in the same voice channel(for most music commands)
def is_connected_to_same_voice():
    async def predicate(ctx):
        if not ctx.author.voice:
            # User is not connected to a voice channel
            raise commands.CheckFailure("You need to be in a voice channel to use this command")
        elif not ctx.voice_client or ctx.author.voice.channel != ctx.voice_client.channel:
            # User is connected to a different voice channel than the bot
            raise commands.CheckFailure("You need to be in the same voice channel as Dollar to use this command")
        return True
    return commands.check(predicate)

# Check if the command is coming from a user in a voice channel(for !join and !leave)
def is_connected_to_voice():
    async def predicate(ctx):
        if not ctx.author.voice:
            # User is not connected to a voice channel
            raise commands.CheckFailure("You need to be in a voice channel to use this command")
        return True
    return commands.check(predicate)

def connect_to_database():
    try:
        connection_pool = pooling.MySQLConnectionPool(
            pool_name="mydb_pool",
            pool_size=8,
            host="localhost",
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PW'),
            database=os.getenv('DB_SCHEMA')
        )
        logger.info("Connected to the database successfully.")
        mydb = connection_pool.get_connection()
        logger.debug("Acquired a database connection from the connection pool.")
        return mydb
    except mysql.connector.Error as err:
        logger.error("Failed to connect to the database: %s", err)
        return None

async def validate_connection(mydb):
    try:
        cursor = mydb.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchall()
        cursor.close()
        logger.debug('Executed validation query')
        return True
    except mysql.connector.Error as error:
        logger.error(f'Error validating connection: {error}')
        return False

async def send_patch_notes(client):
    for guild in client.guilds:
        logger.debug(f'Dollar loaded in {guild.name}, owner: {guild.owner}')
        channel = guild.system_channel # Notify guild's default system channel set in Discord settings
        if channel is not None:
            try:
                file_path = os.path.join("markdown", "patch_notes.md")
                if os.path.isfile(file_path):
                    with open(file_path, "r") as file:
                        desc = file.read()

                embed = discord.Embed(
                    title='Patch: 1.1.3',
                    url='https://en.wikipedia.org/wiki/Dollar',
                    description=desc,
                    colour=discord.Color.green()
                )
                embed.set_author(name='Dollar')
                file_path = os.path.join("images", "dollar.png")
                img = discord.File(file_path, filename='dollar.png')
                embed.set_thumbnail(url="attachment://dollar.png")
                embed.set_footer(text='Feature request? Bug? Please report it by using /reportbug or /featurerequest')

                await channel.send(embed=embed, file=img)
                logger.debug(f'Notified {guild.name} of dollar\'s latest update.')
            except discord.Forbidden:
                logger.warning(f"Could not send message to {channel.name} in {guild.name}. Missing permissions.")
            except discord.HTTPException:
                logger.error(f"Could not send message to {channel.name} in {guild.name}. HTTP exception occurred.")

async def idle_checker(vc, comchannel, guild):
    time = 0
    while True:
        await asyncio.sleep(1)
        time = time + 1
        if time % 30 == 0:
            logger.debug(f'Dollar has been idle for {time} seconds in {str(guild)}')
        if vc.is_playing() and not vc.is_paused():
            time = 0
        if time == 600:
            logger.info(f'10 minutes reached, Dollar disconnecting from {str(guild)}')
            await vc.disconnect()
            await comchannel.purge(limit=500)
            logger.debug('Finished clearing #commands channel')
        if not vc.is_connected():
            break