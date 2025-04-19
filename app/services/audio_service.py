import os
import tempfile
import whisper
from typing import Dict, Optional
import yt_dlp
from ..config import config
from ..errors import YouTubeServiceError

class YouTubeAudioService:
    def __init__(self):
        # 初始化 Whisper 模型
        self.model = whisper.load_model("large", device="cpu")

    @staticmethod
    def get_video_url(video_id: str) -> str:
        """Construct YouTube video URL from video ID"""
        return f"{config.YOUTUBE_BASE_URL}/watch?v={video_id}"

    def download_audio(self, video_id: str) -> str:
        """
        Download audio from YouTube video
        
        Args:
            video_id (str): YouTube video ID
            
        Returns:
            str: Path to the downloaded audio file
        """
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(tempfile.gettempdir(), f'{video_id}.%(ext)s'),
            'quiet': True,
            'cookiesfrombrowser': ('firefox', None, None),
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.get_video_url(video_id)])
                # 获取下载的文件路径
                audio_path = os.path.join(tempfile.gettempdir(), f'{video_id}.mp3')
                if not os.path.exists(audio_path):
                    raise YouTubeServiceError("Failed to download audio")
                return audio_path
        except Exception as e:
            raise YouTubeServiceError(f"Failed to download audio: {str(e)}")

    def generate_subtitles(self, audio_path: str, language: Optional[str] = None) -> str:
        """
        Generate subtitles from audio using Whisper
        
        Args:
            audio_path (str): Path to the audio file
            language (Optional[str]): Language code (e.g., 'en', 'zh')
            
        Returns:
            str: Subtitles in VTT format
        """
        try:
            # 设置语言参数
            kwargs = {}
            if language:
                kwargs['language'] = language

            # 使用 Whisper 生成字幕
            result = self.model.transcribe(audio_path, **kwargs)
            
            # 转换为 VTT 格式
            vtt_content = "WEBVTT\n\n"
            for i, segment in enumerate(result['segments'], 1):
                start = self.format_time(segment['start'])
                end = self.format_time(segment['end'])
                text = segment['text'].strip()
                vtt_content += f"{i}\n{start} --> {end}\n{text}\n\n"

            return vtt_content
        except Exception as e:
            raise YouTubeServiceError(f"Failed to generate subtitles: {str(e)}")
        finally:
            # 清理临时文件
            try:
                os.remove(audio_path)
            except:
                pass

    @staticmethod
    def format_time(seconds: float) -> str:
        """Format seconds to VTT time format (HH:MM:SS.mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}" 