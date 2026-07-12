from flask import Flask, render_template, send_file
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from extensions import mail
from auth import auth_bp
from config import Config
from models import create_admin, db
from cache import cache

app = Flask(__name__)

app.config.from_object(Config)

app.config["CACHE_TYPE"] = "RedisCache"
app.config["CACHE_REDIS_HOST"] = "localhost"
app.config["CACHE_REDIS_PORT"] = 6379
app.config["CACHE_DEFAULT_TIMEOUT"] = 60

db.init_app(app)
cache.init_app(app)
mail.init_app(app)
JWTManager(app)
CORS(app)

app.register_blueprint(auth_bp)

with app.app_context():
    db.create_all()
    create_admin()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/admin")
def admin_dashboard():
    return render_template("admin_dashboard.html")

@app.route("/admin/add-staff")
def add_staff_page():
    return render_template("add_staff.html")

@app.route("/admin/staffs")
def manage_staff_page():
    return render_template("manage_staff.html")

@app.route("/admin/add-trek")
def add_trek_page():
    return render_template("add_trek.html")

@app.route("/admin/manage-treks")
def manage_treks_page():
    return render_template("manage_treks.html")

@app.route("/admin/manage-users")
def manage_users_page():
    return render_template("manage_users.html")

@app.route("/admin/history")
def admin_history_page():
    return render_template("admin_history.html")

@app.route("/admin/report/view")
def view_report():
    return send_file("reports/monthly_report.html")

@app.route("/staff")
def staff_dashboard():
    return render_template("staff_dashboard.html")

@app.route("/staff/treks")
def manage_staff_treks_page():
    return render_template("manage_assigned_treks.html")

@app.route("/staff/trek/<int:trek_id>/participants")
def staff_participants_page(trek_id):
    return render_template("trek_participants.html")

@app.route("/user")
def user_dashboard():
    return render_template("user_dashboard.html")

@app.route("/user/treks")
def available_treks_page():
    return render_template("available_treks.html")

@app.route("/user/bookings")
def my_bookings_page():
    return render_template("my_bookings.html")

@app.route("/user/profile")
def user_profile():
    return render_template("user_profile.html")

if __name__ == "__main__":
    app.run(debug=True)