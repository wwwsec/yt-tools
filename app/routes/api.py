from flask import request, jsonify
from ..services.channel_service import YouTubeChannelService
from ..services.subtitle_service import YouTubeSubtitleService
from ..errors import handle_api_error, InvalidParameterError

@handle_api_error
def get_channel_videos():
    """
    API endpoint to get all videos from a YouTube channel
    Query parameters:
        channel_id: YouTube channel ID (required)
    """
    channel_id = request.args.get('channel_id')
    
    if not channel_id:
        raise InvalidParameterError('Missing required parameter: channel_id')
    
    video_ids = YouTubeChannelService.get_all_videos(channel_id)
    return jsonify({
        'status': 'success',
        'count': len(video_ids),
        'videos': video_ids
    })

@handle_api_error
def get_subtitles():
    """
    API endpoint to get subtitles for a YouTube video
    Query parameters:
        video_id: YouTube video ID (required)
        lang: Language code (default: 'en')
        pure_text: Whether to return only pure text (default: false)
    """
    video_id = request.args.get('video_id')
    lang = request.args.get('lang', 'en')
    pure_text = request.args.get('pure_text', 'false').lower() == 'true'
    
    if not video_id:
        raise InvalidParameterError('Missing required parameter: video_id')

    result = YouTubeSubtitleService.capture_subtitles(video_id, lang, pure_text)
    return jsonify({
        'status': 'success',
        'data': result
    }) 