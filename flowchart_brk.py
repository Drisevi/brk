import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="BRK Inventory Management", layout="wide")

st.title("📦 BRK Inventory Management (Cloud System)")
st.markdown("Sistem alternatif sederhana untuk mencatat mutasi fisik (*barcode*), pengelolaan WIP penjahit, dan penguncian HPP riil.")

# Inisialisasi Database Sederhana di Session State (Simulasi Cloud Database)
if 'stok_kain' not in st.session_state:
    st.session_state.stok_kain = pd.DataFrame(columns=['Tanggal', 'Barcode', 'Nama_Kain', 'Jumlah_Potong', 'Harga_Beli_Rp', 'Supplier'])
if 'wip_penjahit' not in st.session_state:
    st.session_state.wip_penjahit = pd.DataFrame(columns=['Tanggal', 'Barcode', 'Nama_Barang', 'Penjahit', 'Jumlah_Potong_Keluar'])
if 'baju_jadi' not in st.session_state:
    st.session_state.baju_jadi = pd.DataFrame(columns=['Tanggal', 'Barcode_Baju', 'Nama_Baju', 'Modal_Kain', 'Ongkos_Jahit', 'Total_HPP'])

# Sidebar Menu Navigasi
menu = st.sidebar.selectbox("Pilih Menu Operasional", [
    "1. Stok Masuk (Kain)", 
    "2. Kirim ke Penjahit (WIP)", 
    "3. Terima Baju Jadi (Input HPP)", 
    "4. Laporan Stok & HPP"
])

# --- MENU 1: STOK MASUK KAIN ---
if menu == "1. Stok Masuk (Kain)":
    st.header("📥 Input Bahan Baku (Kain Masuk)")
    with st.form("form_kain"):
        col1, col2 = st.columns(2)
        with col1:
            tanggal = st.date_input("Tanggal Masuk", datetime.now())
            barcode = st.text_input("Scan / Masukkan Barcode Kain")
            nama_kain = st.text_input("Nama / Jenis Kain")
        with col2:
            jumlah_potong = st.number_input("Jumlah (Potong/Pcs)", min_value=1, step=1)
            harga_beli = st.number_input("Harga Beli Total (Rp)", min_value=0.0, step=1000.0)
            supplier = st.text_input("Nama Supplier")
        
        submitted = st.form_submit_button("Simpan Stok Kain")
        if submitted and barcode:
            data_baru = pd.DataFrame([[tanggal, barcode, nama_kain, jumlah_potong, harga_beli, supplier]], 
                                     columns=['Tanggal', 'Barcode', 'Nama_Kain', 'Jumlah_Potong', 'Harga_Beli_Rp', 'Supplier'])
            st.session_state.stok_kain = pd.concat([st.session_state.stok_kain, data_baru], ignore_index=True)
            st.success("Stok kain dan harga beli berhasil dicatat!")

    st.subheader("Daftar Kain di Gudang")
    st.dataframe(st.session_state.stok_kain, width='stretch')

# --- MENU 2: KIRIM KE PENJAHIT ---
elif menu == "2. Kirim ke Penjahit (WIP)":
    st.header("📤 Kirim Bahan Baku ke Penjahit (Proses WIP)")
    with st.form("form_wip"):
        col1, col2 = st.columns(2)
        with col1:
            tanggal = st.date_input("Tanggal Kirim", datetime.now())
            barcode = st.text_input("Barcode Kain yang Dikirim")
            nama_barang = st.text_input("Deskripsi / Model Rencana Baju")
        with col2:
            penjahit = st.text_input("Nama Vendor Penjahit")
            jumlah_keluar = st.number_input("Jumlah Kain Diberikan (Potong/Pcs)", min_value=1, step=1)
            
        submitted = st.form_submit_button("Kirim ke Penjahit")
        if submitted and barcode:
            data_wip = pd.DataFrame([[tanggal, barcode, nama_barang, penjahit, jumlah_keluar]], 
                                    columns=['Tanggal', 'Barcode', 'Nama_Barang', 'Penjahit', 'Jumlah_Potong_Keluar'])
            st.session_state.wip_penjahit = pd.concat([st.session_state.wip_penjahit, data_wip], ignore_index=True)
            st.success("Mutasi ke penjahit berhasil dicatat (Tanpa HPP Prematur)!")

    st.subheader("Daftar Barang dalam Proses (WIP di Penjahit)")
    st.dataframe(st.session_state.wip_penjahit, width='stretch')

# --- MENU 3: TERIMA BAJU JADI & KUNCI HPP ---
elif menu == "3. Terima Baju Jadi (Input HPP)":
    st.header("✨ Terima Baju Jadi & Kunci Harga Modal (HPP)")
    st.info("HPP final dihitung dari akumulasi Modal Kain + Ongkos Jahit sebelum masuk ke stok toko.")
    
    with st.form("form_baju"):
        col1, col2 = st.columns(2)
        with col1:
            tanggal = st.date_input("Tanggal Diterima", datetime.now())
            barcode_baju = st.text_input("Scan Barcode Baju Jadi Baru")
            nama_baju = st.text_input("Nama Produk Baju Jadi")
        with col2:
            modal_kain = st.number_input("Nilai Modal Kain Terpakai (Rp)", min_value=0.0, step=500.0)
            ongkos_jahit = st.number_input("Biaya Ongkos Jahit (Rp)", min_value=0.0, step=500.0)
            
        total_hpp = modal_kain + ongkos_jahit
        st.markdown(f"### **Total Modal HPP Final: Rp {total_hpp:,.2f}**")
        
        submitted = st.form_submit_button("Simpan ke Stok Barang Jadi")
        if submitted and barcode_baju:
            data_baju = pd.DataFrame([[tanggal, barcode_baju, nama_baju, modal_kain, ongkos_jahit, total_hpp]], 
                                     columns=['Tanggal', 'Barcode_Baju', 'Nama_Baju', 'Modal_Kain', 'Ongkos_Jahit', 'Total_HPP'])
            st.session_state.baju_jadi = pd.concat([st.session_state.baju_jadi, data_baju], ignore_index=True)
            st.success("Baju jadi berhasil dimasukkan ke sistem dengan HPP terkunci!")

    st.subheader("Datalog Master Baju Jadi & HPP")
    st.dataframe(st.session_state.baju_jadi, width='stretch')

# --- MENU 4: LAPORAN STOK & HPP ---
elif menu == "4. Laporan Stok & HPP":
    st.header("📊 Laporan Pusat (Siap Rekap ke Jurnal.id)")
    st.markdown("Unduh data rekapitulasi operasional di bawah ini untuk dilaporkan atau disinkronkan.")
    
    # Fungsi bantu untuk convert DataFrame ke CSV (bisa dibuka langsung di Excel)
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode('utf-8')

    # 1. Bagian Bahan Baku
    st.subheader("1. Rekapitulasi Bahan Baku")
    st.dataframe(st.session_state.stok_kain, width='stretch')
    if not st.session_state.stok_kain.empty:
        csv_kain = convert_df_to_csv(st.session_state.stok_kain)
        st.download_button(
            label="📥 Download Rekap Kain (CSV/Excel)",
            data=csv_kain,
            file_name='rekap_stok_kain.csv',
            mime='text/csv',
        )
    
    st.markdown("---")
    
    # 2. Bagian WIP Penjahit
    st.subheader("2. Rekapitulasi Barang Dalam Proses (WIP)")
    st.dataframe(st.session_state.wip_penjahit, width='stretch')
    if not st.session_state.wip_penjahit.empty:
        csv_wip = convert_df_to_csv(st.session_state.wip_penjahit)
        st.download_button(
            label="📥 Download Rekap WIP Penjahit (CSV/Excel)",
            data=csv_wip,
            file_name='rekap_wip_penjahit.csv',
            mime='text/csv',
        )
    
    st.markdown("---")
    
    # 3. Bagian Baju Jadi & HPP
    st.subheader("3. Rekapitulasi Barang Jadi & Struktur HPP")
    st.dataframe(st.session_state.baju_jadi, width='stretch')
    if not st.session_state.baju_jadi.empty:
        csv_baju = convert_df_to_csv(st.session_state.baju_jadi)
        st.download_button(
            label="📥 Download Rekap Baju Jadi & HPP (CSV/Excel)",
            data=csv_baju,
            file_name='rekap_baju_jadi_hpp.csv',
            mime='text/csv',
        )
