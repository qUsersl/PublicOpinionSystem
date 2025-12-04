from app import db
from datetime import datetime

class ScrapingRule(db.Model):
    __tablename__ = 'scraping_rules'
    
    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(128), nullable=False, comment='站点名称')
    domain = db.Column(db.String(128), nullable=True, comment='站点域名')
    title_xpath = db.Column(db.String(256), nullable=True, comment='标题XPath')
    content_xpath = db.Column(db.String(256), nullable=True, comment='内容XPath')
    headers = db.Column(db.Text, nullable=True, comment='Request Headers(JSON)')
    description = db.Column(db.String(256), nullable=True, comment='备注')
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'site_name': self.site_name,
            'domain': self.domain,
            'title_xpath': self.title_xpath,
            'content_xpath': self.content_xpath,
            'headers': self.headers,
            'description': self.description,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
