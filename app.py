
from pathlib import Path
from datetime import date, datetime, timedelta
import hashlib

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from PIL import Image

from modules.detector import detect_food
from modules.nutrition import (
    calculate_nutrition,
    calculate_total_nutrition,
)
from modules.diary import (
    load_food_diary,
    save_food_diary,
    get_daily_summary,
    update_food_diary,
    delete_food_diary,
)
from modules.goals import load_goals, save_goals


# =========================================================
# 1. APP CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="FoodVision AI | Smart Nutrition",
    page_icon="🍱",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

FOOD_LABELS = {
    "hamburger": "Hamburger",
    "french_fries": "French Fries",
    "steak": "Steak",
    "pad_thai": "Pad Thai",
    "ramen": "Ramen",
    "sashimi": "Sashimi",
    "som_tam": "Som Tam",
    "sushi": "Sushi",
}

MEAL_OPTIONS = [
    "มื้อเช้า",
    "มื้อกลางวัน",
    "มื้อเย็น",
    "ของว่าง",
]

PAGE_OPTIONS = [
    "Dashboard",
    "AI Food Scanner",
    "Food Diary",
    "Nutrition Analytics",
    "Nutrition Goals",
    "About FoodVision",
]


# =========================================================
# 2. PREMIUM UI STYLE
# =========================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600;700&family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Kanit', 'Inter', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 10% 0%, rgba(124, 58, 237, .15), transparent 30%),
            radial-gradient(circle at 90% 10%, rgba(59, 130, 246, .08), transparent 25%),
            #0d0b14;
        color: #f4f0ff;
    }

    [data-testid="stHeader"] {
        background: rgba(13, 11, 20, .75);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #171224 0%, #100d19 100%);
        border-right: 1px solid rgba(167, 139, 250, .15);
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.5rem;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }

    h1, h2, h3, h4 {
        color: #f7f3ff !important;
        font-weight: 600 !important;
    }

    p, label, span, div {
        letter-spacing: .1px;
    }

    .brand-title {
        font-size: 1.65rem;
        font-weight: 800;
        letter-spacing: -.8px;
        background: linear-gradient(90deg, #ffffff, #b69aff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .brand-subtitle {
        color: #9389a8;
        font-size: .75rem;
        letter-spacing: 2px;
        margin-top: -5px;
    }

    .hero {
        background:
            linear-gradient(120deg, rgba(124, 58, 237, .22), rgba(59, 130, 246, .08)),
            #191426;
        border: 1px solid rgba(167, 139, 250, .22);
        border-radius: 24px;
        padding: 30px;
        margin-bottom: 24px;
        box-shadow: 0 18px 50px rgba(0, 0, 0, .20);
    }

    .hero-kicker {
        color: #b9a4ff;
        font-size: .78rem;
        letter-spacing: 2px;
        font-weight: 600;
    }

    .hero-title {
        font-size: 2rem;
        font-weight: 700;
        line-height: 1.35;
        margin: 8px 0;
        color: #ffffff;
    }

    .hero-description {
        color: #b7aec8;
        font-size: .95rem;
        line-height: 1.7;
    }

    .panel {
        background: linear-gradient(145deg, #1b1727, #15121e);
        border: 1px solid rgba(167, 139, 250, .14);
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, .14);
    }

    .panel-title {
        font-size: 1.05rem;
        font-weight: 600;
        color: #f3edff;
        margin-bottom: 12px;
    }

    .muted {
        color: #9e95ae;
        font-size: .85rem;
    }

    .metric-card {
        background: linear-gradient(145deg, #211a32, #171321);
        border: 1px solid rgba(167, 139, 250, .18);
        border-radius: 18px;
        padding: 19px;
        min-height: 125px;
        transition: .25s ease;
    }

    .metric-card:hover {
        transform: translateY(-4px);
        border-color: rgba(167, 139, 250, .48);
        box-shadow: 0 12px 30px rgba(124, 58, 237, .12);
    }

    .metric-label {
        color: #a99fba;
        font-size: .82rem;
    }

    .metric-value {
        color: #ffffff;
        font-size: 1.8rem;
        font-weight: 700;
        margin-top: 7px;
    }

    .metric-unit {
        color: #a99fba;
        font-size: .78rem;
    }

    .section-heading {
        font-size: 1.35rem;
        font-weight: 650;
        margin: 15px 0 5px;
    }

    .section-description {
        color: #9e95ae;
        font-size: .85rem;
        margin-bottom: 18px;
    }

    .status-pill {
        display: inline-block;
        background: rgba(52, 211, 153, .12);
        color: #6ee7b7;
        border: 1px solid rgba(52, 211, 153, .2);
        border-radius: 30px;
        padding: 5px 12px;
        font-size: .75rem;
    }

    .food-row {
        background: #211b2e;
        border: 1px solid rgba(167, 139, 250, .12);
        border-radius: 14px;
        padding: 13px 15px;
        margin-bottom: 9px;
    }

    .stButton > button {
        border-radius: 12px;
        border: 1px solid rgba(167, 139, 250, .25);
        background: linear-gradient(100deg, #7c3aed, #6d5ce8);
        color: white;
        font-weight: 600;
        min-height: 42px;
        transition: .2s ease;
    }

    .stButton > button:hover {
        border-color: #b69aff;
        background: linear-gradient(100deg, #8b5cf6, #7567f0);
        transform: translateY(-1px);
    }

    .stDownloadButton > button {
        border-radius: 12px;
        background: #211b2e;
        color: #e9ddff;
        border: 1px solid rgba(167, 139, 250, .25);
    }

    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    div[data-baseweb="textarea"] > div {
        background: #1d1829;
        border-color: rgba(167, 139, 250, .2);
        border-radius: 10px;
    }

    [data-testid="stFileUploader"] {
        background: #1b1727;
        border: 1px dashed rgba(167, 139, 250, .4);
        border-radius: 16px;
        padding: 15px;
    }

    [data-testid="stMetric"] {
        background: #1c1728;
        border: 1px solid rgba(167, 139, 250, .13);
        padding: 15px;
        border-radius: 15px;
    }

    [data-testid="stMetricValue"] {
        color: #ffffff;
    }

    [data-testid="stProgressBar"] > div > div {
        background: linear-gradient(90deg, #8b5cf6, #c084fc);
    }

    hr {
        border-color: rgba(167, 139, 250, .13);
    }

    .footer {
        text-align: center;
        color: #756c84;
        font-size: .75rem;
        padding: 30px 0 5px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 3. HELPER FUNCTIONS
# =========================================================

def money(value):
    return f"{float(value):,.0f}"


def get_food_key(food_name):
    """แปลงชื่ออาหารที่แสดงเป็นชื่อ key ในฐานข้อมูลโภชนาการ"""
    value = str(food_name).strip().lower()

    if value in FOOD_LABELS:
        return value

    for key, label in FOOD_LABELS.items():
        if value == label.lower():
            return key

    return value.replace(" ", "_")


def get_food_label(food_name):
    key = get_food_key(food_name)
    return FOOD_LABELS.get(key, str(food_name).replace("_", " ").title())


def safe_float(value, default=0.0):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def make_metric_card(label, value, unit, icon, color="#A78BFA"):
    st.markdown(
        f"""
        <div class="metric-card">
            <div style="font-size:1.35rem;">{icon}</div>
            <div class="metric-label">{label}</div>
            <div class="metric-value" style="color:{color};">{value}</div>
            <div class="metric-unit">{unit}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_heading(title, description=None):
    st.markdown(f'<div class="section-heading">{title}</div>', unsafe_allow_html=True)
    if description:
        st.markdown(
            f'<div class="section-description">{description}</div>',
            unsafe_allow_html=True,
        )


def get_today_data():
    df = load_food_diary()
    if df.empty:
        return df

    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    return df[df["date"] == date.today()]


def get_last_seven_days():
    df = load_food_diary()

    dates = [date.today() - timedelta(days=i) for i in range(6, -1, -1)]
    result = pd.DataFrame({"date": dates, "calories": [0.0] * 7})

    if df.empty:
        return result

    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    df["calories"] = pd.to_numeric(df["calories"], errors="coerce").fillna(0)

    grouped = df.groupby("date", as_index=False)["calories"].sum()
    result = result.drop(columns=["calories"]).merge(grouped, on="date", how="left")
    result["calories"] = result["calories"].fillna(0)

    return result


def get_chart_layout(fig, height=300):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#C9C0D8", family="Kanit"),
        margin=dict(l=10, r=10, t=20, b=10),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#C9C0D8"),
        ),
    )
    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        linecolor="rgba(167,139,250,.12)",
    )
    fig.update_yaxes(
        gridcolor="rgba(167,139,250,.10)",
        zeroline=False,
    )
    return fig


def render_calorie_ring(consumed, target):
    target = max(safe_float(target, 2000), 1)
    consumed = max(safe_float(consumed), 0)
    remaining = max(target - consumed, 0)
    percentage = min(consumed / target * 100, 100)

    fig = go.Figure(
        go.Pie(
            values=[min(consumed, target), max(target - consumed, 0)],
            hole=0.78,
            sort=False,
            direction="clockwise",
            marker=dict(
                colors=["#A78BFA", "#30283D"],
                line=dict(color="#171321", width=4),
            ),
            textinfo="none",
            hoverinfo="skip",
        )
    )

    fig.update_layout(
        height=245,
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        annotations=[
            dict(
                text=f"<b>{money(consumed)}</b><br><span style='font-size:12px;color:#A99FBA'>kcal</span>",
                x=0.5,
                y=0.53,
                showarrow=False,
                font=dict(size=27, color="#FFFFFF", family="Kanit"),
            )
        ],
    )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown(
        f"""
        <div style="text-align:center;margin-top:-22px;">
            <span style="color:#A99FBA;font-size:.8rem;">เป้าหมาย {money(target)} kcal</span><br>
            <span style="color:#BCA7FF;font-weight:600;">
                {percentage:.1f}% ของเป้าหมาย
            </span><br>
            <span style="color:#A99FBA;font-size:.8rem;">
                {"เกินเป้าหมาย " + money(consumed-target) + " kcal" if consumed > target else "เหลืออีก " + money(remaining) + " kcal"}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_macro_progress(label, consumed, target, color):
    target = max(safe_float(target), 1)
    consumed = safe_float(consumed)
    ratio = min(consumed / target, 1.0)

    st.markdown(
        f"""
        <div style="display:flex;justify-content:space-between;margin-bottom:5px;">
            <span style="color:#D8D0E5;">{label}</span>
            <span style="color:#A99FBA;">{consumed:.1f} / {target:.1f} g</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(ratio)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)


# =========================================================
# 4. SESSION STATE
# =========================================================

if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard"

if "scan_cache" not in st.session_state:
    st.session_state.scan_cache = {}

if "last_saved_signature" not in st.session_state:
    st.session_state.last_saved_signature = None


# =========================================================
# 5. SIDEBAR NAVIGATION
# =========================================================

with st.sidebar:
    st.markdown(
        """
        <div style="padding:0 5px 22px;">
            <div style="font-size:2rem;">🍱</div>
            <div class="brand-title">FoodVision AI</div>
            <div class="brand-subtitle">SMART NUTRITION PLATFORM</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div style="color:#8F849F;font-size:.72rem;letter-spacing:1.5px;margin:5px 0 10px;">MAIN MENU</div>',
        unsafe_allow_html=True,
    )

    selected_page = st.radio(
        "Navigation",
        PAGE_OPTIONS,
        index=PAGE_OPTIONS.index(st.session_state.current_page),
        label_visibility="collapsed",
        format_func=lambda x: {
            "Dashboard": "⌂  Dashboard",
            "AI Food Scanner": "✦  AI Food Scanner",
            "Food Diary": "▤  Food Diary",
            "Nutrition Analytics": "◷  Nutrition Analytics",
            "Nutrition Goals": "◎  Nutrition Goals",
            "About FoodVision": "ⓘ  About FoodVision",
        }[x],
    )

    st.session_state.current_page = selected_page

    st.markdown("---")

    st.markdown(
        """
        <div class="panel" style="padding:15px;">
            <div style="font-size:.8rem;color:#BBA6FF;font-weight:600;">
                ✨ YOUR DAILY JOURNEY
            </div>
            <div style="font-size:.78rem;color:#A99FBA;margin-top:7px;line-height:1.6;">
                บันทึกอาหาร วิเคราะห์โภชนาการ และสร้างนิสัยการกินที่ดีขึ้น
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="footer">FOODVISION AI · PREMIUM EDITION</div>',
        unsafe_allow_html=True,
    )


# =========================================================
# 6. LOAD SHARED DATA
# =========================================================

goals = load_goals()
today_summary = get_daily_summary(date.today())


# =========================================================
# 7. DASHBOARD
# =========================================================

if selected_page == "Dashboard":

    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-kicker">YOUR PERSONAL AI NUTRITION ASSISTANT</div>
            <div class="hero-title">กินอย่างเข้าใจ<br>ดูแลสุขภาพอย่างชาญฉลาด</div>
            <div class="hero-description">
                ติดตามอาหาร วิเคราะห์สารอาหาร และดูความคืบหน้าสุขภาพของคุณ
                <br>วันนี้ · {date.today().strftime("%d/%m/%Y")}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Today's Overview")
    st.caption("ภาพรวมโภชนาการที่คุณบันทึกไว้ในวันนี้")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        make_metric_card(
            "พลังงานที่ได้รับ",
            money(today_summary["calories"]),
            "kcal วันนี้",
            "🔥",
            "#C4A7FF",
        )

    with c2:
        make_metric_card(
            "โปรตีน",
            f'{today_summary["protein"]:.1f}',
            "กรัม",
            "💪",
            "#6EE7B7",
        )

    with c3:
        make_metric_card(
            "คาร์โบไฮเดรต",
            f'{today_summary["carbs"]:.1f}',
            "กรัม",
            "⚡",
            "#FBBF77",
        )

    with c4:
        make_metric_card(
            "ไขมัน",
            f'{today_summary["fat"]:.1f}',
            "กรัม",
            "🥑",
            "#F9A8D4",
        )

    st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)

    left, right = st.columns([1, 1.35], gap="large")

    with left:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        section_heading("Daily Calorie Goal", "พลังงานที่ได้รับเทียบกับเป้าหมายประจำวัน")
        render_calorie_ring(
            today_summary["calories"],
            goals.get("calories", 2000),
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        section_heading("Macro Nutrition", "สัดส่วนสารอาหารหลักที่ได้รับวันนี้")

        macro_df = pd.DataFrame(
            {
                "สารอาหาร": ["Protein", "Carbs", "Fat"],
                "ปริมาณ": [
                    today_summary["protein"],
                    today_summary["carbs"],
                    today_summary["fat"],
                ],
            }
        )

        fig = px.pie(
            macro_df,
            names="สารอาหาร",
            values="ปริมาณ",
            hole=0.65,
            color="สารอาหาร",
            color_discrete_map={
                "Protein": "#6EE7B7",
                "Carbs": "#FBBF77",
                "Fat": "#C4A7FF",
            },
        )
        fig.update_traces(
            textposition="outside",
            textinfo="label+percent",
            marker=dict(line=dict(color="#171321", width=3)),
        )
        fig = get_chart_layout(fig, 260)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    left, right = st.columns([1.4, 1], gap="large")

    with left:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        section_heading("Weekly Calorie Overview", "แนวโน้มแคลอรีในช่วง 7 วันที่ผ่านมา")

        weekly = get_last_seven_days()
        fig = px.area(
            weekly,
            x="date",
            y="calories",
            markers=True,
        )
        fig.update_traces(
            line=dict(color="#A78BFA", width=3),
            fillcolor="rgba(167,139,250,.16)",
            marker=dict(size=7, color="#C4A7FF"),
        )
        fig.update_layout(
            yaxis_title="Calories (kcal)",
            xaxis_title="",
            hovermode="x unified",
        )
        fig = get_chart_layout(fig, 280)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        section_heading("Nutrition Targets", "ความคืบหน้าสารอาหารวันนี้")

        render_macro_progress(
            "Protein",
            today_summary["protein"],
            goals.get("protein", 100),
            "#6EE7B7",
        )
        render_macro_progress(
            "Carbohydrates",
            today_summary["carbs"],
            goals.get("carbs", 250),
            "#FBBF77",
        )
        render_macro_progress(
            "Fat",
            today_summary["fat"],
            goals.get("fat", 65),
            "#C4A7FF",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    section_heading("Recent Food Records", "รายการอาหารที่คุณบันทึกไว้ล่าสุด")

    recent_df = load_food_diary()

    if recent_df.empty:
        st.info("ยังไม่มีรายการอาหาร ลองใช้ AI Food Scanner เพื่อเริ่มบันทึกมื้ออาหารของคุณ")
    else:
        recent_df = recent_df.sort_values("datetime", ascending=False).head(5)

        for _, row in recent_df.iterrows():
            meal = row.get("meal_type", "ไม่ระบุ")
            food = get_food_label(row.get("food_name", ""))
            st.markdown(
                f"""
                <div class="food-row">
                    <div style="display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;">
                        <div>
                            <span style="font-size:1.1rem;">🍽️</span>
                            <b style="color:#F4F0FF;"> {food}</b>
                            <span style="color:#A99FBA;font-size:.8rem;"> · {meal}</span>
                        </div>
                        <div style="color:#C4A7FF;font-weight:600;">
                            {safe_float(row.get("calories")):.0f} kcal
                        </div>
                    </div>
                    <div style="color:#91879F;font-size:.78rem;margin-top:5px;">
                        {row.get("date", "")} · {safe_float(row.get("weight")):.0f} g
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# =========================================================
# 8. AI FOOD SCANNER
# =========================================================

elif selected_page == "AI Food Scanner":

    st.markdown(
        """
        <div class="hero">
            <div class="hero-kicker">ARTIFICIAL INTELLIGENCE</div>
            <div class="hero-title">AI Food Scanner</div>
            <div class="hero-description">
                อัปโหลดภาพอาหารเพื่อให้ AI ตรวจจับและแยกอาหารแต่ละรายการ
                พร้อมประเมินสารอาหารเบื้องต้น
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    section_heading("Upload Your Food", "รองรับไฟล์ JPG, JPEG และ PNG")

    uploaded_file = st.file_uploader(
        "เลือกรูปภาพอาหาร",
        type=["jpg", "jpeg", "png"],
        key="food_image_upload",
    )

    if uploaded_file is not None:

        image_bytes = uploaded_file.getvalue()
        signature = hashlib.md5(image_bytes).hexdigest()
        image = Image.open(uploaded_file).convert("RGB")

        left, right = st.columns([1, 1], gap="large")

        with left:
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            section_heading("Original Image", "ภาพอาหารต้นฉบับ")
            st.image(image, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        if signature not in st.session_state.scan_cache:
            with st.spinner("AI กำลังวิเคราะห์ภาพอาหาร..."):
                try:
                    annotated_image, detections = detect_food(image)
                    st.session_state.scan_cache[signature] = {
                        "annotated": annotated_image,
                        "detections": detections,
                    }
                except Exception as error:
                    st.error(f"ไม่สามารถตรวจจับอาหารได้: {error}")
                    st.stop()

        scan_data = st.session_state.scan_cache[signature]
        detections = scan_data["detections"]

        with right:
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            section_heading("AI Detection Result", "กรอบแสดงตำแหน่งอาหารที่ตรวจพบ")
            st.image(scan_data["annotated"], use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

        if not detections:
            st.warning(
                "AI ยังไม่พบอาหารในภาพนี้ ลองเปลี่ยนภาพหรือใช้ภาพที่เห็นอาหารชัดเจนขึ้น"
            )
        else:
            st.markdown(
                f'<div class="status-pill">✓ ตรวจพบอาหาร {len(detections)} รายการ</div>',
                unsafe_allow_html=True,
            )

            section_heading(
                "Detected Foods",
                "ปรับน้ำหนักของอาหารแต่ละรายการก่อนบันทึกลง Food Diary",
            )

            meal_type = st.selectbox(
                "เลือกมื้ออาหาร",
                MEAL_OPTIONS,
                key="scanner_meal_type",
            )

            food_entries = []
            total_preview = {
                "calories": 0.0,
                "protein": 0.0,
                "carbs": 0.0,
                "fat": 0.0,
            }

            for index, detection in enumerate(detections):
                food_key = get_food_key(detection["name"])
                food_label = get_food_label(food_key)
                confidence = safe_float(detection.get("confidence")) * 100

                with st.container(border=True):
                    col1, col2, col3 = st.columns([2, 1, 1])

                    with col1:
                        st.markdown(f"**{index + 1}. {food_label}**")
                        st.caption(f"AI Confidence: {confidence:.1f}%")

                    with col2:
                        weight = st.number_input(
                            "น้ำหนัก (กรัม)",
                            min_value=1,
                            max_value=3000,
                            value=150,
                            step=10,
                            key=f"food_weight_{signature}_{index}",
                        )

                    with col3:
                        st.markdown(" ")
                        st.markdown(" ")
                        st.caption("ประมาณต่อรายการ")

                    try:
                        nutrition = calculate_nutrition(food_key, weight)

                        st.caption(
                            f"🔥 {nutrition['calories']:.0f} kcal  ·  "
                            f"โปรตีน {nutrition['protein']:.1f} g  ·  "
                            f"คาร์บ {nutrition['carbs']:.1f} g  ·  "
                            f"ไขมัน {nutrition['fat']:.1f} g"
                        )

                        food_entries.append(
                            {
                                "name": nutrition["name"],
                                "weight": weight,
                                "calories": nutrition["calories"],
                                "protein": nutrition["protein"],
                                "carbs": nutrition["carbs"],
                                "fat": nutrition["fat"],
                            }
                        )

                        for nutrient in total_preview:
                            total_preview[nutrient] += nutrition[nutrient]

                    except (ValueError, KeyError) as error:
                        st.warning(f"ไม่มีข้อมูลโภชนาการสำหรับ {food_label}: {error}")

            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

            st.markdown('<div class="panel">', unsafe_allow_html=True)
            section_heading("Meal Nutrition Summary", "ผลรวมสารอาหารของอาหารทุกจานในภาพ")

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Calories", f"{total_preview['calories']:.0f} kcal")
            m2.metric("Protein", f"{total_preview['protein']:.1f} g")
            m3.metric("Carbs", f"{total_preview['carbs']:.1f} g")
            m4.metric("Fat", f"{total_preview['fat']:.1f} g")

            st.markdown("</div>", unsafe_allow_html=True)

            if st.button(
                "＋  บันทึกอาหารลง Food Diary",
                use_container_width=True,
                key="save_scanned_food",
            ):
                if not food_entries:
                    st.warning("ไม่มีรายการอาหารที่สามารถบันทึกได้")
                elif st.session_state.last_saved_signature == (
                    signature + meal_type
                ):
                    st.warning("ภาพนี้ถูกบันทึกในมื้อนี้แล้ว")
                else:
                    try:
                        saved_count = save_food_diary(
                            food_entries,
                            meal_type=meal_type,
                        )
                        if saved_count:
                            st.session_state.last_saved_signature = (
                                signature + meal_type
                            )
                            st.success(
                                f"บันทึกอาหารสำเร็จ {saved_count} รายการ!"
                            )
                            st.rerun()
                        else:
                            st.warning("ไม่มีข้อมูลให้บันทึก")
                    except Exception as error:
                        st.error(f"บันทึกข้อมูลไม่สำเร็จ: {error}")

    else:
        st.markdown(
            """
            <div class="panel" style="text-align:center;padding:45px 20px;">
                <div style="font-size:3rem;">📸</div>
                <div style="font-size:1.15rem;font-weight:600;margin-top:10px;">
                    Ready to scan your food?
                </div>
                <div style="color:#A99FBA;font-size:.85rem;margin-top:5px;">
                    อัปโหลดภาพอาหารเพื่อเริ่มวิเคราะห์ด้วย AI
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.caption(
        "หมายเหตุ: น้ำหนักอาหารเป็นค่าที่ผู้ใช้กำหนดเอง ระบบยังไม่สามารถชั่งน้ำหนักอาหารจริงจากภาพได้"
    )


# =========================================================
# 9. FOOD DIARY
# =========================================================

elif selected_page == "Food Diary":

    st.markdown(
        """
        <div class="hero">
            <div class="hero-kicker">YOUR FOOD JOURNAL</div>
            <div class="hero-title">Food Diary</div>
            <div class="hero-description">
                บันทึกทุกมื้ออาหาร ดูย้อนหลัง และจัดการรายการอาหารของคุณ
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df = load_food_diary()

    selected_date = st.date_input(
        "เลือกวันที่ต้องการดู",
        value=date.today(),
        key="diary_selected_date",
    )

    if df.empty:
        st.info("ยังไม่มีประวัติอาหาร ลองสแกนอาหารเพื่อบันทึกข้อมูลก่อน")
    else:
        df = df.copy()
        df["date_parsed"] = pd.to_datetime(
            df["date"], errors="coerce"
        ).dt.date

        daily_df = df[df["date_parsed"] == selected_date].copy()

        if daily_df.empty:
            st.info("ไม่มีรายการอาหารในวันที่เลือก")
        else:
            summary = get_daily_summary(selected_date)

            st.markdown("### Daily Summary")
            c1, c2, c3, c4 = st.columns(4)

            c1.metric("Calories", f"{summary['calories']:.0f} kcal")
            c2.metric("Protein", f"{summary['protein']:.1f} g")
            c3.metric("Carbs", f"{summary['carbs']:.1f} g")
            c4.metric("Fat", f"{summary['fat']:.1f} g")

            st.markdown("---")
            section_heading("Your Meals", "รายการอาหารที่บันทึกในวันที่เลือก")

            for meal in MEAL_OPTIONS + ["ไม่ระบุ"]:
                meal_df = daily_df[
                    daily_df["meal_type"].fillna("ไม่ระบุ") == meal
                ]

                if meal_df.empty:
                    continue

                meal_calories = pd.to_numeric(
                    meal_df["calories"], errors="coerce"
                ).fillna(0).sum()

                st.markdown(
                    f"### {meal} · {meal_calories:.0f} kcal"
                )

                for _, row in meal_df.iterrows():
                    col1, col2, col3 = st.columns([3, 1, 1])

                    with col1:
                        st.markdown(
                            f"**🍽️ {get_food_label(row['food_name'])}**"
                        )
                        st.caption(
                            f"{safe_float(row['weight']):.0f} g · "
                            f"{row.get('datetime', '')}"
                        )

                    with col2:
                        st.markdown(
                            f"**{safe_float(row['calories']):.0f} kcal**"
                        )

                    with col3:
                        st.caption(
                            f"P {safe_float(row['protein']):.1f} · "
                            f"C {safe_float(row['carbs']):.1f} · "
                            f"F {safe_float(row['fat']):.1f}"
                        )

                    st.divider()

            st.markdown("---")
            section_heading("Edit or Delete Food", "เลือกจัดการรายการอาหารที่ต้องการ")

            edit_options = {}
            for _, row in daily_df.iterrows():
                label = (
                    f"{get_food_label(row['food_name'])} · "
                    f"{row.get('meal_type', 'ไม่ระบุ')} · "
                    f"{row.get('datetime', '')} · "
                    f"{safe_float(row['calories']):.0f} kcal"
                )
                edit_options[label] = str(row["id"])

            selected_label = st.selectbox(
                "เลือกรายการอาหาร",
                list(edit_options.keys()),
                key="diary_edit_select",
            )

            selected_id = edit_options[selected_label]
            selected_row = daily_df[
                daily_df["id"].astype(str) == selected_id
            ].iloc[0]

            edit_col, delete_col = st.columns(2, gap="large")

            with edit_col:
                st.markdown('<div class="panel">', unsafe_allow_html=True)
                st.markdown("#### ✏️ Edit Food")

                current_food_key = get_food_key(
                    selected_row["food_name"]
                )
                current_food_label = get_food_label(
                    selected_row["food_name"]
                )

                with st.form("edit_food_form"):
                    new_meal = st.selectbox(
                        "มื้ออาหาร",
                        MEAL_OPTIONS + ["ไม่ระบุ"],
                        index=(
                            MEAL_OPTIONS + ["ไม่ระบุ"]
                        ).index(
                            selected_row.get("meal_type", "ไม่ระบุ")
                        )
                        if selected_row.get("meal_type", "ไม่ระบุ")
                        in MEAL_OPTIONS + ["ไม่ระบุ"]
                        else 0,
                    )

                    st.text_input(
                        "ชื่ออาหาร",
                        value=current_food_label,
                        disabled=True,
                    )

                    new_weight = st.number_input(
                        "น้ำหนักใหม่ (กรัม)",
                        min_value=1,
                        max_value=3000,
                        value=max(
                            1,
                            int(safe_float(selected_row["weight"], 100)),
                        ),
                        step=10,
                    )

                    save_edit = st.form_submit_button(
                        "บันทึกการแก้ไข",
                        use_container_width=True,
                    )

                if save_edit:
                    try:
                        updated_nutrition = calculate_nutrition(
                            current_food_key,
                            new_weight,
                        )

                        success = update_food_diary(
                            selected_id,
                            {
                                "meal_type": new_meal,
                                "weight": new_weight,
                                "calories": updated_nutrition["calories"],
                                "protein": updated_nutrition["protein"],
                                "carbs": updated_nutrition["carbs"],
                                "fat": updated_nutrition["fat"],
                            },
                        )

                        if success:
                            st.success("แก้ไขข้อมูลสำเร็จ")
                            st.rerun()
                        else:
                            st.error("ไม่พบรายการที่ต้องการแก้ไข")

                    except Exception as error:
                        st.error(f"แก้ไขไม่สำเร็จ: {error}")

                st.markdown("</div>", unsafe_allow_html=True)

            with delete_col:
                st.markdown('<div class="panel">', unsafe_allow_html=True)
                st.markdown("#### 🗑️ Delete Food")
                st.write(
                    f"คุณกำลังเลือกลบ **{current_food_label}**"
                )

                confirm_delete = st.checkbox(
                    "ฉันยืนยันว่าต้องการลบรายการนี้",
                    key=f"confirm_delete_{selected_id}",
                )

                if st.button(
                    "ลบรายการอาหาร",
                    disabled=not confirm_delete,
                    use_container_width=True,
                    key="delete_food_button",
                ):
                    if delete_food_diary(selected_id):
                        st.success("ลบรายการสำเร็จ")
                        st.rerun()
                    else:
                        st.error("ไม่สามารถลบรายการนี้ได้")

                st.markdown("</div>", unsafe_allow_html=True)

    all_df = load_food_diary()

    if not all_df.empty:
        st.markdown("---")
        section_heading("Export Your Diary", "ดาวน์โหลดประวัติอาหารเป็นไฟล์ CSV")

        csv_data = all_df.to_csv(
            index=False,
            encoding="utf-8-sig",
        )

        st.download_button(
            "⬇ Download Food Diary CSV",
            data=csv_data,
            file_name="foodvision_food_diary.csv",
            mime="text/csv",
        )


# =========================================================
# 10. NUTRITION ANALYTICS
# =========================================================

elif selected_page == "Nutrition Analytics":

    st.markdown(
        """
        <div class="hero">
            <div class="hero-kicker">DATA & INSIGHTS</div>
            <div class="hero-title">Nutrition Analytics</div>
            <div class="hero-description">
                วิเคราะห์แนวโน้มพลังงานและสารอาหารจากประวัติอาหารของคุณ
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df = load_food_diary()

    if df.empty:
        st.info("ยังไม่มีข้อมูลเพียงพอสำหรับการวิเคราะห์ กรุณาบันทึกอาหารก่อน")
    else:
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        numeric_columns = [
            "calories", "protein", "carbs", "fat", "weight"
        ]

        for column in numeric_columns:
            df[column] = pd.to_numeric(
                df[column], errors="coerce"
            ).fillna(0)

        min_date = df["date"].min().date()
        max_date = df["date"].max().date()

        date_col1, date_col2 = st.columns(2)

        with date_col1:
            start_date = st.date_input(
                "วันที่เริ่มต้น",
                value=max(min_date, max_date - timedelta(days=6)),
                min_value=min_date,
                max_value=max_date,
                key="analytics_start",
            )

        with date_col2:
            end_date = st.date_input(
                "วันที่สิ้นสุด",
                value=max_date,
                min_value=min_date,
                max_value=max_date,
                key="analytics_end",
            )

        if start_date > end_date:
            st.error("วันที่เริ่มต้นต้องไม่เกินวันที่สิ้นสุด")
            st.stop()

        filtered = df[
            (df["date"].dt.date >= start_date)
            & (df["date"].dt.date <= end_date)
        ].copy()

        if filtered.empty:
            st.info("ไม่มีข้อมูลในช่วงวันที่เลือก")
        else:
            total_calories = filtered["calories"].sum()
            average_calories = filtered.groupby(
                filtered["date"].dt.date
            )["calories"].sum().mean()

            total_protein = filtered["protein"].sum()
            total_carbs = filtered["carbs"].sum()
            total_fat = filtered["fat"].sum()

            st.markdown("### Period Overview")

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Calories", f"{total_calories:,.0f} kcal")
            c2.metric("Daily Average", f"{average_calories:,.0f} kcal")
            c3.metric("Food Records", f"{len(filtered)}")
            c4.metric(
                "Total Weight",
                f"{filtered['weight'].sum():,.0f} g",
            )

            st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

            left, right = st.columns(2, gap="large")

            with left:
                st.markdown('<div class="panel">', unsafe_allow_html=True)
                section_heading(
                    "Calorie Trend",
                    "พลังงานรวมในแต่ละวัน",
                )

                calorie_by_day = (
                    filtered.groupby(filtered["date"].dt.date)["calories"]
                    .sum()
                    .reset_index()
                )
                calorie_by_day.columns = ["date", "calories"]

                fig = px.bar(
                    calorie_by_day,
                    x="date",
                    y="calories",
                )
                fig.update_traces(
                    marker_color="#9B7BEB",
                    marker_line_width=0,
                    opacity=.9,
                )
                fig.update_layout(
                    xaxis_title="Date",
                    yaxis_title="Calories (kcal)",
                )
                fig = get_chart_layout(fig, 310)
                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config={"displayModeBar": False},
                )
                st.markdown("</div>", unsafe_allow_html=True)

            with right:
                st.markdown('<div class="panel">', unsafe_allow_html=True)
                section_heading(
                    "Macro Distribution",
                    "สัดส่วนสารอาหารรวมในช่วงเวลาที่เลือก",
                )

                macro_df = pd.DataFrame(
                    {
                        "Macro": ["Protein", "Carbs", "Fat"],
                        "Grams": [
                            total_protein,
                            total_carbs,
                            total_fat,
                        ],
                    }
                )

                fig = px.pie(
                    macro_df,
                    names="Macro",
                    values="Grams",
                    hole=.58,
                    color="Macro",
                    color_discrete_map={
                        "Protein": "#6EE7B7",
                        "Carbs": "#FBBF77",
                        "Fat": "#A78BFA",
                    },
                )
                fig.update_traces(
                    textposition="outside",
                    textinfo="label+percent",
                )
                fig = get_chart_layout(fig, 310)
                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config={"displayModeBar": False},
                )
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

            left, right = st.columns(2, gap="large")

            with left:
                st.markdown('<div class="panel">', unsafe_allow_html=True)
                section_heading(
                    "Nutrition Radar",
                    "เปรียบเทียบปริมาณสารอาหารหลัก",
                )

                radar = go.Figure()
                radar.add_trace(
                    go.Scatterpolar(
                        r=[
                            total_protein,
                            total_carbs,
                            total_fat,
                            total_protein,
                        ],
                        theta=[
                            "Protein",
                            "Carbs",
                            "Fat",
                            "Protein",
                        ],
                        fill="toself",
                        line=dict(color="#A78BFA", width=3),
                        fillcolor="rgba(167,139,250,.20)",
                    )
                )
                radar.update_layout(
                    polar=dict(
                        bgcolor="rgba(0,0,0,0)",
                        radialaxis=dict(
                            visible=True,
                            gridcolor="rgba(167,139,250,.15)",
                            color="#A99FBA",
                        ),
                        angularaxis=dict(
                            gridcolor="rgba(167,139,250,.15)",
                            color="#D8D0E5",
                        ),
                    ),
                    showlegend=False,
                )
                radar = get_chart_layout(radar, 310)
                st.plotly_chart(
                    radar,
                    use_container_width=True,
                    config={"displayModeBar": False},
                )
                st.markdown("</div>", unsafe_allow_html=True)

            with right:
                st.markdown('<div class="panel">', unsafe_allow_html=True)
                section_heading(
                    "Most Recorded Foods",
                    "อาหารที่คุณบันทึกบ่อยที่สุด",
                )

                food_counts = (
                    filtered.groupby("food_name")
                    .size()
                    .reset_index(name="จำนวนครั้ง")
                    .sort_values("จำนวนครั้ง", ascending=False)
                    .head(7)
                )

                food_counts["อาหาร"] = food_counts["food_name"].apply(
                    get_food_label
                )

                fig = px.bar(
                    food_counts,
                    x="จำนวนครั้ง",
                    y="อาหาร",
                    orientation="h",
                )
                fig.update_traces(
                    marker_color="#A78BFA",
                    opacity=.9,
                )
                fig.update_layout(
                    yaxis=dict(autorange="reversed"),
                    xaxis_title="จำนวนครั้ง",
                    yaxis_title="",
                )
                fig = get_chart_layout(fig, 310)
                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config={"displayModeBar": False},
                )
                st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# 11. NUTRITION GOALS
# =========================================================

elif selected_page == "Nutrition Goals":

    st.markdown(
        """
        <div class="hero">
            <div class="hero-kicker">PERSONAL HEALTH PLAN</div>
            <div class="hero-title">Nutrition Goals</div>
            <div class="hero-description">
                ตั้งเป้าหมายโภชนาการที่เหมาะสม และติดตามความคืบหน้าของคุณ
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    section_heading(
        "Set Your Daily Targets",
        "กำหนดเป้าหมายต่อวัน โดยระบบจะนำไปแสดงใน Dashboard",
    )

    with st.form("nutrition_goals_form"):
        col1, col2 = st.columns(2)

        with col1:
            calorie_goal = st.number_input(
                "🔥 พลังงาน (kcal)",
                min_value=500,
                max_value=10000,
                value=int(goals.get("calories", 2000)),
                step=50,
            )

            protein_goal = st.number_input(
                "💪 โปรตีน (กรัม)",
                min_value=10,
                max_value=500,
                value=int(goals.get("protein", 100)),
                step=5,
            )

        with col2:
            carbs_goal = st.number_input(
                "⚡ คาร์โบไฮเดรต (กรัม)",
                min_value=10,
                max_value=1000,
                value=int(goals.get("carbs", 250)),
                step=5,
            )

            fat_goal = st.number_input(
                "🥑 ไขมัน (กรัม)",
                min_value=5,
                max_value=500,
                value=int(goals.get("fat", 65)),
                step=5,
            )

        submitted = st.form_submit_button(
            "บันทึกเป้าหมาย",
            use_container_width=True,
        )

    if submitted:
        new_goals = {
            "calories": calorie_goal,
            "protein": protein_goal,
            "carbs": carbs_goal,
            "fat": fat_goal,
        }

        if save_goals(new_goals):
            st.success("บันทึกเป้าหมายสำเร็จ!")
            st.rerun()
        else:
            st.error("ไม่สามารถบันทึกเป้าหมายได้")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    section_heading("Today's Progress", "ความคืบหน้าเทียบกับเป้าหมายที่ตั้งไว้")

    c1, c2 = st.columns(2, gap="large")

    with c1:
        render_macro_progress(
            "Calories",
            today_summary["calories"],
            goals.get("calories", 2000),
            "#A78BFA",
        )
        render_macro_progress(
            "Protein",
            today_summary["protein"],
            goals.get("protein", 100),
            "#6EE7B7",
        )

    with c2:
        render_macro_progress(
            "Carbohydrates",
            today_summary["carbs"],
            goals.get("carbs", 250),
            "#FBBF77",
        )
        render_macro_progress(
            "Fat",
            today_summary["fat"],
            goals.get("fat", 65),
            "#F9A8D4",
        )


# =========================================================
# 12. ABOUT FOODVISION
# =========================================================

elif selected_page == "About FoodVision":

    st.markdown(
        """
        <div class="hero">
            <div class="hero-kicker">ABOUT THE PROJECT</div>
            <div class="hero-title">FoodVision AI</div>
            <div class="hero-description">
                ระบบตรวจจับอาหารและประเมินคุณค่าทางโภชนาการจากภาพ
                ด้วยเทคโนโลยี Computer Vision และ AI
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### What is FoodVision AI?")

    st.write(
        """
        FoodVision AI เป็นเว็บแอปพลิเคชันที่ช่วยตรวจจับรายการอาหารจากภาพ
        แสดงผลตำแหน่งอาหารที่ตรวจพบ ประเมินพลังงานและสารอาหาร
        พร้อมบันทึกประวัติอาหารเพื่อให้ผู้ใช้ติดตามพฤติกรรมการกินของตนเอง
        """
    )

    st.markdown("### Core Features")

    feature_col1, feature_col2, feature_col3 = st.columns(3)

    with feature_col1:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("### ✦ AI Detection")
        st.write("ตรวจจับอาหารหลายรายการในภาพเดียวด้วยโมเดล Object Detection")
        st.markdown("</div>", unsafe_allow_html=True)

    with feature_col2:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("### 🔥 Nutrition Estimation")
        st.write("คำนวณพลังงาน โปรตีน คาร์โบไฮเดรต และไขมันตามน้ำหนักที่กำหนด")
        st.markdown("</div>", unsafe_allow_html=True)

    with feature_col3:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("### ◷ Food Analytics")
        st.write("บันทึกอาหารและแสดงสถิติการกินในแต่ละวัน")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Current Model Classes")

    class_columns = st.columns(4)

    for index, (key, label) in enumerate(FOOD_LABELS.items()):
        with class_columns[index % 4]:
            st.markdown(
                f"""
                <div class="food-row" style="text-align:center;">
                    <div style="color:#C4A7FF;font-weight:600;">{index + 1:02d}</div>
                    <div style="color:#F4F0FF;">{label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.info(
        "โมเดลปัจจุบันรองรับ 8 คลาสอาหารตามชุดข้อมูลที่ฝึกไว้ "
        "การเพิ่มเป็น 60 เมนูจำเป็นต้องเพิ่มข้อมูลและฝึกโมเดลใหม่"
    )

    st.warning(
        "ค่าพลังงานและสารอาหารเป็นค่าประมาณจากฐานข้อมูลต่อ 100 กรัม "
        "อาหารจริงอาจแตกต่างตามสูตร วัตถุดิบ ปริมาณน้ำมัน และวิธีปรุง "
        "ระบบนี้ไม่ใช่เครื่องมือวินิจฉัยหรือคำแนะนำทางการแพทย์"
    )

    st.markdown("### Technology Stack")

    st.write(
        """
        - Python
        - Streamlit
        - YOLO Object Detection
        - Pandas
        - Plotly
        - Pillow
        - CSV / JSON สำหรับจัดเก็บข้อมูลในเวอร์ชันปัจจุบัน
        """
    )


# =========================================================
# 13. FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
        <div style="font-size:.9rem;color:#B69AFF;font-weight:600;">
            FOODVISION AI
        </div>
        SMART FOOD · SMART NUTRITION · SMART LIVING
        <br>
        <span>AI nutrition estimates are for informational purposes only.</span>
    </div>
    """,
    unsafe_allow_html=True,
)
