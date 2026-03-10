class Config:
    # Recommended Models
    AVAILABLE_MODELS = [
        "gemini-3-flash-preview", 
        "gemini-3.1-flash-lite-preview"
    ]
    DEFAULT_MODEL = "gemini-3-flash-preview"
    
    # Using official Google Generative Language API
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
    UPLOAD_URL = "https://generativelanguage.googleapis.com/upload/v1beta/files"
    API_KEY = None # Will fallback to reading from .env/geminiapikey.txt

    # Chunking configuration (in seconds)
    # Default is 4 minutes (240 seconds). Max is derived flexibly or set to 7 minutes.
    VAD_TARGET_CHUNK_SEC = 240
    VAD_MAX_CHUNK_SEC = 420 
    
    # Flag to use inline data instead of File API (useful for local proxies)
    USE_INLINE_DATA = False
    
    # Native Thinking / Reasoning (Gemini 3.0+)
    # thinking_level: MINIMAL, LOW, MEDIUM, HIGH
    THINKING_LEVEL = "MEDIUM"

config = Config()