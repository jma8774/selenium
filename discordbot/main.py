import asyncio
import os

import discord as discord
from discord.utils import get
from dotenv import load_dotenv

from args import args
from logger import log

discord_client = None
discord_loop = None
guilds = {}
channels = {}
users = {}
roles = {}


def run_discord_bot():
    global discord_client, discord_loop
    load_dotenv()
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    discord_client = MyBot(intents=intents)
    discord_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(discord_loop)
    discord_loop.run_until_complete(discord_client.start(os.getenv("DISCORD_TOKEN")))


class MyBot(discord.Client):
    async def on_ready(self):
        global channels, users, roles
        log.info(f"{discord_client.user} has connected to Discord!")
        guilds = {
            "apes": discord_client.get_guild(152954629993398272),
        }
        channels = {
            "lounge": discord_client.get_channel(420679175465336832),
            "bot-spam": discord_client.get_channel(1018050116424306738),
            "bot-spam-2": discord_client.get_channel(1148302801961758772),
        }
        users = {
            "ricky": 600922329815449632,
            "justin": 152956804270129152,
            "jeemong": 152957206025863168,
        }
        roles = {
            "chodes": 437677551926771732,
            "king": 363803943903428609,
            "tera nibbas": 448189194502668291,
        }

    async def send(
        self, channel, message, user: str = None, role: str = None, delete_after=None
    ):
        global channels, users, roles
        # log.info(f"Sending message to {channel}: {message}")
        if user:
            await channels[channel].send(
                f"<@{users[user]}> " + message, delete_after=delete_after
            )
        elif role:
            await channels[channel].send(
                f"<@&{roles[role]}> " + message, delete_after=delete_after
            )
        else:
            await channels[channel].send(message, delete_after=delete_after)

    async def sendEmbed(
        self,
        channel,
        message,
        name: str = None,
        price: str = None,
        url: str = None,
        picture: str = None,
        user: str = None,
        role: str = None,
        delete_after=None,
    ):
        global channels, users, roles
        # log.info(f"Sending message to {channel}: {message}")
        if user:
            mention = f"<@{users[user]}> "  # Mention user
        elif role:
            mention = f"<@&{roles[role]}> "  # Mention role
        else:
            mention = ""  # No mention

        # Create an embed object
        embed = discord.Embed(
            title=f"{message} - {price}",
            description=f"[{name}]({url})",
            color=discord.Color.blue(),
        )
        embed.set_image(url=picture)

        # Send the message with mention (if any) and the embed
        await channels[channel].send(
            content=mention, embed=embed, delete_after=delete_after
        )


def sendBotChannel(message, user: str = None, role: str = None, delete_after=None):
    global discord_client, discord_loop
    if not discord_client or not discord_loop or args.dev:
        return
    asyncio.run_coroutine_threadsafe(
        discord_client.send("bot-spam-2", message, user, role, delete_after),
        discord_loop,
    )


def send(channel, message, user: str = None, role: str = None, delete_after=None):
    global discord_client, discord_loop
    if not discord_client or not discord_loop or args.dev:
        return
    asyncio.run_coroutine_threadsafe(
        discord_client.send(channel, message, user, role, delete_after), discord_loop
    )


def sendEmbed(
    message,
    name: str = None,
    price: str = None,
    url: str = None,
    picture: str = None,
    user: str = None,
    role: str = None,
    delete_after=None,
):
    global discord_client, discord_loop
    if not discord_client or not discord_loop or args.dev:
        return
    asyncio.run_coroutine_threadsafe(
        discord_client.sendEmbed(
            "bot-spam-2", message, name, price, url, picture, user, role, delete_after
        ),
        discord_loop,
    )
