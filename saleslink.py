import streamlit as st
from supabase import create_client, Client
import pandas as pd

# --- Konfigurasi Supabase ---
# Ganti dengan URL dan Kunci Anon Anda dari pengaturan Supabase
SUPABASE_URL ="https://axgenexhomnoddhhirdd.supabase.co"
SUPABASE_KEY =" eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF4Z2VuZXhob21ub2RkaGhpcmRkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA0NTg2MjEsImV4cCI6MjA3NjAzNDYyMX0.3cx-ftiTi229Q_f4S0srkvsxj1HNBO_3emB37s6VdF8"

# Nama tabel yang ingin Anda tampilkan/edit
TABLE_NAME = "sales_linkr4"

@st.cache_resource
def init_connection():
    """Menginisialisasi koneksi ke Supabase."""
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# Koneksi ke Supabase
supabase: Client = init_connection()

def fetch_data_by_email(email_address: str):
    """Mengambil data dari Supabase berdasarkan alamat email."""
    try:
        # Panggil data dari Supabase
        response = supabase.from_(TABLE_NAME).select("*").eq("Email Address", email_address).execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            
            # **SOLUSI UNTUK ERROR 'object dtypes'**
            # Konversi semua kolom yang merupakan tipe 'object' (string/campuran) 
            # menjadi tipe 'str' eksplisit untuk st.data_editor.
            
            for col in df.columns:
                if df[col].dtype == 'object':
                    # Menggunakan .fillna('') untuk menghindari nilai NaN di kolom string
                    df[col] = df[col].astype(str).fillna('')
            
            return df
        else:
            return pd.DataFrame() 

    except Exception as e:
        st.error(f"Gagal mengambil data dari Supabase: {e}")
        return pd.DataFrame()


# --- Fungsi untuk Memperbarui Data (Edit) ---
def update_data(row_id: int, updates: dict):
    """Memperbarui baris tertentu dalam tabel berdasarkan ID-nya."""
    try:
        # Asumsikan kolom kunci utama adalah 'id'
        response = supabase.table(sales_linkr4).update(updates).eq("id", row_id).execute()
        
        if not response.data:
            st.warning("Data tidak ditemukan untuk diperbarui.")
            return False

        st.success("Data berhasil diperbarui!")
        return True

    except Exception as e:
        st.error(f"Gagal memperbarui data: {e}")
        return False

# --- Aplikasi Streamlit Utama ---
st.title("Aplikasi Tampil dan Edit Data Supabase")

# Input untuk Alamat Email
user_email = st.text_input(
    "Masukkan Alamat Email (Gmail) Anda:", 
    key="email_input"
)

# Tombol untuk memuat data
if st.button("Muat Data"):
    if user_email:
        # 1. Ambil data
        df = fetch_data_by_email(user_email)
        
        if not df.empty:
            st.subheader(f"Data untuk {user_email}")
            st.session_state['data_df'] = df
            st.session_state['data_loaded'] = True
        else:
            st.info(f"Tidak ada data ditemukan untuk {user_email}.")
            st.session_state['data_loaded'] = False
            st.session_state['data_df'] = pd.DataFrame()
    else:
        st.warning("Mohon masukkan alamat email.")

# Tampilkan dan edit data (hanya jika data sudah dimuat)
if st.session_state.get('data_loaded', False):
    
    # 2. Tampilkan DataFrame yang dapat diedit
    st.markdown("---")
    st.subheader("Edit Data di Bawah")
    
    # Menambahkan kolom 'id' ke list kolom yang akan ditampilkan jika belum ada
    if 'id' not in st.session_state['data_df'].columns:
        # Asumsi: Jika data tidak memiliki 'id', ini akan bermasalah saat update.
        # Supabase biasanya menyediakan 'id' otomatis.
        st.error("Kolom 'id' (kunci utama) tidak ditemukan. Pastikan tabel Anda memiliki kolom 'id'.")
    
    # Menampilkan data yang bisa diedit. Gunakan 'st.data_editor'
    edited_df = st.data_editor(
        st.session_state['data_df'],
        key="editor",
        num_rows="dynamic", # Memungkinkan penambahan baris baru jika Anda mau
    )
    
    # 3. Tombol Simpan Perubahan
    if st.button("Simpan Perubahan"):
        original_df = st.session_state['data_df']
        
        # Membandingkan DataFrame yang asli dengan yang diedit untuk menemukan perubahan
        # Ini adalah bagian yang paling rumit, fokus pada baris yang dimodifikasi
        
        changes_detected = False
        update_success = True
        
        # Iterasi melalui baris yang diedit
        for index, edited_row in edited_df.iterrows():
            # Cek apakah baris ini berasal dari data asli (bukan baris baru)
            if index in original_df.index:
                original_row = original_df.loc[index]
                
                # Mendeteksi perubahan pada baris ini
                updates = {}
                for col in edited_row.index:
                    if edited_row[col] != original_row[col]:
                        updates[col] = edited_row[col]
                        
                # Jika ada perubahan, lakukan update
                if updates:
                    changes_detected = True
                    row_id = original_row['id'] # Ambil ID baris yang akan diupdate
                    
                    st.info(f"Memperbarui ID **{row_id}** dengan perubahan: {updates}")
                    
                    if not update_data(row_id, updates):
                        update_success = False
                        break # Hentikan jika ada kegagalan update
        
        if changes_detected and update_success:
            st.success("Semua perubahan berhasil disimpan! Muat ulang data untuk melihat konfirmasi.")
        elif not changes_detected:
            st.info("Tidak ada perubahan terdeteksi.")
        
        # Muat ulang data setelah update
        if update_success:
            st.session_state['data_loaded'] = False # Reset status
            st.button("Muat Data") # Tampilkan tombol muat data lagi