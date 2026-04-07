# 🚀 QUICK START GUIDE
## Price Sensitivity Analysis System

### ⚡ Get Started in 3 Steps

**Step 1: Extract**
```bash
unzip price_sensitivity_app.zip
cd price_sensitivity_app
```

**Step 2: Install**
```bash
pip install -r requirements.txt
```

**Step 3: Run**
```bash
python app.py
```

Then open your browser and go to: **http://localhost:5000**

---

### 📝 First Time Using It?

1. Click **"Use Sample Data"** button
2. Wait 2-3 seconds for analysis
3. Scroll down to see beautiful results!

---

### 📁 Want to Use Your Own Data?

Create a CSV file with these columns:
- **Product_Name** (e.g., "iPhone 15 Pro")
- **Category** (Smartphone, Tablet, Smartwatch, or Earbuds)
- **Price** (e.g., 999.00)
- **Units_Sold** (e.g., 1500)

Then drag & drop it into the upload box!

---

### 💡 What You'll See

✅ **Dataset Summary** - Statistics about your data
✅ **Model Metrics** - How accurate the predictions are
✅ **Price vs Demand Chart** - Visual relationship
✅ **Validation Plot** - Model quality check
✅ **Sensitivity Curves** - THE MAIN FEATURE! Shows optimal prices
✅ **Optimal Prices** - Best prices for maximum revenue
✅ **Coefficients** - How the model works

---

### ❓ Having Issues?

**Python not found?**
- Install Python 3.8+ from python.org

**pip not working?**
```bash
python -m pip install -r requirements.txt
```

**Port 5000 busy?**
Edit `app.py`, line at bottom:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Change to 5001
```

**Can't upload CSV?**
- Check file size < 16MB
- Ensure it's a .csv file
- Verify column names match exactly

---

### 🎯 Example CSV Content

```csv
Product_Name,Category,Price,Units_Sold
iPhone 15 Pro,Smartphone,999,850
Samsung Tab S9,Tablet,799,650
Apple Watch 9,Smartwatch,399,720
AirPods Pro,Earbuds,249,1200
Google Pixel 8,Smartphone,699,1100
iPad Air,Tablet,599,800
Noise Watch,Smartwatch,45,1500
boAt Earbuds,Earbuds,25,1800
```

Save this as `my_data.csv` and upload it!

---

### 🎨 Features You'll Love

- **Clean UI** - Modern, professional design
- **Fast Analysis** - Results in 2-5 seconds
- **Visual Charts** - Beautiful, publication-ready graphs
- **Optimal Pricing** - AI tells you the best price!
- **Mobile Friendly** - Works on phones and tablets

---

### 📧 Need Help?

- Check README.md for detailed documentation
- Review app.py comments for technical details
- Ensure all files are in correct folders

---

**Happy Analyzing! 🎉**

Built at SR University, Warangal | 2026
