from flask import Flask, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from auth import auth_bp
from config import Config
from models import create_admin, db

app = Flask(__name__)

app.config.from_object(Config)

db.init_app(app)
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

@app.route("/staff")
def staff_dashboard():
    return render_template("staff_dashboard.html")

@app.route("/user")
def user_dashboard():
    return render_template("user_dashboard.html")

if __name__ == "__main__":
    app.run(debug=True)