# Olist E-Commerce Performance Analysis Dashboard 📊

## Deskripsi
Dashboard ini dikembangkan untuk menganalisis performa penjualan dan perilaku pelanggan pada platform E-Commerce Olist di Brazil. Fokus analisis mencakup performa kategori produk sepanjang Januari-Agustus 2018, preferensi metode pembayaran pada semester pertama 2018, serta segmentasi pelanggan menggunakan teknik RFM (*Recency, Frequency, Monetary*).

## Struktur Proyek
- `Dashboard/`: Folder utama aplikasi dashboard.
  - `dashboard.py`: File python utama untuk menjalankan aplikasi Streamlit.
  - `all_data.csv`: Dataset yang telah dipangkas (*pruning*) dan dibersihkan untuk kebutuhan dashboard.
- `Data/`: Berisi kumpulan berkas dataset mentah dalam format CSV.
- `Codingcamp_Proyek_Analisis_Data.ipynb`: Dokumentasi lengkap proses analisis data (Wrangling, EDA, Visualization, & Conclusion).
- `requirements.txt`: Daftar pustaka (*library*) Python yang dibutuhkan.
- `url.txt`: Tautan menuju dashboard yang telah di-deploy.

## Setup Environment - Shell/Terminal (Windows)
Sangat disarankan untuk menggunakan **Virtual Environment** agar pustaka proyek ini terisolasi dan tidak mengganggu sistem utama.

1. **Buka Command Prompt atau PowerShell.**

2. **Masuk ke Direktori Proyek:**
   ```cmd
   cd "C:\Path\Ke\Folder\Proyek\Anda"

3. Buat Virtual Enviroment
python -m venv venv

4. Aktifkan Virtual Enviroment
.\venv\Scripts\activate

5. Install Requirements
pip install -r requirements.txt

6. Menjalankan Dashboard di Lokal
streamlit run Dashboard/dashboard.py


Aplikasi ini telah di-deploy dan dapat diakses secara publik melalui tautan berikut:
👉 https://alden-olist-dashboard.streamlit.app/