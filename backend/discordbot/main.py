import asyncio
import os
import threading

import discord as discord
from dotenv import load_dotenv

from args import args
from logger import log

guilds = {}
channels = {}
users = {}
roles = {}

discord_manager = None


class DiscordManager:
    def __init__(self):
        global discord_manager
        discord_manager = self

        load_dotenv()

        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        self.discord_client = MyBot(intents=intents)

        # Create discord event loop and run in separate thread
        self.discord_loop = asyncio.new_event_loop()
        self.discord_thread = threading.Thread(
            target=self._run_discord_bot, daemon=True
        )
        self.discord_thread.start()
        log.info("Discord manager initialized")

    def _run_discord_bot(self):
        asyncio.set_event_loop(self.discord_loop)
        self.discord_loop.run_until_complete(
            self.discord_client.start(os.getenv("DISCORD_TOKEN"))
        )


class MyBot(discord.Client):
    async def on_ready(self):
        global channels, users, roles
        log.info(f"{self.user} has connected to Discord!")
        guilds = {
            "apes": self.get_guild(152954629993398272),
        }
        channels = {
            "lounge": self.get_channel(420679175465336832),
            "bot-spam": self.get_channel(1018050116424306738),
            "bot-spam-2": self.get_channel(1148302801961758772),
        }
        users = {
            "ricky": 600922329815449632,
            "justin": 152956804270129152,
            "jeemong": 152957206025863168,
            "butter": 1047615361886982235,
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
            title=f"{message}\n{price}",
            description=f"[{name}]({url})",
            color=discord.Color.blue(),
        )
        embed.set_image(url=picture)

        # Send the message with mention (if any) and the embed
        await channels[channel].send(
            content=mention, embed=embed, delete_after=delete_after
        )


def sendBotChannel(message, user: str = None, role: str = None, delete_after=None):
    global discord_manager
    if not discord_manager or args.dev:
        log.info(f"Not sending message to bot-spam-2: {message}")
        return
    asyncio.run_coroutine_threadsafe(
        discord_manager.discord_client.send(
            "bot-spam-2", message, user, role, delete_after
        ),
        discord_manager.discord_loop,
    )


def send(channel, message, user: str = None, role: str = None, delete_after=None):
    global discord_manager
    if not discord_manager or args.dev:
        return
    asyncio.run_coroutine_threadsafe(
        discord_manager.discord_client.send(channel, message, user, role, delete_after),
        discord_manager.discord_loop,
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
    global discord_manager
    if not discord_manager or args.dev:
        return
    asyncio.run_coroutine_threadsafe(
        discord_manager.discord_client.sendEmbed(
            "bot-spam-2", message, name, price, url, picture, user, role, delete_after
        ),
        discord_manager.discord_loop,
    )
