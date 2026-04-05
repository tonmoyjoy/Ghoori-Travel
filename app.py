from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file, abort, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, date
import logging
import os
import io
import mimetypes
from PIL import Image
import stripe
import json
import hmac
import hashlib
from werkzeug.utils import secure_filename
from flask_paginate import Pagination
from oauthlib.oauth2 import WebApplicationClient
import requests
from math import radians, sin, cos, sqrt, atan2
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, FloatField, DateField, IntegerField, TextAreaField
from models.models import User, TripPreferences, TravelDiary, TripPackage, BookmarkedPackage, BRACUCentral, Booking, UserFollow, Expense, EmergencyContact, ChatMessage, TransportBooking, Hotel, HotelBooking
from wtforms.validators import DataRequired, Email, Length, NumberRange
from config import Config
GOOGLE_API_KEY = Config.GOOGLE_API_KEY
from models import db, User, TripPreferences, Expense, EmergencyContact, Booking, ChatMessage
from forms import RegistrationForm, LoginForm, TripPreferencesForm, EmergencyContactForm
from forms import FlightBookingForm, BusBookingForm, TrainBookingForm, CarBookingForm, HotelBookingForm
from flask_migrate import Migrate

# Allow OAuth2 to work on HTTP for local development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

from config import Config
from models import db, User, TripPreferences, TravelDiary, TravelDiaryPhoto, TravelDiaryVideo
from models import TripPackage, BookmarkedPackage, BRACUCentral, init_bracu_data
from models.community_models import Community, CommunityMember, CommunityPost, PostReaction, PostComment, CommunityPostPhoto, CommunityPostVideo
from models.models import Booking, UserFollow
from models.event_models import LocalEvent, UserEventNotification, FavoritedEvent
from models.review_models import Review
from sqlalchemy import or_
from forms import RegistrationForm, LoginForm, TripPreferencesForm, TravelDiaryForm

app = Flask(__name__)
app.config.from_object(Config)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'app.db')
app.config['SQLALCHEMY_BINDS'] = {
    'default': app.config['SQLALCHEMY_DATABASE_URI']
}

# Initialize extensions
migrate = Migrate(app, db)

# Fixed prices for different services
PRICES = {
    'flight': {
        'economy': {
            'biman': 5000,
            'us-bangla': 4500,
            'novoair': 4800
        },
        'business': {
            'biman': 12000,
            'us-bangla': 10000,
            'novoair': 11000
        }
    },
    'bus': {
        'ac': 1500,
        'non-ac': 800
    },
    'train': {
        'shovon': {
            'padma': 400,
            'subarna': 450,
            'mohanagar': 400
        },
        'first': {
            'padma': 800,
            'subarna': 850,
            'mohanagar': 800
        },
        'sleeper': {
            'padma': 1200,
            'subarna': 1250,
            'mohanagar': 1200
        }
    },
    'car': {
        'sedan': 5000,
        'suv': 8000,
        'van': 10000
    },
    'hotel': {
        'pan-pacific': {'base': 15000, 'double': 1.3, 'suite': 1.6},
        'le-meridien': {'base': 12000, 'double': 1.3, 'suite': 1.6},
        'radisson': {'base': 10000, 'double': 1.3, 'suite': 1.6},
        'westin': {'base': 13000, 'double': 1.3, 'suite': 1.6}
    }
}
app.config['SQLALCHEMY_BINDS'] = {
    'default': app.config['SQLALCHEMY_DATABASE_URI']
}

# Create instance directory if it doesn't exist
instance_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
if not os.path.exists(instance_dir):
    os.makedirs(instance_dir)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200MB max file size

# Allowed file extensions
ALLOWED_PHOTO_EXT = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_VIDEO_EXT = {'mp4', 'avi', 'mov'}

# Create directories if they don't exist
for directory in ['instance', 'static/uploads/photos', 'static/uploads/videos']:
    dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), directory)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "info"

def allowed_file(filename, allowed_set):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_set

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize database
with app.app_context():
    try:
        def init_db():
            # Create tables if they don't exist, but don't drop existing tables
            db.create_all()
            
            # Create test user if doesn't exist
            test_user = User.query.filter_by(email='test@example.com').first()
            if not test_user:
                test_user = User(
                    email='test@example.com',
                    password=generate_password_hash('password123'),
                    name='Test User',
                    age=25,
                    dark_mode=False,
                    profile_photo=None
                )
                db.session.add(test_user)
                db.session.commit()
                print("Test user created successfully!")
            else:
                print("Test user already exists")
                
            # Create BRACU community if doesn't exist
            bracu_community = Community.query.filter_by(name='BRACU').first()
            if not bracu_community:
                bracu_community = Community(
                    name='BRACU',
                    description='The official community for BRACU students to share travel experiences and connect with fellow students.'
                )
                db.session.add(bracu_community)
                db.session.commit()
                print("BRACU community created successfully!")
            else:
                print("BRACU community already exists")
                
            # Initialize BRACU data
            init_bracu_data()

            sample_packages = [
                {
                    'name': 'Sundarbans Adventure',
                    'duration': '3 Days',
                    'price': 25000.00,
                    'description': 'Explore the world-famous Sundarbans mangrove forest. Experience boat rides, wildlife viewing, and traditional village visits.',
                    'image_file': 'trip_images/sundarbans.jpg'
                },
                {
                    'name': "Cox's Bazar Beach Tour",
                    'duration': '4 Days',
                    'price': 18000.00,
                    'description': 'Relax on the world\'s longest natural sea beach. Visit Inani Beach, Himchari National Park, and enjoy water sports.',
                    'image_file': 'trip_images/coxs_bazar.jpeg'
                },
                {
                    'name': 'Srimangal Tea Tour',
                    'duration': '2 Days',
                    'price': 12000.00,
                    'description': 'Visit tea gardens in Srimangal, learn about tea production, and enjoy scenic views of the Meghalaya Hills.',
                    'image_file': 'trip_images/srimangal.jpg'
                },
                {
                    'name': 'Saint Martin Island Trip',
                    'duration': '3 Days',
                    'price': 22000.00,
                    'description': 'Island hopping, snorkeling, and beach relaxation on Saint Martin Island. Experience the crystal clear waters and coral reefs.',
                    'image_file': 'trip_images/saint_martin.jpg'
                },
                {
                    'name': 'Sylhet Cultural Tour',
                    'duration': '5 Days',
                    'price': 28000.00,
                    'description': 'Explore the cultural heritage of Sylhet. Visit Lalakhal, Ratargul Swamp Forest, and the tea estates.',
                    'image_file': 'trip_images/sylhet.jpg'
                },
                {
                    'name': 'Dhaka City Tour',
                    'duration': '2 Days',
                    'price': 8000.00,
                    'description': 'Explore the historic city of Dhaka, visit Lalbagh Fort, Ahsan Manzil, and the Liberation War Museum.',
                    'image_file': 'trip_images/dhaka.png'
                },
                {
                    'name': 'Chittagong Hill Tracts Tour',
                    'duration': '4 Days',
                    'price': 20000.00,
                    'description': 'Experience the natural beauty of the Chittagong Hill Tracts, visit the Bandarban Hill District, and the Sangu River.',
                    'image_file': 'trip_images/chittagong.jpg'
                },
                {
                    'name': 'Kuakata Beach Tour',
                    'duration': '3 Days',
                    'price': 15000.00,
                    'description': 'Relax on the beautiful Kuakata Beach, visit the Kuakata National Park, and enjoy water sports.',
                    'image_file': 'trip_images/kuakata.png'
                },
                {
                    'name': 'Rangamati Tour',
                    'duration': '3 Days',
                    'price': 18000.00,
                    'description': 'Explore the natural beauty of Rangamati, visit the Kaptai Lake, and the Rangamati Hill District.',
                    'image_file': 'trip_images/rangamati.png'
                },
                {
                    'name': 'Bandarban Tour',
                    'duration': '4 Days',
                    'price': 22000.00,
                    'description': 'Experience the natural beauty of Bandarban, visit the Nilgiri Hill, and the Sangu River.',
                    'image_file': 'trip_images/bandarban.jpg'
                }
            ]
            
            # Create sample packages
            for package_data in sample_packages:
                image_path = os.path.join(app.static_folder, package_data['image_file'])
                image_data = None
                image_mimetype = None
                
                if os.path.exists(image_path):
                    with open(image_path, 'rb') as f:
                        image_data = f.read()
                    image_mimetype = mimetypes.guess_type(image_path)[0]
                
                package = TripPackage(
                    name=package_data['name'],
                    duration=package_data['duration'],
                    price=package_data['price'],
                    description=package_data['description'],
                    image_data=image_data,
                    image_mimetype=image_mimetype
                )
                db.session.add(package)
            
            db.session.commit()
            print("Database initialized successfully!")

        # Call init_db
        init_db()
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        db.session.rollback()



@app.route('/')
def home():
    # Simple redirect to login if not authenticated
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    # If already logged in, go to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        if not email or not password:
            flash('Please fill in all fields', 'danger')
            return redirect(url_for('login'))
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password.', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    # If already logged in, go to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if email already exists
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered. Please login.', 'danger')
            return render_template('register.html', form=form)
        
        # Create new user
        user = User(
            email=form.email.data,
            name=form.name.data,
            age=form.age.data,
            dark_mode=False,
            profile_photo=None
        )
        user.set_password(form.password.data)
        
        # Save to database
        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            print(f"Registration error: {str(e)}")
            flash('Registration failed. Please try again.', 'danger')
    
    return render_template('register.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/upload-profile-photo', methods=['POST'])
@login_required
def upload_profile_photo():
    if 'photo' not in request.files:
        return jsonify({'success': False, 'message': 'No photo provided'}), 400
    
    photo = request.files['photo']
    if photo.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'}), 400
    
    if not allowed_file(photo.filename, ALLOWED_PHOTO_EXT):
        return jsonify({'success': False, 'message': 'Invalid file type'}), 400
    
    try:
        # Ensure upload directory exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Generate a unique filename using user ID and timestamp
        extension = os.path.splitext(photo.filename)[1].lower()
        filename = f"user_{current_user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{extension}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Open the image using Pillow
        img = Image.open(photo)
        
        # Convert to RGB if necessary (for PNG files with transparency)
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])  # Use alpha channel as mask
            img = background
        
        # Resize the image to 200x200 pixels using LANCZOS resampling
        img = img.resize((200, 200), Image.Resampling.LANCZOS)
        
        # Save the resized image
        img.save(filepath, quality=95)
        
        # Update user's profile photo in database
        current_user.profile_photo = filename
        db.session.commit()
        
        return jsonify({'success': True, 'filename': filename})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/dashboard')
@login_required
def dashboard():
    # Start with all trip packages
    trip_packages_query = TripPackage.query
    
    # Variables to track active filters for display
    active_filters = {}
    
    # Apply filters based on URL parameters
    budget = request.args.get('budget')
    duration = request.args.get('duration')
    
    # Duration mapping for display purposes
    duration_mapping = {
        'short': '1-3 Days',
        'medium': '4-7 Days',
        'long': '8-14 Days',
        'extended': '15+ Days'
    }
    
    # Apply budget filter if provided
    if budget:
        if budget == 'budget':
            trip_packages_query = trip_packages_query.filter(TripPackage.price <= 15000)
            active_filters['budget'] = '৳5,000 - ৳15,000'
        elif budget == 'mid_range':
            trip_packages_query = trip_packages_query.filter(TripPackage.price > 15000, TripPackage.price <= 30000)
            active_filters['budget'] = '৳15,000 - ৳30,000'
        elif budget == 'luxury':
            trip_packages_query = trip_packages_query.filter(TripPackage.price > 30000, TripPackage.price <= 50000)
            active_filters['budget'] = '৳30,000 - ৳50,000'
        elif budget == 'ultra_luxury':
            trip_packages_query = trip_packages_query.filter(TripPackage.price > 50000)
            active_filters['budget'] = '৳50,000+'
    
    # Apply duration filter if provided (duration is stored as a string in the format "X days")
    if duration:
        if duration == 'short':
            # Filter packages with durations like "1 day", "2 days", "3 days"
            trip_packages_query = trip_packages_query.filter(
                db.or_(
                    TripPackage.duration.like('1 day%'),
                    TripPackage.duration.like('2 day%'),
                    TripPackage.duration.like('3 day%')
                )
            )
            active_filters['duration'] = duration_mapping.get(duration)
        elif duration == 'medium':
            # 4-7 days
            trip_packages_query = trip_packages_query.filter(
                db.or_(
                    TripPackage.duration.like('4 day%'),
                    TripPackage.duration.like('5 day%'),
                    TripPackage.duration.like('6 day%'),
                    TripPackage.duration.like('7 day%')
                )
            )
            active_filters['duration'] = duration_mapping.get(duration)
        elif duration == 'long':
            trip_packages_query = trip_packages_query.filter(TripPackage.duration.like('%8-14 Days%'))
        elif duration == 'extended':
            trip_packages_query = trip_packages_query.filter(TripPackage.duration.like('%15+ Days%'))
    
    trip_packages = trip_packages_query.all()
    
    # Get bookmarked package IDs for the current user
    bookmarked_package_ids = set()
    if current_user.is_authenticated:
        bookmarked_packages = BookmarkedPackage.query.filter_by(user_id=current_user.id).all()
        bookmarked_package_ids = {bookmark.package_id for bookmark in bookmarked_packages}
    
    # Get booked packages for the current user
    booked_packages = []
    if current_user.is_authenticated:
        bookings = Booking.query.filter_by(user_id=current_user.id).all()
        for booking in bookings:
            package = TripPackage.query.get(booking.package_id)
            if package:
                booked_packages.append((booking, package))
    
    # Get user's trip preferences
    trip_preferences = TripPreferences.query.filter_by(user_id=current_user.id).first()
    
    # Create active filters dictionary for display
    active_filters = {}
    if budget:
        active_filters['budget'] = budget.replace('_', ' ').title()
    if duration:
        active_filters['duration'] = duration.replace('_', ' ').title()
    
    return render_template('dashboard.html',
                          trip_packages=trip_packages,
                          bookmarked_package_ids=bookmarked_package_ids,
                          booked_packages=booked_packages,
                          active_filters=active_filters,
                          trip_preferences=trip_preferences)

@app.route('/trip-preferences', methods=['GET', 'POST'])
@login_required
def trip_preferences():
    preferences = TripPreferences.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        if preferences:
            # Update existing preferences
            preferences.travel_type = request.form.get('travel_type')
            preferences.budget_range = request.form.get('budget_range')
            preferences.preferred_activities = request.form.get('preferred_activities')
            preferences.accommodation_type = request.form.get('accommodation_type')
            preferences.preferred_destinations = request.form.get('preferred_destinations')
            preferences.updated_at = datetime.utcnow()
        else:
            # Create new preferences
            preferences = TripPreferences(
                user_id=current_user.id,
                travel_type=request.form.get('travel_type'),
                budget_range=request.form.get('budget_range'),
                preferred_activities=request.form.get('preferred_activities'),
                accommodation_type=request.form.get('accommodation_type'),
                preferred_destinations=request.form.get('preferred_destinations')
            )
            db.session.add(preferences)
        
        db.session.commit()
        flash('Trip preferences updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('trip_preferences.html', preferences=preferences)

@app.route('/new_travel_history', methods=['GET', 'POST'])
@login_required
def new_travel_history():
    form = TravelDiaryForm()
    diary_id = request.args.get('diary_id')
    
    if diary_id:
        diary = TravelDiary.query.get(diary_id)
        if not diary or diary.user_id != current_user.id:
            flash('Invalid diary ID or unauthorized access.', 'danger')
            return redirect(url_for('dashboard'))
        
        # Pre-fill the form with existing data
        form.title.data = diary.title
        form.description.data = diary.description
        form.content.data = diary.content
        form.hotel.data = diary.hotel
        form.restaurant.data = diary.restaurant
        form.rating.data = diary.rating
        form.is_public.data = diary.is_public
    
    if form.validate_on_submit():
        try:
            # Ensure upload directories exist
            photos_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'photos')
            videos_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'videos')
            os.makedirs(photos_dir, exist_ok=True)
            os.makedirs(videos_dir, exist_ok=True)

            if diary_id:
                # Update existing diary
                diary = TravelDiary.query.get(diary_id)
                if not diary:
                    flash('Diary not found.', 'danger')
                    return redirect(url_for('dashboard'))
                
                # Update all fields
                diary.title = form.title.data
                diary.description = form.description.data
                diary.content = form.content.data
                diary.hotel = form.hotel.data
                diary.restaurant = form.restaurant.data
                diary.rating = form.rating.data
                diary.is_public = form.is_public.data
                
                # Handle new photos
                if form.photos.data:
                    for photo in form.photos.data:
                        if photo and photo.filename:
                            if not allowed_file(photo.filename, ALLOWED_PHOTO_EXT):
                                flash(f'Invalid photo file type: {photo.filename}', 'danger')
                                continue
                                
                            filename = secure_filename(photo.filename)
                            photo_path = os.path.join(photos_dir, filename)
                            try:
                                photo.save(photo_path)
                                # Create a new TravelDiaryPhoto record
                                photo_record = TravelDiaryPhoto(
                                    diary_id=diary_id,
                                    photo_path=filename
                                )
                                db.session.add(photo_record)
                            except Exception as e:
                                flash(f'Error saving photo {filename}: {str(e)}', 'danger')
                                continue
                
                # Handle video uploads
                if form.videos.data:
                    for video in form.videos.data:
                        if video and video.filename:
                            if not allowed_file(video.filename, ALLOWED_VIDEO_EXT):
                                flash(f'Invalid video file type: {video.filename}', 'danger')
                                continue
                                
                            video_filename = secure_filename(video.filename)
                            video_path = os.path.join(videos_dir, video_filename)
                            try:
                                video.save(video_path)
                                # Create a new TravelDiaryVideo record
                                video_record = TravelDiaryVideo(
                                    diary_id=diary_id,
                                    video_path=video_filename
                                )
                                db.session.add(video_record)
                            except Exception as e:
                                flash(f'Error saving video {video_filename}: {str(e)}', 'danger')
                                continue
            else:
                # Create new diary
                diary = TravelDiary(
                    user_id=current_user.id,
                    title=form.title.data,
                    description=form.description.data,
                    content=form.content.data,
                    hotel=form.hotel.data,
                    restaurant=form.restaurant.data,
                    rating=form.rating.data,
                    is_public=form.is_public.data
                )
                db.session.add(diary)
                db.session.flush()  # Get the diary ID
                
                # Handle photos for new diary
                if form.photos.data:
                    for photo in form.photos.data:
                        if photo and photo.filename:
                            if not allowed_file(photo.filename, ALLOWED_PHOTO_EXT):
                                flash(f'Invalid photo file type: {photo.filename}', 'danger')
                                continue
                                
                            filename = secure_filename(photo.filename)
                            photo_path = os.path.join(photos_dir, filename)
                            try:
                                photo.save(photo_path)
                                # Create a new TravelDiaryPhoto record
                                photo_record = TravelDiaryPhoto(
                                    diary_id=diary.id,
                                    photo_path=filename
                                )
                                db.session.add(photo_record)
                            except Exception as e:
                                flash(f'Error saving photo {filename}: {str(e)}', 'danger')
                                continue
                
                # Handle video uploads
                if form.videos.data:
                    for video in form.videos.data:
                        if video and video.filename:
                            if not allowed_file(video.filename, ALLOWED_VIDEO_EXT):
                                flash(f'Invalid video file type: {video.filename}', 'danger')
                                continue
                                
                            video_filename = secure_filename(video.filename)
                            video_path = os.path.join(videos_dir, video_filename)
                            try:
                                video.save(video_path)
                                # Create a new TravelDiaryVideo record
                                video_record = TravelDiaryVideo(
                                    diary_id=diary.id,
                                    video_path=video_filename
                                )
                                db.session.add(video_record)
                            except Exception as e:
                                flash(f'Error saving video {video_filename}: {str(e)}', 'danger')
                                continue
            
            db.session.commit()
            flash('Travel diary saved successfully!', 'success')
            
            # Update user's badge level after creating new diary
            current_user.update_badge()
            
            return redirect(url_for('profile'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error saving travel diary: {str(e)}', 'danger')
            print(f"Error: {str(e)}")  # For debugging
            
    return render_template('diary_form.html', form=form, diary_id=diary_id)

@app.route('/travel_diary/<int:diary_id>')
def view_diary(diary_id):
    diary = TravelDiary.query.get_or_404(diary_id)
    if not diary.is_public and diary.user_id != current_user.id:
        flash('You do not have permission to view this diary', 'danger')
        return redirect(url_for('dashboard'))
    
    return render_template('view_diary.html', diary=diary)

@app.route('/submit_review', methods=['POST'])
@login_required
def submit_review():
    name = request.form.get('name')
    rating = request.form.get('rating')
    review_text = request.form.get('review')
    
    if not all([name, rating, review_text]):
        flash('Please fill in all fields', 'error')
        return redirect(url_for('review_form'))
    
    review = Review(
        user_id=current_user.id,
        name=name,
        rating=int(rating),
        review_text=review_text
    )
    
    db.session.add(review)
    db.session.commit()
    
    flash('Review submitted successfully!', 'success')
    return redirect(url_for('profile'))

@app.route('/get_review_items')
@login_required
def get_review_items():
    review_type = request.args.get('type')
    
    if review_type == 'restaurant':
        # For restaurants, you might want to fetch from a restaurants table
        # For now, I'll return some sample data
        items = [
            {'id': 1, 'name': 'Sample Restaurant 1'},
            {'id': 2, 'name': 'Sample Restaurant 2'},
            {'id': 3, 'name': 'Sample Restaurant 3'}
        ]
    elif review_type == 'hotel':
        # For hotels, you might want to fetch from a hotels table
        # For now, I'll return some sample data
        items = [
            {'id': 1, 'name': 'Sample Hotel 1'},
            {'id': 2, 'name': 'Sample Hotel 2'},
            {'id': 3, 'name': 'Sample Hotel 3'}
        ]
    elif review_type == 'trip_package':
        items = TripPackage.query.all()
        items = [{'id': item.id, 'name': item.name} for item in items]
    else:
        return jsonify({'error': 'Invalid review type'}), 400
    
    return jsonify({'items': items})

@app.route('/review_form')
@login_required
def review_form():
    return render_template('review_form.html')

@app.route('/user_reviews')
@login_required
def user_reviews():
    reviews = Review.query.filter_by(user_id=current_user.id).order_by(Review.created_at.desc()).all()
    return jsonify({
        'reviews': [{
            'id': review.id,
            'name': review.name,
            'rating': review.rating,
            'review_text': review.review_text,
            'created_at': review.created_at.strftime('%Y-%m-%d')
        } for review in reviews]
    })

@app.route('/delete_review/<int:review_id>', methods=['DELETE'])
@login_required
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    if review.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    db.session.delete(review)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/profile')
@login_required
def profile():
    # Load recommendations when page loads
    try:
        # Get user's preferences
        user_preferences = TripPreferences.query.filter_by(user_id=current_user.id).first()
        
        if user_preferences:
            app.logger.info(f"User preferences found: {user_preferences.__dict__}")
        else:
            app.logger.info("No preferences found for user")
            
        # Get all packages for debugging
        packages = TripPackage.query.all()
        app.logger.info(f"Total packages in database: {len(packages)}")
        for package in packages:
            app.logger.info(f"Package: {package.name} - Price: {package.price}")
            
    except Exception as e:
        app.logger.error(f"Error in profile route: {str(e)}")
    
    # Load the user's profile data
    user = User.query.get(current_user.id)
    if not user:
        flash('Error loading profile data', 'danger')
        return redirect(url_for('dashboard'))
    
    # Ensure profile_photo is set to None if it doesn't exist
    if not user.profile_photo:
        user.profile_photo = None
    
    bookmarked_packages = BookmarkedPackage.query.filter_by(user_id=current_user.id).join(TripPackage).all()
    diaries = TravelDiary.query.filter_by(user_id=current_user.id).order_by(TravelDiary.created_at.desc()).all()
    
    # Update user's badge level using the User model's method
    try:
        current_user.update_badge()
        travel_diaries_count = current_user.travel_diaries_count
        badge_level = current_user.badge_level
        merchandise = current_user.badge_merchandise
    except Exception as e:
        print(f"Error updating badge level: {str(e)}")
        travel_diaries_count = 0
        badge_level = 'none'
        merchandise = None
    
    return render_template('profile.html',
                           bookmarked_packages=bookmarked_packages,
                           diaries=diaries,
                           user=current_user,
                           travel_diaries_count=travel_diaries_count,
                           badge_level=badge_level,
                           merchandise=merchandise)

@app.route('/delete_diary/<int:diary_id>', methods=['POST'])
@login_required
def delete_diary(diary_id):
    try:
        diary = TravelDiary.query.get_or_404(diary_id)
        
        # Ensure the user owns this diary
        if diary.user_id != current_user.id:
            flash('Unauthorized access', 'danger')
            return redirect(url_for('profile'))
        
        # Delete the diary and its associated photos
        TravelDiaryPhoto.query.filter_by(diary_id=diary_id).delete()
        db.session.delete(diary)
        
        # Update user's badge level after deletion
        current_user.update_badge()
        
        db.session.commit()
        
        flash('Diary deleted successfully', 'success')
        return redirect(url_for('profile'))
    except Exception as e:
        print(f"Error deleting diary: {str(e)}")
        db.session.rollback()
        flash('Failed to delete diary', 'danger')
        return redirect(url_for('profile'))

@app.route('/toggle-theme', methods=['POST'])
def toggle_theme():
    try:
        if current_user.is_authenticated:
            current_user.dark_mode = not current_user.dark_mode
            db.session.commit()
            return jsonify({'dark_mode': current_user.dark_mode})
        else:
            return jsonify({'dark_mode': False})
    except Exception as e:
        print(f"Error toggling theme: {str(e)}")
        return jsonify({'error': 'Failed to toggle theme'}), 500

@app.route('/toggle_bookmark/<int:package_id>', methods=['POST'])
@login_required
def toggle_bookmark(package_id):
    try:
        # Get the package
        package = TripPackage.query.get_or_404(package_id)
        
        # Check if the package is already bookmarked by this user
        bookmark = BookmarkedPackage.query.filter_by(
            user_id=current_user.id,
            package_id=package_id
        ).first()

        if bookmark:
            # If bookmark exists, delete it
            db.session.delete(bookmark)
            db.session.commit()
            return jsonify({'bookmarked': False})
        else:
            # If no bookmark exists, create a new one
            new_bookmark = BookmarkedPackage(
                user_id=current_user.id,
                package_id=package_id
            )
            db.session.add(new_bookmark)
            db.session.commit()
            return jsonify({'bookmarked': True})
    except Exception as e:
        print(f"Error toggling bookmark: {str(e)}")
        db.session.rollback()
        return jsonify({
            'error': 'Failed to toggle bookmark',
            'message': str(e)
        }), 500

@app.route('/package/<int:package_id>')
def view_package(package_id):
    package = TripPackage.query.get_or_404(package_id)
    
    # Check if the package is bookmarked by the current user
    is_bookmarked = False
    if current_user.is_authenticated:
        is_bookmarked = BookmarkedPackage.query.filter_by(
            user_id=current_user.id,
            package_id=package_id
        ).first() is not None
    
    # Get all bookmarked packages for the current user
    bookmarked_packages = []
    if current_user.is_authenticated:
        bookmarked_packages = BookmarkedPackage.query.filter_by(
            user_id=current_user.id
        ).join(TripPackage).order_by(BookmarkedPackage.created_at.desc()).all()
    
    return render_template('package_details.html', 
                         package=package,
                         is_bookmarked=is_bookmarked,
                         bookmarked_packages=bookmarked_packages,
                         stripe_key=app.config['STRIPE_PUBLISHABLE_KEY'])

@app.route('/communities')
@login_required
def communities():
    try:
        # Get all communities
        communities = Community.query.all()
        
        # Get user's memberships
        user_memberships = {}
        if current_user.is_authenticated:
            memberships = CommunityMember.query.filter_by(user_id=current_user.id).all()
            for membership in memberships:
                user_memberships[membership.community_id] = True
        
        return render_template('communities.html', 
                              communities=communities, 
                              user_memberships=user_memberships)
    except Exception as e:
        import traceback
        print(f"Error in communities route: {str(e)}")
        print(traceback.format_exc())
        flash('An error occurred while loading communities.', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/community/bracu', methods=['GET', 'POST'])
@login_required
def bracu_community():
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        gsuite = request.form.get('gsuite')
        semester = request.form.get('semester')
        mobile_number = request.form.get('mobile_number')
        password = request.form.get('password')

        # Verify BRACU credentials
        bracu_user = BRACUCentral.query.filter_by(student_id=student_id, gsuite=gsuite).first()
        if not bracu_user:
            flash('Invalid student ID or GSuite email', 'danger')
            return redirect(url_for('bracu_community'))

        # Verify password matches user's main account password
        if not current_user.check_password(password):
            flash('Invalid password. Please use your main account password.', 'danger')
            return redirect(url_for('bracu_community'))

        # Check if user is already a member
        existing_member = CommunityMember.query.filter_by(
            community_id=1,  # BRACU community ID
            user_id=current_user.id
        ).first()

        if existing_member:
            flash('You are already a member of this community', 'info')
            return redirect(url_for('community_feed', community_id=1))

        # Add user to community
        member = CommunityMember(
            community_id=1,  # BRACU community ID
            user_id=current_user.id,
            verified=True
        )
        db.session.add(member)
        db.session.commit()

        flash('Successfully joined BRACU community!', 'success')
        return redirect(url_for('community_feed', community_id=1))

    # Handle GET request
    return render_template('bracu_community.html')

@app.route('/community/<int:community_id>')
@login_required
def community_feed(community_id):
    try:
        # Get the community
        community = Community.query.get_or_404(community_id)
        
        # Get all posts for this community
        posts = CommunityPost.query.filter_by(community_id=community_id).order_by(CommunityPost.created_at.desc()).all()
        
        # Get user's reactions for each post
        user_reactions = {}
        for post in posts:
            reaction = PostReaction.query.filter_by(post_id=post.id, user_id=current_user.id).first()
            user_reactions[post.id] = True if reaction else False
        
        # Render the template
        return render_template('community_feed.html', 
                            community=community, 
                            posts=posts, 
                            user_reactions=user_reactions)
    except Exception as e:
        import traceback
        print(f"Error in community_feed: {str(e)}")
        print(traceback.format_exc())
        flash('An error occurred while loading the community feed.', 'danger')
        return redirect(url_for('communities'))

@app.route('/community/<int:community_id>/post', methods=['POST'])
@login_required
def create_post(community_id):
    content = request.form.get('content')
    photos = request.files.getlist('photos')
    videos = request.files.getlist('videos')
    
    if not content:
        flash('Post content cannot be empty', 'danger')
        return redirect(url_for('community_feed', community_id=community_id))

    # Validate file counts
    if len(photos) > 5:
        flash('You can only upload up to 5 photos', 'danger')
        return redirect(url_for('community_feed', community_id=community_id))
    
    if len(videos) > 2:
        flash('You can only upload up to 2 videos', 'danger')
        return redirect(url_for('community_feed', community_id=community_id))

    # Get the community and user's membership
    community = Community.query.get_or_404(community_id)
    member = CommunityMember.query.filter_by(
        community_id=community_id,
        user_id=current_user.id
    ).first_or_404()

    try:
        # Create new post
        post = CommunityPost(
            community_id=community_id,
            author_id=member.id,
            content=content
        )
        db.session.add(post)
        db.session.flush()  # Get the post ID

        # Handle photo uploads
        for photo in photos:
            if photo and photo.filename and allowed_file(photo.filename, ALLOWED_PHOTO_EXT):
                filename = secure_filename(photo.filename)
                photo_path = os.path.join(app.config['UPLOAD_FOLDER'], 'photos', filename)
                photo.save(photo_path)
                
                # Create a new CommunityPostPhoto record
                photo_record = CommunityPostPhoto(
                    post_id=post.id,
                    photo_path=filename
                )
                db.session.add(photo_record)

        # Handle video uploads
        for video in videos:
            if video and video.filename and allowed_file(video.filename, ALLOWED_VIDEO_EXT):
                video_filename = secure_filename(video.filename)
                video_path = os.path.join(app.config['UPLOAD_FOLDER'], 'videos', video_filename)
                video.save(video_path)
                
                # Create a new CommunityPostVideo record
                video_record = CommunityPostVideo(
                    post_id=post.id,
                    video_path=video_filename
                )
                db.session.add(video_record)

        db.session.commit()
        flash('Post created successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error creating post. Please try again.', 'danger')
        print(f"Error creating post: {str(e)}")

    return redirect(url_for('community_feed', community_id=community_id))

@app.route('/community/post/<int:post_id>/react', methods=['POST'])
@login_required
def react_to_post(post_id):
    try:
        reaction_type = request.json.get('reaction_type')
        if not reaction_type:
            return jsonify({'error': 'Reaction type is required'}), 400

        # Get the post
        post = CommunityPost.query.get_or_404(post_id)
        print(f"Processing reaction for post_id={post_id}, reaction_type={reaction_type}")

        # Check if user has already reacted
        existing_reaction = PostReaction.query.filter_by(
            post_id=post_id,
            user_id=current_user.id
        ).first()

        has_reacted = False
        # Handle the reaction (create or toggle)
        if existing_reaction:
            # Toggle the reaction (unlike Instagram, we'll remove it if clicked again)
            db.session.delete(existing_reaction)
            db.session.commit()
            has_reacted = False
            print(f"Removed existing reaction: id={existing_reaction.id}, type={reaction_type}")
        else:
            # Create a new reaction
            reaction = PostReaction(
                post_id=post_id,
                user_id=current_user.id,
                reaction_type=reaction_type
            )
            db.session.add(reaction)
            db.session.commit()
            has_reacted = True
            print(f"Created new reaction: post_id={post_id}, user_id={current_user.id}, type={reaction_type}")

        # Update the post's reaction counts
        post.update_reaction_counts()
        db.session.commit()
        
        print(f"Updated post reaction counts: love={post.love_count}")
        
        # Debug printout of all PostReaction entries for this post
        print('--- PostReaction entries for this post ---')
        for r in PostReaction.query.filter_by(post_id=post_id).all():
            print(f"PostReaction: id={r.id}, post_id={r.post_id}, user_id={r.user_id}, reaction_type={r.reaction_type}")
        
        return jsonify({
            'success': True,
            'has_reacted': has_reacted,
            'love_count': post.love_count
        })
            
    except Exception as e:
        print(f"Unexpected error in react_to_post: {str(e)}")
        db.session.rollback()
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

@app.route('/community/post/<int:post_id>/comment', methods=['POST'])
@login_required
def create_comment(post_id):
    content = request.form.get('content')
    parent_id = request.form.get('parent_id')
    
    # Get the post first
    post = CommunityPost.query.get_or_404(post_id)
    
    if not content:
        flash('Comment cannot be empty', 'danger')
        return redirect(url_for('community_feed', community_id=post.community_id))
    
    # Get user's membership in the community
    member = CommunityMember.query.filter_by(
        community_id=post.community_id,
        user_id=current_user.id
    ).first()
    
    if not member:
        flash('You must be a member of the community to comment.', 'danger')
        return redirect(url_for('community_feed', community_id=post.community_id))
    
    comment = PostComment(
        post_id=post_id,  # Always set post_id explicitly
        author_id=member.id,
        content=content
    )
    
    # Handle parent_id for replies
    if parent_id and parent_id.isdigit():
        parent_comment = PostComment.query.get(int(parent_id))
        if parent_comment and parent_comment.post_id == post_id:
            comment.parent_id = int(parent_id)
        else:
            # Invalid parent_id, ignore it
            comment.parent_id = None
    else:
        comment.parent_id = None
            
    db.session.add(comment)
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'comment': {
                'id': comment.id,
                'content': comment.content,
                'author': {
                    'name': current_user.name
                },
                'created_at': comment.created_at.isoformat()
            }
        })
    
    flash('Comment added successfully!', 'success')
    return redirect(url_for('community_feed', community_id=post.community_id))

@app.route('/community/post/<int:post_id>/comments', methods=['GET'])
@login_required
def load_comments(post_id):
    post = CommunityPost.query.get_or_404(post_id)
    comments = []
    
    for comment in post.comments:
        comment_data = {
            'id': comment.id,
            'author': {
                'name': comment.author.user.name,
                'id': comment.author.user.id
            },
            'content': comment.content,
            'created_at': comment.created_at.isoformat(),
            'replies': []
        }
        
        for reply in comment.replies:
            comment_data['replies'].append({
                'id': reply.id,
                'author': {
                    'name': reply.author.user.name,
                    'id': reply.author.user.id
                },
                'content': reply.content,
                'created_at': reply.created_at.isoformat()
            })
        
        comments.append(comment_data)
    
    return jsonify({
        'success': True,
        'comments': comments
    })

@app.route('/create-checkout-session/<int:package_id>', methods=['POST'])
@login_required
def create_checkout_session(package_id):
    try:
        # Get package details
        package = TripPackage.query.get_or_404(package_id)
        app.logger.info(f"Creating checkout session for package: {package.id} - {package.name}, price: {package.price}")
        
        # Configure Stripe
        stripe.api_key = app.config['STRIPE_SECRET_KEY']
        app.logger.info(f"Using Stripe API key: {app.config['STRIPE_SECRET_KEY'][:10]}...{app.config['STRIPE_SECRET_KEY'][-4:]}")
        
        # Create a checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f"{package.name} - BDT {int(package.price)}",
                            'description': f"Price: BDT {int(package.price)}. {package.description}",
                        },
                        # Use a fixed conversion rate to ensure the exact BDT amount is shown
                        'unit_amount': 100,  # Charge exactly $1 USD as a token amount
                    },
                    'quantity': 1,
                },
            ],
            metadata={
                'package_id': package_id,
                'user_id': current_user.id
            },
            mode='payment',
            success_url=request.host_url + 'payment/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.host_url + 'payment/cancel',
        )
        
        app.logger.info(f"Checkout session created: {checkout_session.id}")
        
        # Create a booking record (unpaid)
        booking = Booking(
            user_id=current_user.id,
            package_id=package_id,
            amount=package.price,
            order_id=checkout_session.id,
            is_paid=False
        )
        db.session.add(booking)
        db.session.commit()
        
        # For XHR requests, return JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'id': checkout_session.id,
                'package_name': package.name,
                'amount': package.price
            })
        
        # For regular form submissions, redirect directly to Stripe
        return redirect(checkout_session.url)
    
    except stripe.error.StripeError as e:
        # Handle Stripe-specific errors
        app.logger.error(f"Stripe error creating checkout session: {str(e)}")
        db.session.rollback()
        flash(f"Payment error: {str(e)}", "danger")
        return redirect(url_for('view_package', package_id=package_id))
    
    except Exception as e:
        app.logger.error(f"Error creating checkout session: {str(e)}")
        db.session.rollback()
        flash(f"An error occurred: {str(e)}", "danger")
        return redirect(url_for('view_package', package_id=package_id))

@app.route('/payment/success')
@login_required
def payment_success():
    session_id = request.args.get('session_id')
    
    if not session_id:
        flash('Invalid payment session', 'danger')
        return redirect(url_for('dashboard'))
    
    try:
        # Configure Stripe
        stripe.api_key = app.config['STRIPE_SECRET_KEY']
        
        # Retrieve the session
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        
        # Update booking record
        booking = Booking.query.filter_by(order_id=session_id).first()
        
        if booking and checkout_session.payment_status == 'paid':
            booking.payment_id = checkout_session.payment_intent
            booking.is_paid = True
            db.session.commit()
            
            # Get package details for display
            package = TripPackage.query.get(booking.package_id)
            package_name = package.name if package else "Unknown Package"
            package_price = package.price if package else 0
            
            flash(f'Payment successful! Your booking for {package_name} (BDT {int(package_price)}) is confirmed.', 'success')
        else:
            flash('Payment verification failed. Please contact support.', 'danger')
        
        return redirect(url_for('dashboard'))
    
    except Exception as e:
        app.logger.error(f"Error processing payment success: {str(e)}")
        flash('Payment verification failed. Please contact support.', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/payment/cancel')
@login_required
def payment_cancel():
    flash('Payment was cancelled.', 'warning')
    return redirect(url_for('dashboard'))

@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        # Configure Stripe
        stripe.api_key = app.config['STRIPE_SECRET_KEY']
        
        event = stripe.Webhook.construct_event(
            payload, sig_header, app.config['STRIPE_WEBHOOK_SECRET']
        )
        
        # Handle the checkout.session.completed event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            
            # Update booking record
            booking = Booking.query.filter_by(order_id=session.id).first()
            
            if booking and session.payment_status == 'paid':
                booking.payment_id = session.payment_intent
                booking.is_paid = True
                db.session.commit()
                
        return jsonify(success=True)
    
    except Exception as e:
        app.logger.error(f"Webhook error: {str(e)}")
        return jsonify(success=False), 400

@app.route('/user/<int:user_id>')
@login_required
def view_user_profile(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('user_profile.html', user=user)

@app.route('/follow/<int:user_id>', methods=['POST'])
@login_required
def follow_user(user_id):
    user_to_follow = User.query.get_or_404(user_id)
    if user_to_follow == current_user:
        flash('You cannot follow yourself', 'danger')
        return redirect(url_for('view_user_profile', user_id=user_id))
    
    follow = UserFollow.query.filter_by(follower_id=current_user.id, followed_id=user_id).first()
    if follow:
        db.session.delete(follow)
        db.session.commit()
        flash('You have unfollowed this user', 'success')
    else:
        follow = UserFollow(follower_id=current_user.id, followed_id=user_id)
        db.session.add(follow)
        db.session.commit()
        flash('You are now following this user', 'success')
    
    return redirect(url_for('view_user_profile', user_id=user_id))

@app.route('/user/<int:user_id>/followers')
@login_required
def user_followers(user_id):
    user = User.query.get_or_404(user_id)
    followers = UserFollow.query.filter_by(followed_id=user_id).all()
    follower_users = [follow.follower for follow in followers]
    return render_template('user_followers.html', user=user, followers=follower_users)

@app.route('/user/<int:user_id>/following')
@login_required
def user_following(user_id):
    user = User.query.get_or_404(user_id)
    following = UserFollow.query.filter_by(follower_id=user_id).all()
    following_users = [follow.followed for follow in following]
    return render_template('user_following.html', user=user, following=following_users)

@app.route('/api/follow/<int:user_id>', methods=['POST'])
@login_required
def api_follow_user(user_id):
    user_to_follow = User.query.get_or_404(user_id)
    if user_to_follow == current_user:
        return jsonify({'success': False, 'message': 'You cannot follow yourself'}), 400
    
    is_following = current_user.is_following(user_to_follow)
    
    if is_following:
        current_user.unfollow(user_to_follow)
        db.session.commit()
        return jsonify({
            'success': True, 
            'following': False,
            'followers_count': user_to_follow.followers_count()
        })
    else:
        current_user.follow(user_to_follow)
        db.session.commit()
        return jsonify({
            'success': True, 
            'following': True,
            'followers_count': user_to_follow.followers_count()
        })

@app.route('/community/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = CommunityPost.query.get_or_404(post_id)
    
    # Check if the current user is the author of the post
    if post.author.user_id != current_user.id:
        flash('You can only delete your own posts.', 'danger')
        return redirect(url_for('community_feed', community_id=post.community_id))
    
    # Delete associated photos and videos first
    for photo in post.photos:
        try:
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], 'photos', photo.photo_path)
            if os.path.exists(photo_path):
                os.remove(photo_path)
        except Exception as e:
            app.logger.error(f"Error deleting photo file: {str(e)}")
        db.session.delete(photo)
    
    for video in post.videos:
        try:
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], 'videos', video.video_path)
            if os.path.exists(video_path):
                os.remove(video_path)
        except Exception as e:
            app.logger.error(f"Error deleting video file: {str(e)}")
        db.session.delete(video)
    
    # Delete all comments and reactions
    PostComment.query.filter_by(post_id=post.id).delete()
    PostReaction.query.filter_by(post_id=post.id).delete()
    
    # Finally delete the post
    db.session.delete(post)
    db.session.commit()
    
    flash('Your post has been deleted.', 'success')
    return redirect(url_for('community_feed', community_id=post.community_id))

@app.route('/community/post/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    post = CommunityPost.query.get_or_404(post_id)
    existing_reaction = PostReaction.query.filter_by(post_id=post_id, user_id=current_user.id).first()
    
    if existing_reaction:
        # Unlike the post
        db.session.delete(existing_reaction)
    else:
        # Like the post
        reaction = PostReaction(post_id=post_id, user_id=current_user.id, reaction_type='love')
        db.session.add(reaction)
    
    db.session.commit()
    post.update_reaction_counts()
    db.session.commit()
    
    return redirect(url_for('community_feed', community_id=post.community_id))

@app.route('/community/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    post = CommunityPost.query.get_or_404(post_id)
    content = request.form.get('content')
    
    if not content:
        flash('Comment cannot be empty.', 'danger')
        return redirect(url_for('community_feed', community_id=post.community_id))
    
    # Get the community member record for the current user
    member = CommunityMember.query.filter_by(
        community_id=post.community_id,
        user_id=current_user.id
    ).first()
    
    if not member:
        flash('You must be a member of the community to comment.', 'danger')
        return redirect(url_for('community_feed', community_id=post.community_id))
    
    comment = PostComment(
        post_id=post_id,
        author_id=member.id,
        content=content
    )
    
    db.session.add(comment)
    db.session.commit()
    
    return redirect(url_for('community_feed', community_id=post.community_id))

@app.route('/package/image/<int:package_id>')
def get_package_image(package_id):
    package = TripPackage.query.get_or_404(package_id)
    if not package.image_data:
        return send_from_directory('static', 'images/default-package.jpg')
    return send_file(
        io.BytesIO(package.image_data),
        mimetype=package.image_mimetype
    )

# Add datetime to all templates
@app.context_processor
def utility_processor():
    return dict(now=datetime.now())

# Initialize Google OAuth client
client = WebApplicationClient(Config.GOOGLE_CLIENT_ID)

# Function to get Google provider configuration
def get_google_provider_cfg():
    try:
        return requests.get(Config.GOOGLE_DISCOVERY_URL, timeout=5).json()
    except Exception as e:
        print(f"Error getting Google provider config: {str(e)}")
        return None

@app.route('/register/google')
def register_with_google():
    # Set a session flag to indicate this is a registration, not a login
    session['registering'] = True
    # Redirect to Google OAuth flow
    return redirect(url_for('google_login'))

@app.route('/login/google')
def google_login():
    print(f"==== GOOGLE LOGIN ROUTE ACCESSED ====")
    
    # Use client library for a more reliable auth flow
    google_provider_cfg = get_google_provider_cfg()
    if not google_provider_cfg:
        flash('Error connecting to Google', 'danger')
        return redirect(url_for('login'))
    
    auth_endpoint = google_provider_cfg["authorization_endpoint"]
    print(f"Authorization endpoint: {auth_endpoint}")
    
    # Dynamically determine the callback URL based on the host URL of the current request
    callback_url = url_for('google_callback', _external=True)
    print(f"Callback URL: {callback_url}")
    
    # Create authorization URL
    request_uri = client.prepare_request_uri(
        auth_endpoint,
        redirect_uri=callback_url,
        scope=["openid", "email", "profile"],
        access_type="offline",
        prompt="consent"
    )
    
    print(f"Request URI: {request_uri}")
    print(f"==== REDIRECTING TO GOOGLE AUTH ====")
    return redirect(request_uri)

@app.route('/login/google/callback')
def google_callback():
    print(f"==== GOOGLE CALLBACK ACCESSED ====")
    # Get authorization code Google sent back
    code = request.args.get("code")
    print(f"Auth code present: {code is not None}")
    
    if not code:
        flash("Authentication failed", "danger")
        return redirect(url_for("login"))
    
    try:
        # Get token endpoint
        google_provider_cfg = get_google_provider_cfg()
        if not google_provider_cfg:
            flash("Error connecting to Google", "danger")
            return redirect(url_for("login"))
        
        token_endpoint = google_provider_cfg["token_endpoint"]
        print(f"Token endpoint: {token_endpoint}")
        
        # Dynamically determine the callback URL based on the host URL of the current request
        callback_url = url_for('google_callback', _external=True)
        print(f"Callback URL: {callback_url}")
        print(f"Request URL: {request.url}")
        
        token_url, headers, body = client.prepare_token_request(
            token_endpoint,
            authorization_response=request.url,
            redirect_url=callback_url,
            code=code
        )
        
        print(f"Token URL: {token_url}")
        print(f"Token headers: {headers}")
        print(f"Token body length: {len(body) if body else 0}")
        
        # Exchange code for tokens
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(Config.GOOGLE_CLIENT_ID, Config.GOOGLE_CLIENT_SECRET),
        )
        
        print(f"Token response status: {token_response.status_code}")
        print(f"Token response body: {token_response.text[:100]}")  # Print first 100 chars
        
        if token_response.status_code != 200:
            print(f"Token error: {token_response.text}")
            flash(f"Authentication error: Invalid token response ({token_response.status_code})", "danger")
            return redirect(url_for("login"))
        
        # Parse tokens
        client.parse_request_body_response(json.dumps(token_response.json()))
        
        # Get user info from Google
        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)
        
        print(f"User info response status: {userinfo_response.status_code}")
        print(f"User info response: {userinfo_response.text[:100]}")  # Print first 100 chars
        
        # Process Google userinfo response
        if userinfo_response.json().get("email_verified"):
            google_id = userinfo_response.json()["sub"]
            email = userinfo_response.json()["email"]
            name = userinfo_response.json().get("name", email.split("@")[0])
            
            print(f"Google OAuth info - ID: {google_id}, Email: {email}, Name: {name}")
            
            # First, try to find user by Google ID (most reliable)
            user_by_google_id = User.query.filter_by(google_id=google_id).first()
            
            # Also try to find by email as fallback
            user_by_email = User.query.filter_by(email=email).first()
            
            # Case 1: User found by Google ID - Definitely a returning Google user
            if user_by_google_id:
                print(f"User found by Google ID: {user_by_google_id.id}")
                login_user(user_by_google_id)
                flash(f"Welcome back, {user_by_google_id.name}!", "success")
                return redirect(url_for("dashboard"))
            
            # Case 2: User found by email but Google ID is not set
            elif user_by_email and not hasattr(user_by_email, 'google_id'):
                print(f"User found by email but no Google ID: {user_by_email.id}")
                # Add google_id attribute to the User model first
                user_by_email.google_id = google_id
                db.session.commit()
                login_user(user_by_email)
                flash(f"Welcome back, {user_by_email.name}! Your account has been linked with Google.", "success")
                return redirect(url_for("dashboard"))
            
            # Case 3: No existing user - this is a registration attempt with Google
            elif 'registering' in session:
                # This is a new registration with Google
                session.pop('registering', None)
                new_user = User(
                    email=email,
                    name=name,
                    age=25,
                    google_id=google_id,
                    password=None,
                    dark_mode=False
                )
                db.session.add(new_user)
                db.session.commit()
                print(f"New user created with Google: {new_user.id}")
                login_user(new_user)
                flash(f"Welcome {name}! Your account has been created using Google authentication.", "success")
                return redirect(url_for("dashboard"))
            
            # Case 4: User tried to log in with Google but hasn't registered yet
            else:
                flash("You haven't registered with this Google account yet. Please register first.", "warning")
                return redirect(url_for("register"))
        else:
            flash("Google authentication failed - email not verified", "danger")
            return redirect(url_for("login"))
    
    except Exception as e:
        print(f"Google authentication error: {str(e)}")
        flash(f"Authentication error: {str(e)}", "danger")
        return redirect(url_for("login"))

@app.route('/local-events', methods=['GET'])
@login_required
def local_events():
    # Get filter parameters from query string
    location = request.args.get('location', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    event_type = request.args.get('event_type', '')
    favorites_only = request.args.get('favorites_only', '') == 'true'
    page = request.args.get('page', 1, type=int)
    
    # Start with all events
    query = LocalEvent.query
    
    # Apply favorites filter if requested
    if favorites_only:
        # Get IDs of all events favorited by the current user
        favorited_event_ids = [favorite.event_id for favorite in current_user.favorited_events]
        query = query.filter(LocalEvent.id.in_(favorited_event_ids))
    
    # Apply location filter if provided
    if location:
        query = query.filter(LocalEvent.location.ilike(f'%{location}%'))
    
    # Apply date filters if provided
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(LocalEvent.event_date >= start_date_obj)
        except ValueError:
            flash('Invalid start date format. Please use YYYY-MM-DD format.', 'danger')
    
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
            # Add one day to include the end date fully
            end_date_obj = end_date_obj + timedelta(days=1)
            query = query.filter(LocalEvent.event_date < end_date_obj)
        except ValueError:
            flash('Invalid end date format. Please use YYYY-MM-DD format.', 'danger')
    
    # Apply event type filter if provided
    if event_type:
        query = query.filter(LocalEvent.event_type == event_type)
    
    # Order by event date
    query = query.order_by(LocalEvent.event_date)
    
    # Paginate results
    events = query.paginate(page=page, per_page=9, error_out=False)
    
    return render_template('local_events.html', events=events, title='Local Events')

@app.route('/events/<int:event_id>/details')
@login_required
def event_details(event_id):
    event = LocalEvent.query.get_or_404(event_id)
    
    # Format the event data for JSON response
    event_data = {
        'id': event.id,
        'title': event.title,
        'description': event.description,
        'detailed_description': event.detailed_description,
        'location': event.location,
        'event_date': event.event_date.isoformat(),
        'event_type': event.event_type
    }
    
    return jsonify({
        'success': True,
        'event': event_data
    })

@app.route('/events/<int:event_id>/favorite', methods=['POST'])
@login_required
def favorite_event(event_id):
    event = LocalEvent.query.get_or_404(event_id)
    
    # Check if already favorited
    existing = FavoritedEvent.query.filter_by(
        user_id=current_user.id,
        event_id=event_id
    ).first()
    
    if existing:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': False,
                'message': 'You have already favorited this event'
            })
        flash('You have already favorited this event', 'info')
        return redirect(url_for('local_events'))
    
    # Create new favorite
    favorite = FavoritedEvent(
        user_id=current_user.id,
        event_id=event_id
    )
    db.session.add(favorite)
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'message': 'Event added to favorites'
        })
    
    flash('Event added to favorites', 'success')
    return redirect(url_for('local_events'))

@app.route('/events/<int:event_id>/unfavorite', methods=['POST'])
@login_required
def unfavorite_event(event_id):
    favorite = FavoritedEvent.query.filter_by(
        user_id=current_user.id,
        event_id=event_id
    ).first_or_404()
    
    db.session.delete(favorite)
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'message': 'Event removed from favorites'
        })
    
    flash('Event removed from favorites', 'success')
    return redirect(url_for('local_events'))


@app.route('/restaurants', methods=['GET', 'POST'])
def restaurants():
    if request.method == 'POST':
        location = request.form.get('location')
        lat, lon = get_coordinates(location)
        if lat and lon:
            restaurants = get_nearby_restaurants(lat, lon)
            return render_template('restaurants.html', restaurants=restaurants, location=location)
    return render_template('restaurants.html')


def get_coordinates(location):
    url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json"
    headers = {'User-Agent': 'TravellingInBangladeshApp'}
    response = requests.get(url, headers=headers)
    data = response.json()
    if data:
        return float(data[0]['lat']), float(data[0]['lon'])
    return None, None

def get_nearby_restaurants(lat, lon):
    overpass_url = "https://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    node(around:1000,{lat},{lon})["amenity"="restaurant"];
    out;
    """
    response = requests.post(overpass_url, data={"data": query})
    data = response.json()
    restaurants = []

    for element in data['elements']:
        name = element['tags'].get('name', 'Unnamed Restaurant')
        place_lat = element['lat']
        place_lon = element['lon']
        map_url = f"https://www.google.com/maps?q={place_lat},{place_lon}"

        restaurants.append({
            'name': name,
            'lat': place_lat,
            'lon': place_lon,
            'map_url': map_url
        })
    return restaurants

@app.route('/hotels', methods=['GET', 'POST'])
def hotels():
    if request.method == 'POST':
        location = request.form.get('location')
        lat, lon = get_coordinates(location)
        if lat and lon:
            hotels = get_nearby_hotels(lat, lon)
            return render_template('hotels.html', hotels=hotels, location=location)
    return render_template('hotels.html')

def get_nearby_hotels(lat, lon):
    overpass_url = "https://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    node(around:1000,{lat},{lon})["tourism"="hotel"];
    out;
    """
    response = requests.post(overpass_url, data={"data": query})
    data = response.json()
    hotels = []

    for element in data['elements']:
        name = element['tags'].get('name', 'Unnamed Hotel')
        place_lat = element['lat']
        place_lon = element['lon']
        map_url = f"https://www.google.com/maps?q={place_lat},{place_lon}"

        hotels.append({
            'name': name,
            'lat': place_lat,
            'lon': place_lon,
            'map_url': map_url
        })
    return hotels

@app.route('/packing_checklist', methods=['GET', 'POST'])
@login_required
def packing_checklist():
    # Define the checklist items
    checklist = {
        "Essentials": [
            "Travel tickets (plane/train/bus)",
            "Wallet with cash & cards",
            "Phone + charger",
            "Itinerary & booking confirmations",
            "Emergency contact info"
        ],
        "Clothing": [
            "T-shirts / Tops",
            "Pants / Shorts",
            "Undergarments",
            "Sleepwear",
            "Jacket / Sweater",
            "Raincoat / Umbrella",
            "Footwear (walking shoes, sandals)",
            "Hat / Cap / Sunglasses",
            "Swimwear (if needed)"
        ],
        "Toiletries": [
            "Toothbrush + Toothpaste",
            "Soap / Body wash",
            "Shampoo / Conditioner",
            "Deodorant",
            "Razor / Shaving kit",
            "Hairbrush / Comb",
            "Towel",
            "Wet wipes / Tissues",
            "Sanitizer",
            "Sunscreen / Lip balm",
            "Sanitary napkins"
        ],
        "Health & Safety": [
            "Medications (prescribed & common)",
            "First-aid kit (band-aids, antiseptic, etc.)",
            "Insect repellent",
            "Face masks (if needed)",
            "Water bottle"
        ],
        "Electronics": [
            "Phone + Power bank",
            "Earphones / Headphones",
            "Camera (if using)"
        ],
        "Other Handy Items": [
            "Backpack / Day bag",
            "Locks for bags",
            "Snacks / Energy bars",
            "Guidebook / Offline maps",
            "Notebook & pen",
            "Laundry bag / Ziplocks"
        ]
    }

    return render_template('packing_checklist.html', checklist=checklist)

def create_booking_expense(booking):
    """Automatically create expense record from booking"""
    try:
        details = json.loads(booking.details)
        amount = 0.0
        
        # Extract amount based on booking type
        match booking.booking_type:
            case 'flight':
                amount = float(details.get('price', 0)) 
                if 'tax' in details:  # Handle additional costs
                    amount += float(details['tax'])
            case 'hotel':
                amount = float(details.get('total_cost', 0))
                if 'service_charge' in details:
                    amount += float(details['service_charge'])
            case 'bus' | 'train':
                amount = float(details.get('fare', 0)) * int(details.get('passengers', 1))
            case 'car':
                base_fare = float(details.get('daily_rate', 0))
                days = int(details.get('rental_days', 1))
                amount = base_fare * days
        
        if amount > 0:
            expense = Expense(
                user_id=booking.user_id,
                category=f"Travel - {booking.booking_type.title()}",
                description=f"{booking.booking_type.title()} Booking",
                amount=amount,
                date=date.today(),  # Use booking date if available
                is_automatic=True
            )
            db.session.add(expense)
            db.session.commit()
            
    except KeyError as ke:
        app.logger.error(f"Missing key in booking details: {str(ke)}")
    except ValueError as ve:
        app.logger.error(f"Invalid value format: {str(ve)}")
    except Exception as e:
        app.logger.error(f"Error creating automatic expense: {str(e)}")
        db.session.rollback()

# ------------------- EMERGENCY CONTACTS -------------------
@app.route('/emergency')
@login_required
def emergency():
    contacts = EmergencyContact.query.filter_by(user_id=current_user.id).all()
    return render_template('emergency.html', contacts=contacts, api_key=GOOGLE_API_KEY)

@app.route('/add_contact', methods=['GET', 'POST'])
@login_required
def add_contact():
    form = EmergencyContactForm()
    if form.validate_on_submit():
        contact = EmergencyContact(
            user_id=current_user.id,
            name=form.name.data,
            relationship=form.relationship.data,
            phone=form.phone.data,
            alternate_phone=form.alternate_phone.data
        )
        db.session.add(contact)
        db.session.commit()
        flash('Contact added successfully!', 'success')
        return redirect(url_for('emergency'))
    return render_template('add_emergency.html', form=form)

@app.route('/delete_contact/<int:contact_id>', methods=['POST'])
@login_required
def delete_contact(contact_id):
    contact = EmergencyContact.query.get_or_404(contact_id)
    if contact.user_id != current_user.id:
        flash("Unauthorized access", "danger")
        return redirect(url_for('emergency'))
    db.session.delete(contact)
    db.session.commit()
    flash('Contact deleted successfully', 'success')
    return redirect(url_for('emergency'))

from flask import render_template, request
import requests

def get_nearby_places(lat, lon, amenity_type, radius=1000):
    """Generic function to get nearby places using Overpass API"""
    try:
        overpass_url = "https://overpass-api.de/api/interpreter"
        query = f"""
        [out:json];
        (
            node["amenity"="{amenity_type}"](around:{radius},{lat},{lon});
            way["amenity"="{amenity_type}"](around:{radius},{lat},{lon});
            relation["amenity"="{amenity_type}"](around:{radius},{lat},{lon});
        );
        out center;
        """
        response = requests.post(overpass_url, data={"data": query})
        data = response.json()
        
        places = []
        for element in data.get('elements', []):
            name = element.get('tags', {}).get('name', f'Unnamed {amenity_type.title()}')
            address = element.get('tags', {}).get('addr:street', 'Address not available')
            
            # Get coordinates
            if 'lat' in element and 'lon' in element:
                plat, plon = element['lat'], element['lon']
            elif 'center' in element:
                plat, plon = element['center']['lat'], element['center']['lon']
            else:
                continue
                
            map_url = f"https://www.google.com/maps?q={plat},{plon}"
            
            places.append({
                'name': name,
                'address': address,
                'lat': plat,
                'lon': plon,
                'map_url': map_url
            })
        
        return places[:10]  # Return top 10 results
        
    except Exception as e:
        print(f"Error fetching {amenity_type} data: {str(e)}")
        return []

@app.route('/hospitals', methods=['GET', 'POST'])
@login_required
def hospitals():
    hospitals = []
    location = None
    error = None
    
    if request.method == 'POST':
        location = request.form.get('location', '').strip()
        if location:
            # First get coordinates from location name
            lat, lon = get_coordinates(location)
            if lat and lon:
                hospitals = get_nearby_places(lat, lon, 'hospital')
                if not hospitals:
                    error = "No hospitals found in this area"
            else:
                error = "Could not find coordinates for this location"
        else:
            error = "Please enter a location"
    
    return render_template('hospitals.html', 
                         hospitals=hospitals,
                         location=location,
                         error=error,
                         api_key=GOOGLE_API_KEY)

@app.route('/police', methods=['GET', 'POST'])
@login_required
def police():
    police_stations = []
    location = None
    error = None
    
    if request.method == 'POST':
        location = request.form.get('location', '').strip()
        if location:
            # First get coordinates from location name
            lat, lon = get_coordinates(location)
            if lat and lon:
                police_stations = get_nearby_places(lat, lon, 'police')
                if not police_stations:
                    error = "No police stations found in this area"
            else:
                error = "Could not find coordinates for this location"
        else:
            error = "Please enter a location"
    
    return render_template('police.html', 
                         police_stations=police_stations,
                         location=location,
                         error=error,
                         api_key=GOOGLE_API_KEY)

def get_coordinates(location):
    """Get coordinates using Nominatim (OpenStreetMap)"""
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json"
        headers = {'User-Agent': 'Ghoori.com'}  # Required by Nominatim policy
        response = requests.get(url, headers=headers)
        data = response.json()
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
        return None, None
    except Exception as e:
        print(f"Geocoding error: {str(e)}")
        return None, None


@app.route('/house')
def house():
    return render_template('home.html')

# Fixed prices for different services
PRICES = {
    'flight': {
        'economy': {
            'biman': 5000,
            'us-bangla': 4500,
            'novoair': 4800
        },
        'business': {
            'biman': 12000,
            'us-bangla': 10000,
            'novoair': 11000
        }
    },
    'bus': {
        'ac': 1500,
        'non-ac': 800
    },
    'train': {
        'shovon': {
            'padma': 400,
            'subarna': 450,
            'mohanagar': 400
        },
        'first': {
            'padma': 800,
            'subarna': 850,
            'mohanagar': 800
        },
        'sleeper': {
            'padma': 1200,
            'subarna': 1250,
            'mohanagar': 1200
        }
    },
    'car': {
        'sedan': 5000,
        'suv': 8000,
        'van': 10000
    },
    'hotel': {
        'pan-pacific': {'base': 15000, 'double': 1.3, 'suite': 1.6},
        'le-meridien': {'base': 12000, 'double': 1.3, 'suite': 1.6},
        'radisson': {'base': 10000, 'double': 1.3, 'suite': 1.6},
        'westin': {'base': 13000, 'double': 1.3, 'suite': 1.6}
    }
}

@app.route('/book/<transport_type>', methods=['GET', 'POST'])
@login_required
def book(transport_type):
    if transport_type not in ['flight', 'bus', 'train', 'car']:
        abort(404)
        
    emoji_map = {
        'flight': '✈️',
        'bus': '🚌',
        'train': '🚆',
        'car': '🚗'
    }
    
    if request.method == 'POST':
        try:
            # Get form data
            source = request.form.get('source')
            destination = request.form.get('destination')
            date_str = request.form.get('date')
            time_str = request.form.get('time')
            passengers = int(request.form.get('passengers', 1))
            
            if not all([source, destination, date_str, time_str, passengers]):
                flash('Please fill in all fields', 'error')
                return render_template(
                    'book_transport.html',
                    transport_type=transport_type,
                    emoji=emoji_map[transport_type],
                    today=date.today().strftime('%Y-%m-%d')
                )
            
            # Calculate fare based on transport type and distance
            base_rates = {
                'flight': 5000,
                'bus': 800,
                'train': 1200,
                'car': 2000
            }
            
            # Simple fare calculation (you can make this more complex)
            base_fare = base_rates[transport_type]
            total_amount = base_fare * passengers
            
            # Create booking
            booking = TransportBooking(
                user_id=current_user.id,
                booking_type=transport_type,
                source=source,
                destination=destination,
                date=datetime.strptime(date_str, '%Y-%m-%d').date(),
                time=datetime.strptime(time_str, '%H:%M').time(),
                passengers=passengers,
                total_amount=total_amount,
                status='confirmed'
            )
            
            db.session.add(booking)
            
            # Create expense record
            expense = Expense(
                user_id=current_user.id,
                category='Transportation',
                description=f'{transport_type.title()} booking from {source} to {destination}',
                amount=total_amount,
                date=datetime.now().date()
            )
            db.session.add(expense)
            
            db.session.commit()
            
            flash(f'{transport_type.title()} booked successfully!', 'success')
            return redirect(url_for('booking_confirmation', booking_id=booking.booking_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Booking failed: {str(e)}', 'error')
            return render_template(
                'book_transport.html',
                transport_type=transport_type,
                emoji=emoji_map[transport_type],
                today=date.today().strftime('%Y-%m-%d')
            )
    
    return render_template(
        'book_transport.html',
        transport_type=transport_type,
        emoji=emoji_map[transport_type],
        today=date.today().strftime('%Y-%m-%d')
    )

@app.route('/booking_confirmation/<booking_id>')
@login_required
def booking_confirmation(booking_id):
    booking = TransportBooking.query.filter_by(booking_id=booking_id).first_or_404()
    
    if booking.user_id != current_user.id:
        abort(403)
    
    # Format the date and time
    booking.formatted_date = booking.date.strftime('%B %d, %Y')
    booking.formatted_time = booking.time.strftime('%I:%M %p')
    
    return render_template('booking_confirmation.html', booking=booking)

@app.route('/download_ticket/<booking_id>')
@login_required
def download_ticket(booking_id):
    booking = TransportBooking.query.filter_by(booking_id=booking_id).first_or_404()
    if booking.user_id != current_user.id:
        abort(403)
        
    # Generate a simple text ticket (you can make this fancier later)
    ticket_text = f"""
    ==========================================
    {booking.booking_type.upper()} TICKET
    ==========================================
    Booking ID: {booking.booking_id}
    From: {booking.source}
    To: {booking.destination}
    Date: {booking.date.strftime('%B %d, %Y')}
    Time: {booking.time.strftime('%I:%M %p')}
    Passengers: {booking.passengers}
    Total Amount: ৳{booking.total_amount}
    Status: {booking.status.upper()}
    ==========================================
    """
    
    # Create a text file response
    response = make_response(ticket_text)
    response.headers['Content-Type'] = 'text/plain'
    response.headers['Content-Disposition'] = f'attachment; filename={booking.booking_id}_ticket.txt'
    
    return response

@app.route('/confirmation/<int:booking_id>')
@login_required
def confirmation(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.user_id != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('home'))
    
    details = json.loads(booking.details)
    
    # Format dates for better display
    for key, value in details.items():
        if isinstance(value, str) and value.startswith('20'):
            try:
                date = datetime.strptime(value, '%Y-%m-%d').strftime('%B %d, %Y')
                details[key] = date
            except ValueError:
                pass
    
    # Format total price with currency
    if 'total_price' in details:
        details['total_price'] = f'৳{details["total_price"]:,.2f}'
    
    # Get booking type specific details
    booking_details = {
        'flight': {
            'title': 'Flight Booking Confirmation',
            'icon': 'fa-plane',
            'from_label': 'Origin',
            'to_label': 'Destination'
        },
        'bus': {
            'title': 'Bus Booking Confirmation',
            'icon': 'fa-bus',
            'from_label': 'Origin',
            'to_label': 'Destination'
        },
        'train': {
            'title': 'Train Booking Confirmation',
            'icon': 'fa-train',
            'from_label': 'From',
            'to_label': 'To'
        },
        'car': {
            'title': 'Car Rental Confirmation',
            'icon': 'fa-car',
            'from_label': 'Pickup Location',
            'to_label': 'Drop Location'
        },
        'hotel': {
            'title': 'Hotel Booking Confirmation',
            'icon': 'fa-hotel',
            'location_label': 'City',
            'duration_label': 'Stay Duration'
        }
    }
    
    type_details = booking_details.get(booking.booking_type, {})
    
    return render_template('confirmation.html',
                           booking=booking,
                           details=details,
                           type_details=type_details)

class ExpenseForm(FlaskForm):
    category = SelectField('Category', choices=[
        ('food', 'Food & Dining'),
        ('transportation', 'Transportation'),
        ('accommodation', 'Accommodation'),
        ('activities', 'Activities & Entertainment'),
        ('shopping', 'Shopping'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired(), Length(max=200)])
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0)])
    date = DateField('Date', validators=[DataRequired()], default=datetime.today)
    submit = SubmitField('Add Expense')

# ------------------- EXPENSE TRACKER -------------------
@app.route('/expenses', methods=['GET', 'POST'])
@login_required
def expenses():
    form = ExpenseForm()
    
    # Handle form submission
    if form.validate_on_submit():
        try:
            # Print form data for debugging
            print(f"Form data: category={form.category.data}, description={form.description.data}, amount={form.amount.data}, date={form.date.data}")
            
            expense = Expense(
                user_id=current_user.id,
                category=form.category.data,
                description=form.description.data,
                amount=form.amount.data,
                date=form.date.data,
                is_automatic=False
            )
            db.session.add(expense)
            db.session.commit()
            flash('Expense added successfully!', 'success')
            return redirect(url_for('expenses'))
        except Exception as e:
            db.session.rollback()
            # Log the full error for debugging
            app.logger.error(f"Error saving expense: {str(e)}")
            flash('Error saving expense. Please try again.', 'danger')

    # Get all expenses
    expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).all()
    total = sum(expense.amount for expense in expenses)
    
    return render_template('expenses.html', 
                         expenses=expenses, 
                         total=total, 
                         form=form)

@app.route('/delete_expense/<int:expense_id>', methods=['POST'])
@login_required
def delete_expense(expense_id):
    try:
        expense = Expense.query.get_or_404(expense_id)
        if expense.user_id != current_user.id:
            flash("Unauthorized: You can only delete your own expenses", "danger")
            return redirect(url_for('expenses'))
            
        db.session.delete(expense)
        db.session.commit()
        flash('Expense deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting expense. Please try again.', 'danger')
        app.logger.error(f"Delete expense error: {str(e)}")
    
    return redirect(url_for('expenses'))

# ------------------- AUTOMATIC EXPENSE TRACKING -------------------
@app.route('/create_booking_expense', methods=['POST'])
@login_required
# Automatically create expense record from booking
def create_booking_expense(booking):
    try:
        # Create expense record
        expense = Expense(
            user_id=booking.user_id,
            category='transportation' if booking.booking_type in ['flight', 'bus', 'train', 'car'] else 'accommodation',
            description=f'{booking.booking_type.capitalize()} booking',
            amount=booking.amount,
            date=datetime.now().date(),
            is_automatic=True
        )
        db.session.add(expense)
        db.session.commit()
        return True
    except Exception as e:
        print(f"Error creating booking expense: {str(e)}")
        return False

def get_ai_response(message):
    """Provide links to free AI chat services with clickable HTML"""
    return (
        "I apologize, but I'm currently not able to provide direct responses. "
        "However, you can get answers to your travel questions using these free AI chat services:<br><br>"
        "1. <a href='https://claude.ai'>Claude AI</a> - Powerful AI assistant by Anthropic<br>"
        "2. <a href='https://www.perplexity.ai'>Perplexity AI</a> - AI search engine with chat<br>"
        "3. <a href='https://you.com'>You.com</a> - Conversational AI platform<br>"
        "4. <a href='https://huggingface.co/chat'>HuggingChat</a> - Free chat by Hugging Face<br><br>"
        "These services are available 24/7 and can help you with any travel-related questions. "
        "Simply click any of the links above to start chatting!"
    )

def get_fallback_response(message):
    """Fallback responses when API fails"""
    message = message.lower()
    
    if any(word in message for word in ['hello', 'hi', 'hey']):
        return "Hello! I'm here to help with your travel needs. What can I assist you with?"
        
    if 'book' in message:
        return "I can help you book flights, buses, trains, or hotels. What type of booking are you interested in?"
        
    if 'expense' in message:
        return "I can help you track your travel expenses. Would you like to add an expense or view your spending summary?"
        
    if any(word in message for word in ['place', 'visit', 'attraction']):
        return "I can recommend great places to visit. Are you interested in tourist attractions, restaurants, or hotels?"
        
    return "I'm here to help with travel planning, bookings, expenses, and recommendations. What would you like to know more about?"

@app.route('/chatbot', methods=['POST'])
@login_required
def chatbot():
    # Validate input
    user_message = request.form.get('message', '').strip()
    if not user_message:
        return jsonify({'response': "Please enter a message"}), 400
    if len(user_message) > 1000:
        return jsonify({'response': "Message too long. Please keep it under 1000 characters."}), 400

    try:
        # Get AI response
        bot_response = get_ai_response(user_message)
        
        try:
            # Save to database
            chat = ChatMessage(
                user_id=current_user.id,
                message=user_message,
                response=bot_response,
                timestamp=datetime.utcnow()
            )
            db.session.add(chat)
            db.session.commit()
        except Exception as e:
            print(f"Error saving chat message: {str(e)}")
            # Continue even if saving fails
        
        return jsonify({'response': bot_response})
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'response': "I apologize, but I'm having trouble right now. I'll be back to help you soon!"}), 500



if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app.run(debug=True, port=5001)
