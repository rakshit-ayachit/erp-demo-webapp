# invoice_encryption_app.py
import streamlit as st
import pandas as pd
# encryption_util.py
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import base64
import os
st.set_page_config(page_title="🔐 Advanced Invoice Encryption", page_icon="🧾", initial_sidebar_state="collapsed")

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

# === CONFIGURATION ===
# Generate a random key once, or load from env
# Use os.urandom(32) once and store it securely
SECRET_KEY = os.environ.get("ERP_AES_KEY")

if not SECRET_KEY:
    # Generate a new key for testing if not set
    key = get_random_bytes(32)  # AES-256
    SECRET_KEY = base64.b64encode(key).decode()
    print("🔑 AES Key for testing (store this securely!):", SECRET_KEY)

# Convert base64 string to bytes
SECRET_KEY = base64.b64decode(SECRET_KEY)

# === FUNCTIONS ===

def encrypt_field(data: str) -> str:
    cipher = AES.new(SECRET_KEY, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(data.encode(), AES.block_size))
    iv = base64.b64encode(cipher.iv).decode()
    ct = base64.b64encode(ct_bytes).decode()
    return f"{iv}:{ct}"

def decrypt_field(data: str) -> str:
    iv, ct = data.split(":")
    iv = base64.b64decode(iv)
    ct = base64.b64decode(ct)
    cipher = AES.new(SECRET_KEY, AES.MODE_CBC, iv=iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    return pt.decode()

# === TEST ===
import streamlit as st
import pandas as pd
import sqlite3


st.title("🔐 Advanced Invoice Encryption System for ERP")
st.markdown("Encrypt & decrypt invoices using AES (128/256-bit) and store in DB.")

# Encryption strength selector
st.sidebar.title("⚙️ Encryption Settings")
encryption_strength = st.sidebar.radio("Select AES Key Size", ["AES-128", "AES-256"])
key_length = 16 if encryption_strength == "AES-128" else 32

# Function to pad/truncate the key to desired length
def get_adjusted_key():
    import base64, os
    key = os.getenv("ERP_AES_KEY", "qv5Y92BexFENB4NFN3MdkcW22r8l6U8EL7d9XHyoZD4=")
    key = base64.b64decode(key)
    return key[:key_length].ljust(key_length, b'0')

# Upload CSV to encrypt multiple invoices
st.subheader("📁 Upload CSV File with Invoice Records (Optional)")
uploaded_csv = st.file_uploader("Upload invoice CSV", type="csv")

if uploaded_csv:
    df = pd.read_csv(uploaded_csv)
    st.write("Preview of Uploaded Data:")
    st.dataframe(df)

    # Encrypt all rows
    encrypted_rows = []
    for _, row in df.iterrows():
        encrypted_rows.append({col: encrypt_field(str(row[col])) for col in df.columns})
    encrypted_df = pd.DataFrame(encrypted_rows)

    st.subheader("🔐 Encrypted Data:")
    st.dataframe(encrypted_df)

    # Decrypted preview
    st.subheader("🔓 Decrypted Preview:")
    decrypted_rows = []
    for _, row in encrypted_df.iterrows():
        decrypted_rows.append({col: decrypt_field(row[col]) for col in encrypted_df.columns})
    decrypted_df = pd.DataFrame(decrypted_rows)
    st.dataframe(decrypted_df)

    # Save to SQLite
    if st.button("💾 Save Encrypted Invoices to Database"):
        conn = sqlite3.connect("erp_sales.db")
        encrypted_df.to_sql("encrypted_invoices", conn, if_exists="append", index=False)
        st.success("✅ Encrypted data saved to 'encrypted_invoices' table in erp_sales.db")

# Manual invoice encryption
st.subheader("🧾 Manual Invoice Entry")

with st.form("manual_encrypt_form"):
    vendor = st.text_input("Vendor")
    invoice_no = st.text_input("Invoice No")
    po_amount = st.text_input("PO Amount")
    approval_status = st.selectbox("Approval Status", ["Approved", "Pending", "Rejected"])
    submitted = st.form_submit_button("🔐 Encrypt Manually")

if submitted:
    encrypted = {
        "vendor": encrypt_field(vendor),
        "invoice_no": encrypt_field(invoice_no),
        "po_amount": encrypt_field(po_amount),
        "approval_status": encrypt_field(approval_status),
    }
    decrypted = {k: decrypt_field(v) for k, v in encrypted.items()}

    col1, col2 = st.columns(2)
    with col1:
        st.write("🔐 Encrypted:")
        st.json(encrypted)
    with col2:
        st.write("🔓 Decrypted:")
        st.json(decrypted)
