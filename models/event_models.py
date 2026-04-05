from datetime import datetime
from models.models import db, User, TripPackage

class LocalEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    detailed_description = db.Column(db.Text)
    location = db.Column(db.String(100), nullable=False)
    event_date = db.Column(db.DateTime, nullable=False)
    event_type = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<LocalEvent {self.id}: {self.title} at {self.location}>'

class UserEventNotification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('local_event.id'), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='event_notifications')
    event = db.relationship('LocalEvent', backref='user_notifications')
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'event_id', name='uq_user_event'),
    )
    
    def __repr__(self):
        return f'<UserEventNotification {self.id}: User {self.user_id} - Event {self.event_id}>'

class FavoritedEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('local_event.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='favorited_events')
    event = db.relationship('LocalEvent', backref='favorited_by')
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'event_id', name='uq_user_favorited_event'),
    )
    
    def __repr__(self):
        return f'<FavoritedEvent {self.id}: User {self.user_id} - Event {self.event_id}>'
