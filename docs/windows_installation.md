# MetroGraph Analytics — Windows Installation & Setup Guide

This guide provides end-to-end instructions for installing and running the MetroGraph Analytics platform on **Microsoft Windows** using Windows PowerShell.

---

## 1. System Requirements

- **Operating System:** Windows 10 or Windows 11 (64-bit)
- **Python Version:** Python >= 3.11, < 3.13 (Python 3.11.x recommended)
- **Memory (RAM):** 4 GB minimum (8 GB recommended)
- **Disk Space:** ~500 MB free space

---

## 2. Installation Walkthrough (PowerShell)

### Step 1: Open PowerShell and Navigate to Project
Launch **Windows PowerShell** or **PowerShell 7** and enter the project folder:
```powershell
cd "C:\Users\devad\OneDrive\Desktop\LSGA PBL"
```

### Step 2: Create a Python 3.11 Virtual Environment
Ensure you create the virtual environment using Python 3.11:
```powershell
py -3.11 -m venv .venv
```

### Step 3: Enable Script Execution & Activate Environment
If script execution is blocked on Windows, set the execution policy for the current process:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```
*(Your prompt should now display `(.venv)`)*

### Step 4: Upgrade Pip and Install Dependencies
```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

## 3. Running the Application

Launch the Streamlit interactive dashboard:
```powershell
python -m streamlit run app.py
```
Streamlit will automatically open your default web browser at `http://localhost:8501`.

---

## 4. Running Tests & Benchmarks

### Run Complete Test Suite
```powershell
python -m pytest -v
```

### Run Static Analysis (Ruff)
```powershell
python -m ruff check .
```

### Run Benchmark Suite
```powershell
python scripts\benchmark_algorithms.py
```

### Reproduce Experimental Results
```powershell
python scripts\reproduce_results.py --dataset metro --benchmarks
```

---

## 5. Windows Troubleshooting

- **`Activate.ps1 cannot be loaded because running scripts is disabled`**:
  Execute `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in the current terminal window.
- **Port 8501 Already in Use**:
  Run Streamlit on an alternate port: `streamlit run app.py --server.port 8502`.
- **Plotly Figure Display in Browser**:
  Modern Chromium browsers (Edge, Chrome) fully support offline WebGL rendering for Plotly schematic diagrams. No internet connection is required.
