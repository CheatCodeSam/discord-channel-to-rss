from xmlrpc.client import boolean
import discord

from models import Announcement
from discord import app_commands

MY_GUILD = discord.Object(id=114594673716232197)


class admin_client(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        print(f"Logged on as {self.user}!")

    async def on_message(self, message):
        print(f"Message from {message.author}: {message.content}")
        Announcement.create(message=message.content)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


intents = discord.Intents.default()
intents.message_content = True

client = admin_client(intents=intents)


@client.tree.command()
async def hello(interaction: discord.Interaction):
    """Says hello!"""
    await interaction.response.send_message(f"Hi, {interaction.user.mention}")


@client.tree.command()
@app_commands.rename(wipe_db="wipe_database")
@app_commands.describe(
    channel="The channel that you want to watch.",
    wipe_db="Rather the database should be wiped or not.",
)
async def watch(
    interaction: discord.Interaction,
    channel: discord.TextChannel,
    wipe_db: boolean = False,
):
    """Starts the RSS bot to watch a channel."""
    if wipe_db:
        Announcement.delete().where(True).execute()
    await interaction.response.send_message(channel.id)
