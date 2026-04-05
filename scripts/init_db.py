import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db, init_bracu_data

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Create instance directory if it doesn't exist
instance_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
if not os.path.exists(instance_dir):
    os.makedirs(instance_dir)

with app.app_context():
    # Drop all existing tables
    db.drop_all()
    
    # Create all tables with new schema
    db.create_all()
    
    # Initialize BRACU data
    init_bracu_data()
    
    print("Database initialized successfully!")
