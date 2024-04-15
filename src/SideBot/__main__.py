"""entrypoint to SideBot."""

# pylint: disable=C0114
import logging

from . import SideBot

SideBot.from_env().run(root_logger=True, log_level=logging.INFO)
