# This file is placed in the Public Domain.


"main"


import logging
import os
import os.path
import pathlib
import signal
import sys
import threading
import time
import _thread


from nixt.auto   import Auto
from nixt.client import Client
from nixt.event  import Event
from nixt.fleet  import Fleet
from nixt.log    import level
from nixt.serial import dumps
from nixt.thread import launch


from .cmds  import Commands, command, parse, scan, table
from .pkg   import mod, mods, modules
from .run   import Main
from .store import pidname, setwd
from .utils import spl


"clients"


class CLI(Client):

    def __init__(self):
        Client.__init__(self)
        self.register("command", command)

    def raw(self, txt):
        out(txt.encode('utf-8', 'replace').decode("utf-8"))


class Console(CLI):

    def announce(self, txt):
        pass

    def callback(self, event):
        super().callback(event)
        event.wait()

    def poll(self):
        evt = Event()
        evt.txt = input("> ")
        evt.type = "command"
        return evt


"daemon"


def daemon(verbose=False):
    pid = os.fork()
    if pid != 0:
        os._exit(0)
    os.setsid()
    pid2 = os.fork()
    if pid2 != 0:
        os._exit(0)
    if not verbose:
        with open('/dev/null', 'r', encoding="utf-8") as sis:
            os.dup2(sis.fileno(), sys.stdin.fileno())
        with open('/dev/null', 'a+', encoding="utf-8") as sos:
            os.dup2(sos.fileno(), sys.stdout.fileno())
        with open('/dev/null', 'a+', encoding="utf-8") as ses:
            os.dup2(ses.fileno(), sys.stderr.fileno())
    os.umask(0)
    os.chdir("/")
    os.nice(10)


def handler(signum, frame):
    print("handler called!")


signal.signal(signal.SIGHUP, handler)


def inits(names):
    modz = []
    for name in spl(names):
        try:
            module = mod(name)
            if not module:
                continue
            if "init" in dir(module):
                thr = launch(module.init)
                modz.append((module, thr))
        except Exception as ex:
            logging.exception(ex)
            _thread.interrupt_main()
    return modz


def pidfile(filename):
    if os.path.exists(filename):
        os.unlink(filename)
    path2 = pathlib.Path(filename)
    path2.parent.mkdir(parents=True, exist_ok=True)
    with open(filename, "w", encoding="utf-8") as fds:
        fds.write(str(os.getpid()))


def privileges():
    import getpass
    import pwd
    pwnam2 = pwd.getpwnam(getpass.getuser())
    os.setgid(pwnam2.pw_gid)
    os.setuid(pwnam2.pw_uid)


"scripts"


def background():
    daemon("-v" in sys.argv)
    privileges()
    level(Main.level or "debug")
    setwd(Main.name)
    pidfile(pidname(Main.name))
    table()
    Commands.add(cmd)
    Commands.add(ver)
    inits(Main.init or "irc,rss")
    forever()


def console():
    import readline # noqa: F401
    parse(Main, " ".join(sys.argv[1:]))
    Main.init = Main.sets.init or Main.init
    Main.verbose = Main.sets.verbose or Main.verbose
    Main.level   = Main.sets.level or Main.level or "warn"
    level(Main.level)
    setwd(Main.name)
    table()
    Commands.add(cmd)
    Commands.add(ver)
    if "v" in Main.opts:
        banner()
    for _mod, thr in inits(Main.init):
        if "w" in Main.opts:
            thr.join(30.0)
    csl = Console()
    csl.start(daemon=True)
    forever()


def control():
    if len(sys.argv) == 1:
        return
    parse(Main, " ".join(sys.argv[1:]))
    level(Main.level or "warn")
    setwd(Main.name)
    table()
    Commands.add(cmd)
    Commands.add(tbl)
    Commands.add(ver)
    csl = CLI()
    evt = Event()
    evt.orig = repr(csl)
    evt.type = "command"
    evt.txt = Main.otxt
    command(evt)
    evt.wait()


def service():
    level(Main.level or "warn")
    setwd(Main.name)
    banner()
    privileges()
    pidfile(pidname(Main.name))
    table()
    Commands.add(cmd)
    Commands.add(ver)
    inits(Main.init or "irc,rss")
    forever()


"commands"


def cmd(event):
    event.reply(",".join(sorted(Commands.names)))


TXT = """[Unit]
Description=%s
After=network-online.target

[Service]
Type=simple
User=%s
Group=%s
ExecStart=/home/%s/.local/bin/%s -s

[Install]
WantedBy=multi-user.target"""


def srv(event):
    import getpass
    name = getpass.getuser()
    event.reply(TXT % (Main.name.upper(), name, name, name, Main.name))


def tbl(event):
    if not check("f"):
        Commands.names = {}
    for mod in mods(empty=True):
        scan(mod)
    event.reply("# This file is placed in the Public Domain.")
    event.reply("")
    event.reply("")
    event.reply('"lookup tables"')
    event.reply("")
    event.reply("")
    event.reply(f"NAMES = {dumps(Commands.names, indent=4, sort_keys=True)}")


def ver(event):
    event.reply(str(Main.version))


"utilities"


def banner():
    tme = time.ctime(time.time()).replace("  ", " ")
    out(f"{Main.name.upper()} {Main.version} since {tme} ({Main.level.upper()})")
    out(f"loaded {",".join(modules())}")


def check(txt):
    args = sys.argv[1:]
    for arg in args:
        if not arg.startswith("-"):
            continue
        for char in txt:
            if char in arg:
                return True
    return False


def forever():
    while True:
        try:
            time.sleep(0.1)
        except (KeyboardInterrupt, EOFError):
            break


def out(txt):
    print(txt)
    sys.stdout.flush()


"runtime"


def wrapped(func):
    try:
        func()
    except (KeyboardInterrupt, EOFError):
        out("")
    Fleet.shutdown()


def wrap(func):
    import termios
    old = None
    try:
        old = termios.tcgetattr(sys.stdin.fileno())
    except termios.error:
        pass
    try:
        wrapped(func)
    finally:
        if old:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old)


def main():
    if check("a"):
        Main.init = ",".join(modules())
    if check("v"):
        setattr(Main.opts, "v", True)
    if check("c"):
        wrap(console)
    elif check("d"):
        background()
    elif check("s"):
        wrapped(service)
    else:
        wrapped(control)


if __name__ == "__main__":
    main()
