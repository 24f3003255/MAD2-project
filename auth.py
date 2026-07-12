from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from werkzeug.security import check_password_hash, generate_password_hash
from cache import cache
from decorators import role_required
from models import Booking, User, db, Trek, StaffProfile, TrekStatistics
from datetime import datetime
import os
from tasks import generate_monthly_report, export_booking_history
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/register", methods=["POST"])
def register():
    data = request.json
    existing_user = User.query.filter_by(email=data["email"]).first()
    if existing_user:
        return jsonify({"message": "Email already exists"}), 400
    user = User(
        username=data["username"],
        email=data["email"],
        password=generate_password_hash(data["password"]),
        role="Trekker",
        is_active=True
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "Registration Successful"}), 201

@auth_bp.route("/api/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(email=data["email"]).first()
    if not user:
        return jsonify({"message": "Invalid Credentials"}), 401
    if not check_password_hash(user.password, data["password"]):
        return jsonify({"message": "Invalid Credentials"}), 401
    if not user.is_active:
        return jsonify({"message": "User account is deactivated"}), 403
    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role}
    )
    return jsonify({
        "token": token,
        "role": user.role,
        "username": user.username
    }), 200


@auth_bp.route("/api/admin/dashboard", methods=["GET"])
@cache.cached(timeout=60)
@jwt_required()
@role_required("Admin")
def admin_dashboard():
    print("Database Hit:", datetime.now())
    user_count = User.query.filter_by(role="Trekker").count()
    staff_count = User.query.filter_by(role="Staff").count()
    trek_count = Trek.query.count()
    booking_count = Booking.query.count()
    return jsonify({
        "total_users": user_count,
        "total_staff": staff_count,
        "total_treks": trek_count,
        "total_bookings": booking_count
    }), 200

@auth_bp.route("/api/admin/add_staff", methods=["POST"])
@jwt_required()
@role_required("Admin")
def add_staff():
    data = request.get_json()
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"message": "Email already exists"}), 400
    new_staff = User(
        username=data["username"],
        email=data["email"],
        password=generate_password_hash(data["password"]),
        role="Staff"
    )
    db.session.add(new_staff)
    db.session.commit()
    staff_profile = StaffProfile(
        user_id=new_staff.id,
        contact_number=data.get("contact_number", ""),
        status="Active"
    )
    db.session.add(staff_profile)
    db.session.commit()
    cache.clear()
    return jsonify({
        "message": "Staff added successfully"
    }), 201

@auth_bp.route("/api/admin/staff/<int:staff_id>/deactivate", methods=["PUT"])
@cache.cached(timeout=60)
@jwt_required()
@role_required("Admin")
def deactivate_staff(staff_id):
    staff = User.query.filter_by(id=staff_id, role="Staff").first()
    if not staff:
        return jsonify({"message": "Staff not found"}), 404
    staff.is_active = False
    if staff.staff_profile:
        staff.staff_profile.status = "Inactive"
    db.session.commit()
    cache.clear()
    return jsonify({"message": "Staff deactivated successfully"}), 200

@auth_bp.route("/api/admin/treks", methods=["POST"])
@jwt_required()
@role_required("Admin")
def add_trek():
    data = request.get_json()
    start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date() if data.get("start_date") else None
    end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date() if data.get("end_date") else None
    trek = Trek(
        trek_name=data["trek_name"],
        location=data["location"],
        difficulty=data["difficulty"],
        duration=int(data["duration"]),
        available_slots=int(data["available_slots"]),
        assigned_staff_id=data.get("assigned_staff_id"),
        status=data.get("status", "Pending"),
        start_date=start_date,
        end_date=end_date,
        description=data.get("description", "")
    )
    db.session.add(trek)
    db.session.commit()
    cache.clear()
    return jsonify({"message": "Trek added successfully"}), 201


@auth_bp.route("/api/admin/treks", methods=["GET"])
@cache.cached(timeout=60)
@jwt_required()
@role_required("Admin")
def get_all_treks():
    treks = Trek.query.all()
    trek_list = []
    for trek in treks:
        trek_list.append({
            "id": trek.id,
            "trek_name": trek.trek_name,
            "location": trek.location,
            "difficulty": trek.difficulty,
            "duration": trek.duration,
            "available_slots": trek.available_slots,
            "assigned_staff_id": trek.assigned_staff_id,
            "assigned_staff_name": trek.staff.user.username if trek.staff and trek.staff.user else "Not Assigned",
            "status": trek.status,
            "start_date": trek.start_date.strftime("%Y-%m-%d") if trek.start_date else "",
            "end_date": trek.end_date.strftime("%Y-%m-%d") if trek.end_date else "",
            "description": trek.description or ""
        })
    return jsonify(trek_list), 200


@auth_bp.route("/api/admin/trek/<int:trek_id>", methods=["PUT"])
@jwt_required()
@role_required("Admin")
def update_trek(trek_id):
    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({"message": "Trek not found"}), 404
    data = request.get_json()
    trek.trek_name = data["trek_name"]
    trek.location = data["location"]
    trek.difficulty = data["difficulty"]
    trek.duration = int(data["duration"])
    trek.available_slots = int(data["available_slots"])
    trek.assigned_staff_id = data.get("assigned_staff_id")
    trek.status = data["status"]
    trek.description = data.get("description", "")
    trek.start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date() if data.get("start_date") else None
    trek.end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date() if data.get("end_date") else None
    db.session.commit()
    cache.clear()
    return jsonify({"message": "Trek updated successfully"}), 200

@auth_bp.route("/api/admin/trek/<int:trek_id>", methods=["DELETE"])
@jwt_required()
@role_required("Admin")
def delete_trek(trek_id):
    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({"message": "Trek not found"}), 404
    db.session.delete(trek)
    db.session.commit()
    cache.clear()
    return jsonify({"message": "Trek deleted successfully"}), 200


@auth_bp.route("/api/admin/staff-options", methods=["GET"])
@jwt_required()
@role_required("Admin")
def staff_options():
    staffs = User.query.filter_by(role="Staff").all()
    staff_list = []
    for staff in staffs:
        if staff.staff_profile:
            staff_list.append({
                "staff_profile_id": staff.staff_profile.id,
                "username": staff.username
            })

    return jsonify(staff_list), 200


@auth_bp.route("/api/admin/users", methods=["GET"])
@jwt_required()
@role_required("Admin")
def get_all_users():
    users = User.query.filter_by(role="Trekker").all()
    user_list = []
    for user in users:
        user_list.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "booking_count": Booking.query.filter_by(user_id=user.id).count(),
            "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
    return jsonify(user_list), 200


@auth_bp.route("/api/admin/user/<int:user_id>/deactivate", methods=["PUT"])
@jwt_required()
@role_required("Admin")
def deactivate_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    if user.role != "Trekker":
        return jsonify({"message": "Only trekker users can be deactivated from this page"}), 400
    user.is_active = False
    db.session.commit()
    cache.clear()
    return jsonify({"message": "User deactivated successfully"}), 200


@auth_bp.route("/api/admin/history", methods=["GET"])
@jwt_required()
@role_required("Admin")
def admin_history():
    bookings = Booking.query.all()
    booking_history = []
    for booking in bookings:
        booking_history.append({
            "booking_id": booking.id,
            "username": booking.user.username,
            "trek_name": booking.trek.trek_name,
            "location": booking.trek.location,
            "booking_date": booking.booking_date.strftime("%Y-%m-%d"),
            "booking_status": booking.booking_status,
            "payment_status": booking.payment_status,
            "trek_status": booking.trek.status
        })
    return jsonify(booking_history), 200

@auth_bp.route("/api/admin/staffs", methods=["GET"])
@jwt_required()
@role_required("Admin")
def get_all_staffs():
    staffs = User.query.filter_by(role="Staff").all()
    staff_list = []
    for staff in staffs:
        profile = staff.staff_profile
        staff_list.append({
            "id": staff.id,
            "username": staff.username,
            "email": staff.email,
            "contact_number": profile.contact_number if profile else "",
            "status": profile.status if profile else "No Profile",
            "is_active": staff.is_active
        })
    return jsonify(staff_list), 200

@auth_bp.route("/api/admin/report", methods=["POST"])
@jwt_required()
@role_required("Admin")
def create_report():

    task = generate_monthly_report.delay()

    return jsonify({
        "message": "Report generation started",
        "task_id": task.id
    })

@auth_bp.route("/api/admin/report/download", methods=["GET"])
@jwt_required()
@role_required("Admin")
def download_report():
    filename = "reports/monthly_report.html"
    if not os.path.exists(filename):
        return jsonify({"message": "Report not found"}), 404
    return send_file(
        filename,
        mimetype="text/html"
    )

@auth_bp.route("/api/staff/dashboard", methods=["GET"])
@cache.cached(timeout=60)
@jwt_required()
@role_required("Staff")
def staff_dashboard():
    user = User.query.get(get_jwt_identity())
    if not user:
        return jsonify({"message": "User not found"}), 404
    if not user.staff_profile:
        return jsonify({"message": "Staff profile not found"}), 404
    staff_id = user.staff_profile.id
    treks = Trek.query.filter_by(assigned_staff_id=staff_id).all()
    trek_ids = [trek.id for trek in treks]
    participant_count = 0
    if trek_ids:
        participant_count = Booking.query.filter(Booking.trek_id.in_(trek_ids)).count()
    return jsonify({
        "staff_name": user.username,
        "assigned_treks": len(treks),
        "registered_trekkers": participant_count
    }), 200

@auth_bp.route("/api/staff/treks", methods=["GET"])
@jwt_required()
@role_required("Staff")
def get_staff_treks():
    user = User.query.get(get_jwt_identity())
    if not user or not user.staff_profile:
        return jsonify([]), 200
    staff_id = user.staff_profile.id
    treks = Trek.query.filter_by(assigned_staff_id=staff_id).all()
    trek_data = []
    for trek in treks:
        participants = Booking.query.filter_by(trek_id=trek.id).count()
        trek_data.append({
            "id": trek.id,
            "trek_name": trek.trek_name,
            "location": trek.location,
            "difficulty": trek.difficulty,
            "duration": trek.duration,
            "available_slots": trek.available_slots,
            "status": trek.status,
            "participants": participants
        })
    return jsonify(trek_data), 200

@auth_bp.route("/api/staff/trek/<int:trek_id>", methods=["PUT"])
@jwt_required()
@role_required("Staff")
def update_staff_trek(trek_id):
    user = User.query.get(get_jwt_identity())
    if not user or not user.staff_profile:
        return jsonify({"message": "Staff profile not found"}), 404
    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({"message": "Trek not found"}), 404
    if trek.assigned_staff_id != user.staff_profile.id:
        return jsonify({"message": "You cannot update this trek"}), 403
    data = request.json
    trek.available_slots = data.get("available_slots", trek.available_slots)
    trek.status = data.get("status", trek.status)
    db.session.commit()
    return jsonify({"message": "Trek updated successfully"}), 200

@auth_bp.route("/api/staff/trek/<int:trek_id>/participants", methods=["GET"])
@jwt_required()
@role_required("Staff")
def get_trek_participants(trek_id):
    user = User.query.get(get_jwt_identity())
    if not user or not user.staff_profile:
        return jsonify({"message": "Staff profile not found"}), 404
    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({"message": "Trek not found"}), 404
    if trek.assigned_staff_id != user.staff_profile.id:
        return jsonify({"message": "You cannot view this trek participants"}), 403
    bookings = Booking.query.filter_by(trek_id=trek_id).all()
    participants = []
    for booking in bookings:
        participants.append({
            "booking_id": booking.id,
            "user_id": booking.user.id,
            "username": booking.user.username,
            "email": booking.user.email,
            "booking_status": booking.booking_status,
            "payment_status": booking.payment_status
        })
    return jsonify({
        "trek_name": trek.trek_name,
        "participants": participants
    }), 200

@auth_bp.route("/api/staff/trek/<int:trek_id>/complete", methods=["PUT"])
@jwt_required()
@role_required("Staff")
def complete_trek(trek_id):
    user = User.query.get(get_jwt_identity())
    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({"message": "Trek not found"}), 404
    if trek.assigned_staff_id != user.staff_profile.id:
        return jsonify({"message": "Unauthorized"}), 403
    trek.status = "Completed"
    bookings = Booking.query.filter_by(trek_id=trek_id).all()
    for booking in bookings:
        booking.booking_status = "Completed"
    db.session.commit()
    cache.clear()
    return jsonify({"message": "Trek completed successfully"}), 200

@auth_bp.route("/api/user/dashboard", methods=["GET"])
@jwt_required()
@role_required("Trekker")
def user_dashboard():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    total_bookings = Booking.query.filter_by(user_id=user_id).count()
    return jsonify({
        "username": user.username,
        "total_bookings": total_bookings
    }), 200


@auth_bp.route("/api/user/treks", methods=["GET"])
@cache.cached(timeout=60)
@jwt_required()
@role_required("Trekker")
def get_available_treks():
    treks = Trek.query.filter(Trek.status != "Closed").all()
    trek_list = []
    for trek in treks:
        staff_name = "Not Assigned"
        if trek.staff and trek.staff.user:
            staff_name = trek.staff.user.username
        trek_list.append({
            "id": trek.id,
            "trek_name": trek.trek_name,
            "location": trek.location,
            "difficulty": trek.difficulty,
            "duration": trek.duration,
            "available_slots": trek.available_slots,
            "status": trek.status,
            "staff_name": staff_name,
            "start_date": trek.start_date.strftime("%Y-%m-%d") if trek.start_date else "",
            "end_date": trek.end_date.strftime("%Y-%m-%d") if trek.end_date else "",
            "description": trek.description or ""
        })
    return jsonify(trek_list), 200

@auth_bp.route("/api/user/book/<int:trek_id>", methods=["POST"])
@jwt_required()
@role_required("Trekker")
def book_trek(trek_id):
    user_id = get_jwt_identity()
    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({"message": "Trek not found"}), 404
    if trek.status != "Open":
        return jsonify({"message": "Booking allowed only when trek status is Open"}), 400
    if trek.available_slots <= 0:
        return jsonify({"message": "No slots available for this trek"}), 400
    existing_booking = Booking.query.filter_by(
        user_id=user_id,
        trek_id=trek_id
    ).first()
    if existing_booking:
        return jsonify({"message": "You have already booked this trek"}), 400
    booking = Booking(
        user_id=user_id,
        trek_id=trek_id,
        booking_status="Booked",
        payment_status="Pending"
    )
    db.session.add(booking)
    trek.available_slots -= 1
    db.session.commit()
    cache.clear()
    return jsonify({"message": "Trek booked successfully"}), 201

@auth_bp.route("/api/user/bookings", methods=["GET"])
@jwt_required()
@role_required("Trekker")
def get_user_bookings():
    user_id = get_jwt_identity()
    bookings = Booking.query.filter_by(user_id=user_id).all()
    booking_list = [
        {
            "booking_id": booking.id,
            "trek_name": booking.trek.trek_name,
            "location": booking.trek.location,
            "difficulty": booking.trek.difficulty,
            "booking_date": booking.booking_date.strftime("%Y-%m-%d %H:%M"),
            "booking_status": booking.booking_status,
            "payment_status": booking.payment_status,
            "trek_status": booking.trek.status,
        }
        for booking in bookings
    ]
    return jsonify(booking_list), 200


@auth_bp.route("/api/user/profile", methods=["GET"])
@jwt_required()
@role_required("Trekker")
def get_profile():
    user = User.query.get(get_jwt_identity())
    return jsonify({
        "username": user.username,
        "email": user.email
    })

@auth_bp.route("/api/user/profile", methods=["PUT"])
@jwt_required()
@role_required("Trekker")
def update_profile():
    user = User.query.get(get_jwt_identity())
    data = request.get_json()
    user.username = data["username"]
    user.email = data["email"]
    db.session.commit()
    cache.clear()
    return jsonify({
        "message": "Profile updated successfully"
    })


@auth_bp.route("/api/user/booking/<int:booking_id>/cancel", methods=["PUT"])
@jwt_required()
@role_required("Trekker")
def cancel_booking(booking_id):
    user_id = get_jwt_identity()
    booking = Booking.query.filter_by(
        id=booking_id,
        user_id=user_id
    ).first()
    if not booking:
        return jsonify({"message":"Booking not found"}),404
    if booking.booking_status == "Cancelled":
        return jsonify({"message":"Already cancelled"}),400
    booking.booking_status = "Cancelled"
    booking.trek.available_slots += 1
    db.session.commit()
    cache.clear()
    return jsonify({"message":"Booking cancelled"})

@auth_bp.route("/api/user/export-history", methods=["POST"])
@jwt_required()
@role_required("Trekker")
def export_history():
    task = export_booking_history.delay(get_jwt_identity())
    return jsonify({
        "message": "CSV export started",
        "task_id": task.id
    })


@auth_bp.route("/api/user/export-status", methods=["GET"])
@jwt_required()
@role_required("Trekker")
def export_status():
    filename = f"exports/history_{get_jwt_identity()}.csv"
    if os.path.exists(filename):
        return jsonify({
            "status": "Completed",
            "file": filename
        })
    return jsonify({
        "status": "Processing"
    })


@auth_bp.route("/api/user/download-export", methods=["GET"])
@jwt_required()
@role_required("Trekker")
def download_export():
    filename = f"exports/history_{get_jwt_identity()}.csv"
    if not os.path.exists(filename):
        return jsonify({
            "message": "CSV not found"
        }), 404
    return send_file(
        filename,
        as_attachment=True,
        download_name="Trekking_History.csv",
        mimetype="text/csv"
    )