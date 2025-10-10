# 🎯 DEPLOY CHEAT SHEET - Copy & Paste Commands

## ✅ ALL FILES CREATED - YOU'RE READY TO DEPLOY!

---

## 🚀 OPTION 1: RENDER (RECOMMENDED - FREE)

### Quick Steps:

**1. Install Git (if needed):**
Download: https://git-scm.com/download/win

**2. Create GitHub Account:**
https://github.com → Sign up

**3. Create Repository:**
- Go to GitHub
- Click "+" → "New repository"  
- Name: `landslide-detection`
- Public → Create

**4. Push Code (Copy-Paste):**

```powershell
cd "D:\data cience\lanslide detection intenship project"
git config --global user.name "YOUR_NAME"
git config --global user.email "YOUR_EMAIL"
git init
git add .
git commit -m "Landslide Detection System"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/landslide-detection.git
git push -u origin main
```

**5. Deploy on Render:**
- Go to: https://render.com
- Sign up with GitHub
- New → Web Service
- Connect `landslide-detection` repository
- Build: `pip install -r requirements_production.txt`
- Start: `gunicorn app:app`
- Create → Wait 5 min → DONE!

**Your URL:** `https://landslide-detection.onrender.com`

---

## 🌐 OPTION 2: PYTHONANYWHERE (EASIEST)

**1. Sign Up:**
https://www.pythonanywhere.com → Create account

**2. Upload Files:**
- Click "Files"
- Upload: app.py, templates/, static/, model.pkl, etc.

**3. Install Packages:**
- Click "Consoles" → Bash
```bash
mkvirtualenv myenv --python=/usr/bin/python3.10
pip install flask numpy pandas matplotlib scikit-learn werkzeug
```

**4. Create Web App:**
- Click "Web" → "Add new web app"
- Flask → Python 3.10
- Done!

**Your URL:** `https://yourusername.pythonanywhere.com`

---

## 📦 FILES I CREATED FOR YOU

✅ `requirements_production.txt` - Dependencies  
✅ `Procfile` - Start command  
✅ `runtime.txt` - Python version  
✅ `.gitignore` - Exclude files  
✅ `render.yaml` - Render config  

**Everything is ready to deploy!**

---

## 🔄 UPDATE WEBSITE (After code changes)

```powershell
git add .
git commit -m "Updated feature"
git push
```

Render auto-deploys in 3-5 min!

---

## 🌍 SHARE YOUR WEBSITE

After deployment, share:
```
https://your-app-name.onrender.com
```

Works on:
- ✅ Computers
- ✅ Phones
- ✅ Tablets
- ✅ Worldwide!

---

## 🎬 START NOW

**Check Git:**
```powershell
git --version
```

**If not installed:** https://git-scm.com

**Then deploy using Render (15 min) or PythonAnywhere (10 min)!**

---

Need help? Tell me which platform you choose!
