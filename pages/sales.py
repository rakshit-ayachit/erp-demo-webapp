import streamlit as st
from db import get_sales_df, insert_sale, generate_invoice_pdf
from datetime import datetime
import streamlit as st
import os
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, Table, Column, Integer, String, Float, MetaData
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import base64
from utils import display_pdf
from io import BytesIO

def sales_page():
    st.subheader("➕ Add a Sales Order")
    with st.form("add_sales_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            order_date = st.date_input("Order Date")
        with col2:
            customer_id = st.number_input("Customer ID", min_value=1000, max_value=9999, step=1)
        with col3:
            sales_channel = st.selectbox("Sales Channel", ['Wholesale', 'Online', 'Retail'])

        col4, col5, col6 = st.columns(3)
        with col4:
            trend_score = st.slider("Customer Trend Score", 0.75, 1.0, 0.85)
        with col5:
            historical_sales = st.number_input("Historical Sales", min_value=100.0, max_value=50000.0)
        with col6:
            revenue = st.number_input("Revenue", min_value=100.0, max_value=200000.0)

        submitted = st.form_submit_button("💾 Add Sales Record")
        if submitted:
            # Save the sales record
            insert_sale({
                'date': datetime.combine(order_date, datetime.now().time()).strftime('%Y-%m-%d %H:%M:%S'),
                'customer_id': customer_id,
                'sales_channel': sales_channel,
                'trend_score': trend_score,
                'historical_sales': historical_sales,
                'revenue': revenue
            })
            st.success("✅ Sales order added successfully!")

            # Set session state to show "Generate Invoice" button
            st.session_state['invoice_customer_id'] = customer_id
            st.session_state['invoice_generated'] = False  # Flag to indicate that invoice is not generated yet

    # Show "Generate Invoice" button after sales record is added
    if st.session_state.get('invoice_customer_id', False):
        if st.button("🔄 Generate Invoice for Order"):
            # Generate the invoice after the button is clicked
            customer_id = st.session_state['invoice_customer_id']
            file_path = generate_invoice_pdf(customer_id)

            # Show the invoice preview in the app (embedded as an iframe)
            st.success(f"✅ Invoice generated for Customer ID: {customer_id}")
            display_pdf(file_path)  # Display PDF in the app

            # Provide a download button for the invoice
            with open(file_path, "rb") as f:
                st.download_button(
                    label="📥 Download Invoice PDF",
                    data=f,
                    file_name=f"invoice_{customer_id}.pdf",
                    mime="application/pdf"
                )

            # Mark invoice as generated
            st.session_state['invoice_generated'] = True
