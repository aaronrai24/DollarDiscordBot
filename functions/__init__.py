"""
This package contains all the functions that are used in the bot.
The functions are divided into different classes based on their functionality.
The classes are:    
    - AutoChannelCreation
    - GeneralFunctions
    - PushNotifications
    - Queries
"""
from .common import AutoChannelCreation
from .common import GeneralFunctions
from .notifications import PushNotifications
from .queries import Queries

__all__ = ["AutoChannelCreation", "GeneralFunctions", "PushNotifications", "Queries"]

print("Functions package initialized")
