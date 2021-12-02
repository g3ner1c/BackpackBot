import asyncio
import datetime
import json
import math
import os
import time

import BackpackTF
import discord
import matplotlib.pyplot as plt
import numpy as np
from discord.ext import commands, tasks
from discord_slash import SlashCommand
from dotenv import load_dotenv
from pretty_help import PrettyHelp
from scipy.interpolate import make_interp_spline

from keep_alive import keep_alive


load_dotenv()

intents = discord.Intents.default()

intents.presences = True
intents.members = True

bot = commands.Bot(intents=intents, command_prefix='>')

bot.help_command = PrettyHelp(color=0x7292a9) # 0x7292a9 should be used for all embeds

global channel_say
channel_say = 0

# client = discord.Client()
slash = SlashCommand(bot, sync_commands=True)

currency = BackpackTF.Currency(apikey=(os.getenv('backpacktoken')))

async def heartbeat():

    global ping_arr
    global time_ping
    ping_arr = np.array([])

    await bot.wait_until_ready()
    while not bot.is_closed():

        if len(ping_arr) < 16:

            ping_arr = np.append(ping_arr, int(round(bot.latency * 1000, 3)))
            time_ping = time.time()

        else:

            ping_arr = np.delete(ping_arr, 0)
            ping_arr = np.append(ping_arr, int(round(bot.latency * 1000, 3)))
            time_ping = time.time()

        await asyncio.sleep(40)


playingStatus = ['Team Fortress 2'
                 ]

watchingStatus = [
                  ]

listeningStatus = [
                   ]


@bot.event
async def on_ready():

    print('Logged in as {0.user}'.format(bot), ' - ', bot.user.id)

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name='Team Fortress 2'))

    # while True:

    #     statusType = random.randint(
    #         1, len(playingStatus)+len(watchingStatus)+len(listeningStatus))

    #     if statusType <= len(playingStatus):
    #         statusNum = random.randint(0, len(playingStatus) - 1)
    #         await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=playingStatus[statusNum]))

    #     elif statusType <= len(playingStatus)+len(watchingStatus):
    #         statusNum = random.randint(0, len(watchingStatus) - 1)
    #         await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=watchingStatus[statusNum]))

    #     elif statusType <= len(playingStatus)+len(watchingStatus)+len(listeningStatus):
    #         statusNum = random.randint(0, len(listeningStatus) - 1)
    #         await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=listeningStatus[statusNum]))

    #     await asyncio.sleep(10)


@bot.command(brief='Returns the current exchange rates for currencies',description='Returns the current exchange rates for currencies')
async def rates(ctx):

    rates_dict = currency.get_currencies()

    embed=discord.Embed(title="Currency Exchange Rate (BP.TF Suggested)", color=0x7292a9)
    embed.add_field(name=rates_dict['metal']['name'], value=("**" + str(rates_dict['metal']['price']['value']) + "** USD"), inline=True)
    embed.add_field(name=rates_dict['hat']['name'], value=("**" + str(rates_dict['hat']['price']['value']) + "** ref"), inline=True)
    embed.add_field(name=rates_dict['key']['name'], value=("**" + str(rates_dict['key']['price']['value']) + "** ref"), inline=True)
    embed.add_field(name=rates_dict['earbuds']['name'], value=("**" + str(rates_dict['earbuds']['price']['value']) + "** ref"), inline=True)

    embed.set_footer(text=((f'Requested by {ctx.message.author.display_name} (') + str(ctx.message.author.id) + ')'))
    embed.timestamp = datetime.datetime.utcnow()
    
    await ctx.send(embed=embed)



# @bot.command(brief='Returns the current price suggestion of an item',description='Returns the current price suggestion of an item')
# async def price(ctx):


@bot.command(brief='Returns user info',description='Returns user info')
async def user(ctx, member: discord.Member):

    embed=discord.Embed(title="User Information", color=0x7292a9)
    embed.add_field(name='Server', value='**'+str(member.guild)+'**', inline=False)
    embed.add_field(name='Username', value=member, inline=False)
    embed.add_field(name='Server Nickname', value=member.nick, inline=False)
    embed.add_field(name='ID', value='`'+str(member.id)+'`', inline=False)
    embed.add_field(name='Status', value='`'+str(member.status)+'`', inline=False)
    embed.add_field(name='Joined', value='`'+str(member.joined_at)+'`', inline=False)
    embed.add_field(name='Role', value=str(member.top_role), inline=False)
    
    embed.set_footer(text=((f'Requested by {ctx.message.author.display_name} (') + str(ctx.message.author.id) + ')'))
    embed.timestamp = datetime.datetime.utcnow()


    # embed.add_field(name='Activity Details', value=str(member.activity.details), inline=False)
    await ctx.send(embed=embed)


@bot.command(brief='Dev command',description='Dev command')
async def exec(ctx, *, command):

    if ctx.author.id == 538921994645798915:

        exec(command)

    else:
        await ctx.send("You're not my dev! >:(")
        print(ctx.author, 'attempted to execute:\n', ctx.content)


@bot.command(brief='Returns latency to the server',description='Returns latency to the server in milliseconds')
async def ping(ctx):

    embed=discord.Embed(title="Pong!", color=0x7292a9)
    embed.add_field(name="Latency", value=(f'`{round(bot.latency * 1000, 3)}ms`'), inline=False)
    embed.set_footer(text=((f'Requested by {ctx.message.author.display_name} (') + str(ctx.message.author.id) + ')'))
    embed.timestamp = datetime.datetime.utcnow()

    await ctx.send(embed=embed)


@bot.command(brief='Returns a latency graph',description='Returns a latency graph over the past 10 minutes')
async def netgraph(ctx):

    time_since_ping = round(time.time() - time_ping)

    x = np.append(np.arange((len(ping_arr) - 1)*-
                  40, 1, 40) - time_since_ping, 0)
    y = np.append(ping_arr, ping_arr[len(ping_arr) - 1])

    X_ = np.linspace(min(x), max(x), 500)
    X_Y_Spline = make_interp_spline(x, y)
    Y_ = X_Y_Spline(X_)

    plt.plot(X_, Y_, color='red')

    plt.xlim(-600, 0)

    plt.ylim(0, max(Y_)*1.1)

    plt.xlabel('Time')

    plt.ylabel('Milliseconds')

    plt.title('Latency within the last 10 minutes')

    plt.savefig("temp/netgraph.png")

    file = discord.File("temp/netgraph.png")
    embed = discord.Embed(color=0x7292a9)
    embed.set_image(url="attachment://netgraph.png")
    embed.set_footer(text=((f'Requested by {ctx.message.author.display_name} (') + str(ctx.message.author.id) + ')'))
    embed.timestamp = datetime.datetime.utcnow()
    await ctx.send(embed=embed, file=file)
    plt.clf()


@bot.command(brief='General information',description='General information')
async def info(ctx):

    await ctx.send('**BackpackBot v0.0.1**\n' \
        'Discord bot for interacting with Backpack.tf developed by awesomeplaya211#5215 (SteamID: 76561198849263860)\n' \
        'Source code is available on GitHub by using *>github*')


# @bot.command(brief='Shows my profile picture',description='Shows my profile picture')
# async def pfp(ctx):

#     file = discord.File("assets/pfp.jpg")
#     embed = discord.Embed(color=0x7292a9)
#     embed.set_image(url="attachment://pfp.jpg")
#     await ctx.send(embed=embed, file=file)


@bot.command(brief='My GitHub Repository',description='My GitHub Repository')
async def github(ctx):

    await ctx.send('https://github.com/awesomeplaya211/BackpackBot')


@bot.command(brief='Add me to your server!',description='Add me to your server!')
async def invite(ctx):
    await ctx.send('Add me to your server!')
    await ctx.send('https://discord.com/api/oauth2/authorize?client_id=915957781843050506&permissions=517880671424&scope=bot')


@bot.command(brief='Status check with uptime',description='Status check with uptime')
async def status(ctx):
    
    t2 = time.time()

    time_online = (
    str(math.floor((t2-t1)/3600)) + ' hours ' +
    str(math.floor(((t2-t1) % 3600)/60)) + ' minutes ' +
    str(round((t2-t1) % 60, 3)) + ' seconds')

    embed=discord.Embed(title="Status", color=0x7292a9)
    embed.add_field(name='Online for', value=time_online, inline=False)
    embed.add_field(name="Online since", value='`'+str(t1)+'`', inline=False)
    embed.set_footer(text=((f'Requested by {ctx.message.author.display_name} (') + str(ctx.message.author.id) + ')'))
    embed.timestamp = datetime.datetime.utcnow()

    await ctx.send(embed=embed)


@bot.command(brief='Kills bot (Dev command)',description='Kills bot (Dev command)')
async def kill(ctx):

    if ctx.author.id == 538921994645798915:
        await ctx.send('*dies*')

        await bot.close()

    else:
        await ctx.send("You're not my dev! >:(")
        print(ctx.author, 'attempted to kill bot')


t1 = time.time()

bot.loop.create_task(heartbeat())

keep_alive()

bot.run(os.getenv('discordtoken'))
