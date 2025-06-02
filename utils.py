from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os
from db import insert_sale, get_sales_df
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
from io import BytesIO


def generate_invoice_pdf(order_id):
    df = get_sales_df()
    order_data = df[df['customer_id'] == order_id].iloc[0]
    
    total_amount = order_data['revenue']
    tax_amount = total_amount * 0.10  # Example tax rate of 10%
    discount_amount = total_amount * 0.05  # Example discount of 5%
    final_amount = total_amount + tax_amount - discount_amount

    # Invoice details
    customer_id = order_data['customer_id']
    sales_channel = order_data['sales_channel']
    order_date = order_data['date']

    # Create PDF file
    file_path = f"invoices/invoice_{order_id}.pdf"
    if not os.path.exists("invoices"):
        os.makedirs("invoices")

    c = canvas.Canvas(file_path, pagesize=letter)
    c.setFont("Helvetica", 12)

    # Title
    c.setFont("Helvetica-Bold", 18)
    c.drawString(200, 750, f"Invoice for Order ID: {order_id}")

    # Order Details
    c.setFont("Helvetica", 12)
    c.drawString(30, 700, f"Customer ID: {customer_id}")
    c.drawString(30, 680, f"Sales Channel: {sales_channel}")
    c.drawString(30, 660, f"Order Date: {order_date}")

    # Itemized List (for now, it's just the order data)
    c.drawString(30, 620, f"Total Amount: ${total_amount:,.2f}")
    c.drawString(30, 600, f"Tax (10%): ${tax_amount:,.2f}")
    c.drawString(30, 580, f"Discount (5%): -${discount_amount:,.2f}")
    c.drawString(30, 560, f"Final Amount: ${final_amount:,.2f}")

    # Invoice Status
    c.drawString(30, 540, f"Status: Unpaid")

    # Footer
    c.setFont("Helvetica", 8)
    c.drawString(30, 30, "Thank you for your business!")
    c.drawString(30, 20, "www.yourcompanywebsite.com")

    # Save PDF
    c.save()

    return file_path

def display_pdf(file_path):
    # Convert PDF to base64 string to display in the iframe
    with open(file_path, "rb") as f:
        pdf_base64 = base64.b64encode(f.read()).decode("utf-8")
    
    pdf_url = f"data:application/pdf;base64,{pdf_base64}"
    
    # Display inline PDF
    st.markdown(f'<iframe src="{pdf_url}" width="700" height="500"></iframe>', unsafe_allow_html=True)

# st.header("📊 Sales Data Exploration")