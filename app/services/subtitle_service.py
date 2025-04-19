from typing import Dict, Optional
import yt_dlp
from ..config import config
from ..errors import YouTubeServiceError

class YouTubeSubtitleService:
    @staticmethod
    def extract_pure_text(vtt_content: str) -> str:
        """Extract pure text from VTT format"""
        lines = vtt_content.split('\n')
        pure_text = []
        
        for line in lines:
            if '-->' in line or not line.strip() or line.strip() == 'WEBVTT':
                continue
            pure_text.append(line.strip())
        
        return ' '.join(pure_text)

    @staticmethod
    def get_video_url(video_id: str) -> str:
        """Construct YouTube video URL from video ID"""
        return f"{config.YOUTUBE_BASE_URL}/watch?v={video_id}"

    @staticmethod
    def get_subtitle_data(sub: Dict, pure_text: bool) -> Optional[str]:
        """Get subtitle data from subtitle URL"""
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                sub_data = ydl.urlopen(sub['url']).read().decode('utf-8')
                if pure_text:
                    sub_data = YouTubeSubtitleService.extract_pure_text(sub_data)
                return sub_data
        except Exception as e:
            print(f"Error downloading subtitle: {str(e)}")
            return None

    @staticmethod
    def capture_subtitles(video_id: str, lang: str = config.DEFAULT_LANGUAGE, pure_text: bool = False) -> Dict:
        """Capture subtitles for a YouTube video"""
        try:
            ydl_opts = {
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': [lang],
                'skip_download': True,
                'outtmpl': '-',
                'quiet': True,
                'cookiesfrombrowser': ('firefox', None, None),
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(YouTubeSubtitleService.get_video_url(video_id), download=False)
                subtitles = info.get('subtitles', {})
                auto_subtitles = info.get('automatic_captions', {})

            result = {
                'video_id': video_id,
                'subtitles': {}
            }

            # Try manual subtitles first
            if lang in subtitles:
                sub_list = subtitles[lang]
                if isinstance(sub_list, list):
                    for sub in sub_list:
                        if sub.get('ext') == 'vtt':
                            sub_data = YouTubeSubtitleService.get_subtitle_data(sub, pure_text)
                            if sub_data:
                                result['subtitles'][lang] = sub_data
                                break

            # Try automatic subtitles if no manual ones found
            if not result['subtitles'] and lang in auto_subtitles:
                sub_list = auto_subtitles[lang]
                if isinstance(sub_list, list):
                    for sub in sub_list:
                        if sub.get('ext') == 'vtt':
                            sub_data = YouTubeSubtitleService.get_subtitle_data(sub, pure_text)
                            if sub_data:
                                result['subtitles'][lang] = sub_data
                                break

            return result

        except Exception as e:
            raise YouTubeServiceError(f"Failed to get subtitles: {str(e)}") 