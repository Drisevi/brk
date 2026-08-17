import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="BRK Inventory Management", layout="wide")

st.title("📦 BRK Inventory Management (Cloud System)")
st.markdown("Sistem pencatatan mutasi fisik (*barcode*), HPP, dan pantauan sisa stok. **Terhubung dengan Google Sheets!**")

# --- 1. KONEKSI KE GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# Fungsi untuk membaca data agar tidak error jika sheet kosong
def get_data(worksheet, columns):
    df = conn.read(worksheet=worksheet, ttl=600).dropna(how="all")
    if df.empty or len(df.columns) == 0:
        return pd.DataFrame(columns=columns)
    return df

# Membaca data secara Real-Time dari Google Sheets
df_kain = get_data("Stok_Kain", ['Tanggal', 'Barcode_Kain', 'Nama_Kain', 'Jumlah_Potong', 'Harga_Beli_Rp', 'Supplier'])
df_wip = get_data("WIP_Penjahit", ['Tanggal', 'Barcode_Kain', 'Nama_Rencana_Baju', 'Penjahit', 'Jumlah_Potong_Keluar'])
df_baju = get_data("Baju_Jadi", ['Tanggal', 'Barcode_Baju', 'Nama_Baju', 'Jumlah_Baju', 'Modal_Kain', 'Ongkos_Jahit', 'Total_HPP'])
# Kolom penjualan ditambahkan HPP_Terjual dan Laba_Kotor
df_jual = get_data("Penjualan", ['Tanggal', 'Barcode_Baju', 'Jumlah_Terjual', 'Harga_Jual_Total', 'Total_HPP_Terjual', 'Laba_Kotor'])

# Inisialisasi PIN Admin Default di Session (hanya untuk sesi ini)
if 'admin_pin' not in st.session_state:
    st.session_state.admin_pin = "INTEGRA123"

# --- 2. MENU NAVIGASI ---
menu = st.sidebar.selectbox("Pilih Menu Operasional", [
    "1. Stok Masuk (Kain)", 
    "2. Kirim ke Penjahit (WIP)", 
    "3. Terima Baju Jadi (Input HPP)",
    "4. Kasir (Penjualan / Keluar)",
    "5. Laporan & Sisa Stok",
    "6. Admin (Hapus Data & Sandi)"
])

# --- MENU 1: STOK MASUK KAIN ---
if menu == "1. Stok Masuk (Kain)":
    st.header("📥 Input Bahan Baku (Kain Masuk)")
    with st.form("form_kain"):
        col1, col2 = st.columns(2)
        with col1:
            tanggal = st.date_input("Tanggal Masuk", datetime.now())
            barcode = st.text_input("Scan Barcode Kain")
            nama_kain = st.text_input("Nama / Jenis Kain")
        with col2:
            jumlah_potong = st.number_input("Jumlah (Potong/Pcs)", min_value=1, step=1)
            harga_beli = st.number_input("Harga Beli Total (Rp)", min_value=0.0, step=1000.0)
            supplier = st.text_input("Nama Supplier")
        
        submitted = st.form_submit_button("Simpan Stok Kain")
        if submitted and barcode:
            data_baru = pd.DataFrame([[tanggal, barcode, nama_kain, jumlah_potong, harga_beli, supplier]], 
                                     columns=['Tanggal', 'Barcode_Kain', 'Nama_Kain', 'Jumlah_Potong', 'Harga_Beli_Rp', 'Supplier'])
            df_kain_updated = pd.concat([df_kain, data_baru], ignore_index=True)
            
            # SIMPAN KE GOOGLE SHEETS
            conn.update(worksheet="Stok_Kain", data=df_kain_updated)
            st.success("Data tersimpan permanen di Google Sheets!")
            st.rerun()

# --- MENU 2: KIRIM KE PENJAHIT ---
elif menu == "2. Kirim ke Penjahit (WIP)":
    st.header("📤 Kirim Bahan Baku ke Penjahit (Proses WIP)")
    with st.form("form_wip"):
        col1, col2 = st.columns(2)
        with col1:
            tanggal = st.date_input("Tanggal Kirim", datetime.now())
            barcode = st.text_input("Scan Barcode Kain yang Dikirim")
            nama_barang = st.text_input("Deskripsi Rencana Baju")
        with col2:
            penjahit = st.text_input("Nama Vendor Penjahit")
            jumlah_keluar = st.number_input("Jumlah Kain Diberikan (Potong/Pcs)", min_value=1, step=1)
            
        submitted = st.form_submit_button("Kirim ke Penjahit")
        if submitted and barcode:
            data_wip = pd.DataFrame([[tanggal, barcode, nama_barang, penjahit, jumlah_keluar]], 
                                    columns=['Tanggal', 'Barcode_Kain', 'Nama_Rencana_Baju', 'Penjahit', 'Jumlah_Potong_Keluar'])
            df_wip_updated = pd.concat([df_wip, data_wip], ignore_index=True)
            
            conn.update(worksheet="WIP_Penjahit", data=df_wip_updated)
            st.success("Proses ke penjahit terekam di Google Sheets!")
            st.rerun()

# --- MENU 3: TERIMA BAJU JADI & KUNCI HPP ---
elif menu == "3. Terima Baju Jadi (Input HPP)":
    st.header("✨ Terima Baju Jadi & Kunci HPP")
    with st.form("form_baju"):
        col1, col2 = st.columns(2)
        with col1:
            tanggal = st.date_input("Tanggal Diterima", datetime.now())
            barcode_baju = st.text_input("Scan Barcode Baju Jadi")
            nama_baju = st.text_input("Nama Produk Baju Jadi")
            jumlah_baju = st.number_input("Jumlah Baju (Pcs)", min_value=1, step=1)
        with col2:
            modal_kain = st.number_input("Nilai Modal Kain Terpakai (Rp)", min_value=0.0, step=500.0)
            ongkos_jahit = st.number_input("Biaya Ongkos Jahit (Rp)", min_value=0.0, step=500.0)
            
        total_hpp = modal_kain + ongkos_jahit
        # Teks direvisi agar lebih jelas bahwa ini adalah HPP Gabungan/Satu Batch
        st.markdown(f"### **Total HPP Produksi (Keseluruhan): Rp {total_hpp:,.2f}**")
        
        submitted = st.form_submit_button("Simpan ke Gudang Baju Jadi")
        if submitted and barcode_baju:
            data_baju = pd.DataFrame([[tanggal, barcode_baju, nama_baju, jumlah_baju, modal_kain, ongkos_jahit, total_hpp]], 
                                     columns=['Tanggal', 'Barcode_Baju', 'Nama_Baju', 'Jumlah_Baju', 'Modal_Kain', 'Ongkos_Jahit', 'Total_HPP'])
            df_baju_updated = pd.concat([df_baju, data_baju], ignore_index=True)
            
            conn.update(worksheet="Baju_Jadi", data=df_baju_updated)
            st.success("Stok Baju Jadi & HPP tersimpan di Google Sheets!")
            st.rerun()

# --- MENU 4: KASIR / PENJUALAN ---
elif menu == "4. Kasir (Penjualan / Keluar)":
    st.header("🛒 Kasir / Penjualan Barang")
    with st.form("form_jual"):
        col1, col2 = st.columns(2)
        with col1:
            tanggal = st.date_input("Tanggal Transaksi", datetime.now())
            barcode_baju = st.text_input("Scan Barcode Baju Terjual")
        with col2:
            jumlah_terjual = st.number_input("Jumlah Terjual (Pcs)", min_value=1, step=1)
            harga_jual = st.number_input("Total Harga Jual (Rp)", min_value=0.0, step=1000.0)
            
        submitted = st.form_submit_button("Proses Penjualan")
        if submitted and barcode_baju:
            # 1. Cari HPP Satuan dari Barcode Baju tersebut di data df_baju
            hpp_satuan = 0.0
            if not df_baju.empty and barcode_baju in df_baju['Barcode_Baju'].values:
                # Ambil data baju terkait berdasarkan barcode (ambil baris pertama yang cocok)
                data_baju_terkait = df_baju[df_baju['Barcode_Baju'] == barcode_baju].iloc[0]
                
                # HPP Satuan = Total HPP / Jumlah Baju saat diproduksi
                # Ditambahkan pengecekan agar tidak error dibagi nol
                if float(data_baju_terkait['Jumlah_Baju']) > 0:
                    hpp_satuan = float(data_baju_terkait['Total_HPP']) / float(data_baju_terkait['Jumlah_Baju'])
            
            # 2. Hitung Total HPP Terjual & Laba Kotor
            total_hpp_terjual = hpp_satuan * jumlah_terjual
            laba_kotor = harga_jual - total_hpp_terjual

            # 3. Simpan ke DataFrame dan Google Sheets
            data_jual = pd.DataFrame([[tanggal, barcode_baju, jumlah_terjual, harga_jual, total_hpp_terjual, laba_kotor]], 
                                     columns=['Tanggal', 'Barcode_Baju', 'Jumlah_Terjual', 'Harga_Jual_Total', 'Total_HPP_Terjual', 'Laba_Kotor'])
            df_jual_updated = pd.concat([df_jual, data_jual], ignore_index=True)
            
            conn.update(worksheet="Penjualan", data=df_jual_updated)
            st.success(f"Penjualan terekam permanen! Laba Kotor dari transaksi ini: Rp {laba_kotor:,.2f}")
            st.rerun()

# --- MENU 5: LAPORAN & SISA STOK ---
elif menu == "5. Laporan & Sisa Stok":
    st.header("📊 Dashboard Laporan & Sisa Stok")
    
    # Kalkulasi sisa kain
    kain_masuk = df_kain.groupby(['Barcode_Kain', 'Nama_Kain'])['Jumlah_Potong'].sum().reset_index() if not df_kain.empty else pd.DataFrame(columns=['Barcode_Kain', 'Nama_Kain', 'Jumlah_Potong'])
    kain_keluar = df_wip.groupby('Barcode_Kain')['Jumlah_Potong_Keluar'].sum().reset_index() if not df_wip.empty else pd.DataFrame(columns=['Barcode_Kain', 'Jumlah_Potong_Keluar'])
    sisa_kain = pd.merge(kain_masuk, kain_keluar, on='Barcode_Kain', how='left').fillna(0)
    if not sisa_kain.empty:
        sisa_kain['Sisa_Gudang (Potong)'] = sisa_kain['Jumlah_Potong'] - sisa_kain['Jumlah_Potong_Keluar']
    
    # Kalkulasi sisa baju jadi
    baju_masuk = df_baju.groupby(['Barcode_Baju', 'Nama_Baju'])['Jumlah_Baju'].sum().reset_index() if not df_baju.empty else pd.DataFrame(columns=['Barcode_Baju', 'Nama_Baju', 'Jumlah_Baju'])
    baju_keluar = df_jual.groupby('Barcode_Baju')['Jumlah_Terjual'].sum().reset_index() if not df_jual.empty else pd.DataFrame(columns=['Barcode_Baju', 'Jumlah_Terjual'])
    sisa_baju = pd.merge(baju_masuk, baju_keluar, on='Barcode_Baju', how='left').fillna(0)
    if not sisa_baju.empty:
        sisa_baju['Sisa_Gudang (Pcs)'] = sisa_baju['Jumlah_Baju'] - sisa_baju['Jumlah_Terjual']

    # Membuat 4 Tab Laporan
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Laporan Keuntungan", "📦 Sisa Stok Saat Ini", "📝 Rekap Bahan & WIP", "💰 Rekap Baju & Penjualan"])
    
    with tab1:
        st.subheader("Ringkasan Keuntungan (Laba Kotor)")
        
        # Kalkulasi Keuntungan dari data penjualan
        total_omzet = df_jual['Harga_Jual_Total'].astype(float).sum() if not df_jual.empty else 0.0
        total_hpp_terjual = df_jual['Total_HPP_Terjual'].astype(float).sum() if not df_jual.empty else 0.0
        total_laba_kotor = df_jual['Laba_Kotor'].astype(float).sum() if not df_jual.empty else 0.0
        
        # Menampilkan metrik besar (Dashboard)
        col1, col2, col3 = st.columns(3)
        col1.metric("💰 Total Omzet Penjualan", f"Rp {total_omzet:,.0f}")
        col2.metric("📉 Total Modal (HPP Keluar)", f"Rp {total_hpp_terjual:,.0f}")
        col3.metric("📈 TOTAL LABA KOTOR", f"Rp {total_laba_kotor:,.0f}")
        
        st.info("💡 **Catatan untuk Finance/Akuntansi:** Angka Laba Kotor di atas adalah hasil pengurangan Omzet dengan HPP. Angka ini belum dikurangi dengan Biaya Operasional (gaji, listrik, sewa, dll) untuk menjadi Laba Bersih.")

    with tab2:
        st.subheader("Sisa Bahan Baku (Kain)")
        st.dataframe(sisa_kain[['Barcode_Kain', 'Nama_Kain', 'Sisa_Gudang (Potong)']] if not sisa_kain.empty else sisa_kain, width='stretch')
        st.subheader("Sisa Barang Jadi (Siap Jual)")
        st.dataframe(sisa_baju[['Barcode_Baju', 'Nama_Baju', 'Sisa_Gudang (Pcs)']] if not sisa_baju.empty else sisa_baju, width='stretch')

    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode('utf-8')

    with tab3:
        st.dataframe(df_kain, width='stretch')
        if not df_kain.empty:
            st.download_button("📥 Download Log Kain", data=convert_df_to_csv(df_kain), file_name='log_kain.csv', mime='text/csv')
        st.write("---")
        st.dataframe(df_wip, width='stretch')
        if not df_wip.empty:
            st.download_button("📥 Download Log WIP", data=convert_df_to_csv(df_wip), file_name='log_wip.csv', mime='text/csv')

    with tab4:
        st.dataframe(df_baju, width='stretch')
        if not df_baju.empty:
            st.download_button("📥 Download Log Baju Jadi", data=convert_df_to_csv(df_baju), file_name='log_baju.csv', mime='text/csv')
        st.write("---")
        st.dataframe(df_jual, width='stretch')
        if not df_jual.empty:
            st.download_button("📥 Download Log Penjualan", data=convert_df_to_csv(df_jual), file_name='log_penjualan.csv', mime='text/csv')

# --- MENU 6: ADMIN (HAPUS DATA & SANDI) ---
elif menu == "6. Admin (Hapus Data & Sandi)":
    st.header("🛠️ Panel Admin Integra")
    
    pin_input = st.text_input("Masukkan PIN Khusus Admin:", type="password")
    
    if pin_input == st.session_state.admin_pin:
        st.success("Akses Diberikan.")
        
        tab_hapus, tab_sandi = st.tabs(["🗑️ Hapus Baris Data", "🔐 Ubah Sandi"])
        
        with tab_hapus:
            tabel_pilihan = st.selectbox("Pilih Tabel Google Sheets:", [
                "1. Stok Masuk Kain", "2. Kirim ke Penjahit (WIP)", 
                "3. Baju Jadi & HPP", "4. Penjualan Kasir"
            ])
            
            if tabel_pilihan == "1. Stok Masuk Kain": df_target, ws_name = df_kain, "Stok_Kain"
            elif tabel_pilihan == "2. Kirim ke Penjahit (WIP)": df_target, ws_name = df_wip, "WIP_Penjahit"
            elif tabel_pilihan == "3. Baju Jadi & HPP": df_target, ws_name = df_baju, "Baju_Jadi"
            else: df_target, ws_name = df_jual, "Penjualan"
                
            st.dataframe(df_target, width='stretch')
            
            if not df_target.empty:
                index_hapus = st.number_input("Masukkan Nomor Indeks Baris yang akan dihapus:", 
                                              min_value=0, max_value=len(df_target)-1, step=1)
                
                if st.button("🗑️ Hapus dari Google Sheets"):
                    df_updated = df_target.drop(index_hapus).reset_index(drop=True)
                    # Kosongkan sheet dulu, lalu tulis ulang agar baris terhapus sempurna
                    conn.clear(worksheet=ws_name)
                    conn.update(worksheet=ws_name, data=df_updated)
                    st.success("Data berhasil dihapus dari Google Sheets!")
                    st.rerun() 
                    
        with tab_sandi:
            pin_baru = st.text_input("Masukkan PIN Baru:", type="password")
            konfirmasi_pin = st.text_input("Konfirmasi PIN Baru:", type="password")
            if st.button("Simpan Sandi Baru"):
                if pin_baru != "" and pin_baru == konfirmasi_pin:
                    st.session_state.admin_pin = pin_baru
                    st.success("Sandi berhasil diperbarui!")
                elif pin_baru != konfirmasi_pin:
                    st.error("Konfirmasi sandi tidak cocok!")
