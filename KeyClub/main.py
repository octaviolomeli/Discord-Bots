import discord
import pandas as pd
from discord.ext import commands
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import csv
import json
import os

client = commands.Bot(command_prefix='kc!')

client.remove_command('help')

# Google Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

creds = None
creds = ServiceAccountCredentials.from_json_keyfile_dict(
        json.loads(os.environ['SERVICE_KEY']), scopes=SCOPES)

# The ID of the buildOn spreadsheet
SPREADSHEET_ID = '1lANIdteNy03_Pmzx2i7KWtXC2JBTBpAHy2r1VnJXw0s'

service = build('sheets', 'v4', credentials=creds)

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

# sends the information of a person
@client.command()
async def kcstats(ctx, *, name='Octavio Lomeli-Castro'):
  # Call the Sheets API and select a range of data
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="Sheet1!A4:E39").execute()

    # Save the information in a CSV file to later read in Pandas
    with open('data/keyclub_stats.csv', 'w', newline='') as csvfile:
      csv_writer = csv.writer(csvfile, delimiter=',')
      for row in result['values']:
        csv_writer.writerow(row)

    # Read the data into a Pandas dataframe
    stat_list = pd.read_csv('data/keyclub_stats.csv')
    
    stat_list = stat_list.fillna(0)
    stat_list.set_index('Name', inplace=True)
    try:
        message = "{} has {} hours and attended {} DCMs".format(name, stat_list['Total'].loc[name], stat_list['DCM\'s Attended'].loc[name])
        await ctx.send(message)
    except:
        await ctx.send(
            '```No member with that name exists. Check your spelling and capitalization.\nIf error, DM june#6598```'
        )


# sends top 3 people with hours
@client.command()
async def kctop(ctx):

  # Call the Sheets API and select a range of data
  sheet = service.spreadsheets()
  result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="Sheet1!A4:E39").execute()
  
  # Save the information in a CSV file to later read in Pandas
  with open('data/keyclub_stats.csv', 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile, delimiter=',')
    for row in result['values']:
      csv_writer.writerow(row)

  stat_list = pd.read_csv('data/keyclub_stats.csv')
  stat_list = stat_list.fillna(0)
  stat_list = stat_list.sort_values("Total", ascending=False, inplace=False)[:3]
  stat_list.reset_index(inplace=True)
  
  # Send the information of the top 3 members
  emb = discord.Embed(title="Top 3",color=11342935)
  names = f"{stat_list['Name'][0]}\n{stat_list['Name'][1]}\n{stat_list['Name'][2]}"
  emb.add_field(name="Name", value=names, inline=True)

  grades = f"{stat_list['Grade'][0]}\n{stat_list['Grade'][1]}\n{stat_list['Grade'][2]}"
  emb.add_field(name="Grade", value=grades, inline=True)
  
  hours = f"{stat_list['Total'][0]}\n{stat_list['Total'][1]}\n{stat_list['Total'][2]}"
  emb.add_field(name="Total", value=hours, inline=True)
      
  await ctx.channel.send(embed=emb)


# sends the number of services a member attended
@client.command()
async def kcattended(ctx, *,member='Octavio Lomeli-Castro'):

  # Call the Sheets API
  sheet = service.spreadsheets()
  result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="Sheet1!A4:EP39").execute()

  # Write the data into a CSV file to read later in Pandas
  with open('data/keyclub_info.csv', 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile, delimiter=',')
    for row in result['values']:
      csv_writer.writerow(row)

  num_list = pd.read_csv('data/keyclub_info.csv')
  num_list = num_list.fillna(0)
  num_list.set_index('Name', inplace=True)
  # Get rid of the unneccesary information for this function
  dropping = ["Position", "Grade", "Total", "DCM's Attended"]
  num_list = num_list.drop(dropping, axis = 1)

  try:
    count = 0
    for column_num in range(len(num_list.columns)):
        if not(num_list.loc[member][column_num] in [0, '0', '', ' ', None]) :
            count += 1
    await ctx.send("{} has attended {} services.".format(member, count))
  except:
    await ctx.send('```No member with that name exists. Check your spelling and capitalization.\nIf error, DM june#6598```')

token = os.environ['KEY']
client.run(token)