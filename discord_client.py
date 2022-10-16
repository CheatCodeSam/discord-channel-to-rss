from datetime import datetime, timedelta
from typing import Optional
import discord
from loguru import logger


from models import Announcement, Event
from discord import app_commands
import parsedatetime

MY_GUILD = discord.Object(id=114594673716232197)

channel_to_watch = 0


def add_message_to_database(msg: discord.Message):
    logger.info(
        f"Message with discord id of {msg.id} was added to the database as Announcment."
    )
    name = msg.author.display_name
    if isinstance(msg.author, discord.Member):
        if msg.author.nick:
            name = msg.author.nick
    return Announcement.create(
        title=msg.content,
        guid=msg.id,
        pubDate=msg.created_at,
        author=name,
    )


class admin_client(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        logger.info(f"Logged on as {self.user}!")

    async def on_message(self, message):
        if message.channel.id == channel_to_watch:
            if message.author != self.user:
                add_message_to_database(message)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


class CalendarEventModel(discord.ui.Modal, title="Calendar Event"):
    name = discord.ui.View


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
    wipe_db: bool = False,
    inherit: app_commands.Range[int, 0, 100] = 10,
):
    """Starts the RSS bot to watch a channel."""
    global channel_to_watch
    if wipe_db:
        Announcement.delete().where(True).execute()
        logger.info("Announcements have been wiped from the database.")
    messages = [message async for message in channel.history(limit=inherit)]
    for message in messages:
        if message.content:
            add_message_to_database(message)
    channel_to_watch = channel.id
    await interaction.response.send_message(
        f"Now watching {channel.mention} for announcements."
    )
    logger.info(f"Now watching {channel.mention} for announcements.")


@client.tree.context_menu(name="Remove from Announcements")
async def remove_from_announcements(
    interaction: discord.Interaction, message: discord.Message
):
    try:
        announcment_to_be_delete = Announcement.get(Announcement.guid == message.id)
        announcment_to_be_delete.delete_instance()
        await interaction.response.send_message(
            f"This message '{message.id}' by {message.author.mention} has been removed from the database",
            ephemeral=True,
        )
        logger.info(
            f"This message '{message.id}' by {message.author.mention} has been removed from the database",
        )
    except:
        await interaction.response.send_message(
            f"This message '{message.id}' by {message.author.mention} was not in the database",
            ephemeral=True,
        )
        logger.error(
            f"This message '{message.id}' by {message.author.mention} was not in the database",
        )


async def delete_calender_event(interaction: discord.Interaction):
    original_interaction_id = interaction.message.id
    logger.debug(f"Attempting to delete event '{original_interaction_id}'")
    try:
        evnt = Event.get(Event.discord_id == original_interaction_id)
        evnt.delete_instance()
        logger.info(f"Calendar event '{original_interaction_id}' deleted")
    except:
        logger.error(f"No Calendar Event model exists for {original_interaction_id}")

    message = await interaction.channel.fetch_message(original_interaction_id)
    await message.edit(content=f"Event '{evnt.title}' has been deleted", view=None)
    await interaction.response.defer()


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

    button = discord.ui.Button(label="Delete Event", style=discord.ButtonStyle.danger)
    button.callback = delete_calender_event
    delete_view = discord.ui.View()
    delete_view.timeout = None
    delete_view.add_item(button)

    await interaction.response.send_message(
        content=f"New event '{title}' created at {start_time} ending at {end_time}",
        view=delete_view,
    )

    original_interaction = await interaction.original_response()

    logger.info(
        f"New event '{title}' created at {start_time} ending at {end_time} with id '{original_interaction.id}'"
    )

    evnt = Event.create(
        discord_id=original_interaction.id,
        title=title,
        start=start_time,
        end=end_time,
        description=description,
    )
