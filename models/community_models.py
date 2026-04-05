from datetime import datetime
from models.models import db
from sqlalchemy import event
from sqlalchemy.orm import Session

class Community(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    members = db.relationship('CommunityMember', backref='community', lazy=True)
    posts = db.relationship('CommunityPost', backref='community', lazy=True)

class CommunityMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    community_id = db.Column(db.Integer, db.ForeignKey('community.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    posts = db.relationship('CommunityPost', backref='author', lazy=True)
    comments = db.relationship('PostComment', backref='author', lazy=True)

class CommunityPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    community_id = db.Column(db.Integer, db.ForeignKey('community.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('community_member.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    photos = db.relationship('CommunityPostPhoto', backref='post', lazy=True)
    videos = db.relationship('CommunityPostVideo', backref='post', lazy=True)
    comments = db.relationship('PostComment', backref='post', lazy=True)
    reactions = db.relationship('PostReaction', backref='post', lazy=True)
    
    # Add reaction count field for direct access
    love_count = db.Column(db.Integer, default=0)
    
    # Method to update reaction counts
    def update_reaction_counts(self):
        self.love_count = PostReaction.query.filter_by(post_id=self.id, reaction_type='love').count()

    def __repr__(self):
        return f'<CommunityPost {self.id}>'

class CommunityPostPhoto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('community_post.id'), nullable=False)
    photo_path = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<CommunityPostPhoto {self.id}>'

class CommunityPostVideo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('community_post.id'), nullable=False)
    video_path = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<CommunityPostVideo {self.id}>'

class PostReaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('community_post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reaction_type = db.Column(db.String(20), nullable=False)  # like, love, wow, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (
        db.UniqueConstraint('post_id', 'user_id', name='uq_post_user_reaction'),
    )

class PostComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('community_post.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('community_member.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    parent_id = db.Column(db.Integer, db.ForeignKey('post_comment.id'))
    children = db.relationship('PostComment', 
                              backref=db.backref('parent', remote_side=[id]),
                              cascade="all, delete-orphan",
                              passive_deletes=True)
    
    def __repr__(self):
        return f'<PostComment id={self.id} post_id={self.post_id} parent_id={self.parent_id}>'

# Event listeners for PostComment
def before_flush_comments(session, flush_context, instances):
    for obj in session.new:
        if isinstance(obj, PostComment) and obj.post_id is None:
            # If this is a reply and post_id is not set, get it from parent
            if obj.parent_id is not None:
                parent = session.get(PostComment, obj.parent_id)
                if parent and parent.post_id:
                    obj.post_id = parent.post_id
                    print(f"Set post_id={obj.post_id} for comment from parent")

event.listen(Session, 'before_flush', before_flush_comments)
