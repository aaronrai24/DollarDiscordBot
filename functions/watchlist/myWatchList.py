from ..common.libraries import(
    discord, commands, mysql, asyncio, requests, BeautifulSoup, date
)
from ..common.generalFunctions import(
    setup_logger
)

logger = setup_logger('watchlist')

class MyWatchList(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    # Convert tags to Icons
    def tag2Icons(self, tag):
        if tag == 'Anime':
            return '🇯🇵'
        elif tag == 'TV':
            return '📺'
        else:
            return '🎥'
        
    # Get UserID from userlist table
    async def getUserId(self, ctx):
        mycursor = self.bot.mydb.cursor()
        try:
            logger.info(f'Executing query to return UserID for {ctx.author}')
            mycursor.execute("SELECT * FROM userlist WHERE Username = \"%s\"" % str(ctx.author))
        except (mysql.connector.Error, mysql.connector.Warning) as e:
            await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
            logger.warning(e)
            return None
        myresult = mycursor.fetchall()
        # Return UserID or -1 if user does not exist
        if len(myresult) == 0:
            return -1
        return myresult[0][0]

    # Get show title and sanitize inputs
    async def getShowTitle(self, ctx):
        await ctx.send(f"{ctx.author.mention} Enter the show name: ")
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        try:
            title = await self.bot.wait_for('message', check=check, timeout=15)
        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.author.mention} Timeout exceeded. Please try again.")
            return -1
        # Sanitize input for \'
        if title.content.find('\'') != -1:
            await ctx.send(f"{ctx.author.mention} Please ensure you do not include apostrophes or other invalid characters.\nTry !addshow again.")
            return -2
        return title.content

    # Get show tag
    async def getShowTag(self, ctx):
        msg = await ctx.send(f"{ctx.author.mention} Select the shows tag (TV 📺, Anime 🇯🇵, Movie 🎥): ")
        await msg.add_reaction('📺')  # TV entry
        await msg.add_reaction('🇯🇵')  # Anime entry
        await msg.add_reaction('🎥')  # Movie entry

        def reaction1check(reaction, user):
            name1 = str(ctx.author).split("#")[0]
            return  user.name == name1 and str(reaction.emoji) in ['🇯🇵', '📺', '🎥']

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=15, check=reaction1check)
            if reaction.emoji == '📺':
                react = 'TV'
            elif reaction.emoji == '🇯🇵':
                react = 'Anime'
            else:
                react = 'Movie'
        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.author.mention} Timeout exceeded. Please try again.")
            return -1
        return react

    # Prompt user to confirm details
    async def getEntryConfirmation(self, ctx, showTitle, showTag, rating):
        if rating == None:
            msg = await ctx.send(f"{ctx.author.mention} Is this correct (Select ✅ or ❌):\nTitle: {showTitle} | Tag: {showTag}")
        else:
            msg = await ctx.send(f"{ctx.author.mention} Is this correct (Select ✅ or ❌):\nTitle: {showTitle} | Rating: {rating} | Tag: {showTag}")
        await msg.add_reaction('✅')  # Acknowledge entry
        await msg.add_reaction('❌')  # Decline entry

        def reaction2check(reaction, user):
            name1 = str(ctx.author).split("#")[0]
            return  user.name == name1 and str(reaction.emoji) in ['✅','❌']
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=15, check=reaction2check)
        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.author.mention} Timeout exceeded. Please try again.")
            return -1
        return reaction

    # Check if show currently exists in table and return index if exists
    async def checkExists(self, ctx, userid, showTitle, table):
        mycursor = self.bot.mydb.cursor()
        try:
            logger.info(f'Executing query to return if show exists in {table} for {ctx.author}')
            mycursor.execute("SELECT * FROM %s WHERE UserID = %d AND ShowName = \'%s\'" % (table, userid, showTitle))
        except (mysql.connector.Error, mysql.connector.Warning) as e:
            await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
            logger.warning(e)
            return None
        userresults = mycursor.fetchall()
        # Entry does not exist
        if not len(userresults):
            return -1
        # Entry exists
        logger.info(f'{showTitle} already exists in {ctx.author}\'s {table}.')
        return userresults[0][4]

    # Remove entry in table
    async def removeEntry(self, ctx, userid, showTitle, table):
        mycursor = self.bot.mydb.cursor()
        try:
            logger.info(f'Executing query to delete {showTitle} in {table} for {ctx.author}')
            mycursor.execute("DELETE FROM %s WHERE UserID = %d AND ShowName = \'%s\'" % (table, userid, showTitle))
        except (mysql.connector.Error, mysql.connector.Warning) as e:
            await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
            logger.warning(e)
            return -1
        self.bot.mydb.commit()
        return 1

    # Get list of either higher or lower indexed shows and update indices
    async def getIndicesAndUpdate(self, ctx, userid, showIndex1, showIndex2, direction1, direction2):
        mycursor = self.bot.mydb.cursor()
        try:
            logger.info(f'Executing query to return list of shows needing to update indices for {ctx.author}')
            if showIndex2 == -1: # Normal remove
                mycursor.execute("SELECT * FROM activelist WHERE UserID = %d AND TableIndex %s %d" % (userid, direction1, showIndex1))
            else: # editing table
                mycursor.execute("SELECT * FROM activelist WHERE UserID = %d AND TableIndex %s %d AND TableIndex %s %d" % (userid, direction1, showIndex1, direction2, showIndex2))
        except (mysql.connector.Error, mysql.connector.Warning) as e:
            await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
            logger.warning(e)
            return None
        results = mycursor.fetchall()
        for x in results:
            # Update indexes by decrementing or incrementing based on the change being made
            try:
                logger.info(f'Executing query to update indices for {ctx.author}')
                if showIndex1 < showIndex2 or showIndex2 == -1: # Decrease other indices
                    mycursor.execute("UPDATE activelist SET TableIndex = %d WHERE UserID = %d AND ShowName = \'%s\'" % (x[4] - 1, userid, x[1]))
                else: # Increase other indices
                    mycursor.execute("UPDATE activelist SET TableIndex = %d WHERE UserID = %d AND ShowName = \'%s\'" % (x[4] + 1, userid, x[1]))
            except (mysql.connector.Error, mysql.connector.Warning) as e:
                await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
                logger.warning(e)
                return None
        self.bot.mydb.commit()

    # Get show rating 1-5 from user; timeout after 15 seconds
    async def getShowRating(self, ctx, showTitle):
        msg2 = await ctx.send(f"{ctx.author.mention} Enter your rating for {showTitle} (1-5): ")
        await msg2.add_reaction('1️⃣')
        await msg2.add_reaction('2️⃣')
        await msg2.add_reaction('3️⃣')
        await msg2.add_reaction('4️⃣')
        await msg2.add_reaction('5️⃣')

        def reaction3check(reaction, user):
            name1 = str(ctx.author).split("#")[0]
            return  user.name == name1 and str(reaction.emoji) in ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=15, check=reaction3check)
            if reaction.emoji == '1️⃣':
                return 1
            elif reaction.emoji == '2️⃣':
                return 2
            elif reaction.emoji == '3️⃣':
                return 3
            elif reaction.emoji == '4️⃣':
                return 4
            else:
                return 5
        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.author.mention} Timeout exceeded. Please try again.")
            return -1

    # Get image result URL from the show's title
    def getShowUrl(self, res, tag):
        searchName = res.replace(" ", "+")
        url = f'https://www.google.com/search?q={searchName}+{tag}&tbm=isch'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        image_results = soup.find_all('img')
        return image_results[1]['src']

    #------------------------------------------------------------------------------------------------
    # WatchList Commands

    # Print user's WatchList if found, else generate entry and initialization message
    @commands.command(aliases=['wl'])
    async def watchlist(self, ctx):
        # Get User ID
        userid = await MyWatchList.getUserId(self, ctx)
        # Initialize entry for user
        mycursor = self.bot.mydb.cursor()
        if userid == -1:
            try:
                logger.info(f'Executing query to create entry in userlist for {ctx.author}')
                mycursor.execute("INSERT INTO userlist (Username) VALUES (\'%s\')" % str(ctx.author))
            except (mysql.connector.Error, mysql.connector.Warning) as e:
                await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
                logger.warning(e)
                return None
            self.bot.mydb.commit()
            await ctx.send(f'{ctx.author.mention} Initialization complete! Created an entry for you!')
            logger.info(f'Entry created for {ctx.author}')
            return
                
        # Print WatchList for user
        logger.info(f'Entry already exists for {ctx.author}, printing their watchlist')
        try:
            logger.info(f'Executing query to return entries in activelist for {ctx.author}')
            mycursor.execute("SELECT * FROM activelist WHERE UserID = \'%s\' ORDER BY TableIndex ASC" % userid)
        except (mysql.connector.Error, mysql.connector.Warning) as e:
            await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
            logger.warning(e)
            return None
        userresults = mycursor.fetchall()
        if not len(userresults):
            await ctx.send(f"{ctx.author.mention} Current list is empty. Please use !addshow to add to your WatchList")
            return
            
        # Embed response
        embed = discord.Embed(title="Current WatchList", colour=discord.Colour.random())
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
        embed.set_thumbnail(url=MyWatchList.getShowUrl(self, userresults[0][1], userresults[0][3]))
        embed.add_field(name='Title', value='', inline=True)
        embed.add_field(name='Tag', value='', inline=True)
        embed.add_field(name='Order', value='', inline=True)
        for x in userresults:
            embed.add_field(name='', value=x[1], inline=True)
            embed.add_field(name='', value=MyWatchList.tag2Icons(self, x[3]), inline=True)
            embed.add_field(name='', value=x[4], inline=True)
        await ctx.send(embed=embed)

    # Add entry to WatchList for user
    @commands.command(aliases=['AddShow', 'addShow', 'Addshow', 'as'])
    async def addshow(self, ctx):
        # Get User ID
        userid = await MyWatchList.getUserId(self, ctx)
        if userid == -1:
            await ctx.send(f'{ctx.author.mention} User does not exist. Try !watchlist to setup user.')
            return

        # Check if 5 entries and get index for new entry
        mycursor = self.bot.mydb.cursor()
        try:
            logger.info(f'Executing query to return highest TableIndex for {ctx.author}')
            mycursor.execute("SELECT TableIndex FROM activelist WHERE UserID = %d ORDER BY TableIndex DESC LIMIT 1" % userid)
        except (mysql.connector.Error, mysql.connector.Warning) as e:
            await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
            logger.warning(e)
            return None
        index = mycursor.fetchall()
        if index == []:
            index = 1
        else:
            index = index[0][0] + 1
        if index > 5:
            await ctx.send(f"{ctx.author.mention} Maximum size of WatchList reached (5).\nPlease use !removeshow to clear an entry")
            return

        # Get show title
        showTitle = await MyWatchList.getShowTitle(self, ctx)
        if showTitle == -1 or showTitle == -2: # timeout / invalid input
            return
        
        # Check if entry already exists
        if (await MyWatchList.checkExists(self, ctx, userid, showTitle, 'activelist')) != -1:
            await ctx.send(f"{ctx.author.mention} {showTitle} already exists in your WatchList. Please use !removeshow to re-create this entry.")
            return

        # Get show tag
        showTag = await MyWatchList.getShowTag(self, ctx)
        if showTag == -1: # timeout
            return

        # Confirm entry
        reaction = await MyWatchList.getEntryConfirmation(self, ctx, showTitle, showTag, None)
        if reaction == -1: # timeout
            return

        # Verify confirmation
        if reaction.emoji == '✅':
            # Insert entry to user's activelist
            imageUrl = 'x' # add query for image later (FR)
            try:
                logger.info(f'Executing query to add {showTitle} to WatchList for {ctx.author}')
                mycursor.execute("INSERT INTO activelist (UserID, ShowName, Image, Tag, TableIndex) VALUES (%d, \'%s\', \'%s\', \'%s\', %d)" % (userid, showTitle, imageUrl, showTag, index))
                self.bot.mydb.commit()
                logger.info(f'Watchlist entry added for {ctx.author}')
                await ctx.send(f"{ctx.author.mention} Added {showTitle} to your WatchList!")
            except (mysql.connector.Error, mysql.connector.Warning) as e:
                await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
                logger.warning(e)
                return None
        else:
            await ctx.send(f"{ctx.author.mention} Didn't confirm entry. Please try !addshow again to create an entry.")
        
    # Remove entry from WatchList for user
    @commands.command(aliases=['rs', 'Removeshow', 'RemoveShow'])
    async def removeshow(self, ctx):
        # Get User ID
        userid = await MyWatchList.getUserId(self, ctx)
        if userid == -1:
            await ctx.send(f'{ctx.author.mention} User does not exist. Try !watchlist to setup user.')
            return

        # Get show title
        showTitle = await MyWatchList.getShowTitle(self, ctx)
        if showTitle == -1 or showTitle == -2: # timeout or invalid input
            return
        # Remove entry from WatchList if exists
        showIndex = await MyWatchList.checkExists(self, ctx, userid, showTitle, 'activelist')
        if showIndex < 0: # -1: Nothing to remove, -2: DELETE query error
            await ctx.send(f"{ctx.author.mention} This show is not in your WatchList. Nothing to remove.")
            return
        elif showIndex == None: # SELECT Query error
            return
        if (await MyWatchList.removeEntry(self, ctx, userid, showTitle, 'activelist')) < 0: # Error
            return
        logger.info(f'{ctx.author}\'s WatchList entry deleted for {showTitle}')
        await ctx.send(f"{ctx.author.mention} Removed WatchList entry for {showTitle}")

        # Update indices for affected shows
        await MyWatchList.getIndicesAndUpdate(self, ctx, userid, showIndex, -1, '>', None)

    # Edit order of WatchList queue for user
    @commands.command(aliases=['eo', 'edit', 'editOrder', 'EditOrder', 'Editorder', 'editshow'])
    async def editorder(self, ctx):
        # Get User ID
        userid = await MyWatchList.getUserId(self, ctx)
        if userid == -1:
            await ctx.send(f'{ctx.author.mention} User does not exist. Try !watchlist to setup user.')
            return

        # Get show title
        showTitle = await MyWatchList.getShowTitle(self, ctx)
        if showTitle == -1 or showTitle == -2: # timeout or invalid input
            return
        
        # Check if entry exists in WatchList
        showIndex = await MyWatchList.checkExists(self, ctx, userid, showTitle, 'activelist')
        if showIndex < 0: # -1: Nothing to remove, -2: DELETE query error
            await ctx.send(f"{ctx.author.mention} This show is not in your WatchList. Use !addshow to add it to your WatchList.")
            return
        elif showIndex == None: # SELECT Query error
            return

        # Get current highest Order Index to verify input
        mycursor = self.bot.mydb.cursor()
        try:
            logger.info(f'Executing query to get count of entries in WatchList for {ctx.author}')
            mycursor.execute("SELECT COUNT(*) FROM activelist WHERE UserID = %d" % (userid))
        except (mysql.connector.Error, mysql.connector.Warning) as e:
            await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
            logger.warning(e)
            return None
        wlCount = mycursor.fetchall()

        # Prompt user for new Index in WatchList table
        indices = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']
        msg = await ctx.send(f"{ctx.author.mention} Select the new Order value for {showTitle}: ")
        for x in range (0, wlCount[0][0]):
            await msg.add_reaction(indices[x])

        def reaction3check(reaction, user):
            name1 = str(ctx.author).split("#")[0]
            return user.name == name1 and str(reaction.emoji) in indices
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=15, check=reaction3check)
            if reaction.emoji == '1️⃣':
                newIndex = 1
            elif reaction.emoji == '2️⃣':
                newIndex = 2
            elif reaction.emoji == '3️⃣':
                newIndex = 3
            elif reaction.emoji == '4️⃣':
                newIndex = 4
            elif reaction.emoji == '5️⃣':
                newIndex = 5
            else:
                newIndex = -1
        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.author.mention} Timeout exceeded. Please try again.")
            newIndex = -1
        if newIndex > wlCount[0][0]: # Reacted with higher than current count
            await ctx.send(f"{ctx.author.mention} Invalid input. Please try !editorder again.")
            return
        if newIndex == showIndex: # No change
            await ctx.send(f"{ctx.author.mention} Inputted current Order value for {showTitle}. Please try !editorder again with a new Order value.")
            return
        
        # Execute changes on requested and affected entries
        if showIndex > newIndex:
            await MyWatchList.getIndicesAndUpdate(self, ctx, userid, showIndex, newIndex, '<', '>=')
        else:
            await MyWatchList.getIndicesAndUpdate(self, ctx, userid, showIndex, newIndex, '>', '<=')
        try:
            logger.info(f'Executing query to update {showTitle} index for {ctx.author}')
            mycursor.execute("UPDATE activelist SET TableIndex = %d WHERE UserID = %d AND ShowName = \'%s\'" % (newIndex, userid, showTitle))
        except (mysql.connector.Error, mysql.connector.Warning) as e:
            await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
            logger.warning(e)
            return None
        self.bot.mydb.commit()
        await ctx.send(f"{ctx.author.mention} Updated your WatchList order!")
        await MyWatchList.watchlist(self, ctx)

    # Print user's WatchHistory if found, else suggest !watchlist to generate entry
    @commands.command(aliases=['wh','History', 'WatchHistory', 'watchhistory', 'watchHistory'])
    async def history(self, ctx, filter=None):
        # Get User ID
        userid = await MyWatchList.getUserId(self, ctx)
        if userid == -1:
            await ctx.send(f'{ctx.author.mention} User does not exist. Try !watchlist to setup user.')
            return
        
        # Apply filters
        if filter == None:
            queryFilter = 'ORDER BY Rating DESC'
        elif filter.lower() == "name":
            queryFilter = "ORDER BY ShowName ASC"
        elif filter.lower() in ['anime', 'movie', 'tv']:
            queryFilter = 'AND Tag = \'%s\' ORDER BY Rating DESC' % filter.lower()
        elif filter.lower() == 'date':
            queryFilter = 'ORDER BY Date DESC'
        else:
            queryFilter = 'ORDER BY Rating DESC'

        # Get WatchHistory results for user
        mycursor = self.bot.mydb.cursor()
        logger.info(f'Printing {ctx.author}\'s WatchHistory')
        try:
            logger.info(f'Executing query to return WatchHistory entries for {ctx.author}')
            mycursor.execute("SELECT * FROM watchhistory WHERE UserID = \'%s\' %s" % (userid, queryFilter))
        except (mysql.connector.Error, mysql.connector.Warning) as e:
            await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
            logger.warning(e)
            return None
        userresults = mycursor.fetchall()
        if not len(userresults):
            await ctx.send(f"{ctx.author.mention} Current list is empty. Please use !addhistory to add to your WatchHistory")
            return
        
        # Embed response
        count = 0
        colour1 = discord.Colour.random()
        embed = discord.Embed(title="Watch History", colour=colour1)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
        embed.set_thumbnail(url=MyWatchList.getShowUrl(self, userresults[0][1], userresults[0][3]))
        embed.add_field(name='Title', value='', inline=True)
        embed.add_field(name='Rating', value='', inline=True)
        embed.add_field(name='Date', value='', inline=True)
        while count < len(userresults) and count < 7:
            print(f'Count={count}')
            embed.add_field(name='', value=userresults[count][1], inline=True)
            embed.add_field(name='', value=userresults[count][2], inline=True)
            embed.add_field(name='', value=userresults[count][4], inline=True)
            count += 1
        await ctx.send(embed=embed)
        # New embeds if WatchHistory contains > 7
        while count < len(userresults):
            embed2 = discord.Embed(title="", colour=colour1)
            innercount = 0
            while ((count + innercount) < len(userresults)) and ((innercount + 1) % 8 != 0):
                embed2.add_field(name='', value=userresults[(count + innercount)][1], inline=True)
                embed2.add_field(name='', value=userresults[(count + innercount)][2], inline=True)
                embed2.add_field(name='', value=userresults[(count + innercount)][4], inline=True)
                innercount += 1
            count += innercount
            await ctx.send(embed=embed2)
        

    # Add entry for WatchHistory after completing a show
    @commands.command(aliases=['ah','Addhistory', 'AddHistory'])
    async def addhistory(self, ctx):
        # Get User ID
        userid = await MyWatchList.getUserId(self, ctx)
        if userid == -1:
            await ctx.send(f'{ctx.author.mention} User does not exist. Try !watchlist to setup user.')
            return

        # Get show title
        showTitle = await MyWatchList.getShowTitle(self, ctx)
        if showTitle == -1 or showTitle == -2: # timeout or invalid input
            return
        
        # Check if entry already exists in WatchHistory
        if (await MyWatchList.checkExists(self, ctx, userid, showTitle, 'watchhistory')) != -1:
            await ctx.send(f"{ctx.author.mention} {showTitle} already exists in your WatchHistory. Please use !removehistory to re-create this entry.")
            return

        # Get show tag
        showTag = await MyWatchList.getShowTag(self, ctx)
        if showTag == -1: # timeout
            return

        # Get show rating
        rating = await MyWatchList.getShowRating(self, ctx, showTitle)
        if rating == -1: # timeout
            return
        
        # Prompt user to confirm details
        reaction = await MyWatchList.getEntryConfirmation(self, ctx, showTitle, showTag, rating)
        if reaction == -1: # timeout
            return
        
        # Verify confirmation
        if reaction.emoji == '✅':
            # Add WatchHistory entry
            mycursor = self.bot.mydb.cursor()
            try:
                today = date.today().strftime("%B %d %y")
                logger.info(f'Executing query to add {showTitle} in WatchHistory for {ctx.author}')
                mycursor.execute("INSERT INTO watchhistory (UserID, ShowName, Rating, Tag, CompletedDate) VALUES (%d, \'%s\', %d, \'%s', \'%s')" % (userid, showTitle, rating, showTag, today))
                self.bot.mydb.commit()
                logger.info(f'WatchHistory entry added for {ctx.author}')
                response = f"{ctx.author.mention} Added {showTitle} to your WatchHistory!"
            except (mysql.connector.Error, mysql.connector.Warning) as e:
                await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
                logger.warning(e)
                return None
        else:
            await ctx.send(f"{ctx.author.mention} Didn't confirm entry. Please try !addhistory again to create an entry.")
            return
        
        # Remove entry from WatchList if exists
        showIndex = await MyWatchList.checkExists(self, ctx, userid, showTitle, 'activelist')
        if showIndex < 0: # -1: Nothing to remove, -2: DELETE query error
            await ctx.send(response)
            return
        elif showIndex == None: # SELECT query error
            return
        if (await MyWatchList.removeEntry(self, ctx, userid, showTitle, 'activelist')) < 0: # Error
            return
        response += f"\nSince you finished it, also removed {showTitle} from your WatchList!"
        logger.info(f'{ctx.author}\'s Watchlist entry deleted for {showTitle}')
        
        # Update indices for affected shows
        await MyWatchList.getIndicesAndUpdate(self, ctx, userid, showIndex, -1, '>', None)

        await ctx.send(response)
        
    # Remove entry from WatchHistory for user
    @commands.command(aliases=['rh', 'Removehistory', 'RemoveHistory', 'removeHistory'])
    async def removehistory(self, ctx):
        # Get User ID
        userid = await MyWatchList.getUserId(self, ctx)
        if userid == -1:
            await ctx.send(f'{ctx.author.mention} User does not exist. Try !watchlist to setup user.')
            return

        # Get show title
        showTitle = await MyWatchList.getShowTitle(self, ctx)
        if showTitle == -1 or showTitle == -2: # timeout or invalid input
            return

        # Remove entry from WatchHistory if exists
        showIndex = await MyWatchList.checkExists(self, ctx, userid, showTitle, 'watchhistory')
        if showIndex == -1 or showIndex == -2: # -1: Nothing to remove, -2: DELETE query error
            await ctx.send(f"{ctx.author.mention} This show is not in your WatchHistory. Nothing to remove.")
            return
        elif showIndex == None: # SELECT query error
            return
        if (await MyWatchList.removeEntry(self, ctx, userid, showTitle, 'watchhistory')) < 0: # Error
            return
        logger.info(f'{ctx.author}\'s WatchHistory entry deleted for {showTitle}')
        await ctx.send(f"{ctx.author.mention} Removed WatchHistory entry for {showTitle}")

    # Edit the rating for an entry in WatchHistory
    @commands.command(aliases=['er','eh', 'EditRating', 'editRating', 'Editrating', 'edithistory'])
    async def editrating(self, ctx):
        # Get User ID
        userid = await MyWatchList.getUserId(self, ctx)
        if userid == -1:
            await ctx.send(f'{ctx.author.mention} User does not exist. Try !watchlist to setup user.')
            return

        # Get show title
        showTitle = await MyWatchList.getShowTitle(self, ctx)
        if showTitle == -1 or showTitle == -2: # timeout or invalid input
            return
        
        # Confirm if entry exists in WatchHistory
        showIndex = await MyWatchList.checkExists(self, ctx, userid, showTitle, 'watchhistory')
        if not isinstance(showIndex, str): # -1: Nothing to remove, -2: DELETE query error
            await ctx.send(f"{ctx.author.mention} This show is not in your WatchHistory. Use !addhistory to add it to your WatchHistory.")
            return
        elif showIndex == None: # SELECT Query error
            return
        
        # Get show rating
        rating = await MyWatchList.getShowRating(self, ctx, showTitle)
        if rating == -1: # timeout
            return
        
        # Get current show's rating
        mycursor = self.bot.mydb.cursor()
        try:
            logger.info(f'Executing query to return {showTitle} current rating for {ctx.author}')
            mycursor.execute("SELECT * FROM watchhistory WHERE UserID = \'%s\' AND ShowName = \'%s\'" % (userid, showTitle))
        except (mysql.connector.Error, mysql.connector.Warning) as e:
            await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
            logger.warning(e)
            return
        userresults = mycursor.fetchall()
        oldrating = userresults[0][2]
        if oldrating == rating: # No change
            await ctx.send(f"{ctx.author.mention} Inputted current rating for {showTitle}. Please try !editrating again with a different rating.")
            return
        
        # Prompt user to confirm details
        msg = await ctx.send(f"{ctx.author.mention} Is this correct (Select ✅ or ❌):\nTitle: {showTitle} | Rating: {oldrating} -> {rating}")
        await msg.add_reaction('✅')  # Acknowledge entry
        await msg.add_reaction('❌')  # Decline entry

        def reaction2check(reaction, user):
            name1 = str(ctx.author).split("#")[0]
            return  user.name == name1 and str(reaction.emoji) in ['✅','❌']
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=15, check=reaction2check)
        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.author.mention} Timeout exceeded. Please try again.")
            return -1
        
        # Verify confirmation
        if reaction.emoji == '✅':
            # Edit WatchHistory entry
            mycursor = self.bot.mydb.cursor()
            try:
                logger.info(f'Executing query to edit {showTitle} in WatchHistory for {ctx.author}')
                mycursor.execute("UPDATE watchhistory SET Rating = %d WHERE UserID = %d AND ShowName = \'%s\'" % (rating, userid, showTitle))
                self.bot.mydb.commit()
                logger.info(f'WatchHistory entry for {showTitle} updated for {ctx.author}')
            except (mysql.connector.Error, mysql.connector.Warning) as e:
                await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
                logger.warning(e)
                return None
            await ctx.send(f"{ctx.author.mention} WatchHistory entry for {showTitle} updated!")
        else:
            await ctx.send(f"{ctx.author.mention} Didn't confirm entry. Please try !addhistory again to create an entry.")
            return

    # Clear all WatchHistory for user
    @commands.command(aliases=['ch', 'Clearhistory', 'ClearHistory', 'clearHistory'])
    async def clearhistory(self, ctx):
        # Get User ID
        userid = await MyWatchList.getUserId(self, ctx)
        if userid == -1:
            await ctx.send(f'{ctx.author.mention} User does not exist. Try !watchlist to setup user.')
            return
        
        # Request user to confirm deletion
        msg = await ctx.send(f"{ctx.author.mention} Please confirm you would like clear all entries in your WatchHistory (Select ✅ or ❌)")
        await msg.add_reaction('✅')  # Acknowledge entry
        await msg.add_reaction('❌')  # Decline entry

        def reaction2check(reaction, user):
            name1 = str(ctx.author).split("#")[0]
            return  user.name == name1 and str(reaction.emoji) in ['✅','❌']
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=15, check=reaction2check)
        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.author.mention} Timeout exceeded. Please try again.")
            return -1
        
        # Verify confirmation
        if reaction.emoji == '✅':
            # Get current WatchHistory entries for user
            mycursor = self.bot.mydb.cursor()
            try:
                logger.info(f'Executing query to return WatchHistory entries for {ctx.author}')
                mycursor.execute("SELECT * FROM watchhistory WHERE UserID = \'%s\'" % userid)
            except (mysql.connector.Error, mysql.connector.Warning) as e:
                await ctx.send(f"{ctx.author.mention} An error occurred. Please try again or use /reportbug to submit an issue.")
                logger.warning(e)
                return
            userresults = mycursor.fetchall()
            if not len(userresults): # Empty WatchHistory list
                await ctx.send(f"{ctx.author.mention} Current list is empty. Please use !addhistory to add to your WatchHistory.")
                return
            
            # Remove all entries from WatchHistory table for user
            for x in userresults:
                if (await MyWatchList.removeEntry(self, ctx, userid, x[1], 'watchhistory')) < 0: # Error
                    return
            await ctx.send(f"{ctx.author.mention} Deleted all entries in your WatchHistory!")
        else:
            await ctx.send(f"{ctx.author.mention} Didn't confirm deletion. Please try !clearhistory again to delete all WatchHistory entries.")

async def setup(bot):
    await bot.add_cog(MyWatchList(bot))