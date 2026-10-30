"""
PakWheels Used Car Scraper — v3
Normalizes make/model names to match car_data_master.py so the ML model
can encode them correctly.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re, os, time, random
from car_data_master import CAR_DATABASE, get_base_price, get_engine_cc

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.pakwheels.com/",
}
BASE_URL = "https://www.pakwheels.com/used-cars/search/-/?page={}"

# ── Make name normalisation ───────────────────────────────────────────────────
MAKE_ALIASES = {
    "toyota":      "Toyota",   "honda":     "Honda",    "suzuki":   "Suzuki",
    "kia":         "Kia",      "hyundai":   "Hyundai",  "mg":       "MG",
    "changan":     "Changan",  "proton":    "Proton",   "prince":   "Prince",
    "united":      "United",   "faw":       "FAW",      "isuzu":    "Isuzu",
    "daihatsu":    "Daihatsu", "mitsubishi":"Mitsubishi","nissan":  "Nissan",
    "mazda":       "Mazda",    "subaru":    "Subaru",   "bmw":      "BMW",
    "mercedes":    "Mercedes-Benz", "mercedes-benz":"Mercedes-Benz",
    "audi":        "Audi",     "haval":     "Haval",    "ford":     "Ford",
    "chevrolet":   "Chevrolet","jeep":      "Jeep",     "gmc":      "GMC",
    "lexus":       "Lexus",    "land":      "Land Rover","byd":     "BYD",
    "chery":       "Chery",    "jaecoo":    "Jaecoo",   "jetour":   "Jetour",
}

# ── Map raw PakWheels model keywords → our database model names ──────────────
MODEL_MAP = {
    # Toyota
    "corolla gli":         ("Toyota", "Corolla Gli"),
    "corolla xli":         ("Toyota", "Corolla Xli"),
    "corolla altis":       ("Toyota", "Corolla Altis"),
    "corolla cross":       ("Toyota", "Corolla Cross"),
    "corolla":             ("Toyota", "Corolla Gli"),   # fallback
    "yaris ativ":          ("Toyota", "Yaris ATIV"),
    "yaris gli":           ("Toyota", "Yaris GLI"),
    "yaris":               ("Toyota", "Yaris GLI"),
    "fortuner legender":   ("Toyota", "Fortuner Legender"),
    "fortuner":            ("Toyota", "Fortuner"),
    "hilux revo":          ("Toyota", "Hilux Revo"),
    "hilux":               ("Toyota", "Hilux Revo"),
    "land cruiser":        ("Toyota", "Land Cruiser"),
    "prado txl":           ("Toyota", "Prado TXL"),
    "prado vx":            ("Toyota", "Prado VX"),
    "prado":               ("Toyota", "Prado TXL"),
    "vitz rs":             ("Toyota", "Vitz RS"),
    "vitz f":              ("Toyota", "Vitz F"),
    "vitz":                ("Toyota", "Vitz F"),
    "raize":               ("Toyota", "Raize"),
    "rush":                ("Toyota", "Rush"),
    "camry":               ("Toyota", "Camry"),
    "aqua":                ("Toyota", "Yaris GLI"),     # similar price range
    "avanza":              ("Toyota", "Avanza"),
    # Honda
    "city 1.2":            ("Honda", "City 1.2"),
    "city 1.5":            ("Honda", "City 1.5 Aspire"),
    "city aspire":         ("Honda", "City 1.5 Aspire"),
    "city":                ("Honda", "City 1.5 Aspire"),
    "civic rs turbo":      ("Honda", "Civic RS Turbo"),
    "civic oriel":         ("Honda", "Civic Oriel"),
    "civic 1.8":           ("Honda", "Civic Oriel"),
    "civic exi":           ("Honda", "Civic Oriel"),
    "civic vti":           ("Honda", "Civic Oriel"),
    "civic":               ("Honda", "Civic Oriel"),
    "br-v":                ("Honda", "BR-V S"),
    "brv":                 ("Honda", "BR-V S"),
    "hr-v":                ("Honda", "HR-V"),
    "hrv":                 ("Honda", "HR-V"),
    "accord":              ("Honda", "Accord"),
    "freed":               ("Honda", "Freed"),
    "n-wagon":             ("Honda", "N-Wagon"),
    "n-box":               ("Honda", "N-Box"),
    "n-one":               ("Honda", "N-One"),
    # Suzuki
    "alto vxr":            ("Suzuki", "Alto VXR"),
    "alto vxl":            ("Suzuki", "Alto VXR"),
    "alto ags":            ("Suzuki", "Alto AGS"),
    "alto":                ("Suzuki", "Alto VX"),
    "cultus vxr":          ("Suzuki", "Cultus VXR"),
    "cultus ags":          ("Suzuki", "Cultus AGS"),
    "cultus":              ("Suzuki", "Cultus VXR"),
    "swift dlx":           ("Suzuki", "Swift GLX"),
    "swift glx":           ("Suzuki", "Swift GLX"),
    "swift gl":            ("Suzuki", "Swift GL"),
    "swift":               ("Suzuki", "Swift GL"),
    "wagon r ags":         ("Suzuki", "Wagon R AGS"),
    "wagon r vxl":         ("Suzuki", "Wagon R VXL"),
    "wagon r":             ("Suzuki", "Wagon R VXL"),
    "mehran vxr":          ("Suzuki", "Mehran VXR"),
    "mehran vx":           ("Suzuki", "Mehran VX"),
    "mehran":              ("Suzuki", "Mehran VX"),
    "bolan":               ("Suzuki", "Bolan"),
    "ravi":                ("Suzuki", "Ravi"),
    "jimny":               ("Suzuki", "Jimny"),
    "vitara":              ("Suzuki", "Vitara"),
    "every":               ("Suzuki", "Every"),
    "apv":                 ("Suzuki", "APV"),
    # Kia
    "picanto":             ("Kia", "Picanto Automatic"),
    "sportage alpha":      ("Kia", "Sportage Alpha"),
    "sportage awd":        ("Kia", "Sportage AWD"),
    "sportage fwd":        ("Kia", "Sportage FWD"),
    "sportage":            ("Kia", "Sportage FWD"),
    "stonic":              ("Kia", "Stonic"),
    "sorento":             ("Kia", "Sorento"),
    "carnival":            ("Kia", "Carnival"),
    # Hyundai
    "tucson awd":          ("Hyundai", "Tucson AWD"),
    "tucson fwd":          ("Hyundai", "Tucson FWD"),
    "tucson":              ("Hyundai", "Tucson FWD"),
    "elantra":             ("Hyundai", "Elantra"),
    "santro":              ("Hyundai", "Grand i10"),
    "creta":               ("Hyundai", "Creta"),
    "grand i10":           ("Hyundai", "Grand i10"),
    "sonata":              ("Hyundai", "Sonata"),
    "santa fe":            ("Hyundai", "Santa Fe"),
    # Daihatsu
    "rocky":               ("Daihatsu", "Rocky"),
    "mira":                ("Daihatsu", "Mira ES"),
    "move":                ("Daihatsu", "Move"),
    "cuore":               ("Daihatsu", "Cuore"),
    "hijet":               ("Daihatsu", "Hijet"),
    # Nissan
    "dayz":                ("Nissan", "Dayz"),
    "moco":                ("Nissan", "Moco"),
    "juke":                ("Nissan", "Juke"),
    "x-trail":             ("Nissan", "X-Trail"),
    "patrol":              ("Nissan", "Patrol"),
    "navara":              ("Nissan", "Navara"),
    # Mitsubishi
    "lancer":              ("Mitsubishi", "Lancer GLX"),
    "outlander":           ("Mitsubishi", "Outlander"),
    "pajero":              ("Mitsubishi", "Pajero"),
    "eclipse cross":       ("Mitsubishi", "Eclipse Cross"),
    "asx":                 ("Mitsubishi", "ASX"),
    # Mazda
    "carol":               ("Mazda", "Carol"),
    "mazda 2":             ("Mazda", "Mazda 2"),
    "mazda 3":             ("Mazda", "Mazda 3"),
    "cx-3":                ("Mazda", "CX-3"),
    "cx-5":                ("Mazda", "CX-5"),
    # Others
    "pleo":                ("Subaru", "Pleo"),
    "forester":            ("Subaru", "Forester"),
    "3 series":            ("BMW", "3 Series 320i"),
    "5 series":            ("BMW", "5 Series 520i"),
    "7 series":            ("BMW", "7 Series 730i"),
    "x1":                  ("BMW", "X1"),
    "x3":                  ("BMW", "X3"),
    "x5":                  ("BMW", "X5"),
    "x7":                  ("BMW", "X7"),
    "c-class":             ("Mercedes-Benz", "C-Class C200"),
    "e-class":             ("Mercedes-Benz", "E-Class E200"),
    "s-class":             ("Mercedes-Benz", "S-Class S450"),
    "gle":                 ("Mercedes-Benz", "GLE 450"),
    "a-class":             ("Mercedes-Benz", "A-Class A200"),
    "a4":                  ("Audi", "A4"),
    "a6":                  ("Audi", "A6"),
    "q5":                  ("Audi", "Q5"),
    "q7":                  ("Audi", "Q7"),
    "alsvin":              ("Changan", "Alsvin Lumiere"),
    "uni-t":               ("Changan", "Uni-T"),
    "oshan":               ("Changan", "Oshan X7"),
    "hs":                  ("MG", "HS STD"),
    "zs":                  ("MG", "ZS"),
    "saga":                ("Proton", "Saga Standard"),
    "x70":                 ("Proton", "X70 Standard"),
    "jolion":              ("Changan", "Uni-T"),       # Haval → closest
    "d-max":               ("Isuzu", "D-Max LS"),
    "mu-x":                ("Isuzu", "MU-X"),
    "v2":                  ("FAW", "V2 Culture"),
}

COLOUR_MAP = {
    "white": "White", "pearl": "Pearl White", "silver": "Silver",
    "grey": "Grey",  "gray": "Grey",          "black": "Black",
    "red": "Red",    "blue": "Blue",           "brown": "Brown",
    "golden": "Golden", "gold": "Golden",      "green": "Green",
    "maroon": "Maroon", "champagne": "Champagne", "beige": "Champagne",
    "navy": "Blue",  "orange": "Red",          "yellow": "Golden",
}

# ── Helpers ──────────────────────────────────────────────────────────────────
def norm_make(raw: str) -> str:
    return MAKE_ALIASES.get(raw.lower().strip(), raw.strip().title())

def match_model(title_lower: str):
    """Try to match title to a known (make, model) pair from MODEL_MAP."""
    # Try longest match first
    for key in sorted(MODEL_MAP.keys(), key=len, reverse=True):
        if key in title_lower:
            return MODEL_MAP[key]
    return None

def parse_price(text: str):
    m = re.search(r"PKR\s*([\d,\.]+)\s*(lacs?|lakhs?|crore|cr)?", text, re.I)
    if not m:
        return None
    num  = float(m.group(1).replace(",", ""))
    unit = (m.group(2) or "").lower()
    if "crore" in unit or unit == "cr":
        return round(num * 10_000_000)
    if "lac" in unit or "lakh" in unit:
        return round(num * 100_000)
    if num > 100_000:
        return round(num)
    if num < 1000:
        return round(num * 100_000)
    return round(num)

def parse_cc(text: str) -> int:
    m = re.search(r"(\d+)\s*cc", text, re.I)
    if m:
        return int(m.group(1))
    if re.search(r"kwh|electric|ev", text, re.I):
        return 0
    return 0   # unknown → will use model default

def parse_km(text: str) -> int:
    m = re.search(r"([\d,]+)\s*km", text, re.I)
    return int(m.group(1).replace(",", "")) if m else 50000

def parse_year(text: str) -> int:
    m = re.search(r"\b(19[89]\d|20[012]\d)\b", text)
    return int(m.group()) if m else 2015

def parse_color(text: str) -> str:
    tl = text.lower()
    for k, v in COLOUR_MAP.items():
        if k in tl:
            return v
    return random.choice(["White", "Silver", "Black", "Grey"])

# ── Parse one card ───────────────────────────────────────────────────────────
def parse_card(card) -> dict | None:
    title_tag = card.select_one("a.car-name")
    if not title_tag:
        return None

    title      = title_tag.get_text(strip=True)
    title      = re.sub(r"\d+\.\d+/10", "", title)
    title      = re.sub(r"for Sale.*", "", title, flags=re.I).strip()
    title_lower = title.lower()
    full_text   = card.get_text(separator=" ", strip=True)

    # ── Match to known make/model ─────────────────────────────────────────
    match = match_model(title_lower)
    if match:
        make, model = match
    else:
        # Can't map → skip (keeps data quality high)
        return None

    # ── Price ────────────────────────────────────────────────────────────
    price = parse_price(full_text)
    if not price or price < 100_000:
        return None

    # ── Year ────────────────────────────────────────────────────────────
    year = parse_year(title + " " + full_text)

    # ── CC — use scraped value if available, else use master db default ──
    scraped_cc  = parse_cc(full_text)
    default_cc  = get_engine_cc(make, model)
    engine_cc   = scraped_cc if scraped_cc > 0 else default_cc

    # ── Other specs ──────────────────────────────────────────────────────
    fuel         = "Diesel" if "diesel" in full_text.lower() else "Petrol"
    transmission = "Automatic" if "automatic" in full_text.lower() else "Manual"
    color        = parse_color(full_text)
    km           = parse_km(full_text)

    year_manufactured = year
    year_bought       = min(year + random.randint(0, 2), 2026)
    year_selling      = 2024
    base_p            = get_base_price(make, model)

    return {
        "make":              make,
        "model":             model,
        "engine_cc":         engine_cc,
        "color":             color,
        "fuel":              fuel,
        "transmission":      transmission,
        "year_manufactured": year_manufactured,
        "year_bought":       year_bought,
        "year_selling":      year_selling,
        "km_driven":         km,
        "accident":          0,
        "accident_parts":    "",
        "failed_parts":      "",
        "base_price":        base_p,
        "price_pkr":         price,
        "data_source":       "PakWheels Real",
    }

# ── Scrape ───────────────────────────────────────────────────────────────────
def scrape_pakwheels(target=800, max_pages=45):
    session  = requests.Session()
    all_data = []
    print(f"\n🔍 PakWheels Scraper — Target: {target} matched listings")
    print("=" * 60)

    for page in range(1, max_pages + 1):
        if len(all_data) >= target:
            break
        url = BASE_URL.format(page)
        try:
            r = session.get(url, headers=HEADERS, timeout=25)
            r.raise_for_status()
        except Exception as e:
            print(f"  Page {page:3d} → ERROR: {e}")
            break

        soup    = BeautifulSoup(r.text, "lxml")
        cards   = soup.select("li.classified-listing")
        matched = 0
        for card in cards:
            rec = parse_card(card)
            if rec:
                all_data.append(rec)
                matched += 1

        print(f"  Page {page:3d} → {len(cards):2d} cards, {matched:2d} matched | Total: {len(all_data)}")
        if not cards:
            break
        time.sleep(random.uniform(1.2, 2.5))

    return pd.DataFrame(all_data)

# ── Clean ────────────────────────────────────────────────────────────────────
def clean(df):
    if df.empty: return df
    before = len(df)
    df = df.drop_duplicates(subset=["make","model","year_manufactured","km_driven"])
    df = df[df["price_pkr"].between(100_000, 200_000_000)]
    df = df[df["km_driven"].between(0, 500_000)]
    df = df[df["year_manufactured"].between(1990, 2026)]
    df = df[df["engine_cc"].between(0, 10_000)]
    print(f"\n✅ Cleaned: {before} → {len(df)} records")
    print(f"   Makes  : {df['make'].nunique()} | Models: {df['model'].nunique()}")
    print(f"   Price  : PKR {df['price_pkr'].min():,.0f} — PKR {df['price_pkr'].max():,.0f}")
    return df.reset_index(drop=True)

# ── Merge & save ─────────────────────────────────────────────────────────────
def merge_and_save(real_df, syn_path="dataset/car_data_synthetic.csv",
                   out_path="dataset/car_data.csv"):
    COLS = ["make","model","engine_cc","color","fuel","transmission",
            "year_manufactured","year_bought","year_selling",
            "km_driven","accident","accident_parts","failed_parts",
            "base_price","price_pkr","data_source"]
    for c in COLS:
        if c not in real_df.columns:
            real_df[c] = 0 if c in ("accident","engine_cc","km_driven","base_price","price_pkr") else ""

    real_df = real_df[COLS].copy()

    if os.path.exists(syn_path):
        syn = pd.read_csv(syn_path)
        syn["data_source"] = "Synthetic"
        merged = pd.concat([real_df, syn], ignore_index=True)
    else:
        merged = real_df

    os.makedirs("dataset", exist_ok=True)
    real_df.to_csv("dataset/pakwheels_scraped.csv", index=False)
    merged.to_csv(out_path, index=False)

    real_n = (merged["data_source"] == "PakWheels Real").sum()
    syn_n  = (merged["data_source"] == "Synthetic").sum()
    print(f"\n📊 Final Training Dataset: {len(merged)} rows")
    print(f"   🌐 PakWheels Real : {real_n}")
    print(f"   🤖 Synthetic      : {syn_n}")
    print(f"   💾 Saved → {out_path}")
    return merged

# ── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Back up current synthetic dataset if not already done
    import shutil
    syn_backup = "dataset/car_data_synthetic.csv"
    if not os.path.exists(syn_backup) and os.path.exists("dataset/car_data.csv"):
        orig = pd.read_csv("dataset/car_data.csv")
        syn_only = orig[orig.get("data_source", "Synthetic") == "Synthetic"] if "data_source" in orig.columns else orig
        syn_only.to_csv(syn_backup, index=False)
        print(f"📦 Synthetic backup saved: {syn_backup}")

    raw    = scrape_pakwheels(target=800, max_pages=45)
    clean_df = clean(raw)

    if clean_df.empty:
        print("\n❌ No data scraped.")
    else:
        merged = merge_and_save(clean_df)
        print("\n🎯 Now train the model:")
        print("   python model.py")
