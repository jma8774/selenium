import requests
from poller import Poller
import threading
import sys
import time
from logger import log
from discord.main import run_discord_bot, sendBotChannel
from selenium_flows import handle_target
from args import args
from dotenv import load_dotenv
import database.main
from platforms.target import Target
from platforms.pokemoncenter import PokemonCenter
from platforms.gamestop import GameStop
from platforms.popmart import PopMart
from platforms.evo import Evo

class Main:
  def __init__(self):
    load_dotenv()
    database.main.Init()
    self.running = True
    self.target = Target(database.main.target_db)
    self.pokemon_center = PokemonCenter(database.main.pk_center_db)
    self.gamestop = GameStop(database.main.gamestop_db)
    self.popmart = PopMart()
    self.evo = Evo(database.main.evo_db)

  def start(self):
    # Discord bot
    threading.Thread(target=run_discord_bot, daemon=True).start()
    time.sleep(3)

    # Main
    # self.target.start_poll_for_stock()
    # self.target.start_poll_for_new_product(15 * 60)
    # self.pokemon_center.start_poll_for_queue() # Doesn't work that well... Anti-bot protection
    # self.gamestop.start_poll_for_stock() # Doesn't work... cloudflare protection
    self.popmart.check_for_have_a_seat()
    self.evo.check_for_price_drop()
    try:
      while self.running:
        time.sleep(1)
    except KeyboardInterrupt:
      log.info("\nShutting down gracefully...")
      self.running = False
      sys.exit(0)

if __name__ == "__main__":
  Main().start()
