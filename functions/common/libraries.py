"""
DESCRIPTION: All file imports, global variables, auth tokens reside here.
Ok to ignore unused libraries.
"""
# pylint: disable=unused-import
# pylint: disable=redefined-builtin
# pylint: disable=wildcard-import
# pylint: disable=ungrouped-imports
# pylint: disable=unused-wildcard-import

import asyncio
import discord
import json
import logging
import logging.handlers
import mysql.connector
import os
import pandas
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
from lyricsgenius import Genius
from mysql.connector import pooling
from pandas import *
from spotipy.oauth2 import SpotifyClientCredentials

# Load environment variables
load_dotenv()

# Global Variables
ADMIN = '⚡️'
MOD = '🌩️'
artist = ''  # pylint: disable=invalid-name
created_channels = []
START_TIME = time.time()
user_usage = defaultdict(lambda: {'timestamp': 0, 'count': 0})

# Auth Tokens for APIs
DISCORD_TOKEN = os.getenv('TOKEN')
genius = Genius('GENIUSTOKEN')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
TRACKER_GG = os.getenv('TRACKERGG')
RIOT_TOKEN = os.getenv('RIOTTOKEN')
GITHUB_TOKEN = os.getenv('GITHUBTOKEN')

# Authenticate application with Spotify
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
