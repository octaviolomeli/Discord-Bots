import discord
import pandas as pd
from discord.ext import commands
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import csv
import json
import os

client = commands.Bot(command_prefix='k!')

client.remove_command('help')

# Google Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

creds = None
creds = ServiceAccountCredentials.from_json_keyfile_dict(
        json.loads(os.environ['SERVICE_KEY']), scopes=SCOPES)

# The ID of the buildOn spreadsheet
SPREADSHEET_ID = '1P1qSe_ACpz3yWTrMAkL85AUoqj0O0hJHEXMrkcjDaoI'

service = build('sheets', 'v4', credentials=creds)

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



# sends the information of a person
@client.command()
async def khours(ctx, *, name='Octavio Lomeli-Castro'):
  # Call the Sheets API and select a range of data
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="Hours!A2:B66").execute()

    # Save the information in a CSV file to later read in Pandas
    with open('data/kiwin_hours.csv', 'w', newline='') as csvfile:
      csv_writer = csv.writer(csvfile, delimiter=',')
      for row in result['values']:
        csv_writer.writerow(row)

    # Read the data into a Pandas dataframe
    stat_list = pd.read_csv('data/kiwin_hours.csv')
    
    stat_list = stat_list.fillna(0)
    stat_list.set_index('Member Name', inplace=True)
    try:
        await ctx.send(f"{name} has {stat_list['Hours'].loc[name]} hours.")
    except:
        await ctx.send(
            '```No member with that name exists. Check your spelling and capitalization.\nIf error, DM june#6598```'
        )


# sends top 3 people with hours
@client.command()
async def ktop(ctx):

  # Call the Sheets API and select a range of data
  sheet = service.spreadsheets()
  result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="Hours!A2:B66").execute()
  
  # Save the information in a CSV file to later read in Pandas
  with open('data/kiwin_hours.csv', 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile, delimiter=',')
    for row in result['values']:
      csv_writer.writerow(row)

  stat_list = pd.read_csv('data/kiwin_hours.csv')
  stat_list = stat_list.fillna(0)
  stat_list = stat_list.sort_values("Hours", ascending=False, inplace=False)[:3]
  stat_list.reset_index(inplace=True)
  
  # Send the information of the top 3 members
  emb = discord.Embed(title="Top 3",color=11342935)
  names = f"{stat_list['Member Name'][0]}\n{stat_list['Member Name'][1]}\n{stat_list['Member Name'][2]}"
  emb.add_field(name="Name", value=names, inline=True)

  hours = f"{stat_list['Hours'][0]}\n{stat_list['Hours'][1]}\n{stat_list['Hours'][2]}"
  emb.add_field(name="Hours", value=hours, inline=True)
      
  await ctx.channel.send(embed=emb)


# sends the number of services a member attended
@client.command()
async def kattended(ctx, *,member='Octavio Lomeli-Castro'):

  # Call the Sheets API
  sheet = service.spreadsheets()
  result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="Hours!A2:O66").execute()

  # Write the data into a CSV file to read later in Pandas
  with open('data/kiwin_info.csv', 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile, delimiter=',')
    for row in result['values']:
      csv_writer.writerow(row)

  num_list = pd.read_csv('data/kiwin_info.csv')
  num_list = num_list.fillna(0)
  num_list.set_index('Member Name', inplace=True)
  # Get rid of the unneccesary information for this function
  dropping = ['Hours']
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