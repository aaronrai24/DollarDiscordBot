# pylint: skip-file
"""
DESCRIPTION: All file imports, global variables, auth tokens reside here.
Ok to ignore unused libraries.
"""

import asyncio
import discord
import json
import logging
import logging.handlers
import os
import pandas
import psycopg2
import psutil
import random
import requests
import signal
import spotipy
import sys
import threading
import time
import traceback
import wavelink

from bs4 import BeautifulSoup
from collections import defaultdict
from datetime import date
from discord.ext import commands, tasks
from dotenv import load_dotenv
from functools import wraps
from lyricsgenius import Genius
from pandas import *
from psycopg2 import DatabaseError, Error, IntegrityError, ProgrammingError, pool
from spotipy.oauth2 import SpotifyClientCredentials

# Load environment variables
load_dotenv()

# Global Variables
ADMIN = '⚡️'
MOD = '🌩️'
artist = ''
created_channels = []
START_TIME = time.time()
user_usage = defaultdict(lambda: {'timestamp': 0, 'count': 0})
guild_text_channels = {}
guild_voice_channels = {}
ERROR_MAPPING = {
    commands.MissingRole: ("Missing Required Role", "User has insufficient role"),
    commands.CommandNotFound: ("Command Not Found", "User tried to use a command that does not exist"),
    commands.BadArgument: ("Invalid Argument", "User provided an invalid argument"),
   	commands.CheckFailure: ("Incorrect Command Usage", "User used command incorrectly"),
    discord.errors.PrivilegedIntentsRequired: ("Missing Required Intent", "Bot is missing required intent"),
    commands.CommandOnCooldown: ("Command Cooldown", "Command on cooldown for user"),
    wavelink.LavalinkException: ("Lavalink Error", "Lavalink error occurred"),
    wavelink.InvalidChannelStateException: ("Invalid Channel State", "Invalid channel state"),
}

# Auth Tokens for APIs
DISCORD_TOKEN = os.getenv('TOKEN')
genius = Genius('GENIUSTOKEN')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
TRACKER_GG = os.getenv('TRACKERGG')
RIOT_TOKEN = os.getenv('RIOTTOKEN')
GITHUB_TOKEN = os.getenv('GITHUBTOKEN')
PATCHES_CHANNEL = os.getenv('PATCHES_CHANNEL')
DEVELOPER = os.getenv('CASH')

# Authenticate application with Spotify
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
