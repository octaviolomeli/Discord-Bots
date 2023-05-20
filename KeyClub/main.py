import discord
import os
from discord.ext import commands

client = commands.Bot(command_prefix='kc!')

client.remove_command('help')

# Types in console when bot is online.
@client.event
async def on_ready():
    await client.change_presence(
        activity=discord.Game('Use kc!help to see commands'))
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
  kc = "Key Club Commands\n`kc!kcstats` - sends the stats of a member (Ex. kc!kcstats Octavio Castro)\n`kc!kctop` - sends the stats of top 3 members with highest hours\n`kc!kcattended` - sends the # of services a member attended (Ex. kc!kcattended Octavio Castro)\n\n"
  emb = discord.Embed(title="Commands", description=(kc), color=2123412)
  await ctx.channel.send(embed=emb)


token = os.environ['KEY']
client.run(token)