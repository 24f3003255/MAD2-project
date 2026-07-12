from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    bookings = db.relationship("Booking", backref="user", lazy=True)
    staff_profile = db.relationship("StaffProfile", backref="user", uselist=False)

class StaffProfile(db.Model):
    __tablename__ = "staff_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    contact_number = db.Column(db.String(15))
    status = db.Column(db.String(30), default="Active")
    assigned_treks = db.relationship("Trek", backref="staff", lazy=True)

class Trek(db.Model):
    __tablename__ = "treks"

    id = db.Column(db.Integer, primary_key=True)
    trek_name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    available_slots = db.Column(db.Integer, nullable=False)
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey("staff_profiles.id"))
    status = db.Column(db.String(30), default="Pending")
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    description = db.Column(db.Text)
    bookings = db.relationship("Booking", backref="trek", lazy=True)

class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey("treks.id"), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    booking_status = db.Column(db.String(30), default="Booked")
    payment_status = db.Column(db.String(30), default="Pending")

class TrekStatistics(db.Model):
    __tablename__ = "trek_statistics"

    id = db.Column(db.Integer, primary_key=True)
    trek_id = db.Column(db.Integer, db.ForeignKey("treks.id"))
    total_bookings = db.Column(db.Integer, default=0)
    completed_users = db.Column(db.Integer, default=0)

def create_admin():
    admin = User.query.filter_by(role="Admin").first()
    if admin is None:
        admin = User(username="admin", email="admin@trek.com", password=generate_password_hash("admin123"), role="Admin")
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully!")