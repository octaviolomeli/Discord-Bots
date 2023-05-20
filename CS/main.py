import discord
import pandas as pd
from discord.ext import commands
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import csv
import json
import os
import random
from datetime import date
from datetime import datetime

client = commands.Bot(command_prefix='cs!')

client.remove_command('help')

# list of image paths
images = ['1.png', '2.png', '3.png', '4.png',  '5.png',  '6.png',  '7.png',  '8.png',  '9.png',  '10.png',  '404.png']

# Google Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

creds = None
creds = ServiceAccountCredentials.from_json_keyfile_dict(
        json.loads(os.environ['SERVICE_KEY']), scopes=SCOPES)

# The ID of the spreadsheet for Computer Science club
SPREADSHEET_ID = '1fTPi0kd__miVKRvF1-gJnKSfj6a-DpcvVf_kdSU4RJQ'

service = build('sheets', 'v4', credentials=creds)

# Types in console when bot is online.
@client.event
async def on_ready():
    await client.change_presence(
        activity=discord.Game('Use cs!help to see commands'))
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
  cs = "CS Club Commands\n`cs!projects` - show a list of projects\n`cs!events` - show a list of planned events, like hackathons or game jams\n`cs!month` - show the month's schedule\n`cs!pfp` - change the bot's pfp\n\n"
  emb = discord.Embed(title="Commands", description=(cs), color=2123412)
  await ctx.channel.send(embed=emb)

# Assign a role to a member clicking a reaction
@client.Cog.listener()
async def on_raw_reaction_add(payload):
    message_id = payload.message_id
    if message_id == 874797444939014154:
        guild_id = payload.guild_id
        guild = discord.utils.find(lambda g : g.id == guild_id, self.client.guilds)

        print(payload.emoji.name)
        if payload.emoji.name == '🧑‍🔬':
            role = discord.utils.get(guild.roles, name='scientist')
        elif payload.emoji.name == '🎮':
            role = discord.utils.get(guild.roles, name='gameDevs')
        elif payload.emoji.name == '🌐':
            role = discord.utils.get(guild.roles, name='webDevs')
        elif payload.emoji.name == '📊':
            role = discord.utils.get(guild.roles, name='data science')
        elif payload.emoji.name == '🧑‍💻':
            role = discord.utils.get(guild.roles, name='technician')
        elif payload.emoji.name == '📱':
            role = discord.utils.get(guild.roles, name='mobileDevs')
        elif payload.emoji.name == '📖':
            role = discord.utils.get(guild.roles, name='learners')
        else:
            role = None

        if role is not None:
            member = payload.member
            if member is not None:
                await member.add_roles(role)
                members_roles = [ i.name for i in member.roles ]
                if 'officers' not in list(members_roles):
                    await member.add_roles(discord.utils.get(guild.roles, name='members'))
                print("Member has been added a role")
            else:
                print("Member not found.")
        else:
            print("No role found")


# Remove the role from a member if they remove their reaction
@client.Cog.listener()
async def on_raw_reaction_remove(payload):
    message_id = payload.message_id
    if message_id == 874797444939014154:
        guild_id = payload.guild_id
        guild = discord.utils.find(lambda g : g.id == guild_id, self.client.guilds)

        if payload.emoji.name == '🧑‍🔬':
            role = discord.utils.get(guild.roles, name='scientist')
        elif payload.emoji.name == '🎮':
            role = discord.utils.get(guild.roles, name='gameDevs')
        elif payload.emoji.name == '🌐':
            role = discord.utils.get(guild.roles, name='webDevs')
        elif payload.emoji.name == '📊':
            role = discord.utils.get(guild.roles, name='data science')
        elif payload.emoji.name == '🧑‍💻':
            role = discord.utils.get(guild.roles, name='technician')
        elif payload.emoji.name == '📱':
            role = discord.utils.get(guild.roles, name='mobileDevs')
        elif payload.emoji.name == '📖':
            role = discord.utils.get(guild.roles, name='learners')
        else:
            role = None

        if role is not None:
            member = await (await self.client.fetch_guild(payload.guild_id)).fetch_member(payload.user_id)
            if role is not None:
              await member.remove_roles(role)
              print("Role removed")
        else:
            print("No role found")


# Show a list of current projects (or just project)
@client.command()
async def projects(ctx):
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="CurrentProjects!A1:C24").execute()

    with open('data/CS_current_projects.csv', 'w', newline='') as csvfile:
      csv_writer = csv.writer(csvfile, delimiter=',')
      for row in result['values']:
        csv_writer.writerow(row)

    stat_list = pd.read_csv('data/CS_current_projects.csv')
    stat_list = stat_list.fillna(0)
    stat_list = stat_list[['Member', 'Category', 'Project Link']]

    dates = " "
    types = " "
    names = " "

    for x in range(len(stat_list.index)):
        dates += stat_list['Project Link'].iloc[x] + "\n"
        types += stat_list['Category'].iloc[x] + "\n"
        names += stat_list['Member'].iloc[x] + "\n"
    
    if len(stat_list.index) == 0:
      emb = discord.Embed(title="Current Projects", color=15418782, description = "There are no current projects.")
      await ctx.channel.send(embed=emb)
    else:
      emb = discord.Embed(title="Current Projects", color=15418782)
      emb.add_field(name="Member", value=names, inline=True)
      emb.add_field(name="Category", value=types, inline=True)
      emb.add_field(name="Project Link", value=dates, inline=True)

      await ctx.channel.send(embed=emb)


# Send 5 events, 1 from the past, 4 from the future
@client.command()
async def events(ctx):
    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="Events!A1:F100").execute()

    # Write data into a CSV file to later use in a dataframe
    with open('data/CS_event_days.csv', 'w', newline='') as csvfile:
      csv_writer = csv.writer(csvfile, delimiter=',')
      for row in result['values']:
        csv_writer.writerow(row)
        
    stat_list = pd.read_csv('data/CS_event_days.csv', header=0)
    stat_list = stat_list.dropna(0)
    stat_list = stat_list[['Date', 'Day', 'Time', 'Type', 'Name', 'Hidden']]
    stat_list = stat_list[stat_list["Hidden"] == False]
    stat_list["Date"] = pd.to_datetime(stat_list["Date"], format="%m/%d/%Y")
    stat_list.reset_index(drop=True, inplace=True)

    emb = discord.Embed(title="Upcoming Events", color=3066993)

    current_date = datetime.now()
    all_dates = stat_list['Date'].to_list()
    starting_index = 0
    # store the index of the event that is before today’s date
    for i, data in enumerate(all_dates):
      if current_date < data:
        starting_index = i - 1
        if starting_index == -1:
          starting_index = 0
        break
    stat_list = stat_list.iloc[starting_index:]
    dates = ""
    types = ""
    names = ""

    stat_list.reset_index(drop=True, inplace=True)
    for x in range(5):
        dates += str(stat_list['Date'].iloc[x].date().month) +"/"+ str(stat_list['Date'].iloc[x].date().day) + " (" + stat_list['Day'].iloc[x]  + ")\n"
        types += stat_list['Type'].iloc[x] + "\n"
        names += stat_list['Name'].iloc[x] + "\n"

    emb.add_field(name="Date", value=dates, inline=True)
    emb.add_field(name="Type", value=types, inline=True)
    emb.add_field(name="Name", value=names, inline=True)
    await ctx.channel.send(embed=emb)

# Changes profile picture of the bot
@client.command()
async def pfp(ctx):
    try:
      members_roles = [ i.name for i in ctx.message.author.roles ]
      if 'officers' not in list(members_roles):
          await ctx.send("You can't use this command.")
      else:

        try:
            decided_pfp = "../images/" + random.choice(images)
            with open(decided_pfp, 'rb') as image:
              await commands.user.edit(avatar=image.read())
            await ctx.send("Done, changed to ", file=discord.File(decided_pfp))
        except:
          await ctx.send("Try again later, you are changing it too quickly.")
        
    except Exception as e:
        print(e)
        await ctx.send("Something has gone wrong. Alert Octavio please.")


# Send 5 events from this month
@client.command()
async def month(ctx):
    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="Events!A1:F100").execute()

    with open('data/CS_event_days.csv', 'w', newline='') as csvfile:
      csv_writer = csv.writer(csvfile, delimiter=',')
      for row in result['values']:
        csv_writer.writerow(row)

    stat_list = pd.read_csv('data/CS_event_days.csv')
    stat_list = stat_list.fillna(0)
    stat_list = stat_list[['Date', 'Day','Time', 'Type', 'Name', 'Hidden']]
    stat_list["Date"] = pd.to_datetime(stat_list["Date"], format="%m/%d/%Y")
    stat_list = stat_list[stat_list["Hidden"] == False]

    current_date = date.today()
    # store the index of the event that is before today’s date
    stat_list = stat_list[stat_list["Date"].dt.month == current_date.month ]
    stat_list.reset_index(drop=True, inplace=True)
    dates = ""
    types = ""
    names = ""
    for x in range(len(stat_list)):
        if stat_list['Date'].iloc[x].date() < current_date: 
          dates += "*" + str(stat_list['Date'].iloc[x].date().month) +"/"+ str(stat_list['Date'].iloc[x].date().day) + " (" + stat_list['Day'].iloc[x]  + ")*\n"
          types += "*" + stat_list['Type'].iloc[x] + "*\n"
          names += "*" + stat_list['Name'].iloc[x] + "*\n"
        else:
          dates += str(stat_list['Date'].iloc[x].date().month) +"/"+ str(stat_list['Date'].iloc[x].date().day) + " (" + stat_list['Day'].iloc[x]  + ")\n"
          types += stat_list['Type'].iloc[x] + "\n"
          names += stat_list['Name'].iloc[x] + "\n"

    if len(stat_list) == 0:
      emb = discord.Embed(title="Events for this month", color=11342935, description="There are no events for this month.")
    else:
      emb = discord.Embed(title="Events for this month", color=11342935)
      emb.add_field(name="Date", value=dates, inline=True)
      emb.add_field(name="Type", value=types, inline=True)
      emb.add_field(name="Name", value=names, inline=True)
  
    await ctx.channel.send(embed=emb)

token = os.environ['KEY']
client.run(token)