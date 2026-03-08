from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
import json
import logging
from logging.handlers import RotatingFileHandler
import time
import numpy as np

# ─── Logging setup ──────────────────────────────────────────────────────────────
LOG_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(LOG_DIR, "app.log")

logger = logging.getLogger("landslide")
logger.setLevel(logging.DEBUG)

# File handler — rotates at 5 MB, keeps 3 backups
_fh = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
_fh.setLevel(logging.DEBUG)
_fh.setFormatter(logging.Formatter(
    "%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
))
logger.addHandler(_fh)

# Console handler — INFO and above
_ch = logging.StreamHandler()
_ch.setLevel(logging.INFO)
_ch.setFormatter(logging.Formatter("%(levelname)-8s | %(message)s"))
logger.addHandler(_ch)

# Also attach to Flask's built-in logger so werkzeug messages go to app.log
app_logger_configured = False  # flag set after app is created

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


def compute_probabilities(prediction, confidence):
    """
    Convert the prediction class + confidence into a probability list.

    Returns a list of four floats (percentages) for:
      [High Risk, Moderate Risk, Low Risk, Safe Zone]

    The predicted class gets `confidence`%; the remainder is split
    equally among the other three classes.
    """
    proba = [0.0] * 4
    proba[prediction] = confidence
    remaining = 100.0 - confidence
    for i in range(4):
        if i != prediction:
            proba[i] = round(remaining / 3, 1)
    return proba


# ─── Input validation ──────────────────────────────────────────────────────────

# Defines each field: (form_name, display_label, min, max)
FIELD_RULES = [
    ("Slope Angle (degrees)", "Slope Angle",    0, 90),
    ("Rainfall (mm)",         "Rainfall",       0, 500),
    ("Moisture Content (%)",  "Moisture Content", 0, 100),
]


def validate_prediction_inputs(form):
    """
    Validate and sanitise the three prediction inputs.

    Returns
    -------
    values : dict          – cleaned float values keyed by form-field name
    errors : list[str]     – human-readable error messages (empty = all OK)
    raw    : dict          – original strings so the template can re-fill inputs
    """
    errors = []
    values = {}
    raw = {}

    for field_name, label, lo, hi in FIELD_RULES:
        raw_val = form.get(field_name, "").strip()
        raw[field_name] = raw_val

        # 1. Empty check
        if not raw_val:
            errors.append(f"{label} is required.")
            continue

        # 2. Safe float conversion
        try:
            num = float(raw_val)
        except ValueError:
            errors.append(f"{label} must be a valid number (got '{raw_val}').")
            continue

        # 3. Range / negative check
        if num < lo:
            errors.append(f"{label} cannot be negative (min {lo}).")
            continue
        if num > hi:
            errors.append(f"{label} must be at most {hi} (got {num}).")
            continue

        values[field_name] = num

    return values, errors, raw


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
            logger.info("LOGIN OK  | user=%s ip=%s", username, request.remote_addr)
            return redirect(url_for("welcome"))
        logger.warning("LOGIN FAIL | user=%s ip=%s", username, request.remote_addr)
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

    user = session.get("username", "unknown")
    logger.info("PREDICT REQUEST | user=%s ip=%s route=/predict", user, request.remote_addr)

    # ── Validate ────────────────────────────────────────────────
    values, errors, raw = validate_prediction_inputs(request.form)

    if errors:
        logger.warning("VALIDATION FAIL | user=%s errors=%s raw=%s", user, errors, raw)
        return render_template(
            "welcome_new.html",
            username=session["username"],
            error="  •  ".join(errors),   # all issues in one banner
            old=raw,                       # repopulate the form fields
        )

    # ── Run prediction (inputs are guaranteed clean) ────────────
    slope_angle = values["Slope Angle (degrees)"]
    rainfall = values["Rainfall (mm)"]
    moisture_content = values["Moisture Content (%)"]

    logger.info("INPUT VALUES | user=%s slope=%.2f rainfall=%.2f moisture=%.2f",
                user, slope_angle, rainfall, moisture_content)

    t0 = time.perf_counter()
    prediction, confidence = predict_landslide(slope_angle, rainfall, moisture_content)
    proba = compute_probabilities(prediction, confidence)
    elapsed_ms = (time.perf_counter() - t0) * 1000

    labels = ["High Risk", "Moderate Risk", "Low Risk", "Safe Zone"]

    logger.info(
        "PREDICTION OK | user=%s result=%s confidence=%.1f%% proba=%s time=%.2fms",
        user, labels[prediction], confidence, proba, elapsed_ms,
    )

    location_info = (
        f"Slope: {slope_angle}°, Rainfall: {rainfall}mm, Moisture: {moisture_content}%"
    )

    return render_template(
        "result.html",
        prediction=prediction,
        confidence=confidence,
        proba=proba,
        labels=labels,
        url=location_info,
        username=session.get("username", "User"),
    )


# ─── JSON API ──────────────────────────────────────────────────────────────────

LABEL_MAP = {0: "High Risk", 1: "Moderate Risk", 2: "Low Risk", 3: "Safe Zone"}


@app.route("/api/predict", methods=["POST"])
def api_predict():
    """
    JSON API endpoint for landslide risk prediction.

    Accepts
    -------
    • application/json   →  {"slope_angle": 45, "rainfall": 200, "moisture_content": 60}
    • form-urlencoded    →  same keys as the HTML form

    Returns
    -------
    200  {"prediction": "High Risk", "prediction_code": 0,
          "confidence": 91.2,
          "probabilities": {"High Risk": 91.2, "Moderate Risk": 2.9, ...},
          "input": {"slope_angle": 45, "rainfall": 200, "moisture_content": 60}}
    400  {"error": "...", "fields": [...]}
    """

    logger.info("API REQUEST | ip=%s content_type=%s", request.remote_addr, request.content_type)

    # ── 1. Parse input (JSON body or form data) ────────────────
    if request.is_json:
        body = request.get_json(silent=True) or {}
        raw_slope    = body.get("slope_angle")
        raw_rain     = body.get("rainfall")
        raw_moisture = body.get("moisture_content")
    else:
        raw_slope    = request.form.get("Slope Angle (degrees)", "").strip() or \
                       request.form.get("slope_angle", "").strip()
        raw_rain     = request.form.get("Rainfall (mm)", "").strip() or \
                       request.form.get("rainfall", "").strip()
        raw_moisture = request.form.get("Moisture Content (%)", "").strip() or \
                       request.form.get("moisture_content", "").strip()

    # ── 2. Validate each field ─────────────────────────────────
    errors = []
    cleaned = {}

    for raw, name, lo, hi in [
        (raw_slope,    "slope_angle",      0, 90),
        (raw_rain,     "rainfall",         0, 500),
        (raw_moisture, "moisture_content", 0, 100),
    ]:
        if raw is None or str(raw).strip() == "":
            errors.append(f"{name} is required.")
            continue
        try:
            val = float(raw)
        except (ValueError, TypeError):
            errors.append(f"{name} must be a number (got '{raw}').")
            continue
        if val < lo:
            errors.append(f"{name} cannot be below {lo} (got {val}).")
            continue
        if val > hi:
            errors.append(f"{name} cannot exceed {hi} (got {val}).")
            continue
        cleaned[name] = val

    if errors:
        logger.warning("API VALIDATION FAIL | ip=%s errors=%s", request.remote_addr, errors)
        return jsonify({"error": "Validation failed", "fields": errors}), 400

    logger.info("API INPUT | ip=%s slope=%.2f rainfall=%.2f moisture=%.2f",
                request.remote_addr, cleaned["slope_angle"], cleaned["rainfall"], cleaned["moisture_content"])

    # ── 3. Run model ───────────────────────────────────────────
    t0 = time.perf_counter()
    prediction, confidence = predict_landslide(
        cleaned["slope_angle"],
        cleaned["rainfall"],
        cleaned["moisture_content"],
    )
    proba = compute_probabilities(prediction, confidence)
    elapsed_ms = (time.perf_counter() - t0) * 1000

    logger.info(
        "API PREDICTION OK | ip=%s result=%s confidence=%.1f%% proba=%s time=%.2fms",
        request.remote_addr, LABEL_MAP[prediction], confidence, proba, elapsed_ms,
    )

    # ── 4. Build JSON response ─────────────────────────────────
    return jsonify({
        "prediction":      LABEL_MAP[prediction],
        "prediction_code": prediction,
        "confidence":      confidence,
        "probabilities":   dict(zip(LABEL_MAP.values(), proba)),
        "input":           cleaned,
    })


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("home"))


@app.route("/index")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    logger.info("════════ SERVER STARTING ════════")
    logger.info("Log file: %s", LOG_FILE)
    print("Starting Landslide Detection System...")
    print("Open http://127.0.0.1:5000 in your browser")
    # use_reloader=False avoids the stat-reloader crash on Python 3.14
    app.run(debug=True, host="127.0.0.1", port=5000, use_reloader=False)
