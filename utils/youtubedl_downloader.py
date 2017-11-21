import youtube_dl
import asyncio


class Extract:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.title = None
        self.yt = None
        self.display_id = None
        self.webpage_url = None
        self.thumbnail = None
        self.upload_url = None
        self.download_url = None
        self.views = None
        self.is_live = None
        self.likes = None
        self.dislikes = None
        self.duration = None
        self.uploader = None
        self.description = None

    async def extract(self, url):
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
            "noplaylist": True,
            'include_ads': False,
            'outtmpl': "data/music/{}/%(id)s.mp3".format(str(id)),
            'forcefilename': True
        }

        ytdl = youtube_dl.YoutubeDL(ytdl_options)
        info = ytdl.extract_info(url, download=True)

        if "entries" in info:
            info = info['entries'][0]

        self.url = url
        self.yt = ytdl
        self.display_id = info.get('display_id')
        self.thumbnail = info.get('thumbnail')
        self.webpage_url = info.get('webpage_url')
        self.download_url = info.get('download_url')
        self.views = info.get('view_count')
        self.likes = info.get('like_count')
        self.dislikes = info.get('dislike_count')
        self.duration = info.get('duration')
        self.uploader = info.get('uploader')

        is_twitch = 'twitch' in url
        if is_twitch:
            self.title = info.get('description')
            self.description = None
        else:
            self.title = info.get('title')
            self.description = info.get('description')

        return self
