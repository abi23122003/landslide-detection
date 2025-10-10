# Landslide Detection Project - Complete Setup Guide

## ✅ Current Status

Your Flask application is **running successfully** on:
- **Local URL**: http://127.0.0.1:5000
- **Network URL**: http://10.244.55.90:5000

## 📋 Working Features

✅ **Available Routes:**
- `/` - Home page (index.html)
- `/login` - User login
- `/register` - New user registration
- `/welcome` - Dashboard (requires login)
- `/logout` - Logout

⚠️ **Not Working:**
- `/predict` - Landslide prediction (model incompatibility issue)

## 🔧 Issue: Model Compatibility

The `model.pkl` file was trained with **scikit-learn 1.2.2** but your environment has **scikit-learn 1.7.2**, causing a pickle incompatibility error.

## 🚀 Solutions

### Option 1: Retrain the Model (Recommended)

If you have the training dataset (`land_slide.csv`):

```powershell
# Navigate to project directory
Set-Location -LiteralPath "D:\data cience\lanslide detection intenship project"

# Run the training script
.\myvenv\Scripts\python.exe final_model.py
```

This will create a new `model.pkl` compatible with your current environment.

### Option 2: Downgrade scikit-learn (Quick Fix)

```powershell
.\myvenv\Scripts\python.exe -m pip install scikit-learn==1.2.2
```

Then restart the Flask app.

### Option 3: Use the App Without Predictions

The login/register/welcome features work perfectly. You can:
1. Register a new account
2. Login
3. Access the welcome dashboard
4. The prediction feature will be disabled until the model is fixed

## 📁 Missing Dataset?

If `land_slide.csv` is missing, you need to:
1. Locate your original dataset
2. Place it in the project root: `D:\data cience\lanslide detection intenship project\land_slide.csv`
3. Run `final_model.py` to retrain

The dataset should have these columns:
- Slope Angle (degrees)
- Rainfall (mm)
- Moisture Content (%)
- Result (0, 1, 2, or 3)

## 🎯 To Run the Complete Project

### Start the Flask Server:

```powershell
Set-Location -LiteralPath "D:\data cience\lanslide detection intenship project"
.\myvenv\Scripts\python.exe app.py
```

### Access the Application:

1. Open your browser
2. Go to: **http://127.0.0.1:5000**
3. You'll see the home page

### Test All Features:

1. **Register** a new account at http://127.0.0.1:5000/register
2. **Login** at http://127.0.0.1:5000/login
3. **Access Dashboard** at http://127.0.0.1:5000/welcome
4. **Make Predictions** at the home page (after fixing model)

## 🛠️ Troubleshooting

### If Flask won't start:
```powershell
# Clear cache
Remove-Item -Recurse -Force -LiteralPath "D:\data cience\lanslide detection intenship project\__pycache__"

# Restart
.\myvenv\Scripts\python.exe app.py
```

### If imports fail:
```powershell
# Reinstall dependencies
.\myvenv\Scripts\python.exe -m pip install --upgrade --force-reinstall -r requirements.txt
```

### Check installed packages:
```powershell
.\myvenv\Scripts\python.exe -m pip list
```

## 📦 Project Structure

```
lanslide detection intenship project/
├── app.py                 # Main Flask application
├── final_model.py        # Model training script
├── model.pkl             # Trained model (needs retraining)
├── users.db              # SQLite database
├── utils.py              # Helper functions
├── create_database.py    # Database setup
├── requirements.txt      # Dependencies
├── templates/            # HTML templates
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── welcome.html
│   └── result.html
├── static/               # CSS, images, graphs
└── myvenv/               # Virtual environment
```

## 📝 Next Steps

1. **Find or create** the `land_slide.csv` dataset
2. **Retrain the model**: Run `.\myvenv\Scripts\python.exe final_model.py`
3. **Restart Flask**: The app will auto-reload with the new model
4. **Test predictions**: Use the form on the home page

## 🌐 Access Points

Once running, visit these URLs:

- Home: http://127.0.0.1:5000/
- Login: http://127.0.0.1:5000/login
- Register: http://127.0.0.1:5000/register
- Dashboard: http://127.0.0.1:5000/welcome (after login)

---

**Current Flask Status**: ✅ Running on http://127.0.0.1:5000
**Model Status**: ⚠️ Needs retraining or scikit-learn downgrade
**Database**: ✅ Created and working
