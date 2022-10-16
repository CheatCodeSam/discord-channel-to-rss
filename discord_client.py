from code import interact
from datetime import datetime, timedelta
from typing import Optional, Union
from xmlrpc.client import boolean
import discord

from models import Announcement, Event
from discord import Interaction, app_commands
import parsedatetime

MY_GUILD = discord.Object(id=114594673716232197)

channel_to_watch = 0


def add_message_to_database(msg: discord.Message):
    name = msg.author.display_name
    if isinstance(msg.author, discord.Member):
        if msg.author.nick:
            name = msg.author.nick
    return Announcement.create(
        message=msg.content,
        discord_id=msg.id,
        posted=msg.created_at,
        author=name,
    )


class admin_client(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        print(f"Logged on as {self.user}!")

    async def on_message(self, message):
        if message.channel.id == channel_to_watch:
            if message.author != self.user:
                if message.content:
                    add_message_to_database(message)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = admin_client(intents=intents)


@client.tree.command()
@app_commands.rename(wipe_db="wipe_database")
@app_commands.describe(
    channel="The channel that you want to watch.",
    wipe_db="Rather the database should be wiped or not.",
    inherit="How many previous messages should be added to the database.",
)
async def watch(
    interaction: discord.Interaction,
    channel: discord.TextChannel,
    wipe_db: boolean = False,
    inherit: app_commands.Range[int, 0, 100] = 10,
):
    """Starts the RSS bot to watch a channel."""
    global channel_to_watch
    if wipe_db:
        Announcement.delete().where(True).execute()
    messages = [message async for message in channel.history(limit=inherit)]
    for message in messages:
        if message.content:
            add_message_to_database(message)
    channel_to_watch = channel.id
    await interaction.response.send_message(
        f"Now watching {channel.name} for announcements."
    )


@client.tree.context_menu(name="Remove from Announcements")
async def remove_from_announcements(
    interaction: discord.Interaction, message: discord.Message
):
    try:
        announcment_to_be_delete = Announcement.get(
            Announcement.discord_id == message.id
        )
        announcment_to_be_delete.delete_instance()
        await interaction.response.send_message(
            f"This message '{message.id}' by {message.author.mention} has been removed from the database",
            ephemeral=True,
        )
    except:
        await interaction.response.send_message(
            f"This message '{message.id}' by {message.author.mention} was not in the database",
            ephemeral=True,
        )


async def gen_delete_calender_event(original_interaction: discord.Interaction, id: int):
    async def delete_calender_event(interaction: discord.Interaction):
        evnt = Event.get(Event.id == id)
        evnt.delete_instance()
        await original_interaction.edit_original_response(
            content=f"Event '{evnt.title}' has been deleted", view=None
        )
        await interaction.response.defer()

    return delete_calender_event


@client.tree.command()
@app_commands.describe(
    title="Event title",
    start="Event date and time",
    ends="When event ends",
    description="Addtional information about the event",
)
async def create(
    interaction: discord.Interaction,
    title: str,
    start: str,
    ends: Optional[str],
    description: Optional[str],
):
    """Creates an event for the calendar on the website."""
    cal = parsedatetime.Calendar()
    time_struct, _ = cal.parse(start)
    start_time = datetime(*time_struct[:6])
    end_time = start_time + timedelta(hours=1)
    if ends:
        time_struct, _ = cal.parse(ends)
        end_time = datetime(*time_struct[:6])

    evnt = Event(title=title, start=start_time, end=end_time, description=description)
    evnt.save()
    print(evnt.id)

    button = discord.ui.Button(label="Delete Event", style=discord.ButtonStyle.danger)
    button.callback = await gen_delete_calender_event(interaction, evnt.id)
    delete_view = discord.ui.View()
    delete_view.add_item(button)

    await interaction.response.send_message(
        f"New event '{title}' created at {start_time} ending at {end_time}",
        view=delete_view,
    )
