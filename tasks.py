from celery_config import celery
from datetime import date, timedelta, datetime
import os
import csv
from flask import Flask, render_template
from flask_mail import Message
from sqlalchemy import func
from config import Config
from models import db, Trek, Booking
from extensions import mail

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
mail.init_app(app)

@celery.task
def daily_trek_reminder():
    with app.app_context():
        tomorrow = date.today() + timedelta(days=1)

        upcoming_treks = Trek.query.filter_by(
            start_date=tomorrow
        ).all()

        if not upcoming_treks:
            return "No upcoming treks"

        for trek in upcoming_treks:

            bookings = Booking.query.filter_by(
                trek_id=trek.id,
                booking_status="Booked"
            ).all()

            for booking in bookings:

                message = Message(
                    subject="Trek Reminder",
                    recipients=[booking.user.email]
                )

                message.body = f"""
Hello {booking.user.username},

This is a reminder that your trek is scheduled for tomorrow.

Trek Name : {trek.trek_name}
Location : {trek.location}
Date : {trek.start_date}

Please arrive on time and carry all the required trekking essentials.

Have a safe and enjoyable trek!

Regards,
Trekking Management Team
"""

                mail.send(message)

        return "Daily reminder emails sent successfully"


@celery.task
def generate_monthly_report():
    with app.app_context():

        total_treks = Trek.query.count()

        total_bookings = Booking.query.count()

        total_participants = Booking.query.filter_by(
            booking_status="Booked"
        ).count()

        completed_treks = Trek.query.filter_by(
            status="Completed"
        ).count()

        popular = (
            db.session.query(
                Trek.trek_name,
                func.count(Booking.id).label("count")
            )
            .join(Booking)
            .group_by(Trek.id)
            .order_by(func.count(Booking.id).desc())
            .first()
        )

        popular_trek = popular.trek_name if popular else "No Data"

        report = render_template(
            "reports/monthly_report.html",
            generated_date=datetime.now(),
            total_treks=total_treks,
            total_bookings=total_bookings,
            total_participants=total_participants,
            completed_treks=completed_treks,
            popular_trek=popular_trek
        )

        os.makedirs("reports", exist_ok=True)

        filename = "reports/monthly_report.html"

        with open(filename, "w") as file:
            file.write(report)

        return filename


@celery.task
def export_booking_history(user_id):
    with app.app_context():

        bookings = Booking.query.filter_by(
            user_id=user_id
        ).all()

        os.makedirs("exports", exist_ok=True)

        filename = f"exports/history_{user_id}.csv"

        with open(filename, "w", newline="") as csv_file:

            writer = csv.writer(csv_file)

            writer.writerow([
                "Booking ID",
                "Trek Name",
                "Location",
                "Booking Date",
                "Booking Status",
                "Payment Status"
            ])

            for booking in bookings:
                writer.writerow([
                    booking.id,
                    booking.trek.trek_name,
                    booking.trek.location,
                    booking.booking_date,
                    booking.booking_status,
                    booking.payment_status
                ])

        return filename