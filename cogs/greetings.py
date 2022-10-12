import discord
from discord.ext import commands
from .. import apikeys


class Greetings(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Commands
    @commands.command()
    async def hello(self, ctx):
        # !hello
        print("HELLO")
        await ctx.send("Shut up! I'm Bender baby!")

    # Events
    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = client.get_channel(apikeys.CHANNELID)
        await channel.send("Bender is the best! DONT TOUCH MY STUFF!")


def setup(client):
    client.add_cog(Greetings(client))