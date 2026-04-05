from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=True)  
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    profile_photo = db.Column(db.String(200), default=None)
    dark_mode = db.Column(db.Boolean, default=False)
    badge_level = db.Column(db.String(20), default='bronze')
    travel_diaries_count = db.Column(db.Integer, default=0)
    progress = db.Column(db.Integer, default=0)
    discount = db.Column(db.Float, default=0.0)
    badge_merchandise = db.Column(db.String(100))
    google_id = db.Column(db.String(120), unique=True, nullable=True)  
    trip_preferences = db.relationship('TripPreferences', backref='user', uselist=False)
    diaries = db.relationship('TravelDiary', backref='user', lazy=True)
    communities = db.relationship('CommunityMember', backref='user', lazy=True)
    reactions = db.relationship('PostReaction', backref='user', lazy=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Define followers relationship
    followers = db.relationship(
        'UserFollow',
        foreign_keys='UserFollow.followed_id',
        backref=db.backref('followed', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    # Define following relationship
    following = db.relationship(
        'UserFollow',
        foreign_keys='UserFollow.follower_id',
        backref=db.backref('follower', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def update_badge(self):
        """Update user's badge level based on travel diaries count"""
        levels = {
            'bronze': 5,
            'silver': 10,
            'gold': 20,
            'platinum': 50
        }
        
        self.travel_diaries_count = len(self.diaries)
        
        # Calculate progress (2% per trip)
        self.progress = min(100, self.travel_diaries_count * 2)
        
        # Update badge level
        if self.travel_diaries_count < 5:
            self.badge_level = "no level achieved yet"
        elif self.travel_diaries_count < 10:
            self.badge_level = "bronze"
            self.discount = 5.0
            self.badge_merchandise = "Bronze Keychain"
        elif self.travel_diaries_count < 20:
            self.badge_level = "silver"
            self.discount = 10.0
            self.badge_merchandise = "Silver Keychain"
        elif self.travel_diaries_count < 50:
            self.badge_level = "gold"
            self.discount = 15.0
            self.badge_merchandise = "Gold Keychain"
        else:
            self.badge_level = "platinum"
            self.discount = 20.0
            self.badge_merchandise = "Platinum Keychain"
    
    def follow(self, user):
        """Follow another user"""
        if not self.is_following(user) and self.id != user.id:
            follow = UserFollow(follower_id=self.id, followed_id=user.id)
            db.session.add(follow)
            return True
        return False
    
    def unfollow(self, user):
        """Unfollow another user"""
        follow = UserFollow.query.filter_by(
            follower_id=self.id,
            followed_id=user.id
        ).first()
        if follow:
            db.session.delete(follow)
            return True
        return False
    
    def is_following(self, user):
        """Check if this user is following another user"""
        if user.id is None:
            return False
        return UserFollow.query.filter_by(
            follower_id=self.id,
            followed_id=user.id
        ).first() is not None
    
    def followers_count(self):
        """Get the number of followers"""
        return UserFollow.query.filter_by(followed_id=self.id).count()
    
    def following_count(self):
        """Get the number of users this user is following"""
        return UserFollow.query.filter_by(follower_id=self.id).count()
    
    def get_followers(self):
        """Get all users who follow this user"""
        follows = UserFollow.query.filter_by(followed_id=self.id).all()
        return [follow.follower for follow in follows]
    
    def get_following(self):
        """Get all users this user is following"""
        follows = UserFollow.query.filter_by(follower_id=self.id).all()
        return [follow.followed for follow in follows]

class TripPreferences(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    travel_type = db.Column(db.String(20), nullable=False)
    budget_range = db.Column(db.String(50), nullable=False)
    preferred_activities = db.Column(db.String(200), nullable=False)
    accommodation_type = db.Column(db.String(50), nullable=False)
    preferred_destinations = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TravelDiaryPhoto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    diary_id = db.Column(db.Integer, db.ForeignKey('travel_diary.id'), nullable=False)
    photo_path = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<TravelDiaryPhoto {self.id}>'

class TravelDiaryVideo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    diary_id = db.Column(db.Integer, db.ForeignKey('travel_diary.id'), nullable=False)
    video_path = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<TravelDiaryVideo {self.id}>'

class TravelDiary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    hotel = db.Column(db.String(100))
    restaurant = db.Column(db.String(100))
    rating = db.Column(db.Integer)
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    photos = db.relationship('TravelDiaryPhoto', backref='diary', lazy=True, cascade='all, delete-orphan')
    videos = db.relationship('TravelDiaryVideo', backref='diary', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<TravelDiary {self.id}: {self.title}>'

class TripPackage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)
    destination = db.Column(db.String(100), nullable=True)  
    image_data = db.Column(db.LargeBinary, nullable=True)  # For storing the actual image
    image_mimetype = db.Column(db.String(100), nullable=True)  # For storing image type
    image_path = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<TripPackage {self.id}: {self.name}>'

class BookmarkedPackage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    package_id = db.Column(db.Integer, db.ForeignKey('trip_package.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='bookmarked_packages')
    package = db.relationship('TripPackage', backref='bookmarks')
    __table_args__ = (
        db.UniqueConstraint('user_id', 'package_id', name='uq_user_package'),
    )

    def __repr__(self):
        return f'<BookmarkedPackage {self.id}: User {self.user_id} - Package {self.package_id}>'

class BRACUCentral(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(8), unique=True, nullable=False)
    gsuite = db.Column(db.String(100), unique=True, nullable=False)
    semester = db.Column(db.String(20))
    mobile_number = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Hotel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    amenities = db.Column(db.Text)
    base_price = db.Column(db.Float, nullable=False)
    image_path = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Hotel {self.name}>'

class HotelBooking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.String(20), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'), nullable=False)
    check_in = db.Column(db.Date, nullable=False)
    check_out = db.Column(db.Date, nullable=False)
    room_type = db.Column(db.String(50), nullable=False)
    num_rooms = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    booking_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='confirmed')
    user = db.relationship('User', backref=db.backref('hotel_bookings', lazy=True))
    hotel = db.relationship('Hotel', backref=db.backref('bookings', lazy=True))
    
    def __init__(self, **kwargs):
        super(HotelBooking, self).__init__(**kwargs)
        if not self.booking_id:
            self.booking_id = f"HT{datetime.now().strftime('%Y%m%d%H%M%S')}"

    def __repr__(self):
        return f'<HotelBooking {self.booking_id}>'

class TransportBooking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.String(20), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    booking_type = db.Column(db.String(20), nullable=False)  # flight, bus, train, car
    source = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    passengers = db.Column(db.Integer, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    booking_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='confirmed')
    
    user = db.relationship('User', backref=db.backref('transport_bookings', lazy=True))
    
    def __init__(self, **kwargs):
        super(TransportBooking, self).__init__(**kwargs)
        if not self.booking_id:
            # Generate a unique booking ID with prefix based on type
            prefix = {
                'flight': 'FL',
                'bus': 'BS',
                'train': 'TR',
                'car': 'CR'
            }.get(self.booking_type, 'BK')
            self.booking_id = f"{prefix}{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def __repr__(self):
        return f'<Booking {self.id}>'

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    package_id = db.Column(db.Integer, db.ForeignKey('trip_package.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_id = db.Column(db.String(100), nullable=True)
    order_id = db.Column(db.String(100), nullable=True)
    is_paid = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='bookings')
    package = db.relationship('TripPackage', backref='bookings')
    
    def __repr__(self):
        return f'<Booking {self.id}>'

class UserFollow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Define unique constraint to prevent duplicate follows
    __table_args__ = (
        db.UniqueConstraint('follower_id', 'followed_id', name='uq_follower_followed'),
    )
    
    def __repr__(self):
        return f'<UserFollow {self.follower_id} -> {self.followed_id}>'

def init_db():
    try:
        # Add test user if not exists
        if User.query.filter_by(email='test@example.com').first() is None:
            test_user = User(
                email='test@example.com',
                name='Test User',
                age=25
            )
            test_user.set_password('password123')
            db.session.add(test_user)
            print('Test user created successfully!')
        else:
            print('Test user already exists')

        # Add sample hotels if not exist
        hotels = [
            {
                'name': 'Pan Pacific Sonargaon',
                'location': 'Dhaka',
                'description': 'Luxury 5-star hotel in the heart of Dhaka',
                'amenities': 'Swimming pool, Spa, Restaurant, Gym',
                'base_price': 15000.0,
                'image_path': '/static/images/hotels/pan-pacific.jpg'
            },
            {
                'name': 'Le Méridien',
                'location': 'Dhaka',
                'description': 'Modern luxury hotel with city views',
                'amenities': 'Restaurant, Gym, Business center',
                'base_price': 12000.0,
                'image_path': '/static/images/hotels/le-meridien.jpg'
            },
            {
                'name': 'Radisson Blu',
                'location': 'Chittagong',
                'description': 'Beachside luxury hotel',
                'amenities': 'Beach access, Pool, Spa',
                'base_price': 10000.0,
                'image_path': '/static/images/hotels/radisson.jpg'
            },
            {
                'name': 'The Westin',
                'location': 'Dhaka',
                'description': 'Premium hotel with modern amenities',
                'amenities': 'Pool, Gym, Restaurant, Bar',
                'base_price': 13000.0,
                'image_path': '/static/images/hotels/westin.jpg'
            }
        ]

        for hotel_data in hotels:
            if not Hotel.query.filter_by(name=hotel_data['name']).first():
                hotel = Hotel(**hotel_data)
                db.session.add(hotel)

        # Add BRACU community if not exists
        if Community.query.filter_by(name='BRACU Travelers').first() is None:
            bracu_community = Community(
                name='BRACU Travelers',
                description='A community for BRACU students who love to travel',
                is_private=False
            )
            db.session.add(bracu_community)
            print('BRACU community created successfully!')
        else:
            print('BRACU community already exists')

        db.session.commit()
        print('Database initialized successfully!')

    except Exception as e:
        print(f'Error initializing database: {str(e)}')
        db.session.rollback()

# Initialize sample BRACU data
def init_bracu_data():
    bracu_data = [
        {
            'student_id': '22101631',
            'gsuite': 'sackline.naien.ridvi@g.bracu.ac.bd',
            'semester': 'Spring22',
            'mobile_number': '01712345678'
        },
        {
            'student_id': '22101632',
            'gsuite': 'john.doe@g.bracu.ac.bd',
            'semester': 'Spring22',
            'mobile_number': '01712345679'
        },
        {
            'student_id': '22101633',
            'gsuite': 'jane.smith@g.bracu.ac.bd',
            'semester': 'Spring22',
            'mobile_number': '01712345680'
        },
        {
            'student_id': '22101634',
            'gsuite': 'mike.brown@g.bracu.ac.bd',
            'semester': 'Spring22',
            'mobile_number': '01712345681'
        },
        {
            'student_id': '22101635',
            'gsuite': 'sarah.wilson@g.bracu.ac.bd',
            'semester': 'Spring22',
            'mobile_number': '01712345682'
        },
        {
            'student_id': '22101636',
            'gsuite': 'david.miller@g.bracu.ac.bd',
            'semester': 'Spring22',
            'mobile_number': '01712345683'
        },
        {
            'student_id': '22101637',
            'gsuite': 'lisa.johnson@g.bracu.ac.bd',
            'semester': 'Spring22',
            'mobile_number': '01712345684'
        },
        {
            'student_id': '22101638',
            'gsuite': 'mark.williams@g.bracu.ac.bd',
            'semester': 'Spring22',
            'mobile_number': '01712345685'
        },
        {
            'student_id': '22101639',
            'gsuite': 'jessica.davis@g.bracu.ac.bd',
            'semester': 'Spring22',
            'mobile_number': '01712345686'
        },
        {
            'student_id': '22101640',
            'gsuite': 'robert.jackson@g.bracu.ac.bd',
            'semester': 'Spring22',
            'mobile_number': '01712345687'
        }
    ]

    for data in bracu_data:
        existing = BRACUCentral.query.filter_by(student_id=data['student_id']).first()
        if not existing:
            bracu = BRACUCentral(**data)
            db.session.add(bracu)
    db.session.commit()

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    is_automatic = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('expenses', lazy=True))

class EmergencyContact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    relationship = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    alternate_phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('emergency_contacts', lazy=True))

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('chat_messages', lazy=True))