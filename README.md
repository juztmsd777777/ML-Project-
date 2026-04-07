# 📊 Price Sensitivity Analysis System

A full-stack web application for analyzing price sensitivity and optimizing pricing strategies using machine learning.

## 🚀 Features

- **AI-Powered Analysis**: Linear regression model for demand prediction
- **Interactive Dashboard**: Real-time visualization of price sensitivity curves
- **Multi-Category Support**: Analyzes Smartphones, Tablets, Smartwatches, and Earbuds
- **Revenue Optimization**: Automatically identifies optimal pricing points
- **Beautiful UI**: Modern, responsive design with smooth animations
- **File Upload**: Supports CSV file uploads or sample data
- **Visual Analytics**: Multiple charts including scatter plots, validation plots, and sensitivity curves

## 🛠️ Tech Stack

**Backend:**
- Flask (Python web framework)
- pandas (Data manipulation)
- scikit-learn (Machine learning)
- matplotlib & seaborn (Visualizations)

**Frontend:**
- HTML5 & CSS3
- JavaScript (Vanilla)
- Modern responsive design
- Google Fonts (Inter)

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## 🔧 Installation

1. **Extract the ZIP folder**
   ```bash
   unzip price_sensitivity_app.zip
   cd price_sensitivity_app
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Open your browser**
   Navigate to: `http://localhost:5000`

## 📁 Project Structure

```
price_sensitivity_app/
│
├── app.py                  # Flask backend application
├── requirements.txt        # Python dependencies
├── README.md              # This file
│
├── templates/
│   └── index.html         # Main HTML template
│
└── static/
    ├── css/
    │   └── style.css      # Styling
    └── js/
        └── main.js        # JavaScript functionality
```

## 📊 Data Format

Your CSV file should have the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| Product_Name | Name of the product | iPhone 15 Pro |
| Category | Product category | Smartphone |
| Price | Price in USD | 999.00 |
| Units_Sold | Demand/sales quantity | 1500 |

**Supported Categories:**
- Smartphone
- Tablet
- Smartwatch
- Earbuds

**Sample CSV:**
```csv
Product_Name,Category,Price,Units_Sold
iPhone 15 Pro,Smartphone,999,850
Samsung Tab S9,Tablet,799,650
Apple Watch 9,Smartwatch,399,720
AirPods Pro,Earbuds,249,1200
```

## 🎯 How to Use

1. **Upload Data:**
   - Click on the upload box or drag & drop your CSV file
   - Or click "Use Sample Data" to try with built-in data

2. **Analyze:**
   - Click "Analyze Data" button
   - Wait for the ML model to process (usually 2-5 seconds)

3. **View Results:**
   - Dataset summary with statistics
   - Model performance metrics (R², RMSE, MAE)
   - Price vs Demand scatter plot
   - Model validation chart
   - Price sensitivity curves for all categories
   - Optimal pricing recommendations
   - Model coefficients with interpretations

## 📈 Model Details

**Algorithm:** Linear Regression with Categorical Encoding

**Features:**
- Price (continuous variable)
- Category (one-hot encoded)

**Target Variable:** Units_Sold (Demand)

**Model Equation:**
```
Demand = β₀ + β₁(Price) + β₂(Category_Smartphone) + β₃(Category_Tablet) + β₄(Category_Smartwatch) + β₅(Category_Earbuds) + ε
```

**Validation:**
- 80-20 train-test split
- Multiple performance metrics
- Visual validation through actual vs predicted plots

## 🎨 Features Highlights

### 1. Data Summary
- Total observations count
- Unique products
- Price and demand ranges
- Category distribution

### 2. Model Performance
- R² Score (measures model fit)
- RMSE (Root Mean Squared Error)
- MAE (Mean Absolute Error)
- Training vs Testing comparison

### 3. Visualizations
- **Scatter Plot**: Shows price-demand relationship across categories
- **Validation Plot**: Actual vs Predicted demand comparison
- **Sensitivity Curves**: Price sensitivity curves for each category

### 4. Optimal Pricing
- Revenue-maximizing price for each category
- Expected demand at optimal price
- Expected revenue calculation

### 5. Model Insights
- Coefficient values
- Interpretation of each coefficient
- Price elasticity information

## 🔐 Security

- File size limited to 16MB
- CSV format validation
- Data sanitization
- No data stored on server (session-based)

## 🐛 Troubleshooting

**Issue: ModuleNotFoundError**
- Solution: Run `pip install -r requirements.txt`

**Issue: Port 5000 already in use**
- Solution: Change port in `app.py`: `app.run(port=5001)`

**Issue: CSV upload fails**
- Solution: Ensure CSV has correct columns: Product_Name, Category, Price, Units_Sold

**Issue: Charts not displaying**
- Solution: Check if matplotlib is installed correctly

## 📝 License

This project is part of the ML research at SR University, Warangal.
Patent Pending - Invention Disclosure Form filed.

## 👥 Contributors

- Mohammed Eliyas
- Lade Gunakar Rao
- Marka Koushik Goud

**Institution:** SR University, Warangal, Telangana, India

## 📧 Contact

For questions or support, please contact the development team at SR University.

## 🎓 Academic Use

This system was developed as part of an ML project on **Dynamic Price Sensitivity Prediction System Using Multi-Category Linear Regression Analysis for Consumer Electronics**.

## 🚀 Future Enhancements

- [ ] Real-time dynamic pricing integration
- [ ] Deep learning models (LSTM, Transformers)
- [ ] Competitor price integration
- [ ] Customer segmentation analysis
- [ ] API endpoints for external integration
- [ ] Database integration for data persistence
- [ ] User authentication
- [ ] Export reports as PDF

## 📚 References

- scikit-learn Documentation
- Flask Documentation
- Price Elasticity Theory
- Revenue Optimization Techniques

---

**Built with ❤️ at SR University | 2026**
