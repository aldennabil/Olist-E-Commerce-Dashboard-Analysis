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
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)
    return daily_orders_df

def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("product_category_name_english").order_item_id.count().sort_values(ascending=False).reset_index()
    return sum_order_items_df

def create_bystate_df(df):
    bystate_df = df.groupby(by="customer_state").customer_unique_id.nunique().sort_values(ascending=False).reset_index()
    bystate_df.rename(columns={"customer_unique_id": "customer_count"}, inplace=True)
    return bystate_df

def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_unique_id", as_index=False).agg({
        "order_purchase_timestamp": "max", 
        "order_id": "nunique",
        "price": "sum"
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    
    # Menghitung recency
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    
    return rfm_df

# --- LOAD DATA ---

# Menggunakan path dinamis agar aman di lokal maupun Streamlit Cloud
base_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(base_dir, "all_data.csv")

if not os.path.exists(file_path):
    st.error(f"File tidak ditemukan: {file_path}")
    st.stop()

all_data_df = pd.read_csv(file_path)

# Konversi kolom waktu (hanya menggunakan kolom yang tersedia di CSV)
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
    try:
        start_date, end_date = st.date_input(
            label='Rentang Waktu',
            min_value=min_date,
            max_value=max_date,
            value=[min_date, max_date]
        )
    except ValueError:
        st.error("Pastikan rentang waktu yang dipilih valid.")
        st.stop()

# Filter Data Berdasarkan Sidebar
main_df = all_data_df[(all_data_df["order_purchase_timestamp"] >= str(start_date)) & 
                      (all_data_df["order_purchase_timestamp"] <= str(end_date))]

# Menyiapkan Dataframe untuk Visualisasi
daily_orders_df = create_daily_orders_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
bystate_df = create_bystate_df(main_df)
rfm_df = create_rfm_df(main_df)

# --- DASHBOARD MAIN PAGE ---

st.header('Olist E-Commerce Dashboard :sparkles:')

# 1. Daily Orders Section
st.subheader('Daily Orders')
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
ax.set_title("Jumlah Pesanan Harian", fontsize=20)
ax.tick_params(axis='x', rotation=45)
st.pyplot(fig)

# 2. Product Performance Section
st.subheader("Best & Worst Performing Product")
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

# Best Performing
sns.barplot(
    x="order_item_id", 
    y="product_category_name_english", 
    data=sum_order_items_df.head(5), 
    palette=colors, 
    hue="product_category_name_english",
    legend=False,
    ax=ax[0]
)
ax[0].set_title("Produk Paling Laris", loc="center", fontsize=50)
ax[0].set_ylabel(None)
ax[0].tick_params(axis='y', labelsize=35)

# Worst Performing
sns.barplot(
    x="order_item_id", 
    y="product_category_name_english", 
    data=sum_order_items_df.sort_values(by="order_item_id", ascending=True).head(5), 
    palette=colors, 
    hue="product_category_name_english",
    legend=False,
    ax=ax[1]
)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Produk Paling Sedikit Terjual", loc="center", fontsize=50)
ax[1].set_ylabel(None)
ax[1].tick_params(axis='y', labelsize=35)

st.pyplot(fig)

# 3. Customer Demographics Section
st.subheader("Customer Demographics")
fig, ax = plt.subplots(figsize=(20, 10))
sns.barplot(
    x="customer_count", 
    y="customer_state",
    data=bystate_df.head(10),
    palette="Blues_r",
    hue="customer_state",
    legend=False,
    ax=ax
)
ax.set_title("Jumlah Pelanggan Berdasarkan Negara Bagian (Top 10)", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=20)
st.pyplot(fig)

# 4. RFM Analysis Section
st.subheader("Best Customer Based on RFM Parameters")
col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Avg Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Avg Frequency", value=avg_frequency)

with col3:
    avg_monetary = format_currency(rfm_df.monetary.mean(), "BRL", locale='pt_BR')
    st.metric("Avg Monetary", value=avg_monetary)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))

# Plot Recency
sns.barplot(
    y="recency", 
    x="customer_id", 
    data=rfm_df.sort_values(by="recency", ascending=True).head(5), 
    palette=colors, 
    hue="customer_id",
    legend=False,
    ax=ax[0]
)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='x', rotation=45, labelsize=30)
ax[0].set_xlabel(None)

# Plot Frequency
sns.barplot(
    y="frequency", 
    x="customer_id", 
    data=rfm_df.sort_values(by="frequency", ascending=False).head(5), 
    palette=colors, 
    hue="customer_id",
    legend=False,
    ax=ax[1]
)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='x', rotation=45, labelsize=30)
ax[1].set_xlabel(None)

# Plot Monetary
sns.barplot(
    y="monetary", 
    x="customer_id", 
    data=rfm_df.sort_values(by="monetary", ascending=False).head(5), 
    palette=colors, 
    hue="customer_id",
    legend=False,
    ax=ax[2]
)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='x', rotation=45, labelsize=30)
ax[2].set_xlabel(None)

st.pyplot(fig)

st.caption('Copyright (c) Alden Nabil 2024')