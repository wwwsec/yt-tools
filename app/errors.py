from functools import wraps
from flask import jsonify

class YouTubeAPIError(Exception):
    """Base exception for YouTube API related errors"""
    pass

class InvalidParameterError(YouTubeAPIError):
    """Exception raised for invalid parameters"""
    pass

class YouTubeServiceError(YouTubeAPIError):
    """Exception raised for YouTube service errors"""
    pass

def handle_api_error(f):
    """Decorator to handle API errors and return appropriate responses"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except InvalidParameterError as e:
            return jsonify({
                'status': 'error',
                'error': str(e)
            }), 400
        except YouTubeServiceError as e:
            return jsonify({
                'status': 'error',
                'error': str(e)
            }), 500
        except Exception as e:
            return jsonify({
                'status': 'error',
                'error': f"Unexpected error: {str(e)}"
            }), 500
    return wrapper 