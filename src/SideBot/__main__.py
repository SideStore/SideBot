# pylint: disable=C0114
from . import SideBot

SideBot.from_env().run(root_logger=True)
