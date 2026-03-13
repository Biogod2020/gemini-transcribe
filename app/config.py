import os

class Config:
    def __init__(self):
        # Recommended Models
        self.AVAILABLE_MODELS = [
            "gemini-3-flash-preview", 
            "gemini-3.1-flash-lite-preview"
        ]
        self.DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3-flash-preview")
        
        # Using official Google Generative Language API or Local Proxy
        self.BASE_URL = os.environ.get("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")
        self.UPLOAD_URL = os.environ.get("GEMINI_UPLOAD_URL", "https://generativelanguage.googleapis.com/upload/v1beta/files")
        
        # API Key management
        self.API_KEY = self._load_api_key()

        # Chunking configuration (in seconds)
        self.VAD_TARGET_CHUNK_SEC = 240
        self.VAD_MAX_CHUNK_SEC = 420 
        
        # Flag to use inline data instead of File API
        self.USE_INLINE_DATA = False
        
        # Native Thinking / Reasoning (Gemini 3.0+)
        self.THINKING_LEVEL = "MEDIUM"

    def _load_api_key(self) -> str:
        """
        Loads the Gemini API key from .env/geminiapikey.txt.
        """
        path = ".env/geminiapikey.txt"
        if os.path.exists(path):
            with open(path, "r") as f:
                return f.read().strip()
        return os.environ.get("GEMINI_API_KEY")

config = Config()
