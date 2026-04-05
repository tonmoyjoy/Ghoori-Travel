# Ghoori.com - Comprehensive Travel Companion for Bangladesh

Ghoori.com is a full-featured Flask-based web application designed as an integrated travel platform for Bangladesh travelers. The platform combines trip planning, social networking, travel logging, and logistical tools into a seamless experience.


### Comprehensive Feature Set
1. Extensive functionality covering user management, bookings, diaries, communities, events, and more.
2. Book flights (Biman, US-Bangla, Novoair), buses, trains, cars, and hotels with dynamic pricing.
3. Community groups, threaded comments, reactions, user following, and public/private posts.
4. Multi-media journals with photos/videos, ratings, and location data.
5. Event discovery, packing checklists, emergency contacts, and place finder using Overpass API.

### Robust Architecture
1. Modern Tech Stack: Flask 3.0, SQLAlchemy ORM, Alembic migrations, WTForms, Flask-Login.
2. Database Models: Well-structured schema with relationships for users, bookings, communities, events, and reviews.
3. Security First: CSRF protection, password hashing, input validation, and secure file uploads.
4. Scalable Design: Paginated views, efficient queries, and modular code organization.

### User Experience Excellence
1. Gamification: Badge system (Bronze→Silver→Gold→Platinum) based on diary contributions.
2. Responsive Design: Clean UI with dark mode support and intuitive navigation.
3. File Handling: Automatic image resizing, secure storage, and support for photos/videos up to 200MB.
4. Integrations: Stripe payments, Google OAuth2 login, Google Maps API, and real-time place data.

### Production-Ready Features
1. Error Handling & Logging: Comprehensive error management and debugging support.
2. Environment Configuration: Secure API key management via .env files.
3. Database Management: Easy initialization, migration scripts, and data seeding.
4. Internationalization: Bangla currency support and Bangladesh-specific destinations.

### Developer-Friendly
1. Modular Structure: Separate directories for models, forms, templates, and static files.
2. Utility Scripts: Database fixes, event seeding, and migration tools.
3. Extensible: Clean code patterns for adding new features like additional payment methods or integrations.

## 🛠️ Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd ghoori.com
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install pillow stripe flask-paginate Flask-Migrate  # Additional dependencies
   ```

4. **Configure Environment**
   - Copy `.env.example` to `.env`
   - Add your API keys (Stripe, Google OAuth, Maps)

5. **Initialize Database**
   ```bash
   python init_db.py
   ```

6. **Run the Application**
   ```bash
   python app.py
   ```
   Access at `http://127.0.0.1:5000`

## 📊 Key Statistics
- **Routes**: 70+
- **Models**: 15 core database models
- **Templates**: 40+ Jinja2 HTML files
- **Integrations**: Stripe, Google OAuth, Maps API, Overpass API
- **File Support**: PNG/JPG/JPEG/GIF photos, MP4/AVI/MOV videos

## 🎯 Use Cases
- Trip planning and booking for Bangladesh travel
- Social networking for travelers
- Travel diary and memory management
- Local event discovery
- Emergency contact and logistics planning

Ghoori.com represents a high-quality, deployable travel application with strong foundations for scaling and expansion.