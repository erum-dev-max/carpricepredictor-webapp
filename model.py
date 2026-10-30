import pandas as pd
import numpy as np
import pickle
import os
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
from car_data_master import get_base_price, get_cc_factor, get_engine_cc

ACCIDENT_PARTS = [
    "Front Gates", "Rear Gates", "Roof", "Bonnet",
    "Fenders", "Front Bumper", "Rear Bumper",
    "Grille & Front Panels", "Trunk Lid",
    "Windshield", "Side Mirrors"
]
FAILED_PARTS = [
    "Tires", "Brakes", "Steering System",
    "Suspension Components", "Headlights & Signal Lights"
]


def load_and_preprocess(filepath="dataset/car_data.csv"):
    df = pd.read_csv(filepath)

    # ── Use ONLY real PakWheels data for training ─────────────────────────────
    if "data_source" in df.columns:
        real_df = df[df["data_source"] == "PakWheels Real"].copy()
        syn_df  = df[df["data_source"] != "PakWheels Real"].copy()
        # Weight real data 4x by repeating it
        df = pd.concat([real_df] * 4 + [syn_df], ignore_index=True)
        print(f"  Training mix: {len(real_df)*4} real (4x weighted) + {len(syn_df)} synthetic = {len(df)} rows")

    # ── Derived features ──────────────────────────────────────────────────────
    df["car_age"]          = df["year_selling"]   - df["year_bought"]
    df["manufacture_age"]  = df["year_selling"]   - df["year_manufactured"]
    df["years_before_buy"] = df["year_bought"]    - df["year_manufactured"]
    df["car_age"]          = df["car_age"].clip(lower=0)
    df["manufacture_age"]  = df["manufacture_age"].clip(lower=0)
    df["years_before_buy"] = df["years_before_buy"].clip(lower=0)

    df["num_accident_parts"] = df["accident_parts"].apply(
        lambda x: len(str(x).split(", ")) if pd.notna(x) and str(x).strip() not in ("", "nan") else 0
    )
    df["num_failed_parts"] = df["failed_parts"].apply(
        lambda x: len(str(x).split(", ")) if pd.notna(x) and str(x).strip() not in ("", "nan") else 0
    )

    # ── Log-transform price to reduce skew ───────────────────────────────────
    df["log_price"] = np.log1p(df["price_pkr"])

    # ── Encode categoricals ───────────────────────────────────────────────────
    le_make = LabelEncoder()
    le_model = LabelEncoder()
    le_color = LabelEncoder()
    le_fuel = LabelEncoder()
    le_transmission = LabelEncoder()

    df["make_enc"]         = le_make.fit_transform(df["make"].fillna("Unknown"))
    df["model_enc"]        = le_model.fit_transform(df["model"].fillna("Unknown"))
    df["color_enc"]        = le_color.fit_transform(df["color"].fillna("White"))
    df["fuel_enc"]         = le_fuel.fit_transform(df["fuel"].fillna("Petrol"))
    df["transmission_enc"] = le_transmission.fit_transform(df["transmission"].fillna("Manual"))

    features = [
        "make_enc", "model_enc", "color_enc",
        "fuel_enc", "transmission_enc",
        "engine_cc",
        "year_manufactured", "year_bought", "year_selling",
        "car_age", "manufacture_age", "years_before_buy",
        "km_driven", "accident",
        "num_accident_parts", "num_failed_parts",
        "base_price"
    ]

    X = df[features]
    y = df["price_pkr"]

    encoders = {
        "make":         le_make,
        "model":        le_model,
        "color":        le_color,
        "fuel":         le_fuel,
        "transmission": le_transmission,
    }

    return X, y, encoders, df


def train_model():
    print("Loading dataset...")
    X, y, encoders, df = load_and_preprocess()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # ── Gradient Boosting — handles real-world data better than Random Forest ─
    print("Training Gradient Boosting model...")
    model = GradientBoostingRegressor(
        n_estimators=500,
        learning_rate=0.05,
        max_depth=6,
        min_samples_split=5,
        min_samples_leaf=3,
        subsample=0.8,
        max_features="sqrt",
        random_state=42,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mae  = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2   = r2_score(y_test, y_pred)

    print("\n========== Model Performance ==========")
    print(f"  R² Score  : {r2:.4f}  ({r2*100:.2f}%)")
    print(f"  MAE       : PKR {mae:,.0f}  ({mae/100000:.2f} Lakh)")
    print(f"  RMSE      : PKR {rmse:,.0f}  ({rmse/100000:.2f} Lakh)")
    print("========================================\n")

    cv_scores = cross_val_score(model, X, y, cv=5, scoring="r2")
    print(f"Cross-Validation R² (5-fold): {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

    os.makedirs("model", exist_ok=True)
    with open("model/car_price_model.pkl", "wb") as f:
        pickle.dump({
            "model":    model,
            "encoders": encoders,
            "features": list(X.columns),
            "metrics": {
                "r2":      round(r2, 4),
                "mae":     round(mae, 2),
                "rmse":    round(rmse, 2),
                "cv_mean": round(cv_scores.mean(), 4),
                "cv_std":  round(cv_scores.std(), 4),
            },
            "algorithm": "GradientBoostingRegressor"
        }, f, protocol=4)  # protocol=4 compatible with Python 3.8+

    print("\nModel saved to model/car_price_model.pkl")
    return model, encoders


def load_model():
    with open("model/car_price_model.pkl", "rb") as f:
        data = pickle.load(f)
    return data["model"], data["encoders"], data.get("metrics", {})


def predict_price(
    make, model_name, color, fuel, transmission,
    engine_cc,
    year_manufactured, year_bought, year_selling,
    km_driven, accident,
    accident_parts: list, failed_parts: list
):
    model_obj, encoders, _ = load_model()

    car_age          = max(0, year_selling - year_bought)
    manufacture_age  = max(0, year_selling - year_manufactured)
    years_before_buy = max(0, year_bought  - year_manufactured)

    # Use master DB engine CC if user passed 0
    if engine_cc == 0:
        engine_cc = get_engine_cc(make, model_name)

    def safe_encode(enc, val):
        try:
            return enc.transform([val])[0]
        except ValueError:
            # Unknown label — use most similar known value
            return 0

    base_p = get_base_price(make, model_name)

    features = pd.DataFrame([{
        "make_enc":          safe_encode(encoders["make"],         make),
        "model_enc":         safe_encode(encoders["model"],        model_name),
        "color_enc":         safe_encode(encoders["color"],        color),
        "fuel_enc":          safe_encode(encoders["fuel"],         fuel),
        "transmission_enc":  safe_encode(encoders["transmission"], transmission),
        "engine_cc":         engine_cc,
        "year_manufactured": year_manufactured,
        "year_bought":       year_bought,
        "year_selling":      year_selling,
        "car_age":           car_age,
        "manufacture_age":   manufacture_age,
        "years_before_buy":  years_before_buy,
        "km_driven":         km_driven,
        "accident":          int(accident),
        "num_accident_parts":len(accident_parts),
        "num_failed_parts":  len(failed_parts),
        "base_price":        base_p,
    }])

    predicted_price = model_obj.predict(features)[0]
    # Floor at 50,000 PKR
    return round(max(50000, predicted_price), -3)


if __name__ == "__main__":
    train_model()
