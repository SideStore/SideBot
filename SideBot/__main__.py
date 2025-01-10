"""entrypoint to SideBot."""

from . import SideBot

SideBot.from_yaml_file().run()
