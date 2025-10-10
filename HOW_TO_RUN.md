# 🚀 How to Run Your Landslide Detection Project (No Extensions Needed)

## ✅ Method 1: Simple PowerShell Command (Recommended)

### Step 1: Open PowerShell
- Press `Windows + X`
- Click "Windows PowerShell" or "Terminal"

### Step 2: Navigate to Project Directory
```powershell
cd "D:\data cience\lanslide detection intenship project"
```

### Step 3: Run the Flask App
```powershell
.\myvenv\Scripts\python.exe app.py
```

### Step 4: Open Browser
- Open any browser (Chrome, Edge, Firefox)
- Go to: **http://127.0.0.1:5000**

### Step 5: Stop the Server
- Press `Ctrl + C` in PowerShell to stop

---

## ✅ Method 2: Using Command Prompt (cmd)

### Step 1: Open Command Prompt
- Press `Windows + R`
- Type: `cmd`
- Press Enter

### Step 2: Navigate and Run
```cmd
cd /d "D:\data cience\lanslide detection intenship project"
myvenv\Scripts\python.exe app.py
```

### Step 3: Open Browser
- Go to: **http://127.0.0.1:5000**

---

## ✅ Method 3: Create a Batch File (.bat) - Double Click to Run

Create a file called **`run_app.bat`** in your project folder with this content:

```batch
@echo off
cd /d "D:\data cience\lanslide detection intenship project"
myvenv\Scripts\python.exe app.py
pause
```

**To Use:**
1. Double-click `run_app.bat`
2. Server starts automatically
3. Open browser: **http://127.0.0.1:5000**
4. Close the window to stop

---

## ✅ Method 4: Create a PowerShell Script (.ps1)

Create a file called **`run_app.ps1`** with this content:

```powershell
Set-Location -LiteralPath "D:\data cience\lanslide detection intenship project"
& ".\myvenv\Scripts\python.exe" app.py
```

**To Run:**
```powershell
.\run_app.ps1
```

---

## ✅ Method 5: Windows Shortcut

### Step 1: Create Shortcut
1. Right-click on Desktop
2. New → Shortcut
3. Enter location:
```
C:\Windows\System32\cmd.exe /k "cd /d "D:\data cience\lanslide detection intenship project" && myvenv\Scripts\python.exe app.py"
```
4. Name it: "Landslide App"

### Step 2: Use
- Double-click shortcut
- Browser opens automatically

---

## ✅ Method 6: Run in Background (No Window)

Create **`run_background.vbs`**:

```vbscript
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd /c cd /d ""D:\data cience\lanslide detection intenship project"" && myvenv\Scripts\python.exe app.py", 0, False
```

**To Use:**
- Double-click the .vbs file
- Server runs silently in background
- Open browser: **http://127.0.0.1:5000**

**To Stop:**
- Open Task Manager (Ctrl+Shift+Esc)
- Find "python.exe"
- End task

---

## ✅ Method 7: Auto-Start with Windows

### Step 1: Create Batch File
Create **`start_app.bat`**:
```batch
@echo off
cd /d "D:\data cience\lanslide detection intenship project"
start /min myvenv\Scripts\python.exe app.py
```

### Step 2: Add to Startup
1. Press `Windows + R`
2. Type: `shell:startup`
3. Copy `start_app.bat` to this folder
4. App starts automatically when Windows boots

---

## ✅ Method 8: Using Python Directly (Any Machine)

If you have Python installed globally:

```powershell
# Navigate to project
cd "D:\data cience\lanslide detection intenship project"

# Activate virtual environment
.\myvenv\Scripts\Activate.ps1

# Run app
python app.py
```

---

## 🌐 Accessing the App

Once running, access from:

### Local Machine:
- http://127.0.0.1:5000
- http://localhost:5000

### Other Devices on Same Network:
- http://10.244.55.90:5000 (your PC's IP)
- Find your IP: `ipconfig` in PowerShell

### From Phone/Tablet on Same WiFi:
1. Find your PC IP: `ipconfig` → look for IPv4 Address
2. Open browser on phone
3. Go to: `http://YOUR_PC_IP:5000`

---

## 🛑 How to Stop the Server

### Method 1: Keyboard
- Press `Ctrl + C` in the terminal/command prompt

### Method 2: Close Window
- Just close the PowerShell/cmd window

### Method 3: Task Manager
- Press `Ctrl + Shift + Esc`
- Find "python.exe"
- Right-click → End Task

---

## 🔧 Troubleshooting

### Issue: "Port 5000 already in use"

**Solution 1 - Use Different Port:**
```powershell
$env:PORT = "8000"
.\myvenv\Scripts\python.exe app.py
```
Then access: **http://127.0.0.1:8000**

**Solution 2 - Kill Process:**
```powershell
# Find process on port 5000
netstat -ano | findstr :5000

# Kill it (replace PID with actual number)
taskkill /PID <PID> /F
```

### Issue: "python.exe not found"

**Solution:**
Use full path:
```powershell
& "D:\data cience\lanslide detection intenship project\myvenv\Scripts\python.exe" app.py
```

### Issue: Cannot connect from other devices

**Solution - Allow through firewall:**
```powershell
# Run as Administrator
New-NetFirewallRule -DisplayName "Flask App" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
```

---

## 📋 Quick Reference Commands

### Start Server:
```powershell
cd "D:\data cience\lanslide detection intenship project"
.\myvenv\Scripts\python.exe app.py
```

### Stop Server:
- Press `Ctrl + C`

### Check if Running:
```powershell
netstat -ano | findstr :5000
```

### View Logs:
- They appear in the terminal window

### Restart Server:
1. Press `Ctrl + C`
2. Press `Up Arrow` (to get last command)
3. Press `Enter`

---

## 🎯 Recommended Method for Daily Use

**Create `START.bat`** in project folder:

```batch
@echo off
title Landslide Detection Server
color 0A
echo ========================================
echo  Landslide Detection System
echo ========================================
echo.
echo Starting server...
echo.
cd /d "D:\data cience\lanslide detection intenship project"
myvenv\Scripts\python.exe app.py
echo.
echo Server stopped.
pause
```

**Usage:**
1. Double-click `START.bat`
2. Server starts in a nice green window
3. Open browser → http://127.0.0.1:5000
4. Close window when done

---

## 📱 Mobile Access (Same WiFi Network)

### Step 1: Find Your PC's IP
```powershell
ipconfig
```
Look for: `IPv4 Address` (e.g., 192.168.1.100)

### Step 2: Start Server
```powershell
.\myvenv\Scripts\python.exe app.py
```

### Step 3: On Phone/Tablet
Open browser and go to:
```
http://192.168.1.100:5000
```
(Replace with your actual IP)

---

## ✅ No Extensions, No Extra Software Needed!

All these methods use **only Windows built-in tools**:
- ✅ PowerShell
- ✅ Command Prompt  
- ✅ Batch Files
- ✅ VBScript
- ✅ Windows Shortcuts

**Your Python environment in `myvenv` has everything needed!**

---

## 🎉 Simplest Method (Copy-Paste)

Just open PowerShell and paste this **one line**:

```powershell
Set-Location "D:\data cience\lanslide detection intenship project"; .\myvenv\Scripts\python.exe app.py
```

Then open: **http://127.0.0.1:5000**

**That's it! No extensions required!** 🚀
