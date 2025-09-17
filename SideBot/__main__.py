import os
import json
from . import SideBot
from .utils import SideBotConfig

config_file = os.environ.get("SIDEBOTCONF", ".sidebot.conf")
with open(config_file, "r") as f:
    config = SideBotConfig(**json.load(f))

SideBot(config).run()
