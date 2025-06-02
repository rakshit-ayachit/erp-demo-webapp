import pandas as pd
from sqlalchemy import create_engine, Table, Column, Integer, String, Float, MetaData
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import base64
from datetime import datetime
from sqlalchemy import create_engine, text

import os
import streamlit as st
# Database Setup
engine = create_engine("sqlite:///erp_sales.db", echo=False)
meta = MetaData()

# Sales Table Schema
sales = Table('sales', meta,
    Column('id', Integer, primary_key=True),
    Column('date', String),
    Column('customer_id', Integer),
    Column('sales_channel', String),
    Column('trend_score', Float),
    Column('historical_sales', Float),
    Column('revenue', Float)
)

# Products Table Schema
products = Table('products', meta,
    Column('id', String, primary_key=False),
    Column('name', String),
    Column('sku', String),
    Column('description', String),
    Column('price', Float),
    Column('image_url', String),
    Column('category', String)
)

# Invoice Table Schema
invoices = Table('invoices', meta,
    Column('order_id', Integer),
    Column('invoice_date', String),
    Column('total_amount', Float),
    Column('tax_amount', Float),
    Column('discount_amount', Float),
    Column('status', String)
)
#Product sales
product_sales = Table('product_sales', meta,
    Column('product_id', String, primary_key=False),
    Column('product_name', String),
    Column('total_units_sold', Integer),
    Column('total_revenue', Float),
    Column('number_of_orders', Integer),
    Column('first_sale_date', String),
    Column('last_sale_date', String),
    Column('average_price', Float),
    Column('avg_revenue_per_order', Float)
)
meta.create_all(engine)

def import_csv_to_db():
    df = pd.read_csv('./datasets/sales.csv')
    df.columns = ['date', 'customer_id', 'historical_sales', 'trend_score', 'sales_channel', 'revenue']
    df = df[['date', 'customer_id', 'sales_channel', 'trend_score', 'historical_sales', 'revenue']]
    with engine.begin() as conn:
        df.to_sql('sales', conn, if_exists='append', index=False)
    st.success("✅ Imported CSV into database successfully.")
def drop_product_sales_table():
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS product_sales"))  # ✅ Wrap with text()
        print("✅ Dropped existing 'product_sales' table.")

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
# Fetch Sales Data
def get_sales_df():
    with engine.connect() as conn:
        return pd.read_sql_table("sales", conn)

# Fetch Product Data
def get_product_df():
    with engine.connect() as conn:
        return pd.read_sql_table("products", conn)

def get_product_sales_df():
    with engine.connect() as conn:
        return pd.read_sql_table("product_sales", conn)


# Insert Sale Record
def insert_sale(values):
    with engine.begin() as conn:
        conn.execute(sales.insert(), values)

# Insert Product Record
def insert_product(values):
    with engine.begin() as conn:
        conn.execute(products.insert(), values)

# Insert Invoice Record
def insert_invoice(values):
    with engine.begin() as conn:
        conn.execute(invoices.insert(), values)

def import_products_csv():
    df = pd.read_csv('./datasets/products.csv')
    
    # Adjust the columns to match the CSV structure (ensure 7 columns)
    df.columns = ['id',  'name', 'sku', 'description', 'price', 'image_url', 'category']  # Match CSV columns with database schema 

    with engine.begin() as conn:
        df.to_sql('products', conn, if_exists='append', index=False)
    st.success("✅ Imported Products CSV into database successfully.")

def get_invoices_ocr_data():
    with engine.connect() as conn:
        return pd.read_sql_table("invoices-ocr", conn)
    
def import_product_sales_csv_to_db():
    df = pd.read_csv('product_sales.csv')
    
    # Adjust the columns to match the CSV structure (ensure 7 columns)
    df.columns = [
            'product_id', 'product_name', 'total_units_sold', 'total_revenue',
            'number_of_orders', 'first_sale_date', 'last_sale_date', 'average_price', 'avg_revenue_per_order'
        ]
    with engine.begin() as conn:
        df.to_sql('product_sales', conn, if_exists='append', index=False)
    st.success("✅ Imported ProductsSales CSV into database successfully.")
