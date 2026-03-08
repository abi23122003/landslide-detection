from flask import Flask, render_template, request, redirect, url_for, session
import os
import json
import numpy as np
import io
import base64

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates"),
    static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), "static"),
)
app.secret_key = "landslide_detection_secret_key_2026"

# Simple file-based user store
USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")


def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}


def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


# ─── Landslide risk prediction logic ───────────────────────────────────────────
def predict_landslide(slope_angle, rainfall, moisture_content):
    """
    Rule-based landslide risk prediction.
    Returns (prediction_class, confidence_percentage)
      0 = High Risk
      1 = Moderate Risk
      2 = Low Risk
      3 = Safe Zone
    """
    # Normalize inputs to a 0-1 risk score
    slope_risk = min(slope_angle / 90.0, 1.0)
    rainfall_risk = min(rainfall / 500.0, 1.0)
    moisture_risk = min(moisture_content / 100.0, 1.0)

    # Weighted risk score
    risk_score = 0.4 * slope_risk + 0.35 * rainfall_risk + 0.25 * moisture_risk

    if risk_score >= 0.7:
        prediction = 0  # High Risk
        confidence = round(70 + risk_score * 30, 1)
    elif risk_score >= 0.5:
        prediction = 1  # Moderate Risk
        confidence = round(60 + risk_score * 30, 1)
    elif risk_score >= 0.3:
        prediction = 2  # Low Risk
        confidence = round(55 + risk_score * 30, 1)
    else:
        prediction = 3  # Safe Zone
        confidence = round(80 + (1 - risk_score) * 15, 1)

    confidence = min(confidence, 99.0)
    return prediction, confidence


def generate_confidence_graph(prediction, confidence):
    """Generate a confidence bar chart and return it as a base64-encoded image URL."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        labels = ["High Risk", "Moderate Risk", "Low Risk", "Safe Zone"]
        colors = ["#d63031", "#fd9644", "#0984e3", "#00b894"]

        # Build confidence values per class
        values = [0, 0, 0, 0]
        values[prediction] = confidence
        remaining = 100 - confidence
        for i in range(4):
            if i != prediction:
                values[i] = round(remaining / 3, 1)

        fig, ax = plt.subplots(figsize=(8, 4))
        bars = ax.barh(labels, values, color=colors, edgecolor="white", height=0.6)
        ax.set_xlim(0, 100)
        ax.set_xlabel("Confidence (%)", fontsize=12)
        ax.set_title("Landslide Risk Confidence", fontsize=14, fontweight="bold")

        for bar, val in zip(bars, values):
            ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2,
                    f"{val}%", va="center", fontsize=10, fontweight="bold")

        plt.tight_layout()

        buf = io.BytesIO()
        fig.savefig(buf, format="png", transparent=True, dpi=100)
        plt.close(fig)
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode("utf-8")
        return f"data:image/png;base64,{img_base64}"
    except ImportError:
        return ""


# ─── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        users = load_users()
        if username in users and users[username]["password"] == password:
            session["username"] = username
            return redirect(url_for("welcome"))
        return render_template("login.html", error="Invalid username or password")
    # Show success message if just registered
    success = None
    if request.args.get("registered"):
        success = "Account created successfully! Please login."
    return render_template("login.html", success=success)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm-password", "")

        if not username or not email or not password:
            return render_template("register.html", error="All fields are required")
        if password != confirm_password:
            return render_template("register.html", error="Passwords do not match")

        users = load_users()
        if username in users:
            return render_template("register.html", error="Username already exists")

        users[username] = {"email": email, "password": password}
        save_users(users)
        return redirect(url_for("login", registered="1"))
    return render_template("register.html")


@app.route("/welcome")
def welcome():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("welcome_new.html", username=session["username"])


@app.route("/predict", methods=["POST"])
def predict():
    if "username" not in session:
        return redirect(url_for("login"))

    try:
        slope_angle = float(request.form.get("Slope Angle (degrees)", 0))
        rainfall = float(request.form.get("Rainfall (mm)", 0))
        moisture_content = float(request.form.get("Moisture Content (%)", 0))
    except (ValueError, TypeError):
        return render_template(
            "welcome_new.html",
            username=session["username"],
            error="Please enter valid numeric values for all fields.",
        )

    prediction, confidence = predict_landslide(slope_angle, rainfall, moisture_content)
    graph = generate_confidence_graph(prediction, confidence)

    location_info = (
        f"Slope: {slope_angle}°, Rainfall: {rainfall}mm, Moisture: {moisture_content}%"
    )

    return render_template(
        "result.html",
        prediction=prediction,
        confidence=confidence,
        graph=graph,
        graph_path=graph,
        url=location_info,
    )


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("home"))


@app.route("/index")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    print("Starting Landslide Detection System...")
    print("Open http://127.0.0.1:5000 in your browser")
    app.run(debug=True, host="127.0.0.1", port=5000)
