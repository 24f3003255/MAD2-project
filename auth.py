from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from werkzeug.security import check_password_hash, generate_password_hash

from decorators import role_required
from models import Booking, User, db

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
@jwt_required()
@role_required("Admin")
def admin_dashboard():
    return jsonify({
        "message": "Welcome Admin"
    }), 200

@auth_bp.route("/api/staff/dashboard", methods=["GET"])
@jwt_required()
@role_required("Staff")
def staff_dashboard():
    user = User.query.get(get_jwt_identity())
    if not user:
        return jsonify({"message": "User not found"}), 404
    return jsonify({
        "staff_name": user.username,
        "message": "Welcome Staff"
    }), 200

@auth_bp.route("/api/user/dashboard", methods=["GET"])
@jwt_required()
@role_required("Trekker")
def user_dashboard():
    user = User.query.get(get_jwt_identity())
    if not user:
        return jsonify({"message": "User not found"}), 404
    total_bookings = Booking.query.filter_by(user_id=user.id).count()
    return jsonify({
        "username": user.username,
        "total_bookings": total_bookings,
        "message": "Welcome Trekker"
    }), 200