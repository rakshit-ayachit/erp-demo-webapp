import streamlit as st
from PIL import Image
from datetime import datetime
import pandas as pd
import plotly.express as px

# --- ERP Feature Modules ---
from pages.sales import sales_page
from pages.products import product_page
from insert_data import insert_data_from_csv
from pages.dashboard import dashboard_page
from pages.lstm import sales_page as lstm_page
from pages.vendors import display_vendor_kpis
from pages.xgboost1 import vendor_approval_prediction_app
from pages.product_sales import generate_product_sales_dashboard
from pages.ocr_inv import ocr_module
from db import get_sales_df, get_product_df, get_product_sales_df
from db import get_product_sales_df

# --- Database Utilities ---
from db import (
    engine,
    import_product_sales_csv_to_db,
    drop_product_sales_table,
    import_csv_to_db
)

st.set_page_config(page_title="RISE-style ERP Simulation", layout="wide", initial_sidebar_state="collapsed")
import streamlit as st

st.markdown(
    """
<style>
    [data-testid="collapsedControl"] {
        display: none
    }
</style>
""",
    unsafe_allow_html=True,
)
st.markdown("""
    <style>
    /* Center align tab headers */
    .stTabs [role="tablist"] {
        border-bottom: 2px solid #E0E0E0;
        justify-content: center;
        margin-bottom: 20px;
        gap: 8px;
    }

    /* Individual tab styles */
    .stTabs [role="tab"] {
        font-weight: 600;
        color: #555 !important;
        padding: 12px 24px;
        border-radius: 10px 10px 0 0;
        background-color: #f8f9fa;
        border: 1px solid #e0e0e0;
        transition: all 0.3s ease;
        box-shadow: 0px 1px 3px rgba(0,0,0,0.08);
    }

    /* Active tab style */
    .stTabs [aria-selected="true"] {
        background-color: #007DB8 !important;
        color: #ffffff !important;
        border-bottom: 3px solid transparent;
        box-shadow: 0px 4px 12px rgba(0,125,184,0.2);
    }

    /* General button styling */
    button[kind="primary"] {
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        background-color: #007DB8;
        color: white;
        border: none;
        transition: 0.3s ease-in-out;
    }

    button[kind="primary"]:hover {
        background-color: #005F87;
        transform: translateY(-2px);
    }

    /* Metric cards spacing and styling */
    .element-container:has(.stMetric) {
        background: #ffffff;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }

    /* Expander styling */
    .st-expander {
        border: 1px solid #d9d9d9 !important;
        border-radius: 8px !important;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.04);
        margin-bottom: 10px;
    }

    /* Dataframe enhancements */
    .stDataFrame {
        border-radius: 10px !important;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }

    /* File uploader styling */
    section[data-testid="stFileUploader"] {
        border: 2px dashed #007DB8;
        background-color: #f3faff;
        padding: 20px;
        border-radius: 10px;
    }

    /* Chat input box */
    input[type="text"] {
        border-radius: 8px;
        padding: 10px;
        border: 1px solid #ccc;
    }

    /* Remove weird gray overlay on hover */
    .stButton > button:hover {
        background-color: #005F87 !important;
        color: white !important;
    }

    /* Avatar image (user profile pic) */
    img[alt="User profile picture"] {
        border-radius: 50%;
        border: 2px solid #007DB8;
        box-shadow: 0 0 8px rgba(0, 125, 184, 0.3);
    }

    /* Reduce spacing between headings */
    h2, h3, h4 {
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Custom styling for tabs
st.markdown("""
    <style>
    .stTabs [role="tablist"] {
        border-bottom: 2px solid #ddd;
        justify-content: center;
        margin-bottom: 10px;
    }
    .stTabs [role="tab"] {
        font-weight: 600;
        color: #4F4F4F;
        padding: 10px 20px;
        border-radius: 5px 5px 0 0;
        background-color: #f0f2f6;
        margin-right: 5px;
        transition: 0.2s;
    }
    .stTabs [aria-selected="true"] {
        background-color: #007DB8 !important;
        color: white !important;
        border-bottom: 3px solid transparent;
    }
    .css-1d391kg {display: none;}
    </style>
""", unsafe_allow_html=True)


# --- HEADER ---
col1, col2, col3 = st.columns([1, 6, 1])
with col1:
    st.image("https://upload.wikimedia.org/wikipedia/commons/5/59/SAP_2011_logo.svg", width=100)
with col2:
    st.markdown("<h2 style='text-align: center;'>ERP Simulation Platform - RISE with SAP Style</h2>", unsafe_allow_html=True)
with col3:
    st.image("https://www.w3schools.com/howto/img_avatar.png", width=60)

st.markdown("---")


# --- REAL TABS ---
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "🏠 Home", 
    "🛒 Sales", 
    "📦 Product Management", 
    "📊 Dashboard", 
    "📈 LSTM Prediction", 
    "✅ Vendor Approval", 
    "📍 Product Sales",
    "🚚 Vendor KPIs",
    "🧾 Invoice Validation"])


 
# --- HOME TAB ---
with tab1:
    st.markdown("🏠 Home")
    st.markdown(f"🕒 **System Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 🔄 Sync: Live")

    st.markdown("### 🚨 Live System Notifications")
    notif_col1, notif_col2 = st.columns(2)
    with notif_col1:
        st.warning("⚠️ Vendor 'SpeedParts Inc' approval pending.")
    with notif_col2:
        st.success("✅ Invoice reconciliation completed for batch #2341.")

    df = get_sales_df()
    products_df = get_product_df()  # Fetch products data for the dashboard
    df["date"] = pd.to_datetime(df["date"])



    st.markdown("### 📊 Business Health Snapshot")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Revenue", f"${df['revenue'].sum():,.2f}", "+5.4%")
    kpi2.metric("Orders", f"{df['historical_sales'].sum():,.0f}", "+3.1%")
    kpi3.metric("Customers", df['customer_id'].nunique(), "+1.2%")
    kpi4.metric("Stockouts", "7", "-2.6%")

    st.markdown("### 🧑‍💼 CRM Snapshot")
    crm1, crm2, crm3 = st.columns(3)
    crm1.metric("Active Leads", "23", "+5")
    crm2.metric("Deals Closing This Week", "6", "+2")
    crm3.metric("Contacts in Pipeline", "89", "+10")

    st.markdown("### 🥇 Top-Selling Products")
    product_sales_df = get_product_sales_df()

    if 'product_name' in product_sales_df.columns and 'total_revenue' in product_sales_df.columns:
        top_rev = product_sales_df.groupby('product_name')['total_revenue'].sum().nlargest(5).reset_index()
        st.subheader("💵 Top 5 Products (by Revenue)")
        st.dataframe(top_rev)
    st.markdown("### 🔥 Inventory Distribution Heatmap")
    df_heatmap = pd.DataFrame({
        "Warehouse": ["East", "West", "North", "South"],
        "Product A": [40, 80, 60, 20],
        "Product B": [25, 70, 45, 90],
        "Product C": [55, 30, 70, 40],
    }).set_index("Warehouse")
    fig = px.imshow(df_heatmap, text_auto=True, aspect="auto", color_continuous_scale="blues")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📦 Data Quality Check")
    dq1, dq2, dq3 = st.columns(3)
    dq1.metric("Missing Data", "1.2%", "-0.4%")
    dq2.metric("Duplicates", "0.6%", "-0.1%")
    dq3.metric("Last Sync", "2 min ago")

    st.markdown("### 🔎 Quick Lookup")
    search_query = st.text_input("Search products, orders, vendors...")
    if search_query:
        st.info(f"Searching for **{search_query}**... (simulate results here)")

    st.markdown("### 🤖 AI & ML Insights")
    with st.expander("Open Recommendations"):
        st.success("🟢 Auto-Replenishment: Enabled for 9 SKUs")
        st.warning("🟡 Low Approval Score: Vendor TechHub Co.")
        st.info("📈 Projected Q3 Revenue: $1.8M")

    st.markdown("### 📋 Pending Approvals Workflow")
    approval_status = pd.DataFrame({
        "Vendor": ["SpeedParts", "TechHub", "QuickTools"],
        "Status": ["Pending", "Under Review", "Approved"]
    })
    st.dataframe(approval_status)

    st.markdown("### 📤 Import New Product File")
    uploaded_file = st.file_uploader("Upload CSV", type="csv")
    if uploaded_file:
        df_upload = pd.read_csv(uploaded_file)
        st.success("✅ File uploaded successfully. Preview below:")
        st.dataframe(df_upload.head())

    st.markdown("### 💬 Support Chat")
    with st.expander("Chat with Support"):
        chat_msg = st.text_input("Type your question...")
        if st.button("Send Message"):
            st.info("👩‍💻 Support will get back to you shortly.")

    st.markdown("### 👤 User Profile")
    st.write("**Name:** John Doe  \n**Role:** Supply Chain Manager  \n**Access Level:** Admin")

    st.markdown("### 📅 Tasks & Reminders")
    tasks = [
        {"task": "Review Vendor X Approval", "due": "Today"},
        {"task": "Sync Product Database", "due": "Tomorrow"},
        {"task": "Analyze Q2 Forecast", "due": "Friday"},
    ]
    for t in tasks:
        st.markdown(f"""
        <div class='task-card'>
            ✅ <b>{t['task']}</b><br><i>Due: {t['due']}</i>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.caption("ERP Simulation App | RISE-Inspired | Powered by Streamlit 💻")

# --- OTHER PAGES ---
with tab2:
    sales_page()

with tab3:
    product_page()

with tab4:
    dashboard_page()

with tab5:
    lstm_page()

with tab6:
    vendor_approval_prediction_app()

with tab7:
    generate_product_sales_dashboard()

with tab8:
    st.markdown("## 🚚 Vendor Scoring KPIs Dashboard")
    display_vendor_kpis()

with tab9:
    st.markdown("## Invoice Validation post OCR")
    ocr_module()


# # --- SIDEBAR NAV ---

# if st.sidebar.button("📥 Import 50K Sales Data"):
#     import_csv_to_db()

# if st.sidebar.button("📥 Import Products Data"):
#     import_products_csv()

# if st.sidebar.button("📥 Drop Products Data"):
#     drop_product_sales_table()

# if st.sidebar.button("📥 Import ProductsSales Data"):
#     import_product_sales_csv_to_db()


