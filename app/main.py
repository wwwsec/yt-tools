from flask import Flask
from .routes.api import get_channel_videos, get_subtitles, get_whisper_subtitles

def create_app():
    app = Flask(__name__)
    
    # Register routes
    app.route('/api/channel/videos', methods=['GET'])(get_channel_videos)
    app.route('/api/subtitles', methods=['GET'])(get_subtitles)
    app.route('/api/whisper/subtitles', methods=['GET'])(get_whisper_subtitles)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000) 