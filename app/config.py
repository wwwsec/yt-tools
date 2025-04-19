from dataclasses import dataclass

@dataclass
class Config:
    YOUTUBE_BASE_URL = "https://www.youtube.com"
    DEFAULT_LANGUAGE = "en"
    MAX_PLAYLIST_ITEMS = 10000

config = Config() 