from app import db
from datetime import datetime

class OpinionData(db.Model):
    __tablename__ = 'opinion_data'
    
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(128), nullable=True)
    title = db.Column(db.String(512), nullable=False)
    url = db.Column(db.String(1024), nullable=True)
    original_url = db.Column(db.String(1024), nullable=True)
    source = db.Column(db.String(128), nullable=True)
    cover_url = db.Column(db.String(1024), nullable=True)
    content = db.Column(db.Text, nullable=True)
    is_deep_crawled = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'keyword': self.keyword,
            'title': self.title,
            'original_url': self.original_url,
            'source': self.source,
            'cover_url': self.cover_url,
            'content': self.content,
            'is_deep_crawled': self.is_deep_crawled,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class OpinionDetail(db.Model):
    __tablename__ = 'opinion_detail'
    
    id = db.Column(db.Integer, primary_key=True)
    opinion_id = db.Column(db.Integer, db.ForeignKey('opinion_data.id'), nullable=False, unique=True)
    title = db.Column(db.String(512), nullable=True)
    content = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationship
    opinion = db.relationship('OpinionData', backref=db.backref('detail', uselist=False))

    def to_dict(self):
        return {
            'id': self.id,
            'opinion_id': self.opinion_id,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
