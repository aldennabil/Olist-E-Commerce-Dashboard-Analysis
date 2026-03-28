import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os
from babel.numbers import format_currency

# Set tema seaborn
sns.set(style='dark')

# --- HELPER FUNCTIONS ---

def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "price": "sum"
    }).reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)
    return daily_orders_df

def create_sum_order_items_df(df):
    # Menghitung revenue per kategori sesuai Pertanyaan 1
    sum_order_items_df = df.groupby("product_category_name_english").price.sum().sort_values(ascending=False).reset_index()
    return sum_order_items_df

def create_bystate_df(df):
    # Menghitung revenue per state sesuai permintaan eksplorasi
    bystate_df = df.groupby(by="customer_state").price.sum().sort_values(ascending=False).reset_index()
    bystate_df.rename(columns={"price": "revenue"}, inplace=True)
    return bystate_df

def create_payment_type_df(df):
    # Menghitung distribusi metode pembayaran sesuai Pertanyaan 2
    payment_type_df = df.groupby(by="payment_type").order_id.nunique().sort_values(ascending=False).reset_index()
    payment_type_df.rename(columns={"order_id": "order_count"}, inplace=True)
    return payment_type_df

def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_unique_id", as_index=False).agg({
        "order_purchase_timestamp": "max", 
        "order_id": "nunique",
        "price": "sum"
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    
    return rfm_df

# --- LOAD DATA ---

base_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(base_dir, "all_data.csv")

if not os.path.exists(file_path):
    st.error(f"File tidak ditemukan: {file_path}")
    st.stop()

all_data_df = pd.read_csv(file_path)

# Konversi kolom waktu
datetime_columns = ["order_purchase_timestamp"]
all_data_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_data_df.reset_index(inplace=True)

for column in datetime_columns:
    all_data_df[column] = pd.to_datetime(all_data_df[column])

# --- SIDEBAR ---

min_date = all_data_df["order_purchase_timestamp"].min()
max_date = all_data_df["order_purchase_timestamp"].max()

with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    
    # Filter Rentang Waktu
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Filter Data Berdasarkan Sidebar
main_df = all_data_df[(all_data_df["order_purchase_timestamp"] >= str(start_date)) & 
                      (all_data_df["order_purchase_timestamp"] <= str(end_date))]

# Menyiapkan Dataframe untuk Visualisasi
daily_orders_df = create_daily_orders_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
bystate_df = create_bystate_df(main_df)
payment_type_df = create_payment_type_df(main_df)
rfm_df = create_rfm_df(main_df)

# --- DASHBOARD MAIN PAGE ---

st.header('Olist E-Commerce Performance Dashboard 📊')

# 1. Daily Orders & Revenue
st.subheader('Daily Orders & Total Revenue')
col1, col2 = st.columns(2)

with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total Orders", value=total_orders)

with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), "BRL", locale='pt_BR') 
    st.metric("Total Revenue", value=total_revenue)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_purchase_timestamp"],
    daily_orders_df["order_count"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.set_title("Trend Jumlah Pesanan Harian", fontsize=20)
st.pyplot(fig)

# 2. Product Category Revenue (Pertanyaan 1)
st.subheader("Best & Worst Product Category by Revenue")
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="price", y="product_category_name_english", data=sum_order_items_df.head(5), palette=colors, hue="product_category_name_english", legend=False, ax=ax[0])
ax[0].set_title("Revenue Tertinggi", loc="center", fontsize=50)
ax[0].set_ylabel(None)
ax[0].tick_params(axis='y', labelsize=35)

sns.barplot(x="price", y="product_category_name_english", data=sum_order_items_df.sort_values(by="price", ascending=True).head(5), palette=colors, hue="product_category_name_english", legend=False, ax=ax[1])
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Revenue Terendah", loc="center", fontsize=50)
ax[1].set_ylabel(None)
ax[1].tick_params(axis='y', labelsize=35)

st.pyplot(fig)

# 3. Revenue by State & Payment Type (Eksplorasi & Pertanyaan 2)
st.subheader("State Revenue & Payment Methods")
col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(20, 15))
    sns.barplot(
        x="revenue", 
        y="customer_state",
        data=bystate_df.head(10),
        palette="Blues_r",
        hue="customer_state",
        legend=False,
        ax=ax
    )
    ax.set_title("Top 10 States by Revenue", fontsize=45)
    ax.tick_params(axis='y', labelsize=35)
    ax.tick_params(axis='x', labelsize=30)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(20, 15))
    ax.pie(
        payment_type_df['order_count'], 
        labels=payment_type_df['payment_type'], 
        autopct='%1.1f%%', 
        colors=sns.color_palette("pastel"),
        textprops={'fontsize': 30}
    )
    ax.set_title("Payment Type Distribution", fontsize=45)
    st.pyplot(fig)

# 4. RFM Analysis
st.subheader("Best Customer Based on RFM Parameters")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Avg Recency (days)", value=round(rfm_df.recency.mean(), 1))

with col2:
    st.metric("Avg Frequency", value=round(rfm_df.frequency.mean(), 2))

with col3:
    st.metric("Avg Monetary", value=format_currency(rfm_df.monetary.mean(), "BRL", locale='pt_BR'))

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))

# Plot Recency
sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, hue="customer_id", legend=False, ax=ax[0])
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='x', rotation=45, labelsize=30)
ax[0].set_xlabel(None)

# Plot Frequency
sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, hue="customer_id", legend=False, ax=ax[1])
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='x', rotation=45, labelsize=30)
ax[1].set_xlabel(None)

# Plot Monetary
sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, hue="customer_id", legend=False, ax=ax[2])
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='x', rotation=45, labelsize=30)
ax[2].set_xlabel(None)

st.pyplot(fig)

st.caption('Copyright (c) Alden Nabil 2026')