from ..common.libraries import(
    discord, commands, requests, os, TRACKER_GG, RIOT_TOKEN
)
from ..common.generalFunctions import(
    setup_logger
)

logger = setup_logger('game-commands')

class GameCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    # Retreive CSGO Stats
    @commands.command(aliases=['cs'])
    async def csgo(self, ctx, player_id):
        url = f'https://public-api.tracker.gg/v2/csgo/standard/profile/steam/{player_id}'
        headers = {'TRN-Api-Key': f'{TRACKER_GG}'}
        
        response = requests.get(url, headers=headers)
        logger.info(f'Retrieving CSGO stats from TrackerGG, player: {player_id}')
        if response.ok:
            data = response.json()
            logger.info('Stats retrieved, embedding')

            embed = discord.Embed(title=f"{data['data']['platformInfo']['platformUserHandle']}'s CSGO Stats", color=0xFFA500)
            avatar_url = data['data']['platformInfo']['avatarUrl']
            embed.set_thumbnail(url='attachment://output.png')
            embed.set_author(name=data['data']['platformInfo']['platformUserHandle'], icon_url=avatar_url)

            for segment in data['data']['segments']:
                segment_title = segment['metadata']['name']
                stats = segment['stats']

                for stat_key, stat_value in stats.items():
                    stat_name = stat_value['displayName']
                    stat_value = stat_value['displayValue']
                    embed.add_field(name=stat_name, value=stat_value, inline=True)

                embed.add_field(name="Segment", value=segment_title, inline=False)
                file_path = os.path.join("images", "csgo.png")
                img = discord.File(file_path, filename='csgo.png')
                embed.set_thumbnail(url="attachment://csgo.png")
            # send the embed message
            await ctx.send(embed=embed, file=img)
        else:
            await ctx.send('Failed to retrieve CSGO stats, are you registered with TrackerGG? If yes, please submit a bug ticket using /reportbug')
            logger.error(f'Failed to retrieve CSGO stats for player: {player_id}')
            logger.warning(response)

    # Retreive Specifc Apex Stats, filters can be weapon, gameMode, mapPool
    @commands.command(aliases=['Apex'])
    async def apex(self, ctx, player_id):
        
        url = f'https://public-api.tracker.gg/v2/apex/standard/profile/origin/{player_id}'
        headers = {'TRN-Api-Key': f'{TRACKER_GG}'}
        
        response = requests.get(url, headers=headers)
        logger.info(f'Retrieving Apex stats from TrackerGG, player: {player_id}')
        if response.ok:
            data = response.json()
            logger.info('Stats retrieved, embedding')
            
            embed = discord.Embed(title=f"{data['data']['platformInfo']['platformUserHandle']}'s Apex Stats", color=0xA70000)
            player_info = data['data']['platformInfo']
            avatar_url = player_info['avatarUrl']
            handle = player_info['platformUserHandle']
            embed.set_author(name=handle, icon_url=avatar_url)

            lifetime_stats = data['data']['segments'][0]['stats']
            level = lifetime_stats['level']['displayValue']
            kills = lifetime_stats['kills']['displayValue']
            embed.add_field(name='Level', value=level, inline=True)
            embed.add_field(name='Lifetime Kills', value=kills, inline=True)

            rank_score = lifetime_stats['rankScore']
            rank_name = rank_score['metadata']['rankName']
            embed.add_field(name='Rank', value=rank_name, inline=True)
            
            active_legend_stats = data['data']['segments'][1]['stats']
            legend_name = data['data']['segments'][1]['metadata']['name']
            embed.add_field(name='Active Legend', value=legend_name, inline=False)

            file_path = os.path.join("images", "apex.png")
            img = discord.File(file_path, filename='apex.png')
            embed.set_thumbnail(url="attachment://apex.png")
            
            await ctx.send(embed=embed, file=img)
        else:
            await ctx.send('Failed to retrieve Apex stats, are you registered with TrackerGG? If yes, please submit a bug ticket using /reportbug')
            logger.error(f'Failed to retrieve Apex stats for player: {player_id}')
            logger.warning(response)

    @commands.command(aliases=['lol', 'league'])
    async def leagueoflegends(self, ctx, player_id):
        region = 'na1'
        summoner_url = f'https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{player_id}'
        summoner_headers = {'X-Riot-Token': RIOT_TOKEN}

        # Get Account Data
        logger.info(f'Getting summoner data from RIOT API, player: {player_id}')
        summoner_response = requests.get(summoner_url, headers=summoner_headers)
        
        # Get Users last matches
        logger.info(f'Getting summoners last match from RIOT API, player: {player_id}')

        # Return all data collected into a discordEmbed
        if summoner_response.status_code == 200:
            logger.info(f'Obtained summoner data, player:{player_id}')
            summoner_data = summoner_response.json()
            summoner_id = summoner_data['id']

            # Get Summoner ranked data
            logger.info('Now obtaining summoner stats from RIOT API')
            stats_url = f'https://{region}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}'
            stats_response = requests.get(stats_url, headers=summoner_headers)

            logger.info('Obtained summoner stats from RIOT API, embedding')
            embed = discord.Embed(title=f'{player_id} Ranked Stats', color=0x9933FF)
            if stats_response.status_code == 200:
                stats = stats_response.json()
                profile_icon_id = summoner_data['profileIconId']
                level = summoner_data['summonerLevel']
                profile_icon_url = f'http://ddragon.leagueoflegends.com/cdn/11.11.1/img/profileicon/{profile_icon_id}.png'

                if not stats:
                    embed.add_field(name='No Results Returned', value='Have you played ranked?')
                else:
                    for stat in stats:
                        embed.add_field(name=stat['queueType'], value=f'{stat["tier"]} {stat["rank"]} ({stat["leaguePoints"]} LP)', inline=True)
                        embed.add_field(name='Wins', value=f'{stat["wins"]}', inline=True)
                        embed.add_field(name='Losses', value=f'{stat["losses"]}', inline=True)
                embed.set_author(name=f'{player_id} LVL: {level}', icon_url=profile_icon_url)
                file_path = os.path.join("images", "league.jpg")
                img = discord.File(file_path, filename='league.jpg')
                embed.set_thumbnail(url="attachment://league.jpg")
                await ctx.send(embed=embed, file=img)
            else:
                logger.info(f'Failed to get summoner stats, response: {stats_response}')
                await ctx.send('Error retrieving stats.')
        else:
            logger.info(f'Failed to get summoner, response: {summoner_response}')
            await ctx.send('Player not found.')

async def setup(bot):
    await bot.add_cog(GameCommands(bot))