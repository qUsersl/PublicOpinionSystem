from datetime import datetime
from app import db

class AIEngine(db.Model):
    __tablename__ = 'ai_engines'

    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(64), nullable=False)  # e.g., OpenAI, Azure, DeepSeek
    api_url = db.Column(db.String(256), nullable=False)
    api_key = db.Column(db.String(256), nullable=False)
    model_name = db.Column(db.String(64), nullable=False) # e.g., gpt-4, gpt-3.5-turbo
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'provider': self.provider,
            'api_url': self.api_url,
            'api_key': self.api_key, # Security warning: usually shouldn't expose this
            'model_name': self.model_name,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
