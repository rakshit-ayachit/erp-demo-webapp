import streamlit as st
from db import get_product_df, insert_product, engine, products
import pandas as pd
from sqlalchemy import create_engine, Table, Column, Integer, String, Float, MetaData


def product_page():
    st.title("📦 Product Management")

    # --- ADD NEW PRODUCT FORM ---
    st.subheader("➕ Add a New Product")
    with st.form("add_product_form"):
        col1, col2 = st.columns(2)
        with col1:
            product_name = st.text_input("Product Name")
        with col2:
            sku = st.text_input("SKU")

        col3, col4 = st.columns(2)
        with col3:
            description = st.text_area("Description")
        with col4:
            price = st.number_input("Price ($)", min_value=0.0, step=0.01)

        image_url = st.text_input("Image URL (optional)")

        add_product = st.form_submit_button("💾 Add Product")
        if add_product:
            with engine.begin() as conn:
                conn.execute(products.insert().values(
                    name=product_name,
                    sku=sku,
                    description=description,
                    price=price,
                    image_url=image_url
                ))
            st.success(f"✅ Product '{product_name}' added successfully!")

    st.subheader("Here is a list of available products:")

    # Fetch the product data
    df = get_product_df()

    if df.empty:
        st.warning("No products available.")
    else:
        # Display the product data in a table format
        st.dataframe(df)

        # Optionally, display more details on click
        product_id = st.selectbox("Select Product ID to view details", df['id'].tolist())
        
        if product_id:
            selected_product = df[df['id'] == product_id].iloc[0]
            st.subheader("Product Details:")
            st.write(f"**Name:** {selected_product['name']}")
            st.write(f"**SKU:** {selected_product['sku']}")
            st.write(f"**Description:** {selected_product['description']}")
            st.write(f"**Price:** ${selected_product['price']:,.2f}")

            if selected_product['image_url']:
                st.image(selected_product['image_url'], caption=selected_product['name'], use_column_width=True)
            else:
                st.warning("No image available for this product.")