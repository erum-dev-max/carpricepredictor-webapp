import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os
import io
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors as rl_colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                 Table, TableStyle, HRFlowable)
from reportlab.lib.enums import TA_CENTER
from car_data_master import (get_all_makes, get_models_for_make,
                              get_base_price, get_engine_cc,
                              ENGINE_CC_OPTIONS, AUTO_HEAVY_MODELS,
                              DIESEL_MODELS, CC_PRICE_FACTOR)

# ─── Page Config — MUST be first Streamlit call ──────────────────────────────
st.set_page_config(
    page_title="Car Price Predictor Pakistan",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Now safe to import model functions ──────────────────────────────────────
from model import predict_price, load_model

# ─── CSS — clean, flat, no gradients, no emojis ──────────────────────────────
st.markdown("""
<style>
    /* ── Global ── */
    html, body, [class*="css"] { font-family: 'Segoe UI', Arial, sans-serif; }
    .main  { background-color: #f4f6f8; }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background-color: #1c2333;
        border-right: 1px solid #2a3347;
    }
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown h4 {
        color: #cfd8e3 !important;
    }
    [data-testid="stSidebar"] hr { border-color: #2a3347; }

    /* ── Page header with moving car ── */
    .page-header {
        background-color: #1c2333;
        padding: 28px 36px 20px 36px;
        border-radius: 6px;
        margin-bottom: 24px;
        overflow: hidden;
        position: relative;
    }
    .page-header h1 {
        color: #ffffff;
        font-size: 1.9rem;
        font-weight: 700;
        margin: 0 0 4px 0;
    }
    .page-header p {
        color: #8a9ab5;
        font-size: 0.92rem;
        margin: 0;
    }

    /* Moving road + car strip */
    .road-strip {
        margin-top: 18px;
        height: 44px;
        background-color: #141d2e;
        border-radius: 4px;
        position: relative;
        overflow: hidden;
    }
    /* Dashed road line */
    .road-strip::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 0;
        width: 200%;
        height: 3px;
        background: repeating-linear-gradient(
            to right,
            #3b7dd8 0px, #3b7dd8 40px,
            transparent 40px, transparent 80px
        );
        animation: road-scroll 1.2s linear infinite;
        transform: translateY(-50%);
    }
    @keyframes road-scroll {
        from { transform: translateX(0) translateY(-50%); }
        to   { transform: translateX(-80px) translateY(-50%); }
    }

    /* Car SVG moving across */
    .car-wrap {
        position: absolute;
        top: 50%;
        transform: translateY(-50%);
        animation: car-drive 6s linear infinite;
    }
    @keyframes car-drive {
        0%   { left: -120px; }
        100% { left: 105%; }
    }

    /* ── Animated counter cards ── */
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #dde3ec;
        border-radius: 6px;
        padding: 18px 16px;
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(59,125,216,0.12);
    }
    .metric-card h2 {
        color: #1c2333;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
    }
    .metric-card p {
        color: #6b7a99;
        margin: 4px 0 0 0;
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    /* ── Animated feature cards ── */
    .feat-card {
        background-color: #ffffff;
        border: 1px solid #dde3ec;
        border-left: 3px solid #3b7dd8;
        border-radius: 6px;
        padding: 20px;
        margin-bottom: 12px;
        min-height: 90px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        animation: fade-in-up 0.6s ease both;
    }
    .feat-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 18px rgba(59,125,216,0.10);
    }
    .feat-card h4 {
        color: #1c2333;
        font-size: 0.95rem;
        font-weight: 600;
        margin: 0 0 6px 0;
    }
    .feat-card p {
        color: #6b7a99;
        font-size: 0.85rem;
        margin: 0;
    }

    /* Stagger animation delay */
    .feat-card:nth-child(1) { animation-delay: 0.05s; }
    .feat-card:nth-child(2) { animation-delay: 0.12s; }
    .feat-card:nth-child(3) { animation-delay: 0.19s; }
    .feat-card:nth-child(4) { animation-delay: 0.26s; }
    .feat-card:nth-child(5) { animation-delay: 0.33s; }
    .feat-card:nth-child(6) { animation-delay: 0.40s; }

    @keyframes fade-in-up {
        from { opacity: 0; transform: translateY(18px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* ── Price result box ── */
    .price-box {
        background-color: #1c2333;
        border: 1px solid #2a3347;
        border-left: 4px solid #3b7dd8;
        border-radius: 6px;
        padding: 28px 24px;
        text-align: center;
        margin-top: 16px;
        animation: pop-in 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) both;
    }
    @keyframes pop-in {
        from { opacity: 0; transform: scale(0.92); }
        to   { opacity: 1; transform: scale(1); }
    }
    .price-box .label {
        color: #8a9ab5;
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 8px;
    }
    .price-box h1 {
        color: #ffffff;
        font-size: 2.6rem;
        font-weight: 700;
        margin: 0;
    }
    .price-box .lakh {
        color: #8a9ab5;
        font-size: 1rem;
        margin-top: 6px;
    }

    /* ── Pulse bar (live indicator) ── */
    .live-bar {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 6px;
        font-size: 0.78rem;
        color: #6b7a99;
    }
    .pulse-dot {
        width: 8px; height: 8px;
        background: #27ae60;
        border-radius: 50%;
        animation: pulse 1.4s ease-in-out infinite;
    }
    @keyframes pulse {
        0%, 100% { transform: scale(1);   opacity: 1; }
        50%       { transform: scale(1.5); opacity: 0.5; }
    }

    /* ── Step box ── */
    .step-box {
        background-color: #ffffff;
        border: 1px solid #dde3ec;
        border-radius: 6px;
        padding: 12px 16px;
        margin-bottom: 8px;
        animation: fade-in-up 0.5s ease both;
    }
    .step-num {
        display: inline-block;
        background-color: #3b7dd8;
        color: #ffffff;
        border-radius: 4px;
        width: 24px;
        height: 24px;
        line-height: 24px;
        text-align: center;
        font-weight: 700;
        font-size: 0.8rem;
        margin-right: 10px;
        flex-shrink: 0;
    }

    /* ── Tags ── */
    .tag {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 0.78rem;
        font-weight: 600;
        margin: 2px;
        border: 1px solid;
    }
    .tag-good    { background: #eaf4eb; color: #276130; border-color: #b6debb; }
    .tag-warn    { background: #fff8e1; color: #7a5a00; border-color: #fde68a; }
    .tag-bad     { background: #fdecea; color: #9b1c1c; border-color: #f5c6c6; }
    .tag-neutral { background: #eef2ff; color: #2d3a8c; border-color: #c7d2fe; }

    /* ── Divider ── */
    hr { border: none; border-top: 1px solid #dde3ec; margin: 20px 0; }

    /* ── Predict button ── */
    .stButton > button[kind="primary"] {
        background-color: #3b7dd8 !important;
        color: white !important;
        border: none !important;
        border-radius: 5px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        padding: 10px !important;
        transition: background-color 0.2s ease !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #2563c4 !important;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        color: #6b7a99;
    }
    .stTabs [aria-selected="true"] {
        color: #1c2333 !important;
        border-bottom-color: #3b7dd8 !important;
    }

    /* ── Stat counter animation ── */
    @keyframes count-up {
        from { opacity: 0; }
        to   { opacity: 1; }
    }

    /* ════════════════════════════════════════════════
       NIGHT CITY SCENE — header animation
    ════════════════════════════════════════════════ */
    .night-scene {
        position: relative;
        width: 100%;
        height: 220px;
        background: linear-gradient(180deg, #05080f 0%, #0b1120 50%, #141c30 100%);
        border-radius: 8px;
        overflow: hidden;
        margin-bottom: 22px;
    }

    /* Stars */
    .stars {
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background-image:
            radial-gradient(1px 1px at 10%  8%, #ffffff 0%, transparent 100%),
            radial-gradient(1px 1px at 22% 14%, #ffffff 0%, transparent 100%),
            radial-gradient(1px 1px at 35%  5%, #ffffff 0%, transparent 100%),
            radial-gradient(1px 1px at 50% 12%, #ffffff 0%, transparent 100%),
            radial-gradient(1px 1px at 65%  7%, #ffffff 0%, transparent 100%),
            radial-gradient(1px 1px at 78% 18%, #ffffff 0%, transparent 100%),
            radial-gradient(1px 1px at 90%  4%, #ffffff 0%, transparent 100%),
            radial-gradient(1.5px 1.5px at 15% 20%, #aec8ff 0%, transparent 100%),
            radial-gradient(1.5px 1.5px at 55% 22%, #aec8ff 0%, transparent 100%),
            radial-gradient(1.5px 1.5px at 88% 15%, #aec8ff 0%, transparent 100%);
        animation: twinkle 3s ease-in-out infinite alternate;
        opacity: 0.8;
    }
    .stars.s2 {
        background-image:
            radial-gradient(1px 1px at 5%  15%, #ffffff 0%, transparent 100%),
            radial-gradient(1px 1px at 30% 10%, #ffffff 0%, transparent 100%),
            radial-gradient(1px 1px at 45%  3%, #ffffff 0%, transparent 100%),
            radial-gradient(1px 1px at 72% 19%, #ffffff 0%, transparent 100%),
            radial-gradient(1px 1px at 95%  9%, #ffffff 0%, transparent 100%);
        animation: twinkle 4.5s ease-in-out infinite alternate-reverse;
        opacity: 0.5;
    }
    @keyframes twinkle {
        from { opacity: 0.4; }
        to   { opacity: 1.0; }
    }

    /* Buildings */
    .buildings {
        position: absolute;
        bottom: 55px;
        width: 100%;
        height: 170px;
    }
    .bld {
        position: absolute;
        bottom: 0;
        border-radius: 2px 2px 0 0;
    }
    /* Lit windows */
    .win {
        position: absolute;
        width: 5px; height: 5px;
        background: #f6d860;
        border-radius: 1px;
        animation: blink-win 4s ease-in-out infinite;
    }
    .win.w2 { animation-delay: 2s; background: #aecbf0; }
    @keyframes blink-win {
        0%,45%,55%,100% { opacity: 1; }
        50%              { opacity: 0.15; }
    }

    /* Used Car Sales sign */
    .sign-wrap {
        position: absolute;
        right: 12%;
        bottom: 55px;
        display: flex;
        flex-direction: column;
        align-items: center;
        z-index: 4;
    }
    .sign-pole {
        width: 3px;
        height: 40px;
        background: #4a5568;
    }
    .sign-box {
        background: #1a2a4a;
        border: 2px solid #3b7dd8;
        border-radius: 4px;
        padding: 5px 8px;
        text-align: center;
        font-size: 0.62rem;
        font-weight: 700;
        color: #7dd3fc;
        line-height: 1.4;
        position: relative;
        box-shadow: 0 0 10px rgba(59,125,216,0.5), 0 0 20px rgba(59,125,216,0.2);
        animation: sign-glow 2s ease-in-out infinite alternate;
    }
    .sign-light {
        position: absolute;
        top: -5px; left: 50%; transform: translateX(-50%);
        width: 5px; height: 5px;
        background: #fbbf24;
        border-radius: 50%;
        box-shadow: 0 0 6px #fbbf24;
        animation: light-pulse 1s ease-in-out infinite;
    }
    @keyframes sign-glow {
        from { box-shadow: 0 0 8px rgba(59,125,216,0.4), 0 0 16px rgba(59,125,216,0.15); }
        to   { box-shadow: 0 0 18px rgba(59,125,216,0.8), 0 0 30px rgba(59,125,216,0.35); }
    }
    @keyframes light-pulse {
        0%,100% { opacity: 1; transform: translateX(-50%) scale(1); }
        50%     { opacity: 0.5; transform: translateX(-50%) scale(1.4); }
    }

    /* Road */
    .road {
        position: absolute;
        bottom: 0; left: 0; right: 0;
        height: 58px;
        background: #0d1218;
        border-top: 2px solid #1e2d42;
        overflow: hidden;
    }
    .lane-marks {
        position: absolute;
        top: 50%;
        left: 0;
        height: 3px;
        width: 400%;
        background: repeating-linear-gradient(
            to right,
            #2a3f5c 0px, #2a3f5c 50px,
            transparent 50px, transparent 100px
        );
        transform: translateY(-50%);
        animation: road-move 1s linear infinite;
    }
    @keyframes road-move {
        from { transform: translateX(0) translateY(-50%); }
        to   { transform: translateX(-100px) translateY(-50%); }
    }

    /* Moving car */
    .car-anim {
        position: absolute;
        bottom: 6px;
        animation: drive-across 7s linear infinite;
        z-index: 5;
    }
    @keyframes drive-across {
        0%   { left: -160px; }
        100% { left: 110%;  }
    }
    /* Headlight beam */
    .beam {
        position: absolute;
        right: -60px;
        top: 22px;
        width: 70px;
        height: 18px;
        background: linear-gradient(to right, rgba(255,249,196,0.6), transparent);
        clip-path: polygon(0 25%, 100% 0%, 100% 100%, 0 75%);
        pointer-events: none;
    }

    /* Text overlay */
    .scene-text {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        text-align: center;
        z-index: 10;
        pointer-events: none;
    }
    .scene-title {
        color: #ffffff;
        font-size: 1.7rem;
        font-weight: 700;
        text-shadow: 0 2px 12px rgba(0,0,0,0.9), 0 0 30px rgba(59,125,216,0.4);
        white-space: nowrap;
    }
    .scene-sub {
        color: #8ab4d4;
        font-size: 0.82rem;
        margin-top: 6px;
        text-shadow: 0 1px 6px rgba(0,0,0,0.8);
    }
</style>
""", unsafe_allow_html=True)

# ─── Constants ───────────────────────────────────────────────────────────────
COLORS = ["White", "Pearl White", "Silver", "Champagne", "Black",
          "Red", "Blue", "Grey", "Brown", "Golden", "Green", "Maroon"]
FUEL_TYPES    = ["Petrol", "Diesel"]
TRANSMISSIONS = ["Manual", "Automatic"]
ACCIDENT_PARTS = [
    "Front Gates", "Rear Gates", "Roof", "Bonnet", "Fenders",
    "Front Bumper", "Rear Bumper", "Grille & Front Panels",
    "Trunk Lid", "Windshield", "Side Mirrors"
]
FAILED_PARTS = [
    "Tires", "Brakes", "Steering System",
    "Suspension Components", "Headlights & Signal Lights"
]
ALL_MAKES = get_all_makes()

# ─── PDF Generator ───────────────────────────────────────────────────────────
def generate_pdf(data: dict) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles  = getSampleStyleSheet()
    title_s = ParagraphStyle("t", parent=styles["Title"], fontSize=18,
                              textColor=rl_colors.HexColor("#1c2333"),
                              alignment=TA_CENTER, spaceAfter=4)
    sub_s   = ParagraphStyle("s", parent=styles["Normal"], fontSize=9,
                              textColor=rl_colors.HexColor("#6b7a99"),
                              alignment=TA_CENTER, spaceAfter=14)
    head_s  = ParagraphStyle("h", parent=styles["Heading2"], fontSize=12,
                              textColor=rl_colors.HexColor("#1c2333"),
                              spaceBefore=14, spaceAfter=6)
    note_s  = ParagraphStyle("n", parent=styles["Normal"], fontSize=8,
                              textColor=rl_colors.HexColor("#999999"),
                              alignment=TA_CENTER, spaceBefore=18)
    story = []

    story.append(Paragraph("Car Price Prediction Report", title_s))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%B %d, %Y  %I:%M %p')}  |  Pakistan Used Car Market",
        sub_s))
    story.append(HRFlowable(width="100%", thickness=1,
                             color=rl_colors.HexColor("#3b7dd8"), spaceAfter=12))

    price_rows = [
        ["PREDICTED MARKET VALUE"],
        [f"PKR {data['price']:,.0f}"],
        [f"{data['price']/100000:.2f} Lakh Pakistani Rupees"],
        [f"Market Range:  PKR {data['price']*0.90:,.0f}  —  PKR {data['price']*1.10:,.0f}"]
    ]
    pt = Table(price_rows, colWidths=[16*cm])
    pt.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(0,0), rl_colors.HexColor("#1c2333")),
        ("BACKGROUND",   (0,1),(0,1), rl_colors.HexColor("#2a3a5c")),
        ("BACKGROUND",   (0,2),(0,2), rl_colors.HexColor("#eef4fd")),
        ("BACKGROUND",   (0,3),(0,3), rl_colors.HexColor("#eef4fd")),
        ("TEXTCOLOR",    (0,0),(0,1), rl_colors.white),
        ("TEXTCOLOR",    (0,2),(0,3), rl_colors.HexColor("#1c2333")),
        ("FONTNAME",     (0,0),(0,0), "Helvetica"),
        ("FONTSIZE",     (0,0),(0,0), 10),
        ("FONTNAME",     (0,1),(0,1), "Helvetica-Bold"),
        ("FONTSIZE",     (0,1),(0,1), 22),
        ("FONTNAME",     (0,2),(0,3), "Helvetica"),
        ("FONTSIZE",     (0,2),(0,3), 10),
        ("ALIGN",        (0,0),(-1,-1), "CENTER"),
        ("VALIGN",       (0,0),(-1,-1), "MIDDLE"),
        ("TOPPADDING",   (0,0),(-1,-1), 8),
        ("BOTTOMPADDING",(0,0),(-1,-1), 8),
    ]))
    story.append(pt)
    story.append(Spacer(1, 0.4*cm))

    bp = data.get("base_price", 0)
    if bp > 0:
        dep = max(0, (1 - data["price"]/bp)*100)
        story.append(Paragraph(
            f"Depreciated {dep:.1f}% from brand-new price of PKR {bp/100000:.1f} Lakh",
            ParagraphStyle("d", parent=styles["Normal"], fontSize=9,
                           textColor=rl_colors.HexColor("#c0392b"),
                           alignment=TA_CENTER, spaceAfter=10)))

    story.append(Paragraph("Car Details", head_s))
    rows = [
        ["Make", data["make"]], ["Model", data["model"]],
        ["Engine CC", f"{data['engine_cc']} cc"], ["Color", data["color"]],
        ["Fuel Type", data["fuel"]], ["Transmission", data["transmission"]],
        ["Year Manufactured", str(data["year_manufactured"])],
        ["Year Bought", str(data["year_bought"])],
        ["Year of Sale", str(data["year_selling"])],
        ["Owned For", f"{data['year_selling']-data['year_bought']} year(s)"],
        ["Total Car Age", f"{data['year_selling']-data['year_manufactured']} year(s)"],
        ["KM Driven", f"{data['km_driven']:,} km"],
    ]
    dt = Table([["Field", "Value"]] + rows, colWidths=[7*cm, 9*cm])
    dt.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(-1,0),  rl_colors.HexColor("#1c2333")),
        ("TEXTCOLOR",    (0,0),(-1,0),  rl_colors.white),
        ("FONTNAME",     (0,0),(-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",     (0,0),(-1,-1), 10),
        ("BACKGROUND",   (0,1),(-1,1),  rl_colors.HexColor("#f7f9fc")),
        ("BACKGROUND",   (0,2),(-1,2),  rl_colors.white),
        ("BACKGROUND",   (0,3),(-1,3),  rl_colors.HexColor("#f7f9fc")),
        ("BACKGROUND",   (0,4),(-1,4),  rl_colors.white),
        ("BACKGROUND",   (0,5),(-1,5),  rl_colors.HexColor("#f7f9fc")),
        ("BACKGROUND",   (0,6),(-1,6),  rl_colors.white),
        ("BACKGROUND",   (0,7),(-1,7),  rl_colors.HexColor("#f7f9fc")),
        ("BACKGROUND",   (0,8),(-1,8),  rl_colors.white),
        ("BACKGROUND",   (0,9),(-1,9),  rl_colors.HexColor("#f7f9fc")),
        ("BACKGROUND",   (0,10),(-1,10),rl_colors.white),
        ("BACKGROUND",   (0,11),(-1,11),rl_colors.HexColor("#f7f9fc")),
        ("BACKGROUND",   (0,12),(-1,12),rl_colors.white),
        ("GRID",         (0,0),(-1,-1), 0.5, rl_colors.HexColor("#dde3ec")),
        ("TOPPADDING",   (0,0),(-1,-1), 6),
        ("BOTTOMPADDING",(0,0),(-1,-1), 6),
        ("LEFTPADDING",  (0,0),(-1,-1), 8),
    ]))
    story.append(dt)

    story.append(Paragraph("Condition Report", head_s))
    cond_rows = [
        ["Accident History", "Yes" if data["accident"] else "No — Accident Free"],
        ["Damaged Body Parts", ", ".join(data["accident_parts"]) if data["accident_parts"] else "None"],
        ["Failed / Worn Parts", ", ".join(data["failed_parts"]) if data["failed_parts"] else "None"],
    ]
    ct = Table(cond_rows, colWidths=[7*cm, 9*cm])
    ct.setStyle(TableStyle([
        ("FONTSIZE",     (0,0),(-1,-1), 10),
        ("BACKGROUND",   (0,0),(-1,0),  rl_colors.HexColor("#f7f9fc")),
        ("BACKGROUND",   (0,1),(-1,1),  rl_colors.white),
        ("BACKGROUND",   (0,2),(-1,2),  rl_colors.HexColor("#f7f9fc")),
        ("GRID",         (0,0),(-1,-1), 0.5, rl_colors.HexColor("#dde3ec")),
        ("TOPPADDING",   (0,0),(-1,-1), 6),
        ("BOTTOMPADDING",(0,0),(-1,-1), 6),
        ("LEFTPADDING",  (0,0),(-1,-1), 8),
        ("FONTNAME",     (0,0),(0,-1),  "Helvetica-Bold"),
    ]))
    story.append(ct)

    story.append(HRFlowable(width="100%", thickness=0.5,
                             color=rl_colors.HexColor("#dde3ec"), spaceBefore=18))
    story.append(Paragraph(
        "Disclaimer: This report is AI-generated. Dataset based on PakWheels market research. "
        "Actual prices may vary. For informational purposes only.",
        note_s))
    story.append(Paragraph(
        "Pakistan Car Price Predictor  |  BS Project 2024  |  Gradient Boosting ML",
        ParagraphStyle("f", parent=styles["Normal"], fontSize=8,
                       textColor=rl_colors.HexColor("#aaaaaa"),
                       alignment=TA_CENTER, spaceBefore=4)))
    doc.build(story)
    return buf.getvalue()


# ─── Page Header — Night City Car Animation ──────────────────────────────────
st.markdown("""
<div class="night-scene">

  <!-- Sky & stars -->
  <div class="stars"></div>
  <div class="stars s2"></div>

  <!-- Buildings (back row) -->
  <div class="buildings back">
    <div class="bld" style="height:110px;width:38px;left:2%;background:#151c2e;"></div>
    <div class="bld" style="height:80px;width:28px;left:7%;background:#131929;"></div>
    <div class="bld" style="height:140px;width:48px;left:12%;background:#0e1520;"></div>
    <div class="bld" style="height:95px;width:32px;left:19%;background:#12182a;"></div>
    <div class="bld" style="height:160px;width:55px;left:26%;background:#0d1420;"></div>
    <div class="bld" style="height:75px;width:30px;left:33%;background:#141c2f;"></div>
    <div class="bld" style="height:130px;width:45px;left:40%;background:#0f1622;"></div>
    <div class="bld" style="height:100px;width:36px;left:48%;background:#111828;"></div>
    <div class="bld" style="height:150px;width:50px;left:55%;background:#0c1320;"></div>
    <div class="bld" style="height:85px;width:28px;left:62%;background:#131b2c;"></div>
    <div class="bld" style="height:120px;width:40px;left:68%;background:#10172a;"></div>
    <div class="bld" style="height:95px;width:32px;left:75%;background:#0e1422;"></div>
    <div class="bld" style="height:145px;width:48px;left:82%;background:#121926;"></div>
    <div class="bld" style="height:70px;width:26px;left:89%;background:#141c2e;"></div>
    <div class="bld" style="height:110px;width:38px;left:94%;background:#0d1420;"></div>
    <!-- building windows (lit) -->
    <div class="win" style="left:3%;bottom:82px;"></div>
    <div class="win" style="left:14%;bottom:108px;"></div>
    <div class="win" style="left:27%;bottom:120px;"></div>
    <div class="win w2" style="left:27%;bottom:100px;"></div>
    <div class="win" style="left:41%;bottom:95px;"></div>
    <div class="win w2" style="left:56%;bottom:115px;"></div>
    <div class="win" style="left:69%;bottom:88px;"></div>
    <div class="win w2" style="left:83%;bottom:110px;"></div>
  </div>

  <!-- Used Car Sales sign -->
  <div class="sign-wrap">
    <div class="sign-pole"></div>
    <div class="sign-box">
      <div class="sign-light"></div>
      USED CAR<br>SALES
    </div>
  </div>

  <!-- Road -->
  <div class="road">
    <div class="lane-marks"></div>
  </div>

  <!-- Moving car (isometric-ish SVG) -->
  <div class="car-anim">
    <svg width="130" height="56" viewBox="0 0 130 56" xmlns="http://www.w3.org/2000/svg">
      <!-- Shadow -->
      <ellipse cx="65" cy="52" rx="52" ry="5" fill="rgba(0,0,0,0.35)"/>
      <!-- Body -->
      <rect x="8" y="22" width="114" height="24" rx="5" fill="#5b8fc9"/>
      <!-- Roof / cabin -->
      <path d="M32 22 L46 6 L88 6 L102 22 Z" fill="#4a7ab5"/>
      <!-- Windshield -->
      <path d="M48 8 L44 22 L86 22 L84 8 Z" fill="#aecbf0" opacity="0.75"/>
      <!-- Side window -->
      <rect x="88" y="9" width="12" height="12" rx="2" fill="#aecbf0" opacity="0.7"/>
      <!-- Door lines -->
      <line x1="66" y1="22" x2="66" y2="46" stroke="#3a6491" stroke-width="1.5"/>
      <!-- Wheels -->
      <circle cx="32" cy="46" r="10" fill="#111827"/>
      <circle cx="32" cy="46" r="5"  fill="#2d3f5c"/>
      <circle cx="32" cy="46" r="2"  fill="#8a9ab5"/>
      <circle cx="98" cy="46" r="10" fill="#111827"/>
      <circle cx="98" cy="46" r="5"  fill="#2d3f5c"/>
      <circle cx="98" cy="46" r="2"  fill="#8a9ab5"/>
      <!-- Headlights glow -->
      <ellipse cx="120" cy="32" rx="10" ry="5" fill="#fffbe6" opacity="0.6"/>
      <rect x="118" y="27" width="8" height="10" rx="3" fill="#fff9c4"/>
      <!-- Tail light -->
      <rect x="5" y="28" width="6" height="8" rx="2" fill="#ff4444" opacity="0.9"/>
    </svg>
    <!-- headlight beam -->
    <div class="beam"></div>
  </div>

  <!-- Overlay text -->
  <div class="scene-text">
    <div class="scene-title">Car Price Predictor &mdash; Pakistan</div>
    <div class="scene-sub">AI-powered used car valuation &nbsp;&bull;&nbsp; 20 Makes &nbsp;&bull;&nbsp;
      Real PakWheels Data &nbsp;&bull;&nbsp; Gradient Boosting ML</div>
  </div>

</div>
""", unsafe_allow_html=True)

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Car Details")
    st.markdown("---")

    st.markdown("**Make & Model**")
    selected_make  = st.selectbox("Car Make", ALL_MAKES, label_visibility="collapsed")
    avail_models   = get_models_for_make(selected_make)
    selected_model = st.selectbox("Car Model", avail_models, label_visibility="collapsed")

    base_ref   = get_base_price(selected_make, selected_model)
    default_cc = get_engine_cc(selected_make, selected_model)
    st.caption(f"New price ref: PKR {base_ref/100000:.1f}L  |  Default CC: {default_cc} cc")

    st.markdown("---")
    st.markdown("**Specifications**")

    cc_index  = ENGINE_CC_OPTIONS.index(default_cc) if default_cc in ENGINE_CC_OPTIONS else 0
    engine_cc = st.selectbox(
        "Engine CC",
        options=ENGINE_CC_OPTIONS,
        index=cc_index,
        format_func=lambda x: f"{x} cc" if x > 0 else "Electric (0 cc)"
    )
    color        = st.selectbox("Color", COLORS)
    fuel         = st.selectbox("Fuel Type", FUEL_TYPES)
    transmission = st.selectbox("Transmission", TRANSMISSIONS)

    if engine_cc != default_cc:
        st.caption(f"Note: Default engine for this model is {default_cc} cc.")
    if selected_model in AUTO_HEAVY_MODELS and transmission == "Manual":
        st.warning(f"{selected_model} is typically Automatic. Manual reduces predicted value.")
    if selected_model in DIESEL_MODELS and fuel == "Petrol":
        st.warning(f"{selected_model} is typically Diesel.")

    st.markdown("---")
    st.markdown("**Year Info**")
    year_manufactured = st.slider("Year Manufactured", 2000, 2025, 2019)
    year_bought       = st.slider("Year Bought",       2000, 2026, 2021)
    year_selling      = st.slider("Year of Sale",      2001, 2026, 2024)

    yr_error = False
    if year_bought < year_manufactured:
        st.warning("Bought year cannot be before manufactured year.")
        yr_error = True
    if year_selling <= year_bought:
        st.warning("Sale year must be after bought year.")
        yr_error = True

    st.markdown("---")
    st.markdown("**Mileage**")
    km_driven = st.number_input("KM Driven", min_value=1000,
                                 max_value=500000, value=50000, step=1000)

    st.markdown("---")
    st.markdown("**Accident History**")
    accident_radio = st.radio("Had an accident?", ["No", "Yes"], horizontal=True)
    accident_val   = 1 if accident_radio == "Yes" else 0

    selected_accident_parts = []
    if accident_val == 1:
        st.markdown("Select damaged body parts:")
        cols_acc = st.columns(2)
        for idx, part in enumerate(ACCIDENT_PARTS):
            with cols_acc[idx % 2]:
                if st.checkbox(part, key=f"acc_{part}"):
                    selected_accident_parts.append(part)

    st.markdown("---")
    st.markdown("**Failed / Worn Parts**")
    st.caption("Parts needing repair or replacement:")
    selected_failed_parts = []
    for part in FAILED_PARTS:
        if st.checkbox(part, key=f"fail_{part}"):
            selected_failed_parts.append(part)

    st.markdown("---")
    predict_btn = st.button("Predict Price", use_container_width=True, type="primary")

# ─── Tabs ─────────────────────────────────────────────────────────────────────
tab0, tab1, tab2, tab3 = st.tabs(["About", "Prediction", "Dataset Insights", "Model Performance"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 0 — ABOUT
# ══════════════════════════════════════════════════════════════════════════════
with tab0:
    st.markdown("## About This Project")

    # Live indicator
    st.markdown("""
    <div class="live-bar">
        <div class="pulse-dot"></div>
        <span>Live PakWheels data &nbsp;|&nbsp; Model active &nbsp;|&nbsp;
        626 real listings trained</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        "This is an AI-powered web application that estimates the resale value of used cars "
        "in the Pakistani market. It is built as a BS Final Project using Gradient Boosting "
        "Machine Learning, trained on real PakWheels listings and synthetic data."
    )

    st.markdown("---")

    c1, c2, c3 = st.columns(3)
    features = [
        ("AI Prediction",      "Gradient Boosting model trained on real PakWheels data. Predicts used car prices in PKR with ~11% average error."),
        ("150+ Car Models",    "Covers Toyota, Honda, Suzuki, Kia, Hyundai, MG, Changan, Proton, BMW, Mercedes, Audi and more."),
        ("PDF Report",         "Download a professional PDF valuation report after prediction."),
        ("Engine CC",          "24 engine options from 660cc kei cars to 4400cc SUVs. Engine size directly impacts predicted value."),
        ("Damage Assessment",  "Select accident-damaged body parts and failed mechanical components for accurate price adjustment."),
        ("Visual Insights",    "Interactive charts on price trends, depreciation, engine CC, fuel type and market comparison."),
    ]
    for i, (title, desc) in enumerate(features):
        col = [c1, c2, c3][i % 3]
        with col:
            st.markdown(f"""
            <div class="feat-card">
                <h4>{title}</h4>
                <p>{desc}</p>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("## How to Use")
    steps = [
        ("1", "Select Car Make", "Choose the brand from the sidebar dropdown, e.g. Toyota, Honda, Suzuki."),
        ("2", "Select Car Model", "Pick the specific model variant, e.g. Corolla Gli, Civic Oriel."),
        ("3", "Set Specifications", "Choose engine CC (auto-filled), color, fuel type, and transmission."),
        ("4", "Enter Year and Mileage", "Set manufacture year, bought year, selling year, and total KM driven."),
        ("5", "Add Condition", "Mark any damaged body parts or failed mechanical parts if applicable."),
        ("6", "Predict and Download", "Click Predict Price, view the result, then download the PDF report."),
    ]
    for num, title, desc in steps:
        st.markdown(f"""
        <div style="background:#fff;border:1px solid #dde3ec;border-radius:5px;
                    padding:11px 15px;margin-bottom:7px;">
            <span class="step-num">{num}</span>
            <strong style="color:#1c2333;font-size:.92rem;">{title}</strong>
            <span style="color:#6b7a99;font-size:.88rem;margin-left:8px;">{desc}</span>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Factors that increase price**")
        st.markdown("""
- Higher engine CC (2000cc+ adds premium)
- Automatic transmission
- Diesel engine
- White or Silver color
- Recent manufacture year
- Low mileage
        """)
    with col2:
        st.markdown("**Factors that decrease price**")
        st.markdown("""
- Older manufacture year (10% per year)
- High mileage (over 50,000 km)
- Accident body damage (5% per part)
- Failed mechanical parts (3% per part)
- Green, Brown, or Maroon color
- Small engine (660cc)
        """)

    st.markdown("---")
    st.markdown("## Dataset Disclaimer")
    st.info(
        "The training dataset combines 626 real listings scraped from PakWheels.com "
        "with 2,000 synthetic records generated from PakWheels market research patterns. "
        "Actual transaction prices may vary due to negotiation, regional demand, "
        "documentation, import duties, and current market conditions. "
        "This tool is for educational and estimation purposes only."
    )

    st.markdown("---")
    st.markdown("## Technology Stack")
    tech_cols = st.columns(4)
    techs = [
        ("Python 3.x",     "Core language"),
        ("Scikit-learn",   "Gradient Boosting ML"),
        ("Streamlit",      "Web application"),
        ("Plotly",         "Interactive charts"),
        ("Pandas",         "Data processing"),
        ("NumPy",          "Numerical operations"),
        ("ReportLab",      "PDF generation"),
        ("BeautifulSoup",  "Web scraping"),
    ]
    for i, (name, desc) in enumerate(techs):
        with tech_cols[i % 4]:
            st.markdown(f"""
            <div class="feat-card" style="padding:14px;min-height:70px;">
                <h4>{name}</h4>
                <p>{desc}</p>
            </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — PREDICTION
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("### Car Summary")
        car_age   = year_selling - year_bought
        total_age = year_selling - year_manufactured

        summary_df = pd.DataFrame({
            "Detail": [
                "Make", "Model", "Engine CC", "Color",
                "Fuel Type", "Transmission",
                "Year Manufactured", "Year Bought", "Year of Sale",
                "Owned For", "Total Age", "KM Driven",
                "Accident History", "Damaged Parts", "Failed Parts"
            ],
            "Value": [
                selected_make, selected_model, f"{engine_cc} cc", color,
                fuel, transmission,
                str(year_manufactured), str(year_bought), str(year_selling),
                f"{car_age} year(s)",
                f"{total_age} year(s) since manufacture",
                f"{km_driven:,} km",
                "Yes" if accident_val else "No",
                ", ".join(selected_accident_parts) if selected_accident_parts else "None",
                ", ".join(selected_failed_parts)   if selected_failed_parts   else "None",
            ]
        })
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

        st.markdown("**Condition Tags**")
        tags = []
        tags.append('<span class="tag tag-bad">Accident</span>'
                    if accident_val else
                    '<span class="tag tag-good">Accident Free</span>')
        tags.append(
            '<span class="tag tag-good">Low Mileage</span>'    if km_driven < 50000  else
            '<span class="tag tag-warn">Moderate Mileage</span>' if km_driven < 120000 else
            '<span class="tag tag-bad">High Mileage</span>')
        tags.append(
            '<span class="tag tag-good">Nearly New</span>'  if total_age <= 3 else
            '<span class="tag tag-warn">Mid Age</span>'     if total_age <= 7 else
            '<span class="tag tag-bad">Older Car</span>')
        tags.append(f'<span class="tag tag-neutral">{fuel}</span>')
        tags.append(f'<span class="tag tag-neutral">{transmission}</span>')
        tags.append(f'<span class="tag tag-neutral">{engine_cc} cc</span>')
        if selected_accident_parts:
            tags.append(f'<span class="tag tag-bad">{len(selected_accident_parts)} Body Part(s) Damaged</span>')
        if selected_failed_parts:
            tags.append(f'<span class="tag tag-bad">{len(selected_failed_parts)} Part(s) Failed</span>')
        st.markdown(" ".join(tags), unsafe_allow_html=True)

    with col2:
        st.markdown("### Price Prediction")

        if predict_btn:
            if yr_error:
                st.error("Fix the year errors in the sidebar first.")
            else:
                with st.spinner("Running prediction..."):
                    try:
                        price = predict_price(
                            selected_make, selected_model,
                            color, fuel, transmission, engine_cc,
                            year_manufactured, year_bought, year_selling,
                            km_driven, accident_val,
                            selected_accident_parts, selected_failed_parts
                        )
                        st.session_state["last_price"]  = price
                        st.session_state["last_inputs"] = {
                            "make": selected_make, "model": selected_model,
                            "engine_cc": engine_cc, "color": color,
                            "fuel": fuel, "transmission": transmission,
                            "year_manufactured": year_manufactured,
                            "year_bought": year_bought,
                            "year_selling": year_selling,
                            "km_driven": km_driven,
                            "accident": accident_val,
                            "accident_parts": selected_accident_parts,
                            "failed_parts":   selected_failed_parts,
                            "price": price,
                            "base_price": get_base_price(selected_make, selected_model),
                        }
                    except FileNotFoundError:
                        st.error("Model not found. Run python model.py first.")
                        st.stop()
                    except Exception as e:
                        st.error(f"Prediction error: {e}")
                        st.stop()

        if "last_price" in st.session_state:
            price      = st.session_state["last_price"]
            inp        = st.session_state["last_inputs"]
            lakh_price = price / 100000

            st.markdown(f"""
            <div class="price-box">
                <div class="label">Estimated Market Value</div>
                <h1>PKR {price:,.0f}</h1>
                <div class="lakh">{lakh_price:.2f} Lakh Pakistani Rupees</div>
            </div>""", unsafe_allow_html=True)

            st.success("Prediction complete.")
            low, high = price * 0.90, price * 1.10
            st.info(f"Market Range: PKR {low:,.0f} — PKR {high:,.0f}")

            new_price = get_base_price(selected_make, selected_model)
            dep_pct   = max(0, (1 - price / new_price) * 100)
            st.markdown(
                f"Depreciated **{dep_pct:.1f}%** from brand-new price "
                f"(PKR {new_price/100000:.1f} Lakh)"
            )

            pdf_bytes = generate_pdf(inp)
            st.download_button(
                label="Download PDF Report",
                data=pdf_bytes,
                file_name=f"car_price_{selected_make}_{selected_model}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

            # ── Animated Depreciation Chart ──────────────────────────────────
            st.markdown("#### Price History — Animated Year by Year")
            total_age_now = year_selling - year_manufactured
            base_est      = price / ((1 - 0.10) ** total_age_now) if total_age_now > 0 else price
            chart_years   = list(range(year_manufactured, year_selling + 1))
            chart_prices  = [
                round(base_est * ((1 - 0.10) ** (yr - year_manufactured)), -3)
                for yr in chart_years
            ]

            # Build animation frames — each frame adds one more year
            frames = []
            for k in range(1, len(chart_years) + 1):
                yr_slice = chart_years[:k]
                pr_slice = chart_prices[:k]

                frame_traces = [
                    go.Scatter(
                        x=yr_slice, y=pr_slice,
                        mode="lines+markers",
                        line=dict(color="#3b7dd8", width=3),
                        marker=dict(size=8, color="#3b7dd8"),
                        fill="tozeroy",
                        fillcolor="rgba(59,125,216,0.08)",
                        hovertemplate="Year: %{x}<br>PKR %{y:,.0f}<extra></extra>",
                        name="Price"
                    )
                ]

                # Ownership shade — only once we pass the bought year
                own_yrs_f = [yr for yr in yr_slice if year_bought <= yr]
                own_prc_f = [chart_prices[chart_years.index(yr)] for yr in own_yrs_f]
                if len(own_yrs_f) >= 2:
                    frame_traces.append(go.Scatter(
                        x=own_yrs_f + own_yrs_f[::-1],
                        y=own_prc_f + [0] * len(own_prc_f),
                        fill="toself",
                        fillcolor="rgba(59,125,216,0.13)",
                        line=dict(color="rgba(0,0,0,0)"),
                        name="Ownership Period",
                        hoverinfo="skip"
                    ))
                else:
                    # Placeholder trace to keep frame structure consistent
                    frame_traces.append(go.Scatter(x=[], y=[], hoverinfo="skip", showlegend=False))

                frames.append(go.Frame(data=frame_traces, name=str(chart_years[k-1])))

            # Initial state — show just the first point
            init_traces = [
                go.Scatter(
                    x=[chart_years[0]], y=[chart_prices[0]],
                    mode="lines+markers",
                    line=dict(color="#3b7dd8", width=3),
                    marker=dict(size=8, color="#3b7dd8"),
                    fill="tozeroy",
                    fillcolor="rgba(59,125,216,0.08)",
                    hovertemplate="Year: %{x}<br>PKR %{y:,.0f}<extra></extra>",
                    name="Price"
                ),
                go.Scatter(x=[], y=[], hoverinfo="skip", showlegend=False)
            ]

            # Key event annotations
            def ann(x, y, txt, clr, ay=-40):
                return dict(x=x, y=y, text=txt, showarrow=True, arrowhead=2,
                            font=dict(color=clr, size=11),
                            arrowcolor=clr, ax=0, ay=ay)

            anns = [ann(year_manufactured, chart_prices[0], "Manufactured", "#27ae60")]
            if year_bought in chart_years:
                idx = chart_years.index(year_bought)
                anns.append(ann(year_bought, chart_prices[idx], "Bought", "#3b7dd8"))
            anns.append(ann(year_selling, chart_prices[-1], "Selling Now", "#e67e22", ay=-55))

            anim_fig = go.Figure(
                data=init_traces,
                frames=frames,
                layout=go.Layout(
                    plot_bgcolor="#ffffff",
                    paper_bgcolor="#ffffff",
                    font_color="#333333",
                    xaxis=dict(
                        range=[year_manufactured - 0.5, year_selling + 0.5],
                        tickmode="linear", dtick=1,
                        gridcolor="#f0f0f0", linecolor="#dde3ec",
                        title="Year"
                    ),
                    yaxis=dict(
                        range=[0, chart_prices[0] * 1.15],
                        gridcolor="#f0f0f0", linecolor="#dde3ec",
                        title="Price (PKR)",
                        tickformat=","
                    ),
                    annotations=anns,
                    height=400,
                    margin=dict(l=10, r=10, t=30, b=60),
                    showlegend=True,
                    legend=dict(bgcolor="#ffffff", x=0.75, y=0.95),
                    updatemenus=[dict(
                        type="buttons",
                        showactive=False,
                        y=-0.18,
                        x=0.5,
                        xanchor="center",
                        buttons=[
                            dict(
                                label="Play",
                                method="animate",
                                args=[None, dict(
                                    frame=dict(duration=400, redraw=True),
                                    fromcurrent=True,
                                    transition=dict(duration=200, easing="cubic-in-out")
                                )]
                            ),
                            dict(
                                label="Pause",
                                method="animate",
                                args=[[None], dict(
                                    frame=dict(duration=0, redraw=False),
                                    mode="immediate",
                                    transition=dict(duration=0)
                                )]
                            )
                        ]
                    )],
                    sliders=[dict(
                        active=0,
                        currentvalue=dict(
                            prefix="Year: ",
                            font=dict(color="#333333", size=13)
                        ),
                        pad=dict(t=40, b=10),
                        len=0.9,
                        x=0.05,
                        steps=[
                            dict(
                                method="animate",
                                args=[[str(yr)], dict(
                                    frame=dict(duration=300, redraw=True),
                                    mode="immediate",
                                    transition=dict(duration=150)
                                )],
                                label=str(yr)
                            )
                            for yr in chart_years
                        ]
                    )]
                )
            )

            st.plotly_chart(anim_fig, use_container_width=True)
            st.caption("Click Play to animate the price depreciation year by year. Drag the slider to any year.")

            st.markdown("#### Price Impact Breakdown")
            cc_f = CC_PRICE_FACTOR.get(engine_cc, 1.0)
            impacts = [f"Engine {engine_cc} cc — price factor: x{cc_f}"]
            if fuel == "Diesel":
                impacts.append("Diesel engine: +5%")
            if transmission == "Automatic":
                impacts.append("Automatic transmission: +8%")
            if km_driven > 50000:
                pen = round(max(0, (km_driven - 50000) / 10000), 1)
                impacts.append(f"High mileage ({km_driven:,} km): -{pen}%")
            if selected_accident_parts:
                impacts.append(f"Body damage ({len(selected_accident_parts)} part(s)): -{len(selected_accident_parts)*5}%")
            if selected_failed_parts:
                impacts.append(f"Failed parts ({len(selected_failed_parts)} part(s)): -{len(selected_failed_parts)*3}%")
            for item in impacts:
                st.markdown(f"- {item}")
        else:
            st.markdown("""
            <div style="background:#ffffff;border:1px solid #dde3ec;border-radius:6px;
                        padding:40px;text-align:center;">
                <p style="color:#6b7a99;font-size:1rem;">
                    Fill in the car details in the left sidebar,<br>
                    then click <strong>Predict Price</strong>.
                </p>
            </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — DATASET INSIGHTS
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### Dataset Overview")
    dataset_path = "dataset/car_data.csv"

    if not os.path.exists(dataset_path):
        st.warning("Dataset not found. Run python generate_dataset.py first.")
    else:
        df = pd.read_csv(dataset_path)
        df["car_age"]   = df["year_selling"] - df["year_bought"]
        df["total_age"] = df["year_selling"] - df["year_manufactured"]

        real_count = int((df["data_source"] == "PakWheels Real").sum()) if "data_source" in df.columns else 0
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f'<div class="metric-card"><h2>{len(df)}</h2><p>Total Records</p></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric-card"><h2>{real_count}</h2><p>Real (PakWheels)</p></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="metric-card"><h2>{df["make"].nunique()}</h2><p>Car Makes</p></div>', unsafe_allow_html=True)
        with c4:
            avg_p = df["price_pkr"].mean() / 100000
            st.markdown(f'<div class="metric-card"><h2>{avg_p:.1f}L</h2><p>Avg Price (PKR)</p></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if "data_source" in df.columns:
            col_s1, col_s2 = st.columns([1, 2])
            with col_s1:
                src_counts = df["data_source"].value_counts().reset_index()
                src_counts.columns = ["Source", "Count"]
                fig_src = px.pie(
                    src_counts, names="Source", values="Count",
                    title="Data Source Split",
                    color_discrete_map={"PakWheels Real": "#3b7dd8", "Synthetic": "#95a5a6"},
                    hole=0.45
                )
                fig_src.update_layout(
                    plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
                    font_color="#333333", height=300,
                    margin=dict(l=10, r=10, t=40, b=10)
                )
                st.plotly_chart(fig_src, use_container_width=True)
            with col_s2:
                st.markdown("#### Dataset Composition")
                real_df = df[df["data_source"] == "PakWheels Real"]
                syn_df  = df[df["data_source"] == "Synthetic"]
                st.markdown(f"""
| Source | Records | Description |
|---|---|---|
| PakWheels Real | {len(real_df)} | Live scraped listings from pakwheels.com |
| Synthetic | {len(syn_df)} | Generated from PakWheels market research |
| Total | {len(df)} | Combined training dataset |
                """)
                if not real_df.empty:
                    top_make = real_df["make"].value_counts().index[0]
                    top_cnt  = real_df["make"].value_counts().iloc[0]
                    st.markdown(f"""
- Price range: PKR {real_df['price_pkr'].min()/100000:.1f}L — PKR {real_df['price_pkr'].max()/100000:.1f}L
- Makes: {real_df['make'].nunique()}
- Most listed: {top_make} ({top_cnt} listings)
                    """)
                st.info("Dataset: 626 real PakWheels listings + 2,000 synthetic records. Disclaimer: real data scraped from pakwheels.com for educational purposes.")

        st.markdown("---")
        CHART_BG = "#ffffff"
        CHART_FT = "#333333"
        CHART_GD = "#f0f0f0"

        col1, col2 = st.columns(2)
        with col1:
            avg_make = df.groupby("make")["price_pkr"].mean().sort_values(ascending=True).reset_index()
            fig1 = px.bar(avg_make, x="price_pkr", y="make", orientation="h",
                          title="Average Price by Make",
                          color="price_pkr", color_continuous_scale="Blues")
            fig1.update_layout(plot_bgcolor=CHART_BG, paper_bgcolor=CHART_BG,
                               font_color=CHART_FT, height=500,
                               xaxis=dict(gridcolor=CHART_GD), yaxis=dict(gridcolor=CHART_GD))
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            cc_counts = df["engine_cc"].value_counts().sort_index().reset_index()
            cc_counts.columns = ["Engine CC", "Count"]
            cc_counts["CC Label"] = cc_counts["Engine CC"].astype(str) + " cc"
            fig_cc = px.bar(cc_counts, x="CC Label", y="Count",
                            title="Engine CC Distribution",
                            color="Count", color_continuous_scale="Blues")
            fig_cc.update_layout(plot_bgcolor=CHART_BG, paper_bgcolor=CHART_BG,
                                 font_color=CHART_FT, height=500, xaxis_tickangle=-45,
                                 xaxis=dict(gridcolor=CHART_GD), yaxis=dict(gridcolor=CHART_GD))
            st.plotly_chart(fig_cc, use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            fig_sc2 = px.scatter(
                df.sample(min(500, len(df)), random_state=42),
                x="engine_cc", y="price_pkr", color="make",
                title="Engine CC vs Price",
                labels={"engine_cc": "Engine CC (cc)", "price_pkr": "Price (PKR)"},
                opacity=0.65
            )
            fig_sc2.update_layout(plot_bgcolor=CHART_BG, paper_bgcolor=CHART_BG,
                                  font_color=CHART_FT, height=380,
                                  xaxis=dict(gridcolor=CHART_GD), yaxis=dict(gridcolor=CHART_GD))
            st.plotly_chart(fig_sc2, use_container_width=True)

        with col4:
            fuel_counts = df["fuel"].value_counts().reset_index()
            fuel_counts.columns = ["Fuel", "Count"]
            fig_fuel = px.pie(
                fuel_counts, names="Fuel", values="Count",
                title="Fuel Type Distribution",
                color_discrete_map={"Petrol": "#3b7dd8", "Diesel": "#e67e22"},
                hole=0.4
            )
            fig_fuel.update_layout(plot_bgcolor=CHART_BG, paper_bgcolor=CHART_BG,
                                   font_color=CHART_FT, height=380)
            st.plotly_chart(fig_fuel, use_container_width=True)

        if "data_source" in df.columns and real_count > 0:
            fig_box = px.box(
                df, x="data_source", y="price_pkr", color="data_source",
                title="Price Distribution: Real vs Synthetic",
                color_discrete_map={"PakWheels Real": "#3b7dd8", "Synthetic": "#95a5a6"},
                labels={"data_source": "Data Source", "price_pkr": "Price (PKR)"}
            )
            fig_box.update_layout(plot_bgcolor=CHART_BG, paper_bgcolor=CHART_BG,
                                  font_color=CHART_FT, height=380, showlegend=False,
                                  xaxis=dict(gridcolor=CHART_GD), yaxis=dict(gridcolor=CHART_GD))
            st.plotly_chart(fig_box, use_container_width=True)

        fig_km = px.scatter(
            df.sample(min(500, len(df)), random_state=42),
            x="km_driven", y="price_pkr", color="make",
            title="KM Driven vs Price", opacity=0.65,
            labels={"km_driven": "KM Driven", "price_pkr": "Price (PKR)"}
        )
        fig_km.update_layout(plot_bgcolor=CHART_BG, paper_bgcolor=CHART_BG,
                             font_color=CHART_FT, height=400,
                             xaxis=dict(gridcolor=CHART_GD), yaxis=dict(gridcolor=CHART_GD))
        st.plotly_chart(fig_km, use_container_width=True)

        with st.expander("View Full Dataset"):
            filter_src = st.selectbox("Filter by source", ["All", "PakWheels Real", "Synthetic"])
            show_df = df if filter_src == "All" else df[df["data_source"] == filter_src]
            st.dataframe(show_df, use_container_width=True)
            st.caption(f"Showing {len(show_df)} records")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — MODEL PERFORMANCE
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### Model Performance")
    model_path = "model/car_price_model.pkl"

    if not os.path.exists(model_path):
        st.warning("Model not found. Run python model.py first.")
    else:
        _, _, metrics = load_model()
        if metrics:
            c1, c2, c3, c4 = st.columns(4)
            with c1: st.markdown(f'<div class="metric-card"><h2>{metrics["r2"]*100:.1f}%</h2><p>R2 Accuracy</p></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="metric-card"><h2>{metrics["mae"]/100000:.2f}L</h2><p>Mean Abs Error</p></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="metric-card"><h2>{metrics["rmse"]/100000:.2f}L</h2><p>RMSE</p></div>', unsafe_allow_html=True)
            with c4: st.markdown(f'<div class="metric-card"><h2>{metrics["cv_mean"]*100:.1f}%</h2><p>Cross-Val Score</p></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
**Algorithm: Gradient Boosting Regressor**
- Sequential ensemble — each tree corrects previous errors
- Trained with 4x weight on real PakWheels data
- Outperforms Random Forest on real-world price data
- Optimized for Pakistani used car market patterns
                """)
            with col2:
                st.markdown("""
**Model Parameters**
- n_estimators = 500
- learning_rate = 0.05
- max_depth = 6
- subsample = 0.8
- max_features = sqrt
                """)

            st.markdown("#### Feature Importance")
            with open(model_path, "rb") as f:
                saved = pickle.load(f)
            model_obj = saved["model"]
            feature_labels = [
                "Car Make", "Car Model", "Color", "Fuel Type", "Transmission",
                "Engine CC", "Year Manufactured", "Year Bought", "Year Selling",
                "Car Age (Owned)", "Total Age (Mfg to Sale)", "Pre-Buy Age",
                "KM Driven", "Accident", "Damaged Parts Count",
                "Failed Parts Count", "Base (New) Price"
            ]
            fi_df = pd.DataFrame({
                "Feature":    feature_labels,
                "Importance": model_obj.feature_importances_
            }).sort_values("Importance", ascending=True)

            fig_fi = px.bar(
                fi_df, x="Importance", y="Feature", orientation="h",
                title="Feature Importance (higher = more impact on predicted price)",
                color="Importance", color_continuous_scale="Blues"
            )
            fig_fi.update_layout(
                plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
                font_color="#333333", height=550,
                xaxis=dict(gridcolor="#f0f0f0"), yaxis=dict(gridcolor="#f0f0f0")
            )
            st.plotly_chart(fig_fi, use_container_width=True)

            st.markdown("#### Training Summary")
            st.markdown(f"""
| Metric | Value |
|---|---|
| Algorithm | Gradient Boosting Regressor |
| Dataset Size | 2,626 records (4x real data weighting = 4,504 training rows) |
| Real PakWheels Data | 626 live scraped listings |
| Synthetic Data | 2,000 generated records |
| Car Makes | 20 |
| Car Models | 150+ |
| Engine CC Options | 24 (660 cc to 8400 cc) |
| Training Split | 80% train / 20% test |
| Cross Validation | 5-Fold CV |
| R2 Score | {metrics["r2"]*100:.2f}% |
| MAE | PKR {metrics["mae"]:,.0f} ({metrics["mae"]/100000:.2f} Lakh) |
| RMSE | PKR {metrics["rmse"]:,.0f} ({metrics["rmse"]/100000:.2f} Lakh) |
| CV Mean R2 | {metrics["cv_mean"]*100:.2f}% plus minus {metrics["cv_std"]*100:.2f}% |
| Total Features | 17 |
| Real-world Avg Error | Approx. 11% — 11 of 15 cars within 15% of actual PakWheels price |
| Data Strategy | Real PakWheels data weighted 4x over synthetic |
            """)

# ─── Footer ──────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<div style="text-align:center;color:#9aa5b8;font-size:0.82rem;padding:8px 0;">'
    'Pakistan Car Price Predictor &nbsp;|&nbsp; 20 Makes &nbsp;|&nbsp; 150+ Models &nbsp;|&nbsp;'
    ' Gradient Boosting ML &nbsp;|&nbsp; BS Project 2024'
    '</div>',
    unsafe_allow_html=True
)
