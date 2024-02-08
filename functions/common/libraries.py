# pylint: skip-file
"""
DESCRIPTION: All file imports, global variables, auth tokens reside here
Ok to ignore unused libraries
"""
import discord
import os
import wavelink
import logging
import asyncio
import logging.handlers
import random
import pandas
import time
import psutil
import threading
import traceback
import sys
import signal
import spotipy
import requests
import json
import psycopg2

from bs4 import BeautifulSoup
from datetime import date
from pandas import *
from discord.ext import commands, tasks
from dotenv import load_dotenv
from lyricsgenius import Genius
from spotipy.oauth2 import SpotifyClientCredentials
from collections import defaultdict
from psycopg2 import pool
from psycopg2 import ProgrammingError, IntegrityError, DatabaseError, Error
from functools import wraps

load_dotenv()

# Global Variables
ADMIN = '⚡️'
MOD = '🌩️'
artist = ''
created_channels = []
START_TIME = time.time()
user_usage = defaultdict(lambda: {'timestamp': 0, 'count': 0})

# Auth Tokens for API's
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
