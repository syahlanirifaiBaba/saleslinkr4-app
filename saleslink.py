import streamlit as st
from supabase import create_client, Client
import pandas as pd

# =========================================================================
# === KONFIGURASI DAN INIITALISASI ===
# =========================================================================

# --- Pengaturan Halaman Streamlit ---
st.set_page_config(
    page_title="Sales Link Region 4", 
    page_icon="📈", 
    layout="wide" # Menggunakan lebar penuh layar
)

# --- Konfigurasi Supabase (ASUMSI DARI st.secrets) ---
# Anda harus memastikan file .streamlit/secrets.toml sudah ada
try:
SUPABASE_URL ="https://axgenexhomnoddhhirdd.supabase.co"
SUPABASE_KEY =" eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF4Z2VuZXhob21ub2RkaGhpcmRkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA0NTg2MjEsImV4cCI6MjA3NjAzNDYyMX0.3cx-ftiTi229Q_f4S0srkvsxj1HNBO_3emB37s6VdF8"

except KeyError:
    st.error("Pastikan Anda telah mendefinisikan SUPABASE_URL dan SUPABASE_KEY di file .streamlit/secrets.toml!")
    st.stop()
    
TABLE_NAME = "sales_linkr4" # Nama tabel

# --- Inisialisasi State dan Koneksi ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = ''

@st.cache_resource
def init_connection():
    """Menginisialisasi koneksi ke Supabase."""
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase: Client = init_connection()

# =========================================================================
# === BAGIAN 1: FUNGSI CRUD Supabase (Tidak Berubah) ===
# =========================================================================

# (Fungsi fetch_data_by_email, insert_data, update_data, delete_data, dan process_updates
#  dari jawaban sebelumnya berada di sini. Saya menghapusnya untuk keringkasan,
#  tapi Anda harus menyertakannya di kode akhir Anda.)

def fetch_data_by_email(email_address: str):
    """Mengambil data dari Supabase berdasarkan alamat email."""
    try:
        response = supabase.from_(TABLE_NAME).select("*").eq("Email Address", email_address).order("id", desc=True).execute()
        if response.data:
            df = pd.DataFrame(response.data)
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].astype(str).fillna('')
            return df
        return pd.DataFrame() 
    except Exception as e:
        st.error(f"Gagal mengambil data dari Supabase: {e}")
        return pd.DataFrame()

def insert_data(new_data: dict):
    """Menambahkan data baru ke tabel Supabase."""
    try:
        response = supabase.table(TABLE_NAME).insert(new_data).execute()
        if response.data:
            st.success("Data baru berhasil ditambahkan! 🎉")
            return True
        else:
            st.error("Gagal menambahkan data.")
            return False
    except Exception as e:
        st.error(f"Gagal menambahkan data: {e}")
        return False

def update_data(row_id: int, updates: dict):
    """Memperbarui baris tertentu dalam tabel berdasarkan ID-nya."""
    try:
        response = supabase.table(TABLE_NAME).update(updates).eq("id", row_id).execute()
        
        if response.data:
            st.success(f"Data ID **{row_id}** berhasil diperbarui!")
            return True
        else:
            st.warning("Data tidak ditemukan untuk diperbarui.")
            return False
    except Exception as e:
        st.error(f"Gagal memperbarui data: {e}")
        return False

def delete_data(row_id: int):
    """Menghapus baris tertentu dalam tabel berdasarkan ID-nya."""
    try:
        response = supabase.table(TABLE_NAME).delete().eq("id", row_id).execute()
        if response.data:
            st.success(f"Data ID **{row_id}** berhasil dihapus! 🗑️")
            return True
        else:
            st.warning("Data tidak ditemukan untuk dihapus.")
            return False
    except Exception as e:
        st.error(f"Gagal menghapus data: {e}")
        return False
        
def process_updates(edited_df: pd.DataFrame, original_df: pd.DataFrame):
    """Logika untuk membandingkan dan menyimpan perubahan (Edit)."""
    
    changes_detected = False
    update_success = True
    
    for index, edited_row in edited_df.iterrows():
        if index in original_df.index:
            original_row = original_df.loc[index]
            updates = {}
            
            for col in edited_row.index:
                original_value = str(original_row[col])
                edited_value = str(edited_row[col])

                if original_value != edited_value:
                    updates[col] = edited_row[col]
                    
            if updates:
                changes_detected = True
                row_id = original_row['id']
                
                updates.pop('id', None)
                updates.pop('Email Address', None)
                
                st.info(f"Memproses update ID **{row_id}**...")
                if not update_data(row_id, updates):
                    update_success = False
                    break 

    if changes_detected and update_success:
        st.success("Semua perubahan berhasil disimpan! Muat ulang data untuk konfirmasi.")
        del st.session_state['data_df']
        st.rerun()
    elif not changes_detected:
        st.info("Tidak ada perubahan yang terdeteksi.")

# =========================================================================
# === BAGIAN 2: TAMPILAN (VIEW) APLIKASI ===
# =========================================================================

def display_login():
    """Tampilan halaman login yang stylish."""
    
    # Header Utama
    st.markdown(
        "<h1 style='text-align: center; color: #4CAF50;'>📈 Sales Link Region 4</h1>", 
        unsafe_allow_html=True
    )
    st.markdown(
        "<h3 style='text-align: center; color: #666;'>Akses Data Sales & CRM Anda</h3>",
        unsafe_allow_html=True
    )
    
    # Menggunakan kolom untuk memposisikan form di tengah
    col_empty, col_form, col_empty2 = st.columns([1, 2, 1])
    
    with col_form:
        st.markdown("---")
        st.subheader("🔑 Otentikasi Pengguna")
        st.info("⚠️ Gunakan kredensial Gmail Anda untuk mengakses data regional. (Saat ini simulasi)")
        
        with st.form("login_form"):
            email_attempt = st.text_input("Email (Gmail):", key="login_email")
            password_attempt = st.text_input("Kata Sandi (Simulasi: 1234):", type="password")
            submitted = st.form_submit_button("Masuk ke Dashboard 🚀", use_container_width=True)
            
            if submitted:
                # --- Logika Mock Auth (Ganti dengan Supabase Auth yang sebenarnya) ---
                if "@gmail.com" in email_attempt and password_attempt == "1234":
                    st.session_state['logged_in'] = True
                    st.session_state['user_email'] = email_attempt
                    st.success(f"Selamat datang kembali, {email_attempt.split('@')[0].title()}!")
                    st.balloons() # Efek keren
                    st.rerun() 
                else:
                    st.error("Email atau Kata Sandi salah. Mohon coba lagi.")

def display_main_app():
    """Tampilan utama aplikasi setelah login dengan tata letak keren."""
    
    # --- Sidebar ---
    st.sidebar.markdown("## 👤 Informasi Sesi")
    st.sidebar.markdown(f"**Email:** `{st.session_state['user_email']}`")
    st.sidebar.markdown("---")
    
    if st.sidebar.button("🚪 Logout", use_container_width=True, help="Keluar dari sesi"):
        st.session_state['logged_in'] = False
        st.session_state['user_email'] = ''
        st.info("Anda telah logout.")
        st.rerun()
        
    # --- Header Utama ---
    st.markdown(
        "<h1 style='color: #4CAF50;'>🚀 Dashboard Sales Link Region 4</h1>", 
        unsafe_allow_html=True
    )
    st.markdown(f"Selamat Datang, **{st.session_state['user_email'].split('@')[0].title()}**! Kelola data sales Anda di sini.")
    st.markdown("---")

    # Pemuatan Data di Awal
    if 'data_df' not in st.session_state or st.session_state['data_df'].empty:
        with st.spinner(f"Memuat data untuk {st.session_state['user_email']}..."):
            df = fetch_data_by_email(st.session_state['user_email'])
            st.session_state['data_df'] = df

    # --- Tampilan Utama Menggunakan Tabs ---
    tab1, tab2, tab3 = st.tabs(["📊 Data Saya", "➕ Tambah Data Baru", "⚙️ Alat"])

    with tab1:
        st.subheader("Lihat dan Edit Data Sales Anda")
        
        # Kolom untuk Muat Ulang dan Informasi Baris
        col_refresh, col_info = st.columns([1, 3])
        with col_refresh:
            if st.button("🔄 Muat Ulang Data dari Supabase", use_container_width=True):
                del st.session_state['data_df']
                st.rerun()
        
        if st.session_state['data_df'].empty:
            col_info.info("Tidak ada data ditemukan. Silakan pindah ke tab 'Tambah Data Baru' untuk memulai.")
        else:
            col_info.metric(
                label="Total Baris Data", 
                value=len(st.session_state['data_df'])
            )

            # Tampilkan DataFrame yang dapat diedit (st.data_editor)
            edited_df = st.data_editor(
                st.session_state['data_df'],
                key="editor",
                use_container_width=True,
                height=400,
                column_config={
                    "Email Address": st.column_config.Column("Email (Read-Only)", disabled=True),
                    "id": st.column_config.NumberColumn("ID", disabled=True)
                },
                num_rows="fixed",
            )
            
            st.markdown("---")
            col_save, col_delete_tool = st.columns([2, 1])

            # Tombol Simpan Perubahan (Edit)
            with col_save:
                if st.button("💾 SIMPAN SEMUA PERUBAHAN DI ATAS", use_container_width=True, type="primary"):
                    process_updates(edited_df, st.session_state['data_df'])

            # Bagian Hapus Data (Pindah ke Tab 3 untuk kerapian)
            with col_delete_tool:
                st.caption("Lihat tab **'Alat'** untuk fitur Hapus Data.")


    with tab2:
        st.subheader("Formulir Input Data Sales Baru")
        
        # --- Form Tambah Data (Create) ---
        with st.form("add_data_form", clear_on_submit=True):
            st.markdown("Isi detail penjualan baru Anda:")
            
            # Sesuaikan dengan skema tabel Anda
            col1, col2, col3 = st.columns(3)
            with col1:
                col_A = st.text_input("Nama Klien/Perusahaan:", max_chars=100)
                col_B = st.number_input("Nilai Transaksi (Rp):", min_value=0)
            with col2:
                col_C = st.selectbox("Status Deal:", ["Lead", "Prospek", "Closed Won", "Closed Lost"])
                col_D = st.date_input("Tanggal Transaksi:")
            with col3:
                col_E = st.text_area("Catatan/Keterangan Tambahan:", height=100)
            
            # Data yang akan diinput
            new_record = {
                "Email Address": st.session_state['user_email'],
                "Nama Klien": col_A, # Sesuaikan
                "Nilai Transaksi": col_B, # Sesuaikan
                "Status Deal": col_C, # Sesuaikan
                "Tanggal Transaksi": col_D.strftime('%Y-%m-%d'), # Format tanggal
                "Catatan": col_E, # Sesuaikan
            }
            
            submitted = st.form_submit_button("➕ SUBMIT DATA BARU", use_container_width=True, type="primary")
            
            if submitted and col_A and col_B > 0:
                if insert_data(new_record):
                    del st.session_state['data_df']
                    # Pindah ke tab data setelah berhasil
                    st.success("Data berhasil ditambahkan! Silakan cek di tab 'Data Saya'.")
            elif submitted:
                 st.error("Mohon isi Nama Klien dan Nilai Transaksi.")
                 
    with tab3:
        st.subheader("Hapus Data Berdasarkan ID")
        st.warning("⚠️ **PERINGATAN:** Tindakan ini tidak dapat dibatalkan. Pastikan ID yang Anda masukkan sudah benar.")
        
        # Menampilkan ID yang tersedia
        if not st.session_state['data_df'].empty:
            id_list = st.session_state['data_df']['id'].tolist()
            id_to_delete = st.selectbox(
                "Pilih ID Baris yang Ingin Dihapus Secara Permanen:", 
                options=[None] + id_list, 
                key="delete_select",
                format_func=lambda x: f"Pilih ID..." if x is None else f"ID: {x}"
            )
            
            if id_to_delete is not None:
                if st.button(f"🗑️ HAPUS PERMANEN DATA ID {id_to_delete}", use_container_width=True, type="danger"):
                    if delete_data(id_to_delete):
                        del st.session_state['data_df']
                        st.rerun()
        else:
             st.info("Tidak ada data yang dapat dihapus.")


# =========================================================================
# === BAGIAN UTAMA: KONTROL ALIR APLIKASI ===
# =========================================================================

if st.session_state['logged_in']:
    display_main_app()
else:
    display_login()

