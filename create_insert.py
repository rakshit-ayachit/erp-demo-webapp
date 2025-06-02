import pandas as pd
from sqlalchemy import create_engine, Column, String, Integer, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load the CSV file into a pandas DataFrame
invoice_df = pd.read_csv("./datasets/invoices-db.csv")

# Create a base class for SQLAlchemy models
Base = declarative_base()

# Define the table schema (model) for the 'invoices' table
class Invoice(Base):
    __tablename__ = 'invoices-ocr'

    # Define the columns of the table based on the CSV structure
    vendor = Column(String, nullable=False)
    invoice_no = Column(String, primary_key=True, nullable=False)
    date = Column(String, nullable=False)
    city = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    gstin_vendor = Column(String, nullable=False)
    client = Column(String, nullable=False)
    gstin_client = Column(String, nullable=False)
    vendor_id = Column(String, nullable=False)
    po_amount = Column(Float, nullable=False)
    approval_status = Column(String, nullable=False)
    vendor_rating = Column(Float, nullable=False)
    lead_time = Column(String, nullable=False)
    product = Column(String, nullable=False)
    service = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total = Column(Float, nullable=False)

# Create SQLite DB connection
engine = create_engine("sqlite:///erp_sales.db")

# Create tables in the database (if they don't exist)
Base.metadata.create_all(engine)

# Create a session to insert data into the database
Session = sessionmaker(bind=engine)
session = Session()

# Insert data into the 'invoices' table
for _, row in invoice_df.iterrows():
    invoice = Invoice(
        vendor=row['vendor'],
        invoice_no=row['invoice_no'],
        date=row['date'],
        city=row['city'],
        phone=row['phone'],
        gstin_vendor=row['gstin_vendor'],
        client=row['client'],
        gstin_client=row['gstin_client'],
        vendor_id=row['vendor_id'],
        po_amount=row['po_amount'],
        approval_status=row['approval_status'],
        vendor_rating=row['vendor_rating'],
        lead_time=row['lead_time'],
        product=row['product'],
        service=row['service'],
        quantity=row['quantity'],
        unit_price=row['unit_price'],
        total=row['total']
    )
    session.add(invoice)

# Commit the session to insert the data into the database
session.commit()

# Close the session
session.close()

print("✅ Table created and invoices data inserted into the 'invoices' table in erp_sales.db.")
