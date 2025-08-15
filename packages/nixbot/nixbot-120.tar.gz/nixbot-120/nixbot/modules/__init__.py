# This file is placed in the Public Domain.


"modules"


import importlib
import importlib.util
import inspect
import logging
import os
import sys
import threading
import _thread


from ..auto   import Auto
from ..fleet  import Fleet
from ..thread import launch
from ..utils  import spl


loadlock = threading.RLock()


path = os.path.dirname(__file__)
pname = __package__


class Main(Auto):

    debug   = False
    ignore  = 'llm,udp,web,wsd'
    init    = ""
    level   = "warn"
    md5     = False
    name    = __package__.split(".", maxsplit=1)[0].lower()
    opts    = Auto()
    verbose = False
    version = 120


def load(name):
    with loadlock:
        if name in Main.ignore:
            return
        module = None
        mname = f"{pname}.{name}"
        module = sys.modules.get(mname, None)
        if not module:
            pth = os.path.join(path, f"{name}.py")
            if not os.path.exists(pth):
                return None
            spec = importlib.util.spec_from_file_location(mname, pth)
            module = importlib.util.module_from_spec(spec)
            sys.modules[mname] = module
            spec.loader.exec_module(module)
        if Main.debug:
            module.DEBUG = True
        return module


def mods(names="", empty=False):
    res = []
    if empty:
        Commands.names = {}
    for nme in sorted(modules(path)):
        if names and nme not in spl(names):
            continue
        mod = load(nme)
        if not mod:
            continue
        res.append(mod)
    return res


def modules(mdir=""):
    return sorted([
            x[:-3] for x in os.listdir(mdir or path)
            if x.endswith(".py") and not x.startswith("__") and
            x[:-3] not in Main.ignore
           ])


class Commands:

    cmds  = {}
    md5   = {}
    names = {}

    @staticmethod
    def add(func, mod=None) -> None:
        Commands.cmds[func.__name__] = func
        if mod:
            Commands.names[func.__name__] = mod.__name__.split(".")[-1]

    @staticmethod
    def get(cmd):
        func = Commands.cmds.get(cmd, None)
        if not func:
            name = Commands.names.get(cmd, None)
            if not name:
                return
            mod = load(name)
            if mod:
                scan(mod)
                func = Commands.cmds.get(cmd)
        return func


def command(evt):
    parse(evt)
    func = Commands.get(evt.cmd)
    if func:
        func(evt)
        Fleet.display(evt)
    evt.ready()


def inits(names):
    modz = []
    for name in spl(names):
        try:
            mod = load(name)
            if not mod:
                continue
            if "init" in dir(mod):
                thr = launch(mod.init)
                modz.append((mod, thr))
        except Exception as ex:
            logging.exception(ex)
            _thread.interrupt_main()
    return modz


def scan(mod):
    for key, cmdz in inspect.getmembers(mod, inspect.isfunction):
        if key.startswith("cb"):
            continue
        if 'event' in cmdz.__code__.co_varnames:
            Commands.add(cmdz, mod)


def table():
    pth = os.path.join(path, "tbl.py")
    if not os.path.exists(pth):
        return
    tbl = load("tbl")
    names = getattr(tbl, "NAMES", None)
    if names:
        Commands.names.update(names)


def parse(obj, txt=None):
    if txt is None:
        if "txt" in dir(obj):
            txt = obj.txt
        else:
            txt = ""
    args = []
    obj.args   = []
    obj.cmd    = ""
    obj.gets   = Auto()
    obj.index  = None
    obj.mod    = ""
    obj.opts   = ""
    obj.result = {}
    obj.sets   = Auto()
    obj.silent = Auto()
    obj.txt    = txt or ""
    obj.otxt   = obj.txt
    _nr = -1
    for spli in obj.otxt.split():
        if spli.startswith("-"):
            try:
                obj.index = int(spli[1:])
            except ValueError:
                obj.opts += spli[1:]
            continue
        if "-=" in spli:
            key, value = spli.split("-=", maxsplit=1)
            setattr(obj.silent, key, value)
            setattr(obj.gets, key, value)
            continue
        elif "==" in spli:
            key, value = spli.split("==", maxsplit=1)
            setattr(obj.gets, key, value)
            continue
        if "=" in spli:
            key, value = spli.split("=", maxsplit=1)
            if key == "mod":
                if obj.mod:
                    obj.mod += f",{value}"
                else:
                    obj.mod = value
                continue
            setattr(obj.sets, key, value)
            continue
        _nr += 1
        if _nr == 0:
            obj.cmd = spli
            continue
        args.append(spli)
    if args:
        obj.args = args
        obj.txt  = obj.cmd or ""
        obj.rest = " ".join(obj.args)
        obj.txt  = obj.cmd + " " + obj.rest
    else:
        obj.txt = obj.cmd or ""


def __dir__():
    return modules()
