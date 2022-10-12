from dis import disco
from mimetypes import init
import discord
from discord.ext import commands
from discord.utils import get
from discord import Member
from discord.ext.commands import has_permissions, MissingPermissions
from apikeys import *
import time, os, json, requests

# pip install discord.py
# pip install -U discord.py[voice]

command_list = ["online", "offline", "dnd", "idle", "joke"]

intents = discord.Intents.all()
intents.members = True

client = commands.Bot(command_prefix="!", intents=intents)

# Are we ready?
@client.event
async def on_ready():
    print("INITIALIZED!")
    await client.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening, name="how great I am!"
        ),
        status=discord.Status.online,
    )


@client.event
@has_permissions(manage_messages=True)
async def on_message(message):
    if message.author.id == client.user.id:
        return
    msg_content = message.content.lower()
    # Bot Primary Commands
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
        elif "lastmessage" in msg_content:
            """Get the last message of a text channel."""
            print("REQUEST")
            channel = client.get_channel(CHANNELID)
            if channel is None:
                await message.channel.send("Could not find that channel.")
                return
            # NOTE: get_channel can return a TextChannel, VoiceChannel,
            # or CategoryChannel. You may want to add a check to make sure
            # the ID is for text channels only

            message = await channel.fetch_message(channel.last_message_id)
            # NOTE: channel.last_message_id could return None; needs a check

            await message.channel.send(
                f"Last message in {channel.name} sent by {message.author.name}:\n"
                + message.content
            )
        else:
            await message.channel.send(f"'{msg_content[8:]}' DOES NOT COMPUTE... Psh")
        await message.author.send(f"{msg_content}    yourself!")
        # time.sleep(5)
        await message.delete()
    elif CHANNELID == message.channel.id:
        # Grab our last message content and replicate
        content = {}
        print(message.embeds)
        print(message.content)
        for item in message.embeds:
            content["author"] = item.author
            content["title"] = item.title
            # print(f"Description: \n\n{item.description}")
            content["description"] = item.description
            # for _, field in item.fields:
            # print(f" Field {_} | {field}")

            content["description"] = content["description"].split("\n")
            # print(content["description2"])
            for index, item in enumerate(content["description"]):
                if "**Discord**" == item:
                    discord_name = content["description"][index + 1]
                if "Discord ID" in item:
                    discord_id = content["description"][index + 1]
        print(f"The discord name is `{discord_name}`")
        discord_obj_from_id = await client.fetch_user(discord_id)
        print(f"The discord id is `{discord_id}`")
        print(f"{discord_obj_from_id.display_name}")
        if discord_name.lower() == str(discord_obj_from_id).lower():
            # we have a match, proceed
            print("MATCH!")
            """ check if user is on server and not already in group '1027839390849966092
                if they are, we make a new post with same data, but with reaction approvals
                ...
                when approved, we delete the message and move to "APPROVED APPLICATIONS" """
            guild = client.get_guild(GUILDID)
            # print(guild.get_member(int(discord_id)))
            if guild.get_member(int(discord_id)):
                if "member" in [
                    y.name.lower() for y in (guild.get_member(int(discord_id)).roles)
                ]:
                    messageDM = "THIS DINGUS IS ALREADY APPROVED???!!!"
                    embed = discord.Embed(title=messageDM)
                    user = get(client.get_all_members(), id=int(discord_id))
                    print(user)
                    if user:
                        await user.send(embed=embed)
                        # found the user
                    else:
                        # Not found the user
                        print("User is no longer in the discord!")
                else:
                    print(guild.get_member(int(discord_id)).roles)
                    # They need approval or denial (the river in Egypt)
                    print("MOVING TO NEXT CHANNEL AND APPLYING REACTS")
            else:
                print("BIG OL DUMMY LEFT THE DISCORD!! DM THAT PERSON!")
        await message.delete()


@client.command()
async def DM(ctx, user: discord.User, *, message=None):
    message = message or "...What?"
    embed = discord.Embed(title=message)
    await user.send(embed=embed)


@client.event
async def on_memeber_remove(member):
    channel = client.get_channel(CHANNELID)
    print(f"user joined! {member}")
    await channel.send("You left? What a loser!")


# @client.command(pass_context=True)
# async def join(ctx):
#     if ctx.author.voice:
#         channel = ctx.message.author.voice.channel
#         await channel.connect()
#     else:
#         await ctx.send("Not in a voice channel.")


# @client.command(pass_context=True)
# async def leave(ctx):
#     if ctx.voice_client:
#         await ctx.guild.voice_client.disconnect()
#         await ctx.send("Left the channel")
#     else:
#         await ctx.send("Not in a voice channel.")


@client.command(pass_context=True)
async def getlastmessage(ctx, ID):
    """Get the last message of a text channel."""
    print("REQUEST")
    channel = client.get_channel(CHANNELID)
    if channel is None:
        await ctx.send("Could not find that channel.")
        return
    # NOTE: get_channel can return a TextChannel, VoiceChannel,
    # or CategoryChannel. You may want to add a check to make sure
    # the ID is for text channels only

    message = await channel.fetch_message(channel.last_message_id)
    # NOTE: channel.last_message_id could return None; needs a check

    await ctx.send(
        f"Last message in {channel.name} sent by {message.author.name}:\n"
        + message.content
    )


@client.command()
async def embed(ctx):
    embedQ = discord.Embed(
        title="Question", url="", description=get_joke()["setup"], color=0xEB4634
    )
    embedA = discord.Embed(
        title="Answer", url="", description=get_joke()["punchline"], color=0x345EEB
    )
    await ctx.send(embed=embedQ)
    time.sleep(5)
    await ctx.send(embed=embedA)


def get_joke():
    url = "https://dad-jokes.p.rapidapi.com/random/joke"

    headers = {
        "X-RapidAPI-Key": DADJOKESAPI,
        "X-RapidAPI-Host": "dad-jokes.p.rapidapi.com",
    }

    response = requests.request("GET", url, headers=headers)
    assert json.loads(response.text)["success"], "No response from the joke server..."
    return json.loads(response.text)["body"][0]


def tell_joke():
    joke = get_joke()
    embedQ = discord.Embed(
        title="Question", url="", description=joke["setup"], color=0xEB4634
    )
    embedA = discord.Embed(
        title="Answer", url="", description=joke["punchline"], color=0x345EEB
    )
    return embedQ, embedA


initial_extensions = []
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        initial_extensions.append("cogs." + filename[:-3])
    # @commands.Cog.listener()
    # async def on_reaction_add()


if __name__ == "__main__":
    for extension in initial_extensions:
        client.load_extension(extension)


client.run(BOTTOKEN)
