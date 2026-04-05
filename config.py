import os

class Config:
    SECRET_KEY = os.urandom(24).hex()  # Generate a random secret key
    SQLALCHEMY_DATABASE_URI = 'sqlite:///ghoori.db'  # Simplified path
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Google OAuth2 settings
    GOOGLE_CLIENT_ID = "REDACTED_GOOGLE_CLIENT_ID"  
    GOOGLE_CLIENT_SECRET = "REDACTED_GOOGLE_CLIENT_SECRET"  
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
    GOOGLE_API_KEY = 'REDACTED_GOOGLE_API_KEY'
    
    # OAuth2 Redirect URI
    OAUTH2_REDIRECT_URI = "http://localhost:5001/login/google/callback"
    
    # File upload settings
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trip_images')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

    # Stripe settings
    STRIPE_PUBLISHABLE_KEY = 'REDACTED_STRIPE_PUBLISHABLE_KEY'
    STRIPE_SECRET_KEY = 'REDACTED_STRIPE_SECRET_KEY'
    STRIPE_WEBHOOK_SECRET = 'REDACTED_STRIPE_WEBHOOK_SECRET'

    # Google Gemini API key (free tier)
    GEMINI_API_KEY = 'REDACTED_GOOGLE_API_KEY'