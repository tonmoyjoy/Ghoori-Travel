from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, IntegerField, FileField, FloatField, DateTimeField, MultipleFileField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional
from datetime import datetime, date
from flask_wtf.file import FileAllowed
from wtforms import ValidationError
from flask_login import current_user
from models import User
from werkzeug.security import check_password_hash
from werkzeug.datastructures import FileStorage

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=13, max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

    def validate(self):
        if not super(LoginForm, self).validate():
            return False
        
        user = User.query.filter_by(email=self.email.data).first()
        if user is None:
            self.email.errors.append('Email does not exist.')
            return False
        
        if not check_password_hash(user.password, self.password.data):
            self.password.errors.append('Password is incorrect.')
            return False
        
        return True

class TripPreferencesForm(FlaskForm):
    budget_range = SelectField('Budget Range (in Taka ৳)',
        choices=[
            ('budget', '৳5,000 - ৳15,000'),
            ('mid_range', '৳15,000 - ৳30,000'),
            ('luxury', '৳30,000 - ৳50,000'),
            ('ultra_luxury', '৳50,000+')
        ],
        validators=[DataRequired()])
    
    preferred_destinations = SelectField('Preferred Destination',
        choices=[
            ('any', 'Any Destination'),
            ('coxs_bazar', "Cox's Bazar"),
            ('sylhet', 'Sylhet'),
            ('rangamati', 'Rangamati'),
            ('bandarban', 'Bandarban'),
            ('saint_martin', "Saint Martin's Island"),
            ('dhaka', 'Dhaka'),
            ('chittagong', 'Chittagong'),
            ('khulna', 'Khulna'),
            ('kuakata', 'Kuakata'),
            ('sundarban', 'Sundarban')
        ],
        validators=[DataRequired()])

class TripForm(FlaskForm):
    destination = StringField('Destination', validators=[DataRequired()])
    name = StringField('Trip Name', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    start_date = DateTimeField('Start Date', format='%Y-%m-%d', validators=[DataRequired()], default=datetime.now)
    end_date = DateTimeField('End Date', format='%Y-%m-%d', validators=[DataRequired()], default=datetime.now)
    description = TextAreaField('Description')
    important_events = TextAreaField('Important Events')
    rating = IntegerField('Rating (out of 5)', validators=[DataRequired(), NumberRange(min=0, max=5)])
    photos = TextAreaField('Photo URLs (one per line)')
    videos = TextAreaField('Video URLs (one per line)')
    is_public = BooleanField('Make Public')
    submit = SubmitField('Add Trip')

class TravelDiaryForm(FlaskForm):
    title = StringField('Trip Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    content = TextAreaField('Trip Details', validators=[DataRequired()], render_kw={
        'placeholder': 'Day 1: \n\nDay 2: \n\nDay 3: \n\n...'
    })
    photos = MultipleFileField('Photos (up to 5)', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Only images are allowed!')
    ])
    videos = MultipleFileField('Videos (up to 2)', validators=[
        FileAllowed(['mp4', 'mov', 'avi'], 'Only video files are allowed!')
    ])
    hotel = TextAreaField('Hotel Information')
    restaurant = TextAreaField('Restaurant Information')
    rating = IntegerField('Rating', validators=[NumberRange(min=0, max=5, message='Rating must be between 0 and 5')])
    is_public = BooleanField('Make this public')
    submit = SubmitField('Save Diary')

    def validate_photos(self, field):
        if field.data:
            if len(field.data) > 5:
                raise ValidationError('You can only upload up to 5 photos')
            for file in field.data:
                if file.filename:
                    if not file.filename.lower().endswith(('jpg', 'jpeg', 'png', 'gif')):
                        raise ValidationError('Only image files are allowed')

    def validate_videos(self, field):
        if field.data:
            if len(field.data) > 2:
                raise ValidationError('You can only upload up to 2 videos')
            for file in field.data:
                if file.filename:
                    if not file.filename.lower().endswith(('mp4', 'mov', 'avi')):
                        raise ValidationError('Only video files are allowed')



class ExpenseForm(FlaskForm):
    category = SelectField('Category', choices=[
        ('flight', 'Flight'), 
        ('hotel', 'Hotel'),
        ('food', 'Food'), 
        ('transport', 'Transport'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    description = StringField('Description')
    amount = FloatField('Amount', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    submit = SubmitField('Add Expense')

class EmergencyContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    relationship = SelectField('Relationship', choices=[
        ('family', 'Family'), 
        ('friend', 'Friend'),
        ('doctor', 'Doctor'), 
        ('other', 'Other')
    ])
    phone = StringField('Phone', validators=[DataRequired()])
    alternate_phone = StringField('Alternate Phone')
    submit = SubmitField('Save Contact')

class FlightBookingForm(FlaskForm):
    origin = StringField('From', validators=[DataRequired()])
    destination = StringField('To', validators=[DataRequired()])
    departure_date = DateField('Departure Date', validators=[DataRequired()])
    return_date = DateField('Return Date')
    airline = SelectField('Airline', choices=[
        ('biman', 'Biman Bangladesh Airlines'),
        ('us-bangla', 'US-Bangla Airlines'),
        ('novoair', 'Novoair')
    ], validators=[DataRequired()])
    travel_class = SelectField('Class', choices=[
        ('economy', 'Economy'),
        ('business', 'Business')
    ], validators=[DataRequired()])
    passengers = IntegerField('Passengers', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Book Flight')

class BusBookingForm(FlaskForm):
    origin = StringField('Origin', validators=[DataRequired()])
    destination = StringField('Destination', validators=[DataRequired()])
    departure_date = DateField('Departure Date', validators=[DataRequired()])
    bus_type = SelectField('Bus Type', choices=[
        ('ac', 'AC Bus - ৳1500 per person'),
        ('non-ac', 'Non-AC Bus - ৳800 per person')
    ], validators=[DataRequired()])
    passengers = IntegerField('Number of Passengers', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Book Bus')

class TrainBookingForm(FlaskForm):
    origin = StringField('From', validators=[DataRequired()])
    destination = StringField('To', validators=[DataRequired()])
    departure_date = DateField('Departure Date', validators=[DataRequired()])
    train_name = SelectField('Train Name', choices=[
        ('padma', 'Padma Express'),
        ('subarna', 'Subarna Express'),
        ('mohanagar', 'Mohanagar Express')
    ], validators=[DataRequired()])
    class_type = SelectField('Class', choices=[
        ('shovon', 'Shovon'),
        ('first', 'First Class'),
        ('sleeper', 'Sleeper')
    ], validators=[DataRequired()])
    passengers = IntegerField('Passengers', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Book Train')

class CarBookingForm(FlaskForm):
    pickup_location = StringField('Pickup Location', validators=[DataRequired()])
    drop_location = StringField('Drop Location', validators=[DataRequired()])
    pickup_date = DateField('Pickup Date', validators=[DataRequired()])
    return_date = DateField('Return Date', validators=[DataRequired()])
    car_type = SelectField('Car Type', choices=[
        ('sedan', 'Sedan - ৳5000 per day'),
        ('suv', 'SUV - ৳8000 per day'),
        ('van', 'Van - ৳10000 per day')
    ], validators=[DataRequired()])
    submit = SubmitField('Book Car')

class HotelBookingForm(FlaskForm):
    city = StringField('City', validators=[DataRequired()])
    hotel_name = SelectField('Hotel', choices=[
        ('pan-pacific', 'Pan Pacific Sonargaon - ৳15000 per night'),
        ('le-meridien', 'Le Meridien - ৳12000 per night'),
        ('radisson', 'Radisson Blu - ৳10000 per night'),
        ('westin', 'The Westin - ৳13000 per night')
    ], validators=[DataRequired()])
    check_in = DateField('Check-in Date', validators=[DataRequired()])
    check_out = DateField('Check-out Date', validators=[DataRequired()])
    guests = IntegerField('Number of Guests', validators=[DataRequired(), NumberRange(min=1)])
    room_type = SelectField('Room Type', choices=[
        ('single', 'Single Room (Base Price)'),
        ('double', 'Double Room (+30%)'),
        ('suite', 'Suite (+60%)')
    ], validators=[DataRequired()])
    submit = SubmitField('Book Hotel')

class ExpenseForm(FlaskForm):
    category = SelectField('Category', choices=[
        ('Food', 'Food & Dining'),
        ('Transport', 'Local Transport'),
        ('Shopping', 'Shopping'),
        ('Entertainment', 'Entertainment'),
        ('Other', 'Other')
    ])
    description = StringField('Description')
    amount = FloatField('Amount', validators=[DataRequired()])
    date = DateField('Date', default=date.today)
    submit = SubmitField('Add Expense')

class BusBookingForm(FlaskForm):
    class Meta:
        csrf = False
    departure_city = StringField('Departure City', validators=[DataRequired()])
    destination_city = StringField('Destination City', validators=[DataRequired()])
    departure_date = DateField('Departure Date', format='%Y-%m-%d')
    passengers = IntegerField('Passengers', validators=[DataRequired()])
    bus_operator = StringField('Bus Company', validators=[DataRequired()])
    seat_numbers = StringField('Seat Numbers')
    total_cost = FloatField('Total Cost', validators=[DataRequired()])
    submit = SubmitField('Confirm Booking')

class CarBookingForm(FlaskForm):
    class Meta:
        csrf = False
    car_type = StringField('Car Type', validators=[DataRequired()])
    pickup_location = StringField('Pickup Location', validators=[DataRequired()])
    dropoff_location = StringField('Drop-off Location')
    pickup_date = DateField('Pickup Date', format='%Y-%m-%d')
    return_date = DateField('Return Date', format='%Y-%m-%d')
    rental_days = IntegerField('Rental Days', validators=[DataRequired()])
    daily_rate = FloatField('Daily Rate', validators=[DataRequired()])
    total_cost = FloatField('Total Cost', validators=[DataRequired()])
    submit = SubmitField('Confirm Rental')

class ChatForm(FlaskForm):
    message = StringField('Message', validators=[DataRequired()])