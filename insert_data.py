import pandas as pd
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.orm import sessionmaker

# Database Setup
engine = create_engine("sqlite:///erp_sales.db", echo=False)
meta = MetaData()

# Load CSV Files
products_df = pd.read_csv("./datasets/products.csv")
sales_df = pd.read_csv("./datasets/sales.csv")

# Define Table Structure (using previous definitions)
from sqlalchemy import Table, Column, Integer, String, Float

# Products Table
products = Table('products', meta,
    Column('id', Integer, primary_key=False),
    Column('name', String),
    Column('sku', String),
    Column('description', String),
    Column('price', Float),
    Column('image_url', String),
    Column('category', String)
)

# Sales Table
sales = Table('sales', meta,
    Column('id', Integer, primary_key=True),
    Column('date', String),
    Column('customer_id', Integer),
    Column('sales_channel', String),
    Column('trend_score', Float),
    Column('historical_sales', Float),
    Column('revenue', Float)
)

# Function to insert data from DataFrame into DB only if it does not exist
def insert_data_from_csv():
    with engine.begin() as conn:
        # Insert Product Data only if not already present
        for index, row in products_df.iterrows():
            # Check if product already exists
            result = conn.execute(products.select().where(products.c.id == row['id'])).fetchone()
            if not result:  # If no record exists with that ID, insert
                conn.execute(products.insert().values(
                    id=row['id'],
                    name=row['name'],
                    sku=row['sku'],
                    description=row['description'],
                    price=row['price'],
                    image_url=row['image_url'],
                    category=row['category']
                ))

        # Insert Sales Data only if not already present
        for index, row in sales_df.iterrows():
            # Check if sale already exists
            result = conn.execute(sales.select().where(sales.c.id == row['id'])).fetchone()
            if not result:  # If no record exists with that ID, insert
                conn.execute(sales.insert().values(
                    id=row['id'],
                    date=row['date'],
                    customer_id=row['customer_id'],
                    sales_channel=row['sales_channel'],
                    trend_score=row['trend_score'],
                    historical_sales=row['historical_sales'],
                    revenue=row['revenue']
                ))

# Insert data into the database
