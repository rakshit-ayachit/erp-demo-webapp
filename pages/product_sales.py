import streamlit as st
import pandas as pd
import plotly.express as px
from db import get_product_sales_df


def generate_product_sales_dashboard():
    st.title("📊 Product Sales Dashboard")

    # Load data
    product_sales_df = get_product_sales_df()
    
    # Ensure datetime conversion
    product_sales_df['first_sale_date'] = pd.to_datetime(product_sales_df['first_sale_date'])
    product_sales_df['last_sale_date'] = pd.to_datetime(product_sales_df['last_sale_date'])

    st.header("📌 Filters")

    # ------------------ FILTERS ------------------

    # Product Name Filter
    product_name_filter = None
    if st.checkbox("Filter by Product Name", value=True):
        product_name_filter = st.selectbox("Select Product Name", product_sales_df['product_name'].unique())

    # Product ID Filter
    product_id_filter = None
    if st.checkbox("Filter by Product ID", value=True):
        product_id_filter = st.selectbox("Select Product ID", product_sales_df['product_id'].unique())

    # Revenue Range Filter
    revenue_range = (product_sales_df['total_revenue'].min(), product_sales_df['total_revenue'].max())
    if st.checkbox("Filter by Total Revenue", value=True):
        revenue_range = st.slider("Select Total Revenue Range", 
                                  int(revenue_range[0]), 
                                  int(revenue_range[1]), 
                                  (int(revenue_range[0]), int(revenue_range[1])))

    # Number of Orders Filter
    order_range = (product_sales_df['number_of_orders'].min(), product_sales_df['number_of_orders'].max())
    if st.checkbox("Filter by Number of Orders", value=True):
        order_range = st.slider("Select Number of Orders Range",
                                int(order_range[0]), int(order_range[1]), 
                                (int(order_range[0]), int(order_range[1])))

    # First Sale Date
    first_sale_date_range = (product_sales_df['first_sale_date'].min().date(), product_sales_df['first_sale_date'].max().date())
    if st.checkbox("Filter by First Sale Date", value=True):
        selected_first_sale_date = st.date_input("Select First Sale Date", 
                                                 min_value=first_sale_date_range[0], 
                                                 max_value=first_sale_date_range[1], 
                                                 value=first_sale_date_range[0])
    else:
        selected_first_sale_date = first_sale_date_range[0]

    # Last Sale Date
    last_sale_date_range = (product_sales_df['last_sale_date'].min().date(), product_sales_df['last_sale_date'].max().date())
    if st.checkbox("Filter by Last Sale Date", value=True):
        selected_last_sale_date = st.date_input("Select Last Sale Date", 
                                                min_value=last_sale_date_range[0], 
                                                max_value=last_sale_date_range[1], 
                                                value=last_sale_date_range[1])
    else:
        selected_last_sale_date = last_sale_date_range[1]

    # ------------------ APPLY FILTERS ------------------

    filtered_data = product_sales_df.copy()

    if product_name_filter:
        filtered_data = filtered_data[filtered_data['product_name'] == product_name_filter]

    if product_id_filter:
        filtered_data = filtered_data[filtered_data['product_id'] == product_id_filter]

    filtered_data = filtered_data[
        (filtered_data['total_revenue'] >= revenue_range[0]) &
        (filtered_data['total_revenue'] <= revenue_range[1]) &
        (filtered_data['number_of_orders'] >= order_range[0]) &
        (filtered_data['number_of_orders'] <= order_range[1]) &
        (filtered_data['first_sale_date'] >= pd.to_datetime(selected_first_sale_date)) &
        (filtered_data['last_sale_date'] <= pd.to_datetime(selected_last_sale_date))
    ]

    # ------------------ DISPLAY DATA ------------------

    st.markdown("### 🎯 Filter Summary")
    st.write(f"""
        **Product Name**: {product_name_filter or 'Any'} |
        **Product ID**: {product_id_filter or 'Any'} |
        **Revenue Range**: {revenue_range} |
        **Orders Range**: {order_range} |
        **First Sale Date ≥** {selected_first_sale_date} |
        **Last Sale Date ≤** {selected_last_sale_date}
    """)

    st.dataframe(filtered_data)

    # ------------------ CHARTS ------------------

    # Revenue Distribution
    st.subheader("💰 Revenue Distribution by Product")
    rev_dist = filtered_data.groupby('product_name')['total_revenue'].sum().reset_index()
    fig1 = px.pie(rev_dist, names='product_name', values='total_revenue', title='Revenue Distribution by Product')
    st.plotly_chart(fig1)

    # Top 10 Products by Revenue
    st.subheader("🏆 Top 10 Products by Revenue")
    top10 = filtered_data.sort_values(by='total_revenue', ascending=False).head(10)
    st.dataframe(top10[['product_name', 'total_units_sold', 'total_revenue', 'number_of_orders']])

    # Time-series Performance
    st.subheader("📈 Sales Performance Over Time")
    ts_data = filtered_data.groupby('first_sale_date')['total_revenue'].sum().reset_index()
    fig2 = px.line(ts_data, x='first_sale_date', y='total_revenue', title='Revenue Over Time')
    st.plotly_chart(fig2)

    # Monthly Revenue Trends
    st.subheader("📆 Monthly Revenue by Product")
    filtered_data['month'] = filtered_data['first_sale_date'].dt.to_period("M").astype(str)
    month_data = filtered_data.groupby(['month', 'product_name'])[['total_revenue']].sum().reset_index()
    fig3 = px.line(month_data, x='month', y='total_revenue', color='product_name', title='Monthly Revenue per Product')
    st.plotly_chart(fig3)

    # ------------------ TOP PRODUCTS SECTION ------------------

    if 'product_name' in product_sales_df.columns and 'total_units_sold' in product_sales_df.columns:
        top_units = product_sales_df.groupby('product_name')['total_units_sold'].sum().nlargest(5).reset_index()
        st.subheader("🔝 Top 5 Products (by Units Sold)")
        st.dataframe(top_units)
        st.bar_chart(top_units.set_index('product_name'))
    elif 'product_name' in product_sales_df.columns and 'total_revenue' in product_sales_df.columns:
        top_rev = product_sales_df.groupby('product_name')['total_revenue'].sum().nlargest(5).reset_index()
        st.subheader("💵 Top 5 Products (by Revenue)")
        st.dataframe(top_rev)
        st.bar_chart(top_rev.set_index('product_name'))

    # ------------------ DOWNLOAD ------------------

    st.subheader("⬇️ Download Filtered Data")
    st.download_button(
        label="Download CSV",
        data=filtered_data.to_csv(index=False).encode('utf-8'),
        file_name='filtered_product_sales.csv',
        mime='text/csv'
    )

# if __name__ == "__main__":
# generate_product_sales_dashboard()
