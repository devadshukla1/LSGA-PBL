# Windows Installation & Environment Setup Guide

**Product:** SmartRoute Analytics  
**Academic Project Title:** Intelligent Emergency Vehicle Routing and Urban Road Network Resilience Analysis Using Large-Scale Graph Algorithms  
**Project Root:** `LSGA PBL`  
**Platform:** Microsoft Windows 10 / 11 (64-bit)  
**Python Runtime:** Python 3.11.x (>=3.11, <3.13)  

---

## 1. Prerequisites

Before installing SmartRoute Analytics, ensure your Windows workstation meets the following requirements:

1. **Operating System:** Windows 10 (version 1903+) or Windows 11 (64-bit).
2. **Python Environment:** Python 3.11 installed from [python.org](https://www.python.org/downloads/) or the Microsoft Store.
   - *Verification Command:*
     ```powershell
     python --version
     ```
     *Expected Output:* `Python 3.11.x` (Note: Python >=3.13 is unsupported due to compiled dependency constraints in GDAL/Fiona/NetworkX bindings).
3. **Pip Package Manager:** Ensure `pip` is upgraded to the latest version:
   ```powershell
   python -m pip install --upgrade pip
   ```
4. **Git for Windows (Optional):** Required if cloning the repository directly.
5. **C++ Build Tools (Optional/Recommended):** Visual Studio C++ Build Tools or standalone wheels for `scipy` and `pydeck` if installing without pre-built binary wheels.

---

## 2. Step-by-Step Installation

### Step 1: Open the Project Directory
Launch PowerShell or Windows Terminal, and navigate to the project directory:
```powershell
cd "C:\Users\devad\OneDrive\Desktop\LSGA PBL"
```

### Step 2: Create a Dedicated Virtual Environment
Create an isolated Python 3.11 virtual environment named `.venv`:
```powershell
python -m venv .venv
```

### Step 3: Activate the Virtual Environment
Activate the environment in PowerShell:
```powershell
.\.venv\Scripts\Activate.ps1
```
*Note on PowerShell Execution Policy:* If you receive an error stating `running scripts is disabled on this system`, allow script execution for the current user process:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\.venv\Scripts\Activate.ps1
```
Your command prompt should now display `(.venv)`.

### Step 4: Install Dependencies
Install all required project packages pinned in `requirements.txt`:
```powershell
python -m pip install -r requirements.txt
```
Key packages installed:
- `networkx>=3.2`: Directed multigraph representations and centrality calculations.
- `osmnx>=1.9.0`: OpenStreetMap road topology extraction.
- `streamlit>=1.32.0`: Interactive multi-page analytics dashboard.
- `pydeck>=0.8.0`: High-performance WebGL geographic visualization.
- `scipy>=1.12.0`: Spatial 3D KD-Tree nearest-neighbor indexing.
- `pytest>=8.0.0` & `ruff>=0.3.0`: Test automation and static analysis.

### Step 5: Verify the Installation
Run the automated verification suite to confirm environment health, graph dependencies, and cached datasets:
```powershell
python scripts/verify_all.py
```
*Expected Output:*
```text
======================================================================
9 / 9 suites passed (100% SUCCESS)
ALL PHASES VERIFIED SUCCESSFULLY.
======================================================================
```

---

## 3. Application Startup

To launch the interactive multi-page dashboard:
```powershell
python -m streamlit run app.py
```
Streamlit will initialize the local HTTP server and output:
```text
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```
Open `http://localhost:8501` in your browser (Google Chrome, Microsoft Edge, or Mozilla Firefox).

---

## 4. Troubleshooting & Common Windows Issues

### Issue 1: PowerShell Script Execution Disabled
- **Symptom:** `.\.venv\Scripts\activate : File ... cannot be loaded because running scripts is disabled on this system.`
- **Resolution:** Run:
  ```powershell
  Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
  ```

### Issue 2: Port 8501 Already in Use
- **Symptom:** Streamlit fails to bind to port 8501 or starts on port 8502.
- **Resolution:** Explicitly specify an open port or stop existing Python processes:
  ```powershell
  python -m streamlit run app.py --server.port 8505
  ```

### Issue 3: Offline Dataset Selection & OSMnx Network Timeouts
- **Symptom:** Attempting to download dynamic road networks over strict college firewalls or proxy servers results in `ConnectionError` or `Timeout`.
- **Resolution:** Use the bundled offline datasets! In the sidebar of `app.py`, choose **"Offline Sample (4x4 Grid)"** or the pre-cached **"Chandigarh Core"** GraphML dataset. The application operates 100% offline without internet access.

### Issue 4: PyDeck Map Tile Connectivity
- **Symptom:** The PyDeck map shows paths and vectors, but the underlying satellite or carto map tiles appear blank.
- **Resolution:** This occurs when the browser has no internet connection to fetch Carto/Mapbox background tiles. The node points, directed edge lines, and route overlays remain 100% functional and interactive on the blank canvas.

---

## 5. Clean Environment Teardown

To exit the virtual environment after evaluation:
```powershell
deactivate
```
