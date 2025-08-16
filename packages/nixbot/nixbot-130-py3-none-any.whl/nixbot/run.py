# This file is placed in the Public Domain.


"runtime"


from nixt.auto import Auto


class Main(Auto):

    debug   = False
    init    = ""
    level   = "warn"
    md5     = False
    name    = __package__.split(".", maxsplit=1)[0].lower()
    opts    = Auto()
    verbose = False
    version = 130


def __dir__():
    return (
        'Main',
    )
