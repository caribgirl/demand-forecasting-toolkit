# 🚀 How to Run This Project

Complete step-by-step instructions for running the Demand Forecasting Toolkit.

---

## 📋 Prerequisites

Before you begin, make sure you have:

- **Python 3.8 or higher** (check with `python3 --version`)
- **pip** (Python package manager)
- **A web browser** (Chrome, Firefox, Safari, or Edge)

---

## 🛠️ Initial Setup (One-Time)

### Step 1: Navigate to Project Directory

```bash
cd /Users/mondellesimeon/Documents/demand-forecasting-toolkit
```

### Step 2: Create Virtual Environment (if not already created)

```bash
python3 -m venv venv
```

### Step 3: Activate Virtual Environment

**On macOS/Linux:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

You should see `(venv)` at the beginning of your terminal prompt.

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages. It may take a few minutes.

**Note:** If you encounter any installation errors, try:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🎯 Running the Interactive Dashboard (Recommended)

The dashboard is the easiest way to use the toolkit - no coding required!

### Quick Start

1. **Activate virtual environment** (if not already active):
   ```bash
   source venv/bin/activate  # macOS/Linux
   # or
   venv\Scripts\activate     # Windows
   ```

2. **Start the dashboard:**
   ```bash
   streamlit run dashboards/streamlit_app.py
   ```

3. **Open your browser:**
   - The dashboard will automatically open at `http://localhost:8501`
   - If it doesn't open automatically, manually navigate to: `http://localhost:8501`

### What You'll See

- **Upload your data** or use the sample Saskatchewan retail data
- **Adjust forecast parameters** (horizon, confidence intervals)
- **Generate forecasts** with one click
- **View business impact** and ROI calculations
- **Download results** as CSV or PDF

### Stopping the Dashboard

Press `Ctrl+C` in the terminal where Streamlit is running.

### Troubleshooting Dashboard

**Issue: "This site can't be reached"**
- Make sure Streamlit is running (check terminal for errors)
- Try `http://127.0.0.1:8501` instead of `localhost:8501`
- Check if port 8501 is already in use: `lsof -i :8501`
- Try a different port: `streamlit run dashboards/streamlit_app.py --server.port 8502`

**Issue: "Module not found"**
- Make sure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

**Issue: Streamlit asks for email**
- Run with: `STREAMLIT_BROWSER_GATHER_USAGE_STATS=false streamlit run dashboards/streamlit_app.py`

---

## 📓 Running Jupyter Notebooks

Perfect for exploring the business case and learning the code.

### Step 1: Start Jupyter

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Launch Jupyter
jupyter notebook
```

This will open Jupyter in your browser automatically.

### Step 2: Open a Notebook

- Navigate to the `notebooks/` folder
- Click on `01_business_case.ipynb` to start
- Run cells using `Shift+Enter` or click "Run All" in the menu

### Available Notebooks

- **01_business_case.ipynb** - ROI calculator and business impact analysis
- Additional notebooks can be added for data exploration, model training, etc.

### Stopping Jupyter

Press `Ctrl+C` in the terminal, then type `y` to confirm shutdown.

---

## 🔧 Running Individual Components

### Generate Sample Data

```bash
# Activate virtual environment
source venv/bin/activate

# Navigate to generators
cd data/generators

# Run generator
python retail_generator.py
```

This creates:
- `data/sample_retail_sales.csv` - Clean data
- `data/sample_retail_sales_with_issues.csv` - Data with quality issues

### Test Baseline Models

```bash
# Activate virtual environment
source venv/bin/activate

# Navigate to models
cd src/models

# Run baseline models
python baseline.py
```

This will:
- Load sample data
- Train multiple forecasting models
- Compare accuracy metrics
- Display results

---

## 🌐 Running on Different Ports

If port 8501 is already in use, you can specify a different port:

```bash
streamlit run dashboards/streamlit_app.py --server.port 8502
```

Then access at `http://localhost:8502`

---

## 🔍 Verifying Installation

Run these commands to verify everything is set up correctly:

```bash
# Check Python version (should be 3.8+)
python3 --version

# Check if packages are installed
python3 -c "import streamlit, pandas, numpy, plotly; print('✅ All packages installed')"

# Test data generator
cd data/generators && python retail_generator.py

# Test models
cd ../../src/models && python baseline.py
```

---

## 📝 Common Commands Reference

### Activate Virtual Environment
```bash
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

### Deactivate Virtual Environment
```bash
deactivate
```

### Install/Update Dependencies
```bash
pip install -r requirements.txt
pip install --upgrade -r requirements.txt
```

### Run Dashboard
```bash
streamlit run dashboards/streamlit_app.py
```

### Run Dashboard (Headless - No Browser)
```bash
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false streamlit run dashboards/streamlit_app.py --server.headless=true
```

### Run Dashboard (Custom Port)
```bash
streamlit run dashboards/streamlit_app.py --server.port 8502
```

### Start Jupyter
```bash
jupyter notebook
```

### Check What's Running on Port 8501
```bash
lsof -i :8501  # macOS/Linux
netstat -ano | findstr :8501  # Windows
```

### Stop All Streamlit Processes
```bash
pkill -f streamlit  # macOS/Linux
taskkill /F /IM streamlit.exe  # Windows
```

---

## 🐛 Troubleshooting

### Problem: "Command not found: streamlit"

**Solution:**
- Make sure virtual environment is activated
- Install dependencies: `pip install -r requirements.txt`

### Problem: "Port already in use"

**Solution:**
- Find and stop the process using the port:
  ```bash
  lsof -i :8501  # Find process
  kill -9 <PID>  # Kill process (replace <PID> with actual process ID)
  ```
- Or use a different port (see "Running on Different Ports" above)

### Problem: "ModuleNotFoundError"

**Solution:**
- Activate virtual environment: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`
- If specific package fails, install individually: `pip install <package-name>`

### Problem: Dashboard loads but shows errors

**Solution:**
- Check terminal output for specific error messages
- Verify sample data exists: `ls data/sample_retail_sales.csv`
- Regenerate sample data: `cd data/generators && python retail_generator.py`

### Problem: Jupyter won't start

**Solution:**
- Make sure virtual environment is activated
- Install Jupyter: `pip install jupyter`
- Try: `python -m jupyter notebook`

---

## 🚀 Quick Start Summary

For the fastest way to get started:

```bash
# 1. Navigate to project
cd /Users/mondellesimeon/Documents/demand-forecasting-toolkit

# 2. Activate virtual environment
source venv/bin/activate

# 3. Run dashboard
streamlit run dashboards/streamlit_app.py

# 4. Open browser to http://localhost:8501
```

That's it! You're ready to use the toolkit.

---

## 📚 Next Steps

Once you have the dashboard running:

1. **Try the sample data** - Select "Use Sample Saskatchewan Retail Data"
2. **Generate a forecast** - Set horizon to 7 days and click "Generate Forecast"
3. **Explore the results** - Check accuracy metrics and business impact
4. **Read the case study** - See `case_studies/retail_case_study.md` for real-world examples
5. **Open the business notebook** - Run `jupyter notebook` and open `notebooks/01_business_case.ipynb`

---

## 💡 Tips

- **Keep the terminal open** while Streamlit is running
- **Use the sample data first** to understand how it works
- **Check the terminal** for any error messages if something doesn't work
- **Bookmark** `http://localhost:8501` for quick access

---

## 📞 Need Help?

If you encounter issues not covered here:

1. Check the terminal output for specific error messages
2. Review `QUICK_START.md` for additional guidance
3. See `PROJECT_SUMMARY.md` for project overview
4. Check `README.md` for general information

---

**Last Updated:** January 2025  
**Project:** Demand Forecasting Toolkit  
**Author:** Mondelle Simeon

