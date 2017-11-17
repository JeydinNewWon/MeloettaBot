import os
import discord
from discord import bin
from discord import opus

OPUS_LIBS = ["libopus-0.x86.dll", "libopus-0.x64.dll", "libopus-0.dll", "libopus.so.0", "libopus.so", "libopus.0.dylib"]

def load_opus_lib(opus_libs=OPUS_LIBS):
    for opus_lib in opus_libs:
        try:
            opus.load_opus(opus_lib)
            if opus.is_loaded():
                return 'Successfully loaded Opus Libary "{}".'.format(opus_lib)
        except OSError:
            pass
    return "COULD NOT LOAD OPUS LIBS {}".format(', '.join(OPUS_LIBS))
