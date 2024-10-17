import Utils.config_loader as cfg_loader
from first_setup import first_setup
from colorama import Fore, Style
import Utils.logger
from Utils.logger import LOGGER_CONFIG
import logging.config
import colorama
import sys
import os
from vertex import Vertex
import Utils.exceptions as excs
from locales.localizer import Localizer

if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))
else:
    os.chdir(os.path.dirname(__file__))

folders = ["configs", "logs", "storage", "storage/cache", "storage/products"]
for folder in folders:
    if not os.path.exists(folder):
        os.makedirs(folder)

files = ["configs/auto_delivery.cfg", "configs/auto_response.cfg"]
for file in files:
    if not os.path.exists(file):
        with open(file, "w", encoding="utf-8") as f:
            pass

if os.path.exists("storage/cache/block_list.json"):
    os.rename("storage/cache/block_list.json", "storage/cache/blacklist.json")

colorama.init()

logging.config.dictConfig(LOGGER_CONFIG)
logging.raiseExceptions = False
logger = logging.getLogger("main")
logger.debug("------------------------------------------------------------------")

if not os.path.exists("configs/_main.cfg"):
    first_setup()
    sys.exit()

try:
    logger.info("Loading main configuration (_main.cfg)...")
    MAIN_CFG = cfg_loader.load_main_config("configs/_main.cfg")
    localizer = Localizer(MAIN_CFG["Other"]["language"])
    _ = localizer.translate

    logger.info("Loading auto response configuration (auto_response.cfg)...")
    AR_CFG = cfg_loader.load_auto_response_config("configs/auto_response.cfg")
    RAW_AR_CFG = cfg_loader.load_raw_auto_response_config("configs/auto_response.cfg")

    logger.info("Loading auto delivery configuration (auto_delivery.cfg)...")
    AD_CFG = cfg_loader.load_auto_delivery_config("configs/auto_delivery.cfg")
except excs.ConfigParseError as e:
    logger.error(e)
    logger.error("Terminating program...")
    sys.exit()
except UnicodeDecodeError:
    logger.error("UTF-8 decoding error occurred. Ensure the file encoding is UTF-8 and the line endings are LF.")
    logger.error("Terminating program...")
    sys.exit()
except Exception as e:
    logger.critical("An unexpected error occurred.")
    logger.debug("TRACEBACK", exc_info=True)
    logger.error("Terminating program...")
    sys.exit()

localizer = Localizer(MAIN_CFG["Other"]["language"])

try:
    Vertex(MAIN_CFG, AD_CFG, AR_CFG, RAW_AR_CFG).init().run()
except KeyboardInterrupt:
    logger.info("Terminating program...")
    sys.exit()
except Exception as e:
    logger.critical("An unhandled error occurred while running Vertex.")
    logger.debug("TRACEBACK", exc_info=True)
    logger.critical("Terminating program...")
    sys.exit()
