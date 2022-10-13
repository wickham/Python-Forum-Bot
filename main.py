#!/usr/bin/env python3
import discord
import time, os, json, requests
import emoji
from discord.ext import commands
from discord.utils import get
from discord import Member, ui, app_commands
from discord.ext.commands import has_permissions, MissingPermissions
from apikeys import *
from datetime import datetime

# pip install discord.py
# pip install -U discord.py[voice]
# pip install requests
# pip install emoji

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
        status=discord.Status.do_not_disturb,
    )


@client.event
@has_permissions(manage_messages=True)
async def on_message(message):
    if message.author.id == client.user.id:
        return
    msg_content = message.content.lower()
    # Bot Primary Commands
    if any(word in msg_content for word in ["!bender"]):
        if "online" in msg_content:
            await client.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.listening, name="how great I am!"
                ),
                status=discord.Status.online,
            )
        elif "offline" in msg_content:
            await client.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.listening, name="how great I am!"
                ),
                status=discord.Status.offline,
            )
        elif "dnd" in msg_content:
            await client.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.listening, name="how great I am!"
                ),
                status=discord.Status.do_not_disturb,
            )
        elif "idle" in msg_content:
            await client.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.listening, name="how great I am!"
                ),
                status=discord.Status.idle,
            )
        elif "joke" in msg_content:
            Q, A = tell_joke()
            await message.channel.send(embed=Q)
            time.sleep(5)
            await message.channel.send(embed=A)
        elif "lastmessage" in msg_content:
            """Get the last message of a text channel."""
            channel = client.get_channel(PENDINGID)
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
    elif PENDINGID == message.channel.id:
        print("NEW APPLICATION")
        # Grab our last message content and replicate
        content = {}
        for item in message.embeds:
            content["author"] = item.author
            content["title"] = item.title
            content["description"] = item.description
            content["description"] = content["description"].split("\n")
            for index, item in enumerate(content["description"]):
                if "**Discord**" == item:
                    discord_name = content["description"][index + 1]
                if "Discord ID" in item:
                    discord_id = content["description"][index + 1]
        discord_obj_from_id = await client.fetch_user(discord_id)
        if discord_name.lower() == str(discord_obj_from_id).lower():
            # we have a match, proceed
            print("MATCH!")
            """ check if user is on server and not already in group '1027839390849966092
                if they are, we make a new post with same data, but with reaction approvals
                ...
                when approved, we delete the message and move to "APPROVED APPLICATIONS" """
            guild = client.get_guild(GUILDID)

            if guild.get_member(int(discord_id)):
                if "member" in [
                    y.name.lower() for y in (guild.get_member(int(discord_id)).roles)
                ]:
                    title = "DINGUS, YOURE ALREADY APPROVED!\n"
                    msg = "Visit: [#👋・welcome](https://discord.gg/9VdHkjc5Vv)"
                    messageDM = "DINGUS, YOURE ALREADY APPROVED!\nVisit: [#👋・welcome](https://discord.gg/9VdHkjc5Vv)"
                    embed = discord.Embed(title=title, description=msg).set_author(
                        name="ChronoRP", icon_url="https://i.imgur.com/knLQPpi.png"
                    )
                    user = get(client.get_all_members(), id=int(discord_id))

                    if user:
                        await user.send(embed=embed)
                        await message.delete()
                        # found the user
                    else:
                        # Not found the user
                        print("User is no longer in the discord!")
                else:

                    # They need approval or denial (the river in Egypt)
                    yes = await guild.fetch_emoji(emojis["yes"])
                    no = await guild.fetch_emoji(emojis["no"])
                    warn = await guild.fetch_emoji(emojis["warning"])

                    print("ADDING REACTIONS")
                    moji_list = [yes, no, warn]
                    for item in moji_list:
                        await message.add_reaction(f"{item}")

            else:

                print("EITHER NOT IN DISCORD OR INCORRECT INFORMATION FED")


@client.command()
async def DM(ctx, user: discord.User, *, message=None):
    message = message or "...What?"
    embed = discord.Embed(title=message)
    await user.send(embed=embed)


@client.event
async def on_memeber_remove(member):
    channel = client.get_channel(PENDINGID)
    # print(f"user joined! {member}")
    await channel.send("You left? What a loser!")


@client.event
async def on_reaction_add(reaction, user):
    embed = reaction.message.embeds[0]
    emoj = reaction.emoji
    guild = client.get_guild(GUILDID)
    yes = await guild.fetch_emoji(emojis["yes"])
    no = await guild.fetch_emoji(emojis["no"])
    warn = await guild.fetch_emoji(emojis["warning"])
    reverse = await guild.fetch_emoji(emojis["unoreverse"])

    if user == client.user:
        return
    content = {}
    for item in reaction.message.embeds:
        content["author"] = item.author
        content["title"] = item.title
        content["description"] = item.description

        for index, item in enumerate(content["description"]):
            if "**Discord**" == item:
                discord_name = content["description"][index + 1]
            if "Discord ID" in item:
                discord_id = content["description"][index + 1]

    content["description"] = content["description"].split("\n")

    for index, item in enumerate(content["description"]):
        if "**Discord**" == item:
            discord_name = content["description"][index + 1]
        if "Discord ID" in item:
            discord_id = content["description"][index + 1]

    if emoj == yes:
        print("YES")
        # APPROVE
        channel = client.get_channel(APPROVEDID)

        await channel.send(
            embed=discord.Embed(
                title="",
                url="",
                description=embed.description,
                color=0x42FF5F,
            )
        )
        await reaction.message.delete()
        # Message user about good news
        # Giver user role

        member = guild.get_member(int(discord_id))
        role = get(guild.roles, id=MEMBERROLE)
        denied = get(guild.roles, id=DENIEDROLE)

        await member.add_roles(role)
        for role in member.roles:
            if role.id == DENIEDROLE:
                print("removing denied role")
                await member.remove_roles(denied)
        # message user
        title = "Congratulations!\n"
        msg = """You've been __**accepted**__\nNOW GET OUT THERE MEAT BAG AND MAKE BENDER PROUD!\n\n
                Few Channels to Visit:\n
                [👋・welcome](https://discord.gg/9VdHkjc5Vv)\n
                [📜・table-of-contents](https://discord.com/channels/979545493577293824/1029181982783045646)\n
                [✨・self-role](https://discord.com/channels/979545493577293824/1028127399583432735)\n
                *and learn what to do next*."""
        embed = discord.Embed(title=title, description=msg, color=0x42FF5F).set_author(
            name="ChronoRP",
            icon_url="https://i.imgur.com/knLQPpi.png",
        )
        await member.send(embed=embed)
    elif emoj == no:
        # DENY
        print("DENIED")
        channel = client.get_channel(DENIEDID)

        # Move the document
        moved = await channel.send(
            embed=discord.Embed(
                title="", url="", description=embed.description, color=0xF73B31
            )
        )
        await reaction.message.delete()
        await moved.add_reaction(f"{reverse}")
        # Message User
        member = guild.get_member(int(discord_id))
        role = get(guild.roles, id=DENIEDROLE)
        await member.add_roles(role)

        # message user
        application = await channel.fetch_message(channel.last_message_id)
        embed = discord.Embed(
            description=reaction.message.embeds[0].description,
            color=0xFFFFFF,
        )
        await member.send(embed=embed)

        title = "Sorry.\n"
        msg = f"""Your application was __**denied**__\nYou may be able to re-apply!\n\n
                Review your application above to see maybe where it can be improved...\n
                Visit the channel below if you would like to appeal or find out more.\n
                [SUPPLY THIS DENIED URL!](https://discord.com/channels/{GUILDID}/{DENIEDID}/{application.id})\n
                [🏰・appeal](https://discord.com/channels/979545493577293824/1029928358588465162)\n
                """
        embed = discord.Embed(title=title, description=msg, color=0xF73B31,).set_author(
            name="ChronoRP",
            icon_url="https://i.imgur.com/knLQPpi.png",
        )
        message = await member.send(embed=embed)
    elif emoj == warn:
        print("warning")
        channel = client.get_channel(PENDINGID)
        await reaction.message.delete()
        message = await channel.send(
            embed=discord.Embed(
                title="",
                url="",
                description=embed.description,
                color=0xF5D60F,
            )
        )
        yes = await guild.fetch_emoji(emojis["yes"])
        no = await guild.fetch_emoji(emojis["no"])
        moji_list = [yes, no]
        for item in moji_list:
            await message.add_reaction(f"{item}")
    elif emoj == reverse:
        print("reversed ban")
        channel = client.get_channel(PENDINGID)
        await reaction.message.delete()
        message = await channel.send(
            embed=discord.Embed(
                title="",
                url="",
                description=embed.description,
                color=0xF5D60F,
            )
        )
        moji_list = [yes, no, warn]
        for item in moji_list:
            await message.add_reaction(f"{item}")
    else:
        return


@client.command(pass_context=True)
async def getlastmessage(ctx, ID):
    """Get the last message of a text channel."""
    print("REQUEST")
    channel = client.get_channel(PENDINGID)
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
