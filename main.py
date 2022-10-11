from dis import disco
from mimetypes import init
import discord
from discord.ext import commands
from discord import Member
from discord.ext.commands import has_permissions, MissingPermissions
from apikeys import *
import time, os, json, requests
# pip install discord.py
# pip install -U discord.py[voice]

command_list = ["online", "offline", "dnd", "idle", "joke"]

intents = discord.Intents.all()
intents.members = True

client = commands.Bot(command_prefix = "!", intents=intents)

# Are we ready?
@client.event
async def on_ready():
    print("INITIALIZED!")
    await client.change_presence(status=discord.Status.online, activity=discord.Game("Your Ugly Face!"))

@client.event
@has_permissions(manage_messages=True)
async def on_message(message):
    if message.author.id == client.user.id:
        return
    msg_content = message.content.lower()
    if any(word in msg_content for word in ["!bender"]):

        print(f"{msg_content}")
        if "online" in msg_content:
            await client.change_presence(status=discord.Status.online)
        elif "offline" in msg_content:
            await client.change_presence(status=discord.Status.offline)
        elif "dnd" in msg_content:
            await client.change_presence(status=discord.Status.do_not_disturb)
        elif "idle" in msg_content:
            await client.change_presence(status=discord.Status.idle)
        elif "joke" in msg_content:
            Q, A = tell_joke()
            await message.channel.send(embed=Q)
            time.sleep(5)
            await message.channel.send(embed=A)

        await message.author.send("WHAT")
        # time.sleep(5)
        await message.delete()

@client.command()
async def DM(ctx, user:discord.User, *, message=None):
    message = message or "...What?"
    embed = discord.Embed(title=message)
    await user.send(embed=embed)


@client.event
async def on_memeber_join(member):
    channel = client.get_channel(CHANNELID)
    print(f"user joined! {member}")
    await channel.send("Bender is the best! DONT TOUCH MY STUFF!")

@client.event
async def on_memeber_remove(member):
    channel = client.get_channel(CHANNELID)
    print(f"user joined! {member}")
    await channel.send("You left? What a loser!")

@client.command(pass_context = True)
async def join(ctx):
    if(ctx.author.voice):
        channel = ctx.message.author.voice.channel
        await channel.connect()
    else:
        await ctx.send("Not in a voice channel.")

@client.command(pass_context = True)
async def leave(ctx):
    if(ctx.voice_client):
        await ctx.guild.voice_client.disconnect()
        await ctx.send("Left the channel")
    else:
        await ctx.send("Not in a voice channel.")

@client.command()
async def embed(ctx):
    embedQ = discord.Embed(title="Question", url="", description=get_joke()["setup"], color=0xeb4634)
    embedA = discord.Embed(title="Answer", url="", description=get_joke()["punchline"], color=0x345eeb)
    await ctx.send(embed=embedQ)
    time.sleep(5)
    await ctx.send(embed=embedA)

def get_joke():
    url = "https://dad-jokes.p.rapidapi.com/random/joke"

    headers = {
        "X-RapidAPI-Key": DADJOKESAPI,
        "X-RapidAPI-Host": "dad-jokes.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers)
    assert json.loads(response.text)["success"], "No response from the joke server..."
    return json.loads(response.text)["body"][0]

def tell_joke():
    joke = get_joke()
    embedQ = discord.Embed(title="Question", url="", description=joke["setup"], color=0xeb4634)
    embedA = discord.Embed(title="Answer", url="", description=joke["punchline"], color=0x345eeb)
    return embedQ,embedA


initial_extensions = []
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        initial_extensions.append("cogs."+filename[:-3])
    # @commands.Cog.listener()
    # async def on_reaction_add()


if __name__ == "__main__":
    for extension in initial_extensions:
        client.load_extension(extension)
        

client.run(BOTTOKEN)