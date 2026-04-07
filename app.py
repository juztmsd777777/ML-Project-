from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        # Get uploaded file or use sample data
        if 'file' in request.files and request.files['file'].filename:
            file = request.files['file']
            df = pd.read_csv(file)
        else:
            # Use sample data
            df = create_sample_data()
        
        # Validate columns
        required_cols = ['Product_Name', 'Category', 'Price', 'Units_Sold']
        if not all(col in df.columns for col in required_cols):
            return jsonify({'error': 'CSV must have columns: Product_Name, Category, Price, Units_Sold'}), 400
        
        # Clean data
        df = df.dropna()
        df = df[df['Price'] > 0]
        df = df[df['Units_Sold'] > 0]
        
        if len(df) < 10:
            return jsonify({'error': 'Need at least 10 valid data points'}), 400
        
        # Prepare data
        df_encoded = pd.get_dummies(df, columns=['Category'], drop_first=False)
        
        category_cols = [col for col in df_encoded.columns if col.startswith('Category_')]
        feature_cols = ['Price'] + category_cols
        
        X = df_encoded[feature_cols]
        y = df_encoded['Units_Sold']
        
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train model
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        # Predictions
        y_train_pred = model.predict(X_train)
        y_test_pred = model.predict(X_test)
        
        # Metrics
        train_r2 = r2_score(y_train, y_train_pred)
        test_r2 = r2_score(y_test, y_test_pred)
        test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
        test_mae = mean_absolute_error(y_test, y_test_pred)
        
        # Model coefficients
        coefficients = {
            'Intercept': float(model.intercept_),
            'Price': float(model.coef_[0])
        }
        for i, cat_col in enumerate(category_cols):
            coefficients[cat_col.replace('Category_', '')] = float(model.coef_[i + 1])
        
        # Generate price sensitivity curves
        categories = df['Category'].unique()
        price_min = df['Price'].min()
        price_max = df['Price'].max()
        price_range = np.linspace(price_min, price_max, 100)
        
        curves_data = {}
        optimal_prices = {}
        
        for category in categories:
            # Create feature matrix for this category
            X_curve = pd.DataFrame({'Price': price_range})
            for cat_col in category_cols:
                cat_name = cat_col.replace('Category_', '')
                X_curve[cat_col] = 1 if cat_name == category else 0
            
            # Predict demand
            demand_pred = model.predict(X_curve[feature_cols])
            
            # Calculate revenue
            revenue = price_range * demand_pred
            
            # Find optimal price
            optimal_idx = np.argmax(revenue)
            optimal_price = float(price_range[optimal_idx])
            optimal_demand = float(demand_pred[optimal_idx])
            optimal_revenue = float(revenue[optimal_idx])
            
            curves_data[category] = {
                'prices': price_range.tolist(),
                'demands': demand_pred.tolist()
            }
            
            optimal_prices[category] = {
                'price': round(optimal_price, 2),
                'demand': round(optimal_demand, 0),
                'revenue': round(optimal_revenue, 2)
            }
        
        # Generate visualizations
        charts = generate_charts(df, y_test, y_test_pred, curves_data, categories)
        
        # Prepare response
        response = {
            'metrics': {
                'train_r2': round(train_r2, 4),
                'test_r2': round(test_r2, 4),
                'rmse': round(test_rmse, 2),
                'mae': round(test_mae, 2)
            },
            'coefficients': coefficients,
            'optimal_prices': optimal_prices,
            'curves': curves_data,
            'charts': charts,
            'data_summary': {
                'total_observations': len(df),
                'unique_products': df['Product_Name'].nunique(),
                'categories': df['Category'].value_counts().to_dict(),
                'price_range': [round(df['Price'].min(), 2), round(df['Price'].max(), 2)],
                'demand_range': [int(df['Units_Sold'].min()), int(df['Units_Sold'].max())]
            }
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def create_sample_data():
    """Create sample data based on real patterns"""
    np.random.seed(42)
    data = []
    
    products = {
        'Smartphone': [
            ('Redmi Note 11 Pro', 260), ('Nokia 150', 30), ('Samsung Galaxy M13', 180),
            ('Redmi A1', 75), ('OnePlus Nord CE', 220)
        ],
        'Tablet': [
            ('Wacom Drawing Tablet', 40), ('Lenovo Tab M8', 90)
        ],
        'Smartwatch': [
            ('Fire-Boltt Gladiator', 45), ('Noise ColorFit Pro', 35), ('boAt Xtend', 50)
        ],
        'Earbuds': [
            ('Boult Audio Omega', 25), ('JBL C100SI', 22), ('Infinity Glide', 18)
        ]
    }
    
    for category, product_list in products.items():
        for product_name, base_price in product_list:
            for _ in range(np.random.randint(4, 6)):
                price = base_price * np.random.uniform(0.85, 1.15)
                
                # Inverse demand relationship
                if category == 'Smartphone':
                    demand = int((1500 / (price + 20)) * 180 * np.random.uniform(0.85, 1.15))
                elif category == 'Tablet':
                    demand = int((1200 / (price + 15)) * 120 * np.random.uniform(0.85, 1.15))
                elif category == 'Smartwatch':
                    demand = int((1600 / (price + 10)) * 90 * np.random.uniform(0.85, 1.15))
                else:  # Earbuds
                    demand = int((2000 / (price + 5)) * 80 * np.random.uniform(0.85, 1.15))
                
                demand = max(400, min(demand, 2200))
                
                data.append({
                    'Product_Name': product_name,
                    'Category': category,
                    'Price': round(price, 2),
                    'Units_Sold': demand
                })
    
    return pd.DataFrame(data)

def generate_charts(df, y_test, y_test_pred, curves_data, categories):
    """Generate base64 encoded charts"""
    charts = {}
    
    # 1. Price vs Demand Scatter
    plt.figure(figsize=(12, 7))
    colors = {'Smartphone': '#FF6B6B', 'Tablet': '#4ECDC4', 'Smartwatch': '#45B7D1', 'Earbuds': '#FFA07A'}
    for category in df['Category'].unique():
        cat_data = df[df['Category'] == category]
        plt.scatter(cat_data['Price'], cat_data['Units_Sold'], 
                   label=category, alpha=0.6, s=100, color=colors.get(category, '#999'))
    plt.xlabel('Price ($)', fontsize=12, fontweight='bold')
    plt.ylabel('Units Sold', fontsize=12, fontweight='bold')
    plt.title('Price vs Demand - All Categories', fontsize=14, fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3)
    charts['scatter'] = fig_to_base64(plt.gcf())
    plt.close()
    
    # 2. Actual vs Predicted
    plt.figure(figsize=(10, 7))
    plt.scatter(y_test, y_test_pred, alpha=0.6, s=100, color='#4ECDC4', edgecolors='black', linewidth=0.5)
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 
             'r--', lw=3, label='Perfect Prediction')
    plt.xlabel('Actual Units Sold', fontsize=12, fontweight='bold')
    plt.ylabel('Predicted Units Sold', fontsize=12, fontweight='bold')
    plt.title('Model Validation: Actual vs Predicted', fontsize=14, fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3)
    charts['validation'] = fig_to_base64(plt.gcf())
    plt.close()
    
    # 3. Price Sensitivity Curves
    plt.figure(figsize=(14, 8))
    for category in categories:
        prices = curves_data[category]['prices']
        demands = curves_data[category]['demands']
        plt.plot(prices, demands, linewidth=3, label=category, color=colors.get(category, '#999'))
    plt.xlabel('Price ($)', fontsize=13, fontweight='bold')
    plt.ylabel('Predicted Demand (Units)', fontsize=13, fontweight='bold')
    plt.title('Price Sensitivity Curves by Category', fontsize=15, fontweight='bold')
    plt.legend(fontsize=12)
    plt.grid(True, alpha=0.3)
    charts['curves'] = fig_to_base64(plt.gcf())
    plt.close()
    
    return charts

def fig_to_base64(fig):
    """Convert matplotlib figure to base64 string"""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    return img_str

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
