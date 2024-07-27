"""
This package contains all the functions that are used in the bot.
The functions are divided into different classes based on their functionality.
The classes are:    
    - AutoChannelCreation
    - GeneralFunctions
"""
from .autochannelcreation import AutoChannelCreation
from .generalfunctions import GeneralFunctions

__all__ = ["AutoChannelCreation", "GeneralFunctions"]

print("Functions package initialized")
