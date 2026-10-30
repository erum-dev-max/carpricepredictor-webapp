import pandas as pd
import numpy as np
import os
from car_data_master import (CAR_DATABASE, DIESEL_MODELS, AUTO_HEAVY_MODELS,
                              get_base_price, get_engine_cc, get_cc_factor)

np.random.seed(42)
n = 2000

COLORS = ["White", "Silver", "Black", "Red", "Blue", "Grey",
          "Brown", "Golden", "Green", "Maroon", "Pearl White", "Champagne"]

COLOR_FACTOR = {
    "White": 1.03, "Pearl White": 1.04, "Silver": 1.02, "Black": 1.01,
    "Red": 0.98,   "Blue": 0.99,        "Grey": 1.00,   "Brown": 0.97,
    "Golden": 1.01,"Champagne": 1.01,   "Green": 0.96,  "Maroon": 0.97
}

ACCIDENT_PARTS = [
    "Front Gates", "Rear Gates", "Roof", "Bonnet",
    "Fenders", "Front Bumper", "Rear Bumper",
    "Grille & Front Panels", "Trunk Lid", "Windshield", "Side Mirrors"
]
FAILED_PARTS = [
    "Tires", "Brakes", "Steering System",
    "Suspension Components", "Headlights & Signal Lights"
]

# ── Build pairs ───────────────────────────────────────────────────────────────
all_pairs = [(mk, mo) for mk, mods in CAR_DATABASE.items() for mo in mods]
sampled   = [all_pairs[i] for i in np.random.randint(0, len(all_pairs), size=n)]
makes     = [p[0] for p in sampled]
models    = [p[1] for p in sampled]

# ── Engine CC — use real CC for each model (with ±1 step noise occasionally) ─
engine_ccs = []
for mk, mo in sampled:
    real_cc = get_engine_cc(mk, mo)
    engine_ccs.append(real_cc)

# ── Years ─────────────────────────────────────────────────────────────────────
year_manufactured = np.random.randint(2000, 2025, size=n)
year_bought       = np.clip(year_manufactured + np.random.randint(0, 4, size=n),
                            year_manufactured, 2026)
year_selling      = np.clip(year_bought + np.random.randint(1, 9, size=n),
                            year_bought + 1, 2026)

km_driven = np.random.randint(5000, 280000, size=n)
accident  = np.random.choice([0, 1], size=n, p=[0.72, 0.28])
color     = np.random.choice(COLORS, size=n)

fuel = [
    np.random.choice(["Petrol","Diesel"], p=[0.20,0.80])
    if mo in DIESEL_MODELS
    else np.random.choice(["Petrol","Diesel"], p=[0.92,0.08])
    for mo in models
]

transmission = [
    np.random.choice(["Manual","Automatic"], p=[0.10,0.90])
    if mo in AUTO_HEAVY_MODELS
    else np.random.choice(["Manual","Automatic"], p=[0.60,0.40])
    for mo in models
]

accident_parts_col = [
    "" if acc == 0
    else ", ".join(np.random.choice(ACCIDENT_PARTS,
                   size=min(np.random.randint(1,5), len(ACCIDENT_PARTS)),
                   replace=False))
    for acc in accident
]

failed_parts_col = []
for _ in range(n):
    k = np.random.choice([0,0,0,1,1,2,3], p=[0.40,0.15,0.15,0.15,0.05,0.05,0.05])
    if k == 0:
        failed_parts_col.append("")
    else:
        failed_parts_col.append(
            ", ".join(np.random.choice(FAILED_PARTS,
                      size=min(k, len(FAILED_PARTS)), replace=False))
        )

# ── Price calculation ─────────────────────────────────────────────────────────
prices = []
for i in range(n):
    base      = get_base_price(makes[i], models[i])
    cc_factor = get_cc_factor(engine_ccs[i])
    total_age = int(year_selling[i]) - int(year_manufactured[i])

    price = base * cc_factor * (1 - 0.10) ** max(total_age, 0)

    km_penalty = max(0, (km_driven[i] - 50000) / 10000) * 0.01
    price *= (1 - km_penalty)

    num_acc  = len(accident_parts_col[i].split(", ")) if accident_parts_col[i] else 0
    price   *= (1 - 0.05 * num_acc)

    num_fail = len(failed_parts_col[i].split(", ")) if failed_parts_col[i] else 0
    price   *= (1 - 0.03 * num_fail)

    if fuel[i] == "Diesel":
        price *= 1.05
    if transmission[i] == "Automatic":
        price *= 1.08

    price *= COLOR_FACTOR.get(color[i], 1.00)

    noise = np.random.normal(0, price * 0.04)
    price = max(50000, price + noise)
    prices.append(round(price, -3))

base_prices_col = [get_base_price(makes[i], models[i]) for i in range(n)]

df = pd.DataFrame({
    "make":              makes,
    "model":             models,
    "engine_cc":         engine_ccs,
    "color":             color,
    "fuel":              fuel,
    "transmission":      transmission,
    "year_manufactured": year_manufactured,
    "year_bought":       year_bought,
    "year_selling":      year_selling,
    "km_driven":         km_driven,
    "accident":          accident,
    "accident_parts":    accident_parts_col,
    "failed_parts":      failed_parts_col,
    "base_price":        base_prices_col,
    "price_pkr":         prices
})

os.makedirs("dataset", exist_ok=True)
df.to_csv("dataset/car_data.csv", index=False)
print(f"Dataset generated: {len(df)} rows")
print(f"Makes: {df['make'].nunique()} | Models: {df['model'].nunique()}")
print(f"Engine CC range: {df['engine_cc'].min()} — {df['engine_cc'].max()}")
print(f"Price range: PKR {df['price_pkr'].min():,.0f} — PKR {df['price_pkr'].max():,.0f}")
