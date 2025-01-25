import discord
import os
import json
from discord.ext import commands
from discord.ext import tasks
from keep_alive import keep_alive


client = discord.Client()

token="TOKEN HERE"
PREFIX = 's.'
intents = discord.Intents.default()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

script_dir = os.path.dirname(__file__)
rel_path = "bot_stuff/"
abs_file_path = os.path.join(script_dir, rel_path)

global gameRunning

prefFile = "prefixes.json"

global games
games = {}

@tasks.loop(seconds=0.1)
async def tick():
  global games
  for game in list(games.values()):
    try:
      await game.tick()
    except: 
      print("oops")

@bot.event
async def on_ready():
  global games
  print(f'Logged in as: {bot.user.name}')
  print(f'With ID: {bot.user.id}')
  await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='Snake Bot'))
  name = "[s.]" + " SnakeGame"
  await bot.user.edit(nick=name)
  await tick.start()
  print(len(games))
  
  
	
def get_prefix(client, message):
  if message.guild:
    with open((abs_file_path+prefFile),"r") as f:
      prefixes = json.load(f)
    return prefixes[str(message.guild.id)]
bot.command_prefix = get_prefix

@bot.event
async def on_guild_join(guild):
  with open((abs_file_path+prefFile),"r") as f:
    prefixes = json.load(f)

  prefixes[str(guild.id)] = "s."

  with open((abs_file_path+prefFile),"w") as f:
    json.dump(prefixes,f)

  name = "[s.] SnakeGame" 

  await bot.user.edit(nick=name)

@bot.command()
async def prefix(ctx, prefix):
  if prefix == "" or prefix == " " or not prefix:
    await ctx.send("No empty input please!")
  else:
    with open((abs_file_path+prefFile),"r") as f:
      prefixes = json.load(f)

    prefixes[str(ctx.guild.id)] = prefix

    with open((abs_file_path+prefFile),"w") as f:
      json.dump(prefixes,f)
    await ctx.send("My prefix was changed to ``" + prefix + "``")

    name = "[" + prefix + "] SnakeGame" 

    i = bot.user.id
                
    member = await ctx.guild.fetch_member(i)

    await member.edit(nick=name)

@bot.command()
async def invite(ctx):
  await ctx.send("https://discord.com/oauth2/authorize?client_id=867372404363755540&permissions=4228381783&scope=bot")

@bot.command()
async def snake(ctx):
  auth = str(ctx.author.id)
  games[auth] = Game(ctx.author)

  message = ctx.message
  game1 = games[auth]

  embed = discord.Embed(color=0x00f111, description=game1.make_game())

  msg = await message.channel.send(embed=embed)
  game1.message = msg


  await msg.add_reaction("◀️")
  await msg.add_reaction("▶️")
  await msg.add_reaction("🔽")
  await msg.add_reaction("🔼")

class Game:
  async def tick(self):
    if self.game_stopped: 
      return
    try:
      if not self.game_over:
        print("Update")
        await self.move()
        await self.update_board()
      if self.game_over:
        await self.end_game()
    except:
      pass
    
  def __init__(self, user_id):
    self.x = 10
    self.y = 10
    self.columns = 20
    self.length = self.columns
    self.snake = snakeClass(3,self)
    self.rows = []

    u = 0
    while u < self.columns:
      self.rows.append(row(self.length,self))
      u+=1

    self.ticks = 0
    self.message = None
    self.game_over = False
    self.user_id = user_id
    self.game_stopped = False
    self.score = 0
    #0: left , 1: up , 2: right , 3: down
    self.direction = 2

  async def update_board(self):
    embed = self.message.embeds[0]
    embed.description = self.update_snake()
    embed.clear_fields()
    embed.add_field(name="Score", value=self.score, inline=True)
    await self.message.edit(embed=embed)

  async def end_game(self):
    self.rows[10].info = {"⬛⬛⬛⬛⬛⬛⬛  Game Over  ⬛⬛⬛⬛⬛⬛⬛\n"}
    embed = self.message.embeds[0]
    embed.description = self.make_game()
    embed.clear_fields()
    embed.add_field(name="Score", value=self.score, inline=True)
    await self.message.edit(embed=embed)
    await self.message.remove_reaction("◀️",bot.user)
    await self.message.remove_reaction("▶️",bot.user)
    await self.message.remove_reaction("🔽",bot.user)
    await self.message.remove_reaction("🔼",bot.user)

  def unpause_game(self):
    self.game_stopped = False
    
  async def move(self):
    if self.direction == 0:
      if self.x == 0:
        self.game_over = True
      else:
        self.x -= 1

    elif self.direction == 1:
      if self.y == 0:
        self.game_over = True
      else:
        self.y -= 1
    elif self.direction == 2:
      if self.x == self.length-1:
        self.game_over = True
      else:
        self.x += 1
    elif self.direction == 3:
      if self.y == self.columns-1:
        self.game_over = True
      else:
        self.y +=1

  def update_snake(self):
    for index in range(len(self.snake.parts)-1, 0, -1):
      x = self.snake.parts[index-1].x
      y = self.snake.parts[index-1].y
      self.snake.parts[index].x = x
      self.snake.parts[index].y = y
    self.snake.parts[0].x = self.x
    self.snake.parts[0].y = self.y
    for part in self.snake.parts:
      self.rows[part.y].info[part.x] = part.block
    return self.make_game()

  def make_game(self):
    erg = "```"
    for row in self.rows:
      erg+=row.getInfo()
    erg+="```"
    return erg
class snakeClass:
  def __init__(self,length,game1):
    self.length = length
    self.parts = []
    self.game = game1
    self.parts.append(Part(10,10,"🟩"))
    self.parts.append(Part(9,10,"⬛"))

    #def addPart(self):
      #self.parts[len(self.parts)-1] = "🟩"
      #self.parts.append(Part(x,y),"⬛")    
  
class Part:
    def __init__(self,x,y,block):
      self.x = x
      self.y = y
      self.block = block
    
    def rando(self):
      return


class row:
      def __init__(self,length1,game):
        self.length = length1
        self.game = game
        self.info = []
        i = 0
        while i < self.length:
          self.info.append("⬛")
          i+=1
        self.info.append("\n")
        
      
      def getInfo(self):
        return ''.join(self.info)

@bot.event
async def on_reaction_add(reaction,user):
  global games
  if user != bot.user and games[str(user.id)]:
    if not games[str(user.id)].game_stopped:
      game1 = games[str(user.id)]
      await game1.message.remove_reaction(reaction.emoji,user)
      print("reacted!")
      if reaction.emoji == "◀️":
        game1.direction = 0
      if reaction.emoji == "▶️":
        game1.direction = 2
      if reaction.emoji == "🔽":
        game1.direction = 3
      if reaction.emoji == "🔼":
        game1.direction = 1

keep_alive()
bot.run(token)
client.run(os.getenv('token'))
