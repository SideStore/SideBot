# pylint: disable=C0114
from . import SideBot

with open(".env", "r", encoding="utf-8") as env:
    conf = {k: v for line in env
            if (k := line.strip().split("=", 1)[0]) and \
               (v := line.strip().split("=", 1)[1])}


SideBot().run(conf['DTOKEN'])
