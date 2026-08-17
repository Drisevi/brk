import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="BRK Inventory Management", layout="wide")

st.title("📦 BRK Inventory Management (Cloud System)")
st.markdown("Sistem alternatif sederhana untuk mencatat mutasi fisik (*barcode*), pengelolaan WIP penjahit, penguncian HPP riil, dan pantauan sisa stok.")

# --- 1. INISIALISASI DATABASE SEDERHANA ---
if 'stok_kain' not in st.session_state:
    st.session_state.stok_kain = pd.DataFrame(columns=['Tanggal', 'Barcode_Kain', 'Nama_Kain', 'Jumlah_Potong', 'Harga_Beli_Rp', 'Supplier'])
if 'wip_penjahit' not in st.session_state:
    st.session_state.wip_penjahit = pd.DataFrame(columns=['Tanggal', 'Barcode_Kain', 'Nama_Rencana_Baju', 'Penjahit', 'Jumlah_Potong_Keluar'])
if 'baju_jadi' not in st.session_state:
    st.session_state.baju_jadi = pd.DataFrame(columns=['Tanggal', 'Barcode_Baju', 'Nama_Baju', 'Jumlah_Baju', 'Modal_Kain', 'Ongkos_Jahit', 'Total_HPP'])
if 'penjualan' not in st.session_state:
    st.session_state.penjualan = pd.DataFrame(columns=['Tanggal', 'Barcode_Baju', 'Jumlah_Terjual', 'Harga_Jual_Total'])

# --- 2. MENU NAVIGASI ---
menu = st.sidebar.selectbox("Pilih Menu Operasional", [
    "1. Stok Masuk (Kain)", 
    "2. Kirim ke Penjahit (WIP)", 
    "3. Terima Baju Jadi (Input HPP)",
    "4. Kasir (Penjualan / Keluar)",
    "5. Laporan & Sisa Stok",
    "6. Admin (Hapus Data)"
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
            st.session_state.stok_kain = pd.concat([st.session_state.stok_kain, data_baru], ignore_index=True)
            st.success("Stok kain berhasil dicatat!")

# --- MENU 2: KIRIM KE PENJAHIT ---
elif menu == "2. Kirim ke Penjahit (WIP)":
    st.header("📤 Kirim Bahan Baku ke Penjahit (Proses WIP)")
    st.info("Pencatatan ini akan otomatis mengurangi Sisa Stok Kain di gudang.")
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
            st.session_state.wip_penjahit = pd.concat([st.session_state.wip_penjahit, data_wip], ignore_index=True)
            st.success("Kain berhasil diproses ke penjahit!")

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
        st.markdown(f"### **Total HPP Final: Rp {total_hpp:,.2f}**")
        
        submitted = st.form_submit_button("Simpan ke Gudang Baju Jadi")
        if submitted and barcode_baju:
            data_baju = pd.DataFrame([[tanggal, barcode_baju, nama_baju, jumlah_baju, modal_kain, ongkos_jahit, total_hpp]], 
                                     columns=['Tanggal', 'Barcode_Baju', 'Nama_Baju', 'Jumlah_Baju', 'Modal_Kain', 'Ongkos_Jahit', 'Total_HPP'])
            st.session_state.baju_jadi = pd.concat([st.session_state.baju_jadi, data_baju], ignore_index=True)
            st.success("Stok Baju Jadi bertambah & HPP terkunci!")

# --- MENU 4: KASIR / PENJUALAN ---
elif menu == "4. Kasir (Penjualan / Keluar)":
    st.header("🛒 Kasir / Penjualan Barang")
    st.info("Input di sini akan memotong stok Baju Jadi secara real-time.")
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
            data_jual = pd.DataFrame([[tanggal, barcode_baju, jumlah_terjual, harga_jual]], 
                                     columns=['Tanggal', 'Barcode_Baju', 'Jumlah_Terjual', 'Harga_Jual_Total'])
            st.session_state.penjualan = pd.concat([st.session_state.penjualan, data_jual], ignore_index=True)
            st.success("Transaksi berhasil! Stok baju jadi telah dikurangi.")

# --- MENU 5: LAPORAN & SISA STOK ---
elif menu == "5. Laporan & Sisa Stok":
    st.header("📊 Dashboard Sisa Stok & Rekapitulasi")
    
    kain_masuk = st.session_state.stok_kain.groupby(['Barcode_Kain', 'Nama_Kain'])['Jumlah_Potong'].sum().reset_index()
    kain_keluar = st.session_state.wip_penjahit.groupby('Barcode_Kain')['Jumlah_Potong_Keluar'].sum().reset_index()
    sisa_kain = pd.merge(kain_masuk, kain_keluar, on='Barcode_Kain', how='left').fillna(0)
    sisa_kain['Sisa_Gudang (Potong)'] = sisa_kain['Jumlah_Potong'] - sisa_kain['Jumlah_Potong_Keluar']
    
    baju_masuk = st.session_state.baju_jadi.groupby(['Barcode_Baju', 'Nama_Baju'])['Jumlah_Baju'].sum().reset_index()
    baju_keluar = st.session_state.penjualan.groupby('Barcode_Baju')['Jumlah_Terjual'].sum().reset_index()
    sisa_baju = pd.merge(baju_masuk, baju_keluar, on='Barcode_Baju', how='left').fillna(0)
    sisa_baju['Sisa_Gudang (Pcs)'] = sisa_baju['Jumlah_Baju'] - sisa_baju['Jumlah_Terjual']

    tab1, tab2, tab3 = st.tabs(["📦 SISA STOK SAAT INI", "📝 Rekap Bahan & WIP", "💰 Rekap Baju Jadi & Penjualan"])
    
    with tab1:
        st.subheader("Sisa Bahan Baku (Kain)")
        st.dataframe(sisa_kain[['Barcode_Kain', 'Nama_Kain', 'Sisa_Gudang (Potong)']], width='stretch')
        st.subheader("Sisa Barang Jadi (Siap Jual)")
        st.dataframe(sisa_baju[['Barcode_Baju', 'Nama_Baju', 'Sisa_Gudang (Pcs)']], width='stretch')

    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode('utf-8')

    with tab2:
        st.dataframe(st.session_state.stok_kain, width='stretch')
        if not st.session_state.stok_kain.empty:
            st.download_button("📥 Download Log Kain", data=convert_df_to_csv(st.session_state.stok_kain), file_name='log_kain.csv', mime='text/csv')
        st.write("---")
        st.dataframe(st.session_state.wip_penjahit, width='stretch')
        if not st.session_state.wip_penjahit.empty:
            st.download_button("📥 Download Log WIP", data=convert_df_to_csv(st.session_state.wip_penjahit), file_name='log_wip.csv', mime='text/csv')

    with tab3:
        st.dataframe(st.session_state.baju_jadi, width='stretch')
        if not st.session_state.baju_jadi.empty:
            st.download_button("📥 Download Log Baju Jadi", data=convert_df_to_csv(st.session_state.baju_jadi), file_name='log_baju.csv', mime='text/csv')
        st.write("---")
        st.dataframe(st.session_state.penjualan, width='stretch')
        if not st.session_state.penjualan.empty:
            st.download_button("📥 Download Log Penjualan", data=convert_df_to_csv(st.session_state.penjualan), file_name='log_penjualan.csv', mime='text/csv')

# --- MENU 6: ADMIN (HAPUS DATA) ---
elif menu == "6. Admin (Hapus Data)":
    st.header("🛠️ Panel Admin Integra (Akses Terbatas)")
    st.warning("Menu ini digunakan untuk mengoreksi atau menghapus data yang salah input.")
    
    # Kunci Keamanan Sederhana
    pin_input = st.text_input("Masukkan PIN Khusus Admin:", type="password")
    
    if pin_input == "INTEGRA123":
        st.success("Akses Diberikan. Silakan pilih data yang ingin dihapus.")
        
        # Pilih tabel yang mau dikoreksi
        tabel_pilihan = st.selectbox("Pilih Tabel Basis Data:", [
            "1. Stok Masuk Kain", 
            "2. Kirim ke Penjahit (WIP)", 
            "3. Baju Jadi & HPP", 
            "4. Penjualan Kasir"
        ])
        
        # Mapping nama tabel ke dataframe di session_state
        if tabel_pilihan == "1. Stok Masuk Kain":
            df_target = 'stok_kain'
        elif tabel_pilihan == "2. Kirim ke Penjahit (WIP)":
            df_target = 'wip_penjahit'
        elif tabel_pilihan == "3. Baju Jadi & HPP":
            df_target = 'baju_jadi'
        else:
            df_target = 'penjualan'
            
        st.dataframe(st.session_state[df_target], width='stretch')
        
        if not st.session_state[df_target].empty:
            st.markdown("Cek **angka indeks paling kiri** (0, 1, 2, dst.) pada tabel di atas untuk baris yang ingin dihapus.")
            index_hapus = st.number_input("Masukkan Nomor Indeks Baris yang akan dihapus:", 
                                          min_value=0, max_value=len(st.session_state[df_target])-1, step=1)
            
            if st.button("🗑️ Hapus Baris Data Ini"):
                # Menghapus baris berdasarkan indeks dan mereset ulang penomoran indeks
                st.session_state[df_target] = st.session_state[df_target].drop(index_hapus).reset_index(drop=True)
                st.success("Data berhasil dihapus dari sistem!")
                st.rerun() # Memuat ulang halaman agar tabel langsung terupdate
    
    elif pin_input != "":
        st.error("PIN Salah! Anda tidak memiliki akses untuk mengubah data.")
