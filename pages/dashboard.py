import streamlit as st
import plotly.express as px
import pandas as pd
from db import get_sales_df, get_product_df, get_product_sales_df

def dashboard_page():
    st.title("📊 Sales Dashboard")

    # Fetching sales and products data
    df = get_sales_df()
    products_df = get_product_df()  # Fetch products data for the dashboard
    df["date"] = pd.to_datetime(df["date"])

    # -------------------- KPIs --------------------
    k1, k2, k3 = st.columns(3)
    k1.metric("💰 Total Revenue", f"${df['revenue'].sum():,.2f}")
    k2.metric("📦 Total Sales Volume", f"{df['historical_sales'].sum():,.0f}")
    k3.metric("👥 Unique Customers", df['customer_id'].nunique())

    st.divider()

    # -------------------- Revenue by Channel --------------------
    fig1 = px.pie(df, names='sales_channel', values='revenue', title="Revenue by Sales Channel")
    st.plotly_chart(fig1, use_container_width=True)

    # -------------------- Monthly Revenue Trend --------------------
    monthly_revenue = (
        df.groupby(df['date'].dt.to_period('M').dt.to_timestamp())
        .sum(numeric_only=True)
        .reset_index()
    )
    fig2 = px.line(monthly_revenue, x='date', y='revenue', title="Monthly Revenue Trend")
    st.plotly_chart(fig2, use_container_width=True)

    # -------------------- Revenue vs Customer Trend Score --------------------
    st.subheader("📈 Revenue vs Customer Trend Score")
    fig3 = px.scatter(
        df.sample(min(1000, len(df))), x='trend_score', y='revenue',
        color='sales_channel', trendline='ols', opacity=0.6
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.divider()

    # -------------------- Product Sales Insights --------------------
    st.header("📦 Product Sales Insights")

    # Fetch product sales data from the database
    # product_sales_df = get_product_sales_df()  # Fetch product sales data from the DB

    # # -------------------- Total Revenue by Product --------------------
    # fig_product_revenue = px.bar(
    #     product_sales_df,
    #     x='product_name', y='total_revenue',
    #     title="Total Revenue by Product",
    #     labels={'product_name': 'Product Name', 'total_revenue': 'Total Revenue ($)'},
    #     color='product_name'
    # )
    # st.plotly_chart(fig_product_revenue, use_container_width=True)

    # # -------------------- Total Units Sold by Product --------------------
    # fig_units_sold = px.bar(
    #     product_sales_df,
    #     x='product_name', y='total_units_sold',
    #     title="Total Units Sold by Product",
    #     labels={'product_name': 'Product Name', 'total_units_sold': 'Units Sold'},
    #     color='product_name'
    # )
    # st.plotly_chart(fig_units_sold, use_container_width=True)

    # # -------------------- Top Products by Number of Orders --------------------
    # top_ordered_products = product_sales_df.nlargest(10, 'number_of_orders')
    # fig_top_orders = px.bar(
    #     top_ordered_products,
    #     x='product_name', y='number_of_orders',
    #     title="Top 10 Products by Number of Orders",
    #     labels={'product_name': 'Product Name', 'number_of_orders': 'Number of Orders'},
    #     color='product_name'
    # )
    # st.plotly_chart(fig_top_orders, use_container_width=True)

    # # -------------------- Average Price by Product --------------------
    # fig_avg_price = px.bar(
    #     product_sales_df,
    #     x='product_name', y='average_price',
    #     title="Average Price by Product",
    #     labels={'product_name': 'Product Name', 'average_price': 'Average Price ($)'},
    #     color='product_name'
    # )
    # st.plotly_chart(fig_avg_price, use_container_width=True)

    # # -------------------- Revenue Per Order by Product --------------------
    # fig_revenue_per_order = px.bar(
    #     product_sales_df,
    #     x='product_name', y='avg_revenue_per_order',
    #     title="Revenue Per Order by Product",
    #     labels={'product_name': 'Product Name', 'avg_revenue_per_order': 'Revenue Per Order ($)'},
    #     color='product_name'
    # )
    # st.plotly_chart(fig_revenue_per_order, use_container_width=True)

    # st.divider()

    # -------------------- Product Performance --------------------
    st.header("📦 Product Performance")

    st.subheader("💲 Most Expensive Products")

    # Sort products by price and take top 10
    top_expensive = products_df.sort_values(by='price', ascending=False).head(10)

    fig_expensive = px.bar(
        top_expensive,
        x='name', y='price',
        title='💲 Top 10 Most Expensive Products',
        labels={'name': 'Product Name', 'price': 'Price ($)'},
        color='category'
    )
    st.plotly_chart(fig_expensive, use_container_width=True)

    # -------------------- 📋 Product Summary Table --------------------
    st.subheader("📋 Product Summary")
    st.dataframe(products_df[['name', 'sku', 'price', 'category']])

if __name__ == "__main__":
    dashboard_page()
