import os
import sqlite3
from pathlib import Path
from typing import Tuple

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    abort,
)

import pickle
import numpy as np
import matplotlib

# Use non-GUI backend for server environments
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from werkzeug.security import generate_password_hash, check_password_hash

from utils import login_required, set_session
from create_database import setup_database


DB_PATH = "users.db"
MODEL_PATH = "model.pkl"
STATIC_DIR = Path("static")
GRAPH_FILE = STATIC_DIR / "confidence_graph.png"


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    
    # Ensure database exists
    setup_database(DB_PATH)

    # Load model lazily and cache on app
    app.model = load_model(MODEL_PATH)

    register_routes(app)
    return app


def load_model(path: str):
    if not Path(path).exists():
        print(f"[WARN] Model file '{path}' not found. Run 'python final_model.py' to train and create it.")
        return None
    try:
        with open(path, "rb") as f:
            model = pickle.load(f)
        # Basic capability check
        if not hasattr(model, "predict"):
            raise ValueError("Loaded object has no predict method")
        return model
    except Exception as e:
        print(f"[ERROR] Failed to load model: {e}")
        return None


def get_db_conn():
    return sqlite3.connect(DB_PATH)


def parse_features(form) -> Tuple[np.ndarray, list]:
    feature_names = [
        "Slope Angle (degrees)",
        "Rainfall (mm)",
        "Moisture Content (%)",
    ]
    values = []
    for name in feature_names:
        raw = form.get(name)
        if raw is None:
            raise ValueError(f"Missing form field: {name}")
        try:
            values.append(float(raw))
        except ValueError:
            raise ValueError(f"Invalid numeric value for '{name}': {raw}")
    return np.array([values]), feature_names


def make_confidence_plot(probas, classes):
    STATIC_DIR.mkdir(exist_ok=True, parents=True)
    plt.figure(figsize=(4, 3))
    bars = plt.bar(range(len(probas)), probas, color="#2c5282")
    plt.xticks(range(len(probas)), classes)
    plt.ylim(0, 1)
    for bar, p in zip(bars, probas):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, f"{p*100:.1f}%", ha="center", fontsize=8)
    plt.tight_layout()
    plt.savefig(GRAPH_FILE, dpi=150, transparent=True)
    plt.close()
    return str(GRAPH_FILE).replace('\\', '/')


def register_routes(app: Flask):
    @app.route("/")
    def index():
        # Use the new landing page
        return render_template("home.html")

    @app.route("/predict", methods=["POST"])
    @login_required
    def predict():
        if app.model is None:
            return render_template("welcome_new.html", username=session.get("username"), error="Model not loaded. Please contact administrator to retrain the model."), 400
        try:
            X, feature_names = parse_features(request.form)
        except ValueError as e:
            return render_template("welcome_new.html", username=session.get("username"), error=str(e)), 400

        try:
            pred = int(app.model.predict(X)[0])
            if hasattr(app.model, "predict_proba"):
                proba = app.model.predict_proba(X)[0]
            else:
                # Fallback: fake uniform probabilities
                classes = sorted(set(getattr(app.model, "classes_", [0, 1, 2, 3])))
                proba = np.array([1/len(classes)] * len(classes))
            classes = list(getattr(app.model, "classes_", range(len(proba))))
            graph_path = make_confidence_plot(proba, classes)
            confidence = float(np.max(proba) * 100)
        except Exception as e:
            return render_template("welcome_new.html", username=session.get("username"), error=f"Prediction failed: {e}"), 500
        
        return render_template(
            "result.html",
            prediction=pred,
            confidence=f"{confidence:.2f}",
            graph=graph_path,
            graph_path=graph_path,
            url=request.url_root.rstrip('/'),
        )

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            remember = request.form.get("remember-me") == "on"
            if not username or not password:
                return render_template("login.html", error="All fields required")
            with get_db_conn() as conn:
                cur = conn.cursor()
                cur.execute("SELECT password, email FROM users WHERE username = ?", (username,))
                row = cur.fetchone()
            if not row or not check_password_hash(row[0], password):
                return render_template("login.html", error="Invalid username or password")
            set_session(username, row[1], remember)
            return redirect(url_for("welcome"))
        return render_template("login.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "")
            confirm = request.form.get("confirm-password", "")
            if not all([username, email, password, confirm]):
                return render_template("register.html", error="All fields required")
            if password != confirm:
                return render_template("register.html", error="Passwords do not match")
            hashed = generate_password_hash(password)
            try:
                with get_db_conn() as conn:
                    conn.execute(
                        "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                        (username, hashed, email),
                    )
            except sqlite3.IntegrityError:
                return render_template("register.html", error="Username already exists")
            set_session(username, email, False)
            return redirect(url_for("welcome"))
        return render_template("register.html")

    @app.route("/welcome")
    @login_required
    def welcome():
        # Use the new welcome page with prediction form
        return render_template("welcome_new.html", username=session.get("username"))
    
    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("index"))

    @app.errorhandler(404)
    def not_found(e):
        return render_template("home.html", error="Page not found"), 404


app = create_app()


if __name__ == "__main__":
    # Helpful startup message
    if app.model is None:
        print("[INFO] No model loaded. Run: python final_model.py to create 'model.pkl'.")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
