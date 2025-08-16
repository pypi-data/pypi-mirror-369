# This file is placed in the Public Domain.


"imports"



import importlib
import importlib.util
import os
import sys
import threading


loadlock = threading.RLock()
path = os.path.dirname(__file__)
path = os.path.join(path, "modules")
pname = f"{__package__}.modules"


def mod(name, debug=False):
    with loadlock:
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
        if debug:
            module.DEBUG = True
        return module


def mods(names="", empty=False):
    res = []
    if empty:
        Commands.names = {}
    for nme in sorted(modules(path)):
        if names and nme not in spl(names):
            continue
        module = mod(nme)
        if not mod:
            continue
        res.append(module)
    return res


def modules(mdir=""):
    return sorted([
            x[:-3] for x in os.listdir(mdir or path)
            if x.endswith(".py") and not x.startswith("__")
           ])


def __dir__():
    return (
        'mod',
        'mods',
        'modules'
    )
