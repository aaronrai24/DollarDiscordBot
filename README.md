# DollarDiscordBot
My first discord bot

This discord bot leverages lavalink to play music from popular websites, but its much more than that. Dollar spans past just music and becomes a full moderator for your discord. Dollar has the ability to create personal voice channels for users. Dollar is also smart enough to recognize and responsd to only one channel and will remove commands entered in the wrong text channel. Dollar also will only respond to (music related) commands when the user is in a voice channel. 

Requirements to be able to use Dollar in your discord:

1. Must have a text channel that starts with 'commands', if you have emojis after the commands string that is fine. 
2. Must have a role with 🎧(exact copy is from here: https://emojipedia.org/headphone/) as the title. Dollar automatically adds/removes this role to users when the join/leave voice channels. Dollar only responsds to users with this role. 

To use auto channel creation feature:
1. Must have a voice channel with 'JOIN HERE💎' as the tittle of that voice channel. Dollar recognizes users joining this voice channel, and will automatically create a channel for that user and then move them to that channel. Once that created channel is empty, dollar will remove that channel. 
