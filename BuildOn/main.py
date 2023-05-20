import discord
import pandas as pd
from discord.ext import commands
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import csv
import json
import os

client = commands.Bot(command_prefix='b!')

client.remove_command('help')

# Types in console when bot is online.
@client.event
async def on_ready():
    await client.change_presence(
        activity=discord.Game('Use b!help to see commands'))
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
  buildon = "buildOn Commands\n`b!stats` - sends the stats of a member (Ex. b!stats Octavio Castro)\n`b!btop` - sends the stats of top 3 members with highest hours\n`b!battended` - sends the # of services a member attended (Ex. b!battended Octavio Castro)\n\n"
  emb = discord.Embed(title="Commands", description=(buildon), color=2123412)
  await ctx.channel.send(embed=emb)


# Google Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

creds = None
creds = ServiceAccountCredentials.from_json_keyfile_dict(
        json.loads(os.environ['SERVICE_KEY']), scopes=SCOPES)

# The ID of the buildOn spreadsheet
SPREADSHEET_ID = '1ZTjoYnyJgF23qdyULC9vXwCpJs7iW-hOksXha7wgYpU'

service = build('sheets', 'v4', credentials=creds)

# sends the information of a person
@client.command()
async def stats(ctx, *, name='Octavio Castro'):
# Call the Sheets API and select a range of data
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="2020-2021 Hours!B2:F98").execute()

    # Save the information in a CSV file to later read in Pandas
    with open('data/buildOn_stats.csv', 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile, delimiter=',')
    for row in result['values']:
        csv_writer.writerow(row)

    # Read the data into a Pandas dataframe
    stat_list = pd.read_csv('data/buildOn_stats.csv')

    stat_list = stat_list.fillna(0)
    stat_list.set_index('Member Name', inplace=True)
    try:
        emb = discord.Embed(title=name,color=11342935)
        emb.add_field(name="Grade", value=stat_list.loc[name]['Grade'], inline=True)
        emb.add_field(name="Hours Gained", value=stat_list.loc[name]['Hours Gained'], inline=True)
        emb.add_field(name="Goal", value=stat_list.loc[name]['Goal'], inline=True)
    
        await ctx.channel.send(embed=emb)
    except:
        await ctx.send(
            '```No member with that name exists. Check your spelling and capitalization.\nIf error, DM june#6598```'
        )


# sends top 3 people with hours
@client.command()
async def btop(ctx):

    # Call the Sheets API and select a range of data
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="2020-2021 Hours!B2:F98").execute()

    # Save the information in a CSV file to later read in Pandas
    with open('data/buildOn_stats.csv', 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',')
        for row in result['values']:
        csv_writer.writerow(row)

    stat_list = pd.read_csv('data/buildOn_stats.csv')
    stat_list = stat_list.fillna(0)
    stat_list = stat_list.sort_values("Hours Gained", ascending=False, inplace=False)[:3]
    stat_list.reset_index(inplace=True)

    # Send the information of the top 3 members
    emb = discord.Embed(title="Top 3",color=11342935)
    names = f"{stat_list['Member Name'][0]}\n{stat_list['Member Name'][1]}\n{stat_list['Member Name'][2]}"
    emb.add_field(name="Name", value=names, inline=True)

    grades = f"{stat_list['Grade'][0]}\n{stat_list['Grade'][1]}\n{stat_list['Grade'][2]}"
    emb.add_field(name="Grade", value=grades, inline=True)

    hours = f"{stat_list['Hours Gained'][0]}\n{stat_list['Hours Gained'][1]}\n{stat_list['Hours Gained'][2]}"
    emb.add_field(name="Hours Gained", value=hours, inline=True)
        
    await ctx.channel.send(embed=emb)


# sends the number of services a member attended
@client.command()
async def battended(ctx, *,member='Octavio Castro'):

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="2020-2021 Hours!B2:AR98").execute()

    # Write the data into a CSV file to read later in Pandas
    with open('data/buildOn_services.csv', 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',')
        for row in result['values']:
        csv_writer.writerow(row)

    num_list = pd.read_csv('data/buildOn_services.csv')
    num_list = num_list.fillna(0)
    num_list.set_index('Member Name', inplace=True)
    # Get rid of the unneccesary information for this function
    dropping = ['Grade', 'Hours Gained', 'Goal', 'Hours Needed']
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