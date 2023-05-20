import discord
import os
from discord.ext import commands

client = commands.Bot(command_prefix='k!')

client.remove_command('help')

# Types in console when bot is online.
@client.event
async def on_ready():
    await client.change_presence(
        activity=discord.Game('Use k!help to see commands'))
    print('Bot is ready.')

  
# Sends a message to users saying the command they attempted does not exist
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('No such command.')
    else:
        print(error)

# Sends users a list of commands and explains their parameters if any
@client.command()
async def help(ctx):
  k = "KIWIN's Commands\n`k!khours` - sends the hours of a member (Ex. k!khours Octavio Castro)\n`k!ktop` - sends the stats of top 3 members with highest hours\n`k!kattended` - sends the # of services a member attended (Ex. k!kattended Octavio Castro)"
  emb = discord.Embed(title="Commands", description=(k), color=2123412)
  await ctx.channel.send(embed=emb)


token = os.environ['KEY']
client.run(token)