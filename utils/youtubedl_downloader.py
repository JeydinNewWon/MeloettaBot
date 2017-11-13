import youtube_dl
import os
import sys
import shutil
import asyncio

ytdl_options = {
    'default_search': 'auto',
    'format': 'bestaudio/best',
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'audioformat': 'mp3',
    'extractaudio': True,
    'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
    }],
    'force_ipv4': True,
    'source_address': '0.0.0.0',
    "playlist_items": "0",
    "playlist_end": "0",
    "noplaylist": True
}


def get_ytdl(id):
    format = ytdl_format_options
    format["outtmpl"] = "data/music/{}/%(id)s.mp3".format(id)
    return youtube_dl.YoutubeDL(format)
