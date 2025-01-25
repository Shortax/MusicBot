import asyncio
from collections import deque
from datetime import datetime, date
import discord
from discord.ext import commands
from discord.ext import tasks
import json
import math
from mutagen.mp3 import MP3
import os
import random as rand
import requests
import shutil
import sys
from threading import Thread
import time
from time import sleep
from time import strftime
from time import localtime
import youtube_dl
from youtube_dl import YoutubeDL
from threading import Thread
import threading

script_dir = os.path.dirname(__file__)
rel_path = "bot_stuff/"
abs_file_path = os.path.join(script_dir, rel_path)

readTok = open((script_dir+"\\conf"),"r")
TOKEN = readTok.read().split("DiscordToken=")[1]
readTok.close()
if "TOKENHERE" in TOKEN:
    print("please enter a valid Discord Bot Token")
    time.sleep(1)
    exit(1)

client = discord.Client()

PREFIX = 'm.'
intents = discord.Intents.default()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)


global songpath
songfolder = "Queue/"
songpath = os.path.join(script_dir,songfolder)

global r
r = {}

global order
order = {}

global currentSong
currentSong = {}

def getOrder():
    global order
    return order

def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()

def is_connected(guild):
    voice_client = getClient(guild)
    return voice_client and voice_client.is_connected()

def readJson(filename):
  with open((abs_file_path+filename+".json"), "r") as f:
    data = json.load(f)
    f.close
  return data

def appendJson(filename,data):
  with open((abs_file_path+filename+".json"), "a") as f:
      f.write(data)
      f.write("\n")

def writeJson(filename,data):
  with open((abs_file_path+filename+".json"), "w") as f:
    json.dump(data,f)

def getClient(guildID):
  g = getGuild(guildID)
  return discord.utils.get(bot.voice_clients,guild=g)

def getGuild(guildID):
  global r
  try:
    return r[str(guildID)]
  except:
    return None

@bot.command()
async def parseEmote(ctx,emoji):
  print(emoji)

@bot.event
async def on_ready():
  global timeCheck
  print(f'Logged in as: {bot.user.name}')
  print(f'With ID: {bot.user.id}')
  await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=':)'))

  guilds = readJson("guilds")

  for g in guilds:
    data = await bot.fetch_guild(g)
    r[str(g)] = data

  timeCheck = datetime.now()
  print(timeCheck)
  #await tick.start()

def get_prefix(client, message):
  if message.guild:
    prefixes = readJson("prefixes")
    return prefixes[str(message.guild.id)]
bot.command_prefix = get_prefix

def getPrefix1(guild):
  if guild:
    prefixes = readJson("prefixes")
    return prefixes[str(guild.id)]

@bot.event
async def on_guild_join(guild):
  global r
  prefixes = readJson("prefixes")

  prefixes[str(guild.id)] = "m."

  writeJson("prefixes",prefixes)
        
  name = "[f.] SnakeMusic" 
  member = bot.user
  await member.edit(nick=name)

  r[str(guild.id)] = guild

  guilds = readJson("guilds")
  guilds[str(guild.id)] = guild.id
  writeJson("guilds",guilds)

@bot.command()
async def prefix(ctx, prefix):
  if prefix == "" or prefix == " " or not prefix:
    await ctx.send("Invalid input")
  else:
    prefixes = readJson("prefixes")

    prefixes[str(ctx.guild.id)] = prefix

    writeJson("prefixes",prefixes)
    await ctx.send("My prefix was changed to ``" + prefix + "``")
    
    name = "[" + prefix + "] SnakeMusic"
    i = bot.user.id
    member1 = await ctx.guild.fetch_member(i)
    await member1.edit(nick=name)

def messageEmb(auth: discord.Member,message,ctx):
  if auth.id == 389062672953376769:
    col = 0x990099
  elif auth.id == 501312057002426389:
    col = 0x67eb34
  elif auth.id == 744497461728641065:
    col = 0x34c9eb
  elif auth.id == 587293229087457313:
    col = 0xbf0011
  elif auth.id == 694586297725222952:
    col = 0x42e3f5
  elif auth.id == 625666593774370835 or 724852367425798225:
    col = 0xf5e342
  elif auth.id == 744146220745752599:
    col = 0x110770
  else:
    col = 0x333333

  stringo = "{} chose to play".format(auth.name)
  cl = getClient(ctx.guild.id)
  if cl:
      if cl.is_playing():
          stringo = "{} added to the Queue".format(auth.name)
  
  embedVar = discord.Embed(color=col, title=("**{}**: ").format(stringo),description=message)
  url1 = str(auth.avatar_url).replace("1024","32")
  embedVar.set_thumbnail(url=url1)
  return embedVar

def search(SearchKey):
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}

    with YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            video = ydl.extract_info(f"ytsearch:{SearchKey}", download=False)['entries'][0]
        except:
            video = ydl.extract_info(SearchKey, download=False)

    template = "{}".format(video['title'])
    template += "\n"
    template += "https://www.youtube.com/watch?v={}".format(video['id'])

    i = rand.randint(0,1000)
    
    url = 'https://i.ytimg.com/vi/{}/maxresdefault.jpg'.format(video['id'])
    req = requests.get(url, allow_redirects=True)
    open('maxresdefault{}.png'.format(i), 'wb').write(req.content)

    template = template+"TRENNUNG"+"maxresdefault{}.png".format(i)
    
    return template

@bot.command(name='play',aliases=['pl', 'p','Play'],description="Adds to the queue or plays the linked song")
async def play(ctx, *url):
    global songpath
    global songs
    global order

    iDee = str(ctx.guild.id)
    
    #search argument build
    nUrl = ""
    for st in url:
        if  nUrl != "":
            nUrl += " "
        if st != " " or st != "":
            nUrl += st
    url = nUrl

    if ctx.author.voice:
        voiceChannel = ctx.author.voice.channel
        client = getClient(ctx.guild.id)
        if not client:
            await voiceChannel.connect()
        elif not client.is_connected():
            await voiceChannel.connect()
            
    else:
        await ctx.send("You arent connected to a channel!")
        return

    #searcg argument handling
    if "http" not in url and "youtube" not in url and "youtu.be" not in url:
        ar = search(url)
        ar = ar.split("TRENNUNG")
        
        url = ar[0]
        foil = ar[1]
        
        emb = messageEmb(ctx.author,url,ctx)

        url = url.split("\n")[1]
        
        f = discord.File(foil)
        emb.set_image(url="attachment://{}".format(foil))        
        await ctx.send(file=f,embed=emb)
        
        os.remove(foil)

    try:
      order[iDee]
    except:
      order[iDee] = deque()

    order[iDee].append(url)
    
    await ctx.send("Downloading..")

def isPlaying(guildID):
    cl = getClient(guildID)
    if cl:
        return cl.is_playing()

def isPaused(guildID):
  cl = getClient(guildID)
  if cl:
    return cl.is_playing()

def nextSong(song,guildID):
  global currentSong
  cur = getClient(guildID)
  if not cur:
      return
  if cur.is_connected() and not cur.is_playing() and not cur.is_paused():
    cur.play(discord.FFmpegPCMAudio(song))
    try:
        s = currentSong[str(guildID)]
        os.remove(s)
    except:
        pass
    currentSong[str(guildID)] = song

def getCurrentSong(guildID):
    try:
        s = currentSong[str(guildID)]
        return s
    except:
        return None

def clearFolder(guildID):
    global songpath
    sp = os.path.join(songpath,"{}/".format(guildID))
    for filename in os.listdir(sp):
        file_path = os.path.join(sp, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
              print('Failed to delete %s. Reason: %s' % (file_path, e))

@bot.command(name='skip',aliases=['s', 'SkipSong','skipSong','Skipsong','next','skipsong'],description="Skips the currently played song")
async def skipSong(ctx):
  cur = getClient(ctx.guild.id)

  if cur.is_connected():
    if cur.is_playing():
      cur.stop()
      sleep(1)
      
      s = getCurrentSong(ctx.guild.id)
      #emb = discord.Embed(description=":fast_forward: Skipped: \n {}".format(s))
      if s:
          os.remove(s)
          del currentSong[str(ctx.guild.id)]
    else:
      await ctx.send("Not even playing!")
  else:
    await ctx.send("Not even connected!")

@bot.command(name='leave',aliases=['l', 'left','disconnect'],description="Disconnects the Bot from the channel")
async def leave(ctx):
    cur = getClient(ctx.guild.id)

    if not cur:
        await ctx.send("Not connected")
    elif cur.is_connected():
        await cur.disconnect()
        clearFolder(ctx.guild.id)
    else:
        await ctx.send("The bot is not connected to a voice channel.")

##@bot.command(name='queue',aliases=['q', 'list'],description="Displays the current queue")
##async def queue(ctx):
##    stringo = ""
##    cur = getClient(ctx.guild.id)
##    if not cur.is_connected():
##      await ctx.send("Not even connected!")
##      return
##    elif not cur.is_playing():
##      await ctx.send("Not even playing anything!")
##      return
##    g = readJson(("warteschlange{}".format(ctx.guild.id)))
##
##    if getCurrentSong(ctx.guild.id):
##      stringo+="__Now Playing:__ "
##      stringo+=getCurrentSong(ctx.guild.id)
##      stringo+="\n"
##
##    c = 1
##    for key in g:
##      string+="{}.:".format(c)
##      stringo+=g[key]
##      stringo+="\n"
##    emb = discord.Embed(title="**Queue:**",color=0x9DAF89,description=stringo)
##    await ctx.send(embed=emb)

@bot.command(name='connect',aliases=['c', 'con','ct','join'],description="Connects the Bot to the channel")
async def connect(ctx):
    if ctx.author.voice:
        voiceChannel = ctx.author.voice.channel
        try:
          await voiceChannel.connect()
        except:
          await ctx.send("Already connected!")
    else:
        await ctx.send("You are not connected to a valid channel")
        return

##@bot.command()
##async def pause(ctx):
##  if not ctx.author.voice:
##    await ctx.send("Not connected")
##  elif ctx.author.voice:
##    cur = getClient(ctx.guild.id)
##    if cur:
##      if cur.is_connected():
##        if cur.is_playing():
##          if not cur.is_paused():
##            cur.pause()
##          else:
##            await ctx.send("Already paused")
##        else:
##          await ctx.send("I am not even playing")

def init():
    bot.run(TOKEN)
    client.start(os.getenv('TOKEN'))
