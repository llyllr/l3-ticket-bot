import discord
from discord.ext import commands, tasks
from discord.utils import get
import os
import SERVER
import asyncio
import pyrebase
import re

config = {
  "apiKey": "AIzaSyCgMBK9JVpDvQhbcISyq20G0mb5xj7u9VU",
  "authDomain": "l3-db-7f0e8.firebaseapp.com",
  "databaseURL": "https://l3-db-7f0e8-default-rtdb.firebaseio.com",
  "storageBucket": "l3-db-7f0e8.appspot.com"
}
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
user = auth.sign_in_with_email_and_password(os.getenv('EMAIL'), os.getenv('PASSWORD'))
db=firebase.database()

clientDC = discord.Client()
clientDC = commands.Bot(command_prefix = '*')
clientDC.remove_command('help')
caregoryId=819882587757215794
supportRoleId=819610209587691552

@clientDC.event
async def on_reaction_add(reaction, user):
  if(user.bot==False):
    if reaction.emoji == '🔒':
        message=await reaction.message.channel.send('Do you sure want close this ticket?'+user.mention)
        await message.add_reaction('✅')
        await message.add_reaction('❌')
        #await reaction.message.channel.delete()
    elif(reaction.emoji=='✅'):
      global db
      messages = await reaction.message.channel.history(limit=None,after=0).flatten()
      hisMessage=''
      for message in messages:
        hisMessage+=message.content+'\n'
      db.child('tickets').child(user.id).child(user.name).child(reaction.message.channel.id).set(hisMessage)
      openning=db.child('tickets').child(user.id).child(user.name).child('openning').get().val()
      db.child('tickets').child(user.id).child(user.name).child('openning').set(openning-1)
      await reaction.message.channel.delete()
      
    elif(reaction.emoji=='❌'):
      await reaction.message.channel.purge(limit=1)
@clientDC.command(name='create', help="")
#@commands.has_permissions(manage_channels=False, manage_roles=False)
async def create(ctx,*,name):
  global db
  username=await clientDC.fetch_user(ctx.author.id)
  #db.child('tickets').child(ctx.author.id).child(username.name).push(1)
  if( not db.child('tickets').child(username.id).child(username.name).shallow().get().val() or int(db.child('tickets').child(username.id).child(username.name).child('openning').get().val())<=2):
    guild = ctx.guild
    autorize_role = ctx.message.author
    overwrites = {
      guild.default_role: discord.PermissionOverwrite(read_messages=False),
      guild.me: discord.PermissionOverwrite(read_messages=True),
      autorize_role:discord.PermissionOverwrite(read_messages=True)
    }
    channel_name=str(username).replace('#',' ')
    category= clientDC.get_channel(caregoryId)
    channel=await guild.create_text_channel(name+'-'+channel_name, overwrites=overwrites,category=category)
    mod = discord.utils.get(ctx.guild.roles, id=supportRoleId)
    message=await channel.send('hello '+username.mention+'\n'+mod.mention+' to help you!')
    await message.add_reaction('🔒')
    if(not db.child('tickets').child(username.id).child(username.name).shallow().get().val()):
      db.child('tickets').child(username.id).child(username.name).child('openning').set(1)
      db.child('tickets').child(username.id).child(username.name).child(channel.id).set('')
    else:
      openning=db.child('tickets').child(username.id).child(username.name).child('openning').get().val()
      db.child('tickets').child(username.id).child(username.name).child('openning').set(openning+1)
      db.child('tickets').child(username.id).child(username.name).child(channel.id).set('')
  else:
    await ctx.send('You openning maximum `3` tickets')
    await asyncio.sleep(3)
    await ctx.message.channel.purge(limit=1)

@clientDC.command(name='close', help="Close ticket")
#@commands.has_permissions(manage_channels=False, manage_roles=False)
async def close(ctx):
    guild = ctx.guild
    global db
    messages = await ctx.channel.history(limit=None,after=0).flatten()
    #messages=messages.reverse()
    hisMessage=''
    i=0
    for message in messages:
      if(i==0):
        firstMessage=message.content
        authorId=re.search(r'\<\@(.*?)\>', str(firstMessage)).group(1)
      hisMessage+=message.content+'\n'
      i+=1
    user=await clientDC.fetch_user(authorId)
    db.child('tickets').child(user.id).child(user.name).child(ctx.message.channel.id).set(hisMessage)
    openning=db.child('tickets').child(user.id).child(user.name).child('openning').get().val()
    db.child('tickets').child(user.id).child(user.name).child('openning').set(openning-1)
    await ctx.channel.delete()
SERVER.b()
clientDC.run(os.getenv('TOKEN'))
