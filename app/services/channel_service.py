from typing import List, Dict
import yt_dlp
from ..config import config
from ..errors import YouTubeServiceError

class YouTubeChannelService:
    @staticmethod
    def get_channel_url(channel_id: str) -> str:
        """Construct YouTube channel URL from channel ID"""
        return f"{config.YOUTUBE_BASE_URL}/{channel_id}"

    @staticmethod
    def get_playlists_url(channel_id: str) -> str:
        """Construct YouTube channel playlists URL"""
        return f"{config.YOUTUBE_BASE_URL}/{channel_id}/playlists"

    @staticmethod
    def get_video_ids_from_entries(entries: List[Dict]) -> List[str]:
        """Extract video IDs from entries"""
        # xx = [entry['id'] for entry in entries if entry.get('id')]
        print("get_video_ids_from_entries..")
        reqult = []
        for entry in entries:
            if entry.get('entries'):
                for sub in entry.get('entries'):
                    if sub.get("id"):
                        reqult.append(sub.get("id"))
            elif  entry.get('id'):
                reqult.append(entry.get("id"))
            print(reqult)
        return reqult

        
        # return [entry['id'] for entry in entries if entry.get('id')]

    @staticmethod
    def get_all_videos(channel_id: str) -> List[str]:
        """
        Get all video IDs from a YouTube channel, including videos in playlists
        
        Args:
            channel_id (str): The ID of the YouTube channel
            
        Returns:
            List[str]: List of video IDs
        """
        ydl_opts = {
            'extract_flat': True,
            'quiet': True,
            'ignoreerrors': True,
            'playlistend': config.MAX_PLAYLIST_ITEMS,
            'extract_playlist': True,
            'cookiesfrombrowser': ('firefox', None, None),
        }
        
        video_ids = set()
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Get channel videos
                channel_url = YouTubeChannelService.get_channel_url(channel_id)
                channel_info = ydl.extract_info(channel_url, download=False)
                print(channel_info)
                
                if not channel_info:
                    return []
                
                if 'entries' in channel_info:
                    video_ids.update(YouTubeChannelService.get_video_ids_from_entries(channel_info['entries']))
                
                # Get videos from playlists
                # playlists_url = YouTubeChannelService.get_playlists_url(channel_id)
                # playlists_info = ydl.extract_info(playlists_url, download=False)
                
                # if playlists_info and 'entries' in playlists_info:
                #     for playlist in playlists_info['entries']:
                #         if playlist.get('id'):
                #             playlist_url = f"{config.YOUTUBE_BASE_URL}/playlist?list={playlist['id']}"
                #             try:
                #                 playlist_info = ydl.extract_info(playlist_url, download=False)
                #                 if playlist_info and 'entries' in playlist_info:
                #                     video_ids.update(YouTubeChannelService.get_video_ids_from_entries(playlist_info['entries']))
                #             except Exception as e:
                #                 print(f"Error processing playlist {playlist['id']}: {str(e)}")
                #                 continue
                
        except Exception as e:
            raise YouTubeServiceError(f"Failed to get channel videos: {str(e)}")
        
        return list(video_ids) 