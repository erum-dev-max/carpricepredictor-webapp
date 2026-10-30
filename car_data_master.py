# ─── Master Car Database — All Pakistani Market Makes & Models ───────────────
# Structure: { "Make": { "Model": (base_price_pkr, engine_cc) } }

CAR_DATABASE = {

    # ── TOYOTA ────────────────────────────────────────────────────────────────
    "Toyota": {
        "Corolla Gli":          (5500000,  1600),
        "Corolla Xli":          (4800000,  1300),
        "Corolla Altis":        (7500000,  1800),
        "Corolla Cross":       (10000000,  1800),
        "Yaris GLI":            (5200000,  1300),
        "Yaris ATIV":           (4500000,  1000),
        "Fortuner":            (16000000,  2700),
        "Fortuner Legender":   (19000000,  2800),
        "Hilux Revo":          (13000000,  2800),
        "Hilux Single Cab":     (9000000,  2500),
        "Land Cruiser":        (55000000,  4000),
        "Prado TXL":           (23000000,  2700),
        "Prado VX":            (28000000,  4000),
        "Vitz F":               (3200000,  1000),
        "Vitz RS":              (3800000,  1300),
        "Rush":                (10000000,  1500),
        "Raize":                (8500000,  1000),
        "Avanza":               (6500000,  1500),
        "Camry":               (17000000,  2500),
    },

    # ── HONDA ─────────────────────────────────────────────────────────────────
    "Honda": {
        "City 1.2":             (4500000,  1200),
        "City 1.5 Aspire":      (5500000,  1500),
        "City 1.5 ADAS":        (6000000,  1500),
        "Civic Oriel":          (8000000,  1500),
        "Civic RS Turbo":      (10500000,  1500),
        "Civic eHEV":          (14000000,  2000),
        "BR-V S":               (6500000,  1500),
        "BR-V V":               (7500000,  1500),
        "HR-V":                (11000000,  1800),
        "WR-V":                 (8000000,  1500),
        "Accord":              (18000000,  2000),
        "Freed":                (5000000,  1500),
        "N-Wagon":              (3200000,   660),
        "N-Box":                (4200000,   660),
        "N-One":                (3500000,   660),
    },

    # ── SUZUKI ────────────────────────────────────────────────────────────────
    "Suzuki": {
        "Alto VX":              (2600000,  660),
        "Alto VXR":             (3000000,  660),
        "Alto AGS":             (3300000,  660),
        "Cultus VXR":           (3500000, 1000),
        "Cultus AGS":           (4000000, 1000),
        "Swift GL":             (4200000, 1200),
        "Swift GLX":            (4800000, 1200),
        "Swift Automatic":      (5200000, 1200),
        "Wagon R VXL":          (3200000,  660),
        "Wagon R AGS":          (3600000,  660),
        "Mehran VX":            (1000000,  800),
        "Mehran VXR":           (1200000,  800),
        "Bolan":                (1400000,  800),
        "Ravi":                 (1200000,  800),
        "Jimny":               (10000000, 1500),
        "Vitara":               (9500000, 1600),
        "APV":                  (3500000, 1600),
        "Every":                (3200000,  660),
    },

    # ── KIA ───────────────────────────────────────────────────────────────────
    "Kia": {
        "Picanto Manual":       (3200000, 1000),
        "Picanto Automatic":    (3600000, 1000),
        "Sportage Alpha":       (8000000, 2000),
        "Sportage FWD":         (9000000, 2000),
        "Sportage AWD":        (10500000, 2000),
        "Stonic":               (6500000, 1000),
        "Sorento":             (14000000, 2500),
        "Carnival":            (17000000, 2500),
        "Stinger":             (22000000, 3300),
        "Telluride":           (25000000, 3500),
        "EV6":                 (25000000,    0),
    },

    # ── HYUNDAI ───────────────────────────────────────────────────────────────
    "Hyundai": {
        "Tucson FWD":           (9500000, 2000),
        "Tucson AWD":          (11000000, 2000),
        "Elantra":              (8000000, 2000),
        "Sonata":              (14000000, 2500),
        "Santa Fe":            (18000000, 2500),
        "Creta":                (7500000, 1500),
        "Grand i10":            (3500000, 1000),
        "Ioniq 5":             (28000000,    0),
    },

    # ── MG ────────────────────────────────────────────────────────────────────
    "MG": {
        "HS STD":               (6000000, 1500),
        "HS Excite":            (6800000, 1500),
        "HS Trophy":            (7500000, 2000),
        "ZS":                   (4500000, 1500),
        "ZS EV":               (10000000,    0),
        "RX5":                  (7000000, 2000),
        "GT":                   (5500000, 1500),
        "Gloster":             (14000000, 2000),
    },

    # ── CHANGAN ───────────────────────────────────────────────────────────────
    "Changan": {
        "Alsvin Comfort":       (2800000, 1000),
        "Alsvin Lumiere":       (3200000, 1500),
        "Alsvin Lumiere CVT":   (3600000, 1500),
        "Oshan X7":             (6500000, 1500),
        "Uni-T":                (5500000, 1500),
        "Uni-V":                (5000000, 1500),
        "Karvaan":              (3000000, 1500),
        "M9":                  (25000000, 3000),
    },

    # ── PROTON ────────────────────────────────────────────────────────────────
    "Proton": {
        "Saga Standard":        (2200000, 1300),
        "Saga Premium":         (2600000, 1300),
        "X70 Standard":         (5500000, 1800),
        "X70 Executive":        (6500000, 1800),
        "X70 Premium":          (7500000, 1800),
        "Ertiga":               (4000000, 1500),
    },

    # ── PRINCE (DFSK) ─────────────────────────────────────────────────────────
    "Prince": {
        "Pearl":                (1300000,  800),
        "Prince 1.3":           (1500000, 1300),
        "EC-Star":              (1600000, 1000),
    },

    # ── UNITED ────────────────────────────────────────────────────────────────
    "United": {
        "Bravo":                (1400000,  800),
        "Alpha":                (1600000, 1000),
        "US-300":               (2200000, 1000),
        "US-700":               (2800000, 1300),
    },

    # ── FAW ───────────────────────────────────────────────────────────────────
    "FAW": {
        "V2 Comfort":           (1800000, 1000),
        "V2 Culture":           (2100000, 1000),
        "Carrier":              (1500000,  800),
        "Sirius":               (2500000, 1300),
    },

    # ── ISUZU ─────────────────────────────────────────────────────────────────
    "Isuzu": {
        "D-Max Standard":       (6000000, 2500),
        "D-Max LS":             (7000000, 3000),
        "D-Max V-Cross":        (8500000, 3000),
        "MU-X":                 (9500000, 3000),
    },

    # ── DAIHATSU ──────────────────────────────────────────────────────────────
    "Daihatsu": {
        "Mira ES":              (3000000,  660),
        "Mira L":               (3400000,  660),
        "Move":                 (3600000,  660),
        "Cuore":                (1800000,  800),
        "Coure CX":             (1500000,  800),
        "Hijet":                (2500000,  660),
        "Rocky":                (7500000, 1000),
    },

    # ── MITSUBISHI ────────────────────────────────────────────────────────────
    "Mitsubishi": {
        "Lancer GLX":           (2800000, 1600),
        "Outlander":            (8000000, 2400),
        "Pajero":              (12000000, 3800),
        "Eclipse Cross":        (8500000, 1500),
        "ASX":                  (6000000, 2000),
    },

    # ── NISSAN ────────────────────────────────────────────────────────────────
    "Nissan": {
        "Dayz":                 (1900000,  660),
        "Moco":                 (1800000,  660),
        "Juke":                 (5500000, 1600),
        "X-Trail":              (8000000, 2000),
        "Patrol":              (20000000, 4000),
        "Navara":               (8500000, 2500),
    },

    # ── MAZDA ─────────────────────────────────────────────────────────────────
    "Mazda": {
        "Carol":                (1800000,  660),
        "Mazda 2":              (3000000, 1500),
        "Mazda 3":              (5000000, 2000),
        "CX-3":                 (5500000, 2000),
        "CX-5":                 (8000000, 2500),
    },

    # ── SUBARU ────────────────────────────────────────────────────────────────
    "Subaru": {
        "Pleo":                 (2100000,  660),
        "Forester":             (7000000, 2000),
        "Outback":              (9000000, 2500),
        "XV":                   (6500000, 2000),
    },

    # ── BMW ───────────────────────────────────────────────────────────────────
    "BMW": {
        "3 Series 320i":       (12000000, 2000),
        "5 Series 520i":       (18000000, 2000),
        "7 Series 730i":       (35000000, 3000),
        "X1":                  (12000000, 2000),
        "X3":                  (18000000, 2000),
        "X5":                  (30000000, 3000),
        "X7":                  (45000000, 4400),
    },

    # ── MERCEDES-BENZ ─────────────────────────────────────────────────────────
    "Mercedes-Benz": {
        "C-Class C200":        (15000000, 2000),
        "E-Class E200":        (22000000, 2000),
        "S-Class S450":        (60000000, 3000),
        "GLE 450":             (35000000, 3000),
        "GLS 450":             (50000000, 3000),
        "A-Class A200":        (12000000, 1300),
    },

    # ── AUDI ──────────────────────────────────────────────────────────────────
    "Audi": {
        "A3":                  (12000000, 1400),
        "A4":                  (18000000, 2000),
        "A6":                  (28000000, 3000),
        "Q3":                  (15000000, 2000),
        "Q5":                  (25000000, 2000),
        "Q7":                  (40000000, 3000),
    },
}

# ── Engine CC options (all valid options for dropdown) ────────────────────────
ENGINE_CC_OPTIONS = [660, 800, 1000, 1200, 1300, 1500, 1600, 1800,
                     2000, 2400, 2500, 2700, 2800, 3000, 3300, 3500,
                     3800, 4000, 4400, 5000, 5700, 6500, 8000, 8400]

# CC premium factor — higher CC = higher price multiplier
CC_PRICE_FACTOR = {
    660:  0.82,  800:  0.87,  1000: 0.92,  1200: 0.95,
    1300: 0.97,  1500: 1.00,  1600: 1.03,  1800: 1.06,
    2000: 1.10,  2400: 1.16,  2500: 1.20,  2700: 1.25,
    2800: 1.28,  3000: 1.35,  3300: 1.42,  3500: 1.48,
    3800: 1.55,  4000: 1.65,  4400: 1.75,  5000: 1.90,
    5700: 2.10,  6500: 2.35,  8000: 2.80,  8400: 3.00,
}

# ── Fuel preferences ─────────────────────────────────────────────────────────
DIESEL_MODELS = {
    "Hilux Revo", "Hilux Single Cab", "D-Max Standard",
    "D-Max LS", "D-Max V-Cross", "MU-X",
    "Land Cruiser", "Prado TXL", "Prado VX",
    "Fortuner", "Fortuner Legender", "Navara"
}

# ── Automatic-heavy models ────────────────────────────────────────────────────
AUTO_HEAVY_MODELS = {
    "Civic Oriel", "Civic RS Turbo", "Civic eHEV",
    "Corolla Altis", "Corolla Cross",
    "Fortuner", "Fortuner Legender", "Land Cruiser",
    "Prado TXL", "Prado VX",
    "Sportage Alpha", "Sportage FWD", "Sportage AWD",
    "Tucson FWD", "Tucson AWD",
    "HS STD", "HS Excite", "HS Trophy",
    "Alsvin Lumiere CVT", "Wagon R AGS", "Cultus AGS", "Alto AGS",
    "X70 Premium", "X70 Executive",
    "3 Series 320i", "5 Series 520i", "7 Series 730i",
    "C-Class C200", "E-Class E200", "S-Class S450",
    "A4", "A6", "Q5", "Q7",
}

# ── Helper functions ──────────────────────────────────────────────────────────
def get_all_makes():
    return sorted(CAR_DATABASE.keys())

def get_models_for_make(make):
    return sorted(CAR_DATABASE.get(make, {}).keys())

def get_base_price(make, model):
    entry = CAR_DATABASE.get(make, {}).get(model, (3000000, 1500))
    return entry[0]

def get_engine_cc(make, model):
    """Return the default engine CC for a given make/model."""
    entry = CAR_DATABASE.get(make, {}).get(model, (3000000, 1500))
    return entry[1]

def get_cc_factor(cc):
    """Return the price multiplier for a given engine CC."""
    return CC_PRICE_FACTOR.get(cc, 1.00)
