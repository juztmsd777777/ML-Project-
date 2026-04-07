from pathlib import Path
import base64
import io

from flask import Flask, jsonify, render_template, request
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

matplotlib.use("Agg")

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATASET = BASE_DIR / "sample_data.csv"

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (10, 6)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data_source = "uploaded file"
        if "file" in request.files and request.files["file"].filename:
            uploaded_file = request.files["file"]
            df = pd.read_csv(uploaded_file)
            source_label = uploaded_file.filename
        else:
            df = load_default_dataset()
            data_source = "built-in retail sample"
            source_label = DEFAULT_DATASET.name

        required_cols = ["Product_Name", "Category", "Price", "Units_Sold"]
        if not all(col in df.columns for col in required_cols):
            return (
                jsonify(
                    {
                        "error": (
                            "CSV must have columns: Product_Name, Category, Price, Units_Sold"
                        )
                    }
                ),
                400,
            )

        df = clean_dataset(df)
        raw_observations = int(len(df))
        df = aggregate_dataset(df)
        if len(df) < 10:
            return jsonify({"error": "Need at least 10 valid data points"}), 400

        products = sorted(df["Product_Name"].unique().tolist())
        categories = sorted(df["Category"].unique().tolist())
        baseline_product = products[0]
        baseline_category = categories[0]

        X, feature_names = build_feature_matrix(
            df, products, categories, baseline_product, baseline_category
        )
        y = df["Units_Sold"].astype(float)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        model = Ridge(alpha=5.0)
        model.fit(X_train, y_train)

        y_train_pred = model.predict(X_train)
        y_test_pred = model.predict(X_test)

        train_r2 = r2_score(y_train, y_train_pred)
        test_r2 = r2_score(y_test, y_test_pred)
        test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
        test_mae = mean_absolute_error(y_test, y_test_pred)

        coefficients = build_coefficients(model, feature_names, baseline_product)
        product_profiles, curves_data, optimal_prices = build_product_outputs(
            df, model, products, baseline_product
        )
        charts = generate_charts(df, curves_data, product_profiles)

        response = {
            "meta": {
                "dataset_name": source_label,
                "data_source": data_source,
                "model_name": "Regularized product-wise pricing model",
                "baseline_product": baseline_product,
                "baseline_category": baseline_category,
                "records_analyzed": int(len(df)),
                "raw_observations": raw_observations,
            },
            "metrics": {
                "train_r2": round(train_r2, 4),
                "test_r2": round(test_r2, 4),
                "rmse": round(test_rmse, 2),
                "mae": round(test_mae, 2),
            },
            "coefficients": coefficients,
            "optimal_prices": optimal_prices,
            "product_profiles": product_profiles,
            "curves": curves_data,
            "charts": charts,
            "highlights": build_highlights(df, optimal_prices, product_profiles),
            "insights": build_insights(df, optimal_prices, product_profiles, test_r2),
            "data_summary": {
                "total_observations": int(len(df)),
                "unique_products": int(df["Product_Name"].nunique()),
                "categories": df["Category"].value_counts().to_dict(),
                "price_range": [
                    round(float(df["Price"].min()), 2),
                    round(float(df["Price"].max()), 2),
                ],
                "demand_range": [
                    int(df["Units_Sold"].min()),
                    int(df["Units_Sold"].max()),
                ],
            },
        }

        return jsonify(response)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


def load_default_dataset():
    if DEFAULT_DATASET.exists():
        return pd.read_csv(DEFAULT_DATASET)
    return create_sample_data()


def clean_dataset(df):
    cleaned = df.copy()
    cleaned = cleaned.dropna(subset=["Product_Name", "Category", "Price", "Units_Sold"])
    cleaned["Category"] = cleaned["Category"].astype(str).str.strip()
    cleaned["Product_Name"] = cleaned["Product_Name"].astype(str).str.strip()
    cleaned["Price"] = pd.to_numeric(cleaned["Price"], errors="coerce")
    cleaned["Units_Sold"] = pd.to_numeric(cleaned["Units_Sold"], errors="coerce")
    cleaned = cleaned.dropna(subset=["Price", "Units_Sold"])
    cleaned = cleaned[(cleaned["Price"] > 0) & (cleaned["Units_Sold"] > 0)]
    return cleaned.reset_index(drop=True)


def aggregate_dataset(df):
    return (
        df.groupby(["Product_Name", "Category", "Price"], as_index=False)["Units_Sold"]
        .sum()
        .sort_values(["Category", "Product_Name", "Price"])
        .reset_index(drop=True)
    )


def build_feature_matrix(df, products, categories, baseline_product, baseline_category):
    features = pd.DataFrame({"Price": df["Price"].astype(float)})
    feature_names = ["Price"]

    for category in categories:
        if category == baseline_category:
            continue

        category_col = f"Category_{category}"
        category_price_col = f"Price_x_Category_{category}"
        category_values = (df["Category"] == category).astype(int)
        features[category_col] = category_values
        features[category_price_col] = df["Price"] * category_values
        feature_names.extend([category_col, category_price_col])

    for product in products:
        if product == baseline_product:
            continue

        indicator_col = f"Product_{product}"
        indicator_values = (df["Product_Name"] == product).astype(int)
        features[indicator_col] = indicator_values
        feature_names.append(indicator_col)

    return features, feature_names


def build_coefficients(model, feature_names, baseline_product):
    named_coefficients = {"Intercept": round(float(model.intercept_), 4)}
    for index, feature_name in enumerate(feature_names):
        named_coefficients[feature_name] = round(float(model.coef_[index]), 4)

    named_coefficients["Baseline Product"] = baseline_product
    return named_coefficients


def build_product_outputs(df, model, products, baseline_product):
    product_profiles = {}
    curves_data = {}
    optimal_prices = {}

    base_intercept = float(model.intercept_)
    coef_lookup = {}
    feature_index = 0
    coef_lookup["Price"] = float(model.coef_[feature_index])
    feature_index += 1

    categories = sorted(df["Category"].unique().tolist())
    baseline_category = categories[0]
    for category in categories:
        if category == baseline_category:
            continue
        coef_lookup[f"Category_{category}"] = float(model.coef_[feature_index])
        coef_lookup[f"Price_x_Category_{category}"] = float(model.coef_[feature_index + 1])
        feature_index += 2

    for product in products:
        if product == baseline_product:
            continue
        coef_lookup[f"Product_{product}"] = float(model.coef_[feature_index])
        feature_index += 1

    global_demand_cap = float(df["Units_Sold"].quantile(0.95) * 1.35)

    for product in products:
        product_rows = df[df["Product_Name"] == product]
        category = product_rows["Category"].mode().iat[0]
        price_min = float(product_rows["Price"].min())
        price_max = float(product_rows["Price"].max())
        price_mean = float(product_rows["Price"].mean())
        median_price = float(product_rows["Price"].median())
        average_demand = float(product_rows["Units_Sold"].mean())
        unique_prices = int(product_rows["Price"].nunique())

        if unique_prices <= 1:
            observed_range = max(price_mean * 0.1, 5)
            curve_min = max(1.0, price_mean - observed_range)
            curve_max = price_mean + observed_range
        else:
            observed_range = price_max - price_min
            curve_min = max(1.0, price_min - observed_range * 0.15)
            curve_max = price_max + observed_range * 0.15

        price_range = np.linspace(curve_min, curve_max, 120)

        product_intercept = (
            base_intercept
            + coef_lookup.get(f"Category_{category}", 0.0)
            + coef_lookup.get(f"Product_{product}", 0.0)
        )
        product_slope = coef_lookup["Price"] + coef_lookup.get(
            f"Price_x_Category_{category}", 0.0
        )

        demand_cap = max(
            float(product_rows["Units_Sold"].max()) * 1.25,
            float(product_rows["Units_Sold"].mean()) * 1.4,
            global_demand_cap,
        )
        demand_pred = np.clip(
            product_intercept + (product_slope * price_range),
            0,
            demand_cap,
        )
        revenue = price_range * demand_pred

        optimal_index = int(np.argmax(revenue))
        optimal_price = float(price_range[optimal_index])
        optimal_demand = float(demand_pred[optimal_index])
        optimal_revenue = float(revenue[optimal_index])

        reference_demand = float(
            np.clip(
                product_intercept + (product_slope * median_price),
                1.0,
                demand_cap,
            )
        )
        elasticity = product_slope * median_price / reference_demand
        sensitivity_band = classify_sensitivity(elasticity)
        current_average_revenue = float((product_rows["Price"] * product_rows["Units_Sold"]).mean())
        improvement = optimal_revenue - current_average_revenue

        if unique_prices <= 1:
            optimal_price = price_mean
            optimal_demand = float(np.clip(average_demand, 0, demand_cap))
            optimal_revenue = optimal_price * optimal_demand
            improvement = optimal_revenue - current_average_revenue
            sensitivity_band = "Low confidence: limited price variation"
            elasticity = 0.0

        curves_data[product] = {
            "prices": round_list(price_range),
            "demands": round_list(demand_pred),
            "revenues": round_list(revenue),
        }

        optimal_prices[product] = {
            "price": round(optimal_price, 2),
            "demand": round(optimal_demand),
            "revenue": round(optimal_revenue, 2),
        }

        product_profiles[product] = {
            "category": category,
            "avg_price": round(float(product_rows["Price"].mean()), 2),
            "avg_units": round(average_demand),
            "observations": int(len(product_rows)),
            "observed_min": round(price_min, 2),
            "observed_max": round(price_max, 2),
            "price_slope": round(product_slope, 4),
            "elasticity": round(float(elasticity), 4),
            "sensitivity_band": sensitivity_band,
            "optimal_price": round(optimal_price, 2),
            "optimal_revenue": round(optimal_revenue, 2),
            "current_revenue": round(current_average_revenue, 2),
            "revenue_uplift": round(improvement, 2),
            "unique_prices": unique_prices,
        }

    return product_profiles, curves_data, optimal_prices


def classify_sensitivity(elasticity):
    magnitude = abs(elasticity)
    if magnitude >= 1.2:
        return "Highly price sensitive"
    if magnitude >= 0.75:
        return "Balanced response"
    return "Relatively price resilient"


def build_highlights(df, optimal_prices, product_profiles):
    current_revenue = float((df["Price"] * df["Units_Sold"]).sum())
    best_product = max(
        optimal_prices.items(), key=lambda item: item[1]["revenue"]
    )[0]
    most_sensitive_product = min(
        product_profiles.items(), key=lambda item: item[1]["elasticity"]
    )[0]
    category_revenue = (df["Price"] * df["Units_Sold"]).groupby(df["Category"]).sum()
    best_category = category_revenue.idxmax()

    return {
        "current_market_revenue": round(current_revenue, 2),
        "average_price": round(float(df["Price"].mean()), 2),
        "average_units": round(float(df["Units_Sold"].mean())),
        "best_revenue_product": best_product,
        "most_sensitive_product": most_sensitive_product,
        "top_category": best_category,
    }


def build_insights(df, optimal_prices, product_profiles, test_r2):
    best_product, best_offer = max(
        optimal_prices.items(), key=lambda item: item[1]["revenue"]
    )
    most_sensitive_product, most_sensitive_profile = min(
        product_profiles.items(), key=lambda item: item[1]["elasticity"]
    )
    most_resilient_product, resilient_profile = max(
        product_profiles.items(), key=lambda item: item[1]["elasticity"]
    )

    return [
        (
            f"{best_product} has the strongest modeled revenue opportunity, with an "
            f"estimated sweet spot near ${best_offer['price']}."
        ),
        (
            f"{most_sensitive_product} is the most price-sensitive product in this dataset, "
            f"so discounting or overpricing will move demand more sharply."
        ),
        (
            f"{most_resilient_product} appears more resilient to pricing shifts, "
            f"with an elasticity of {resilient_profile['elasticity']}."
        ),
        (
            f"The model explains about {round(test_r2 * 100, 1)}% of the holdout variance, "
            f"which is solid enough for directional pricing exploration."
        ),
        (
            f"The dataset spans {int(df['Product_Name'].nunique())} products across "
            f"{len(df['Category'].unique())} categories, giving the dashboard a broader market view."
        ),
    ]


def generate_charts(df, curves_data, product_profiles):
    charts = {}
    colors = {
        "Smartphone": "#f97316",
        "Tablet": "#06b6d4",
        "Smartwatch": "#22c55e",
        "Earbuds": "#f43f5e",
    }

    plt.figure(figsize=(12, 7))
    for category in sorted(df["Category"].unique()):
        cat_rows = df[df["Category"] == category]
        plt.scatter(
            cat_rows["Price"],
            cat_rows["Units_Sold"],
            label=category,
            alpha=0.75,
            s=95,
            color=colors.get(category, "#64748b"),
            edgecolors="#0f172a",
            linewidth=0.4,
        )
    plt.xlabel("Observed Price ($)", fontsize=12, fontweight="bold")
    plt.ylabel("Units Sold", fontsize=12, fontweight="bold")
    plt.title("Observed Price vs Demand Landscape", fontsize=15, fontweight="bold")
    plt.legend()
    plt.grid(True, alpha=0.25)
    charts["scatter"] = fig_to_base64(plt.gcf())
    plt.close()

    featured_products = sorted(
        product_profiles.items(),
        key=lambda item: item[1]["optimal_revenue"],
        reverse=True,
    )[:6]

    plt.figure(figsize=(14, 8))
    for product, profile in featured_products:
        plt.plot(
            curves_data[product]["prices"],
            curves_data[product]["demands"],
            linewidth=3,
            label=shorten_label(product, 22),
            color=colors.get(profile["category"], "#64748b"),
        )
    plt.xlabel("Candidate Price ($)", fontsize=12, fontweight="bold")
    plt.ylabel("Predicted Demand", fontsize=12, fontweight="bold")
    plt.title("Product Demand Curves for Top Opportunities", fontsize=15, fontweight="bold")
    plt.legend()
    plt.grid(True, alpha=0.25)
    charts["curves"] = fig_to_base64(plt.gcf())
    plt.close()

    revenue_products = sorted(
        product_profiles.items(),
        key=lambda item: item[1]["optimal_revenue"],
        reverse=True,
    )[:10]
    product_names = [shorten_label(product, 26) for product, _ in revenue_products][::-1]
    optimal_revenues = [profile["optimal_revenue"] for _, profile in revenue_products][::-1]
    bar_colors = [colors.get(profile["category"], "#64748b") for _, profile in revenue_products][::-1]

    plt.figure(figsize=(13, 8))
    bars = plt.barh(product_names, optimal_revenues, color=bar_colors)
    plt.xlabel("Estimated Optimal Revenue ($)", fontsize=12, fontweight="bold")
    plt.title("Revenue Headroom by Product", fontsize=15, fontweight="bold")
    plt.grid(True, axis="x", alpha=0.25)
    for bar, revenue in zip(bars, optimal_revenues):
        plt.text(
            bar.get_width(),
            bar.get_y() + bar.get_height() / 2,
            f"${revenue:,.0f}",
            ha="left",
            va="center",
            fontsize=10,
            fontweight="bold",
        )
    charts["revenue"] = fig_to_base64(plt.gcf())
    plt.close()

    return charts


def round_list(values, digits=2):
    return [round(float(value), digits) for value in values]


def shorten_label(value, limit=26):
    if len(value) <= limit:
        return value
    return f"{value[: limit - 1]}..."


def fig_to_base64(fig):
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=100, bbox_inches="tight")
    buffer.seek(0)
    image_string = base64.b64encode(buffer.read()).decode("utf-8")
    buffer.close()
    return image_string


def create_sample_data():
    np.random.seed(42)
    data = []

    products = {
        "Smartphone": [
            ("Redmi Note 11 Pro", 260),
            ("Nokia 150", 30),
            ("Samsung Galaxy M13", 180),
            ("Redmi A1", 75),
            ("OnePlus Nord CE", 220),
        ],
        "Tablet": [("Wacom Drawing Tablet", 40), ("Lenovo Tab M8", 90)],
        "Smartwatch": [
            ("Fire-Boltt Gladiator", 45),
            ("Noise ColorFit Pro", 35),
            ("boAt Xtend", 50),
        ],
        "Earbuds": [
            ("Boult Audio Omega", 25),
            ("JBL C100SI", 22),
            ("Infinity Glide", 18),
        ],
    }

    for category, product_list in products.items():
        for product_name, base_price in product_list:
            for _ in range(np.random.randint(4, 6)):
                price = base_price * np.random.uniform(0.85, 1.15)

                if category == "Smartphone":
                    demand = int(
                        (1500 / (price + 20)) * 180 * np.random.uniform(0.85, 1.15)
                    )
                elif category == "Tablet":
                    demand = int(
                        (1200 / (price + 15)) * 120 * np.random.uniform(0.85, 1.15)
                    )
                elif category == "Smartwatch":
                    demand = int(
                        (1600 / (price + 10)) * 90 * np.random.uniform(0.85, 1.15)
                    )
                else:
                    demand = int(
                        (2000 / (price + 5)) * 80 * np.random.uniform(0.85, 1.15)
                    )

                demand = max(400, min(demand, 2200))

                data.append(
                    {
                        "Product_Name": product_name,
                        "Category": category,
                        "Price": round(price, 2),
                        "Units_Sold": demand,
                    }
                )

    return pd.DataFrame(data)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
