import asyncio
import sys
import threading
import time

from dotenv import load_dotenv

import database.main
from args import args
from discordbot.main import DiscordManager, sendBotChannel
from logger import log
from platforms.amd import AMD
from platforms.brainyquote import BrainyQuote
from platforms.evo import Evo
from platforms.gamestop import GameStop
from platforms.pokemoncenter import PokemonCenter
from platforms.popmart import PopMart
from platforms.target import Target
from platforms.bestbuy import BestBuy
from poller import Poller


class Main:
    """
    This is the main class that will be used to run the program.
    In total, we have 2 event loops, each living in their own thread. The discord event loop will handle async discord functions.
    While the main event loop will allow us to queue up tasks to run.
        1. Discord bot event loop
        2. Main program event loop
    """

    def __init__(self):
        load_dotenv()
        database.main.Init()
        self.running = True

        # Initialize platforms
        self.target = Target(database.main.target_db)
        self.pokemon_center = PokemonCenter(database.main.pk_center_db)
        self.gamestop = GameStop(database.main.gamestop_db)
        self.popmart = PopMart()
        self.evo = Evo(database.main.evo_db)
        self.brainy_quote = BrainyQuote(database.main.common_db)
        self.amd = AMD(database.main.common_db)
        self.bestbuy = BestBuy(database.main.common_db)

        # Start Discord bot in its own thread with its own event loop
        self.discord_manager = DiscordManager()

        # These might need fixing, but if too lazy, just call queue_task() on them
        # self.queue_task(self.pokemon_center.poll_for_queue())
        # self.queue_task(self.gamestop.poll_for_stock())
        # self.queue_task(self.target.poll_for_stock())
        # self.queue_task(self.target.poll_for_new_product())

        # Queue a task once
        self.queue_task(
            self.popmart.check_for_have_a_seat
        )  # This popmart task runs forever

        # Requeue tasks every interval
        self.requeue_task_every(self.evo.check_for_price_drop, 60 * 60)
        self.requeue_task_every(self.amd.check_for_7600x3d, 60 * 60)
        self.requeue_task_every(self.brainy_quote.check_for_daily_quote, 60 * 60)
        self.requeue_task_every(self.bestbuy.check_for_airpods, 60 * 60)

    """
    This function will queue a task to be run in a separate thread.
    The task should be a regular function, not a coroutine.
    """

    def queue_task(self, task, should_log=True):
        if should_log:
            # log.info(f"Queueing task: {task.__name__}")
            pass

        def thread_target():
            try:
                result = task()
                return result
            except Exception as e:
                log.error(f"Task failed with error: {str(e)}")
                raise

        # Create and start the thread
        thread = threading.Thread(target=thread_target, daemon=True)
        thread.start()
        return thread

    """
    This function will requeue a task every delay seconds.
    IMPORTANT: The tasks that you queue should return, they should not be infinite loops. (Otherwise, we will generate lots of threads that won't stop)
    """

    def requeue_task_every(self, task, delay=5):
        def thread_target():
            while self.running:
                try:
                    # log.info(f"Running task: {task.__name__}")
                    task()
                    time.sleep(delay)
                except Exception as e:
                    log.error(f"Error in periodic task {task.__name__}: {str(e)}")
                    time.sleep(delay)

        # Create and start the thread
        thread = threading.Thread(target=thread_target, daemon=True)
        thread.start()
        return thread

    def start(self):
        while True:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                self.running = False
                log.info("\nShutting down gracefully...")
                sys.exit(0)


if __name__ == "__main__":
    Main().start()
