import streamlit as st
import pandas as pd
import numpy as np

# Konfigurasi Halaman
st.set_page_config(page_title="Kalkulator Dampak ICP ke RAPBN", layout="wide")

st.title("🛢️ Kalkulator Dampak Harga Minyak thd RAPBN 2026")
st.markdown("Ubah parameter di bawah ini untuk melihat simulasi dampak pergerakan harga minyak dunia terhadap ketahanan fiskal kita secara *real-time*.")

# --- PROSES BERPIKIR & RUMUS ---
with st.expander("🧠 Proses Berpikir & Asal Rumus (Klik untuk membuka)", expanded=True):
    st.markdown("""
    **Alur Logika Hitungan:**
    1. **Menghitung Beban Negara:** Setiap ada kenaikan harga minyak mentah $1/barel, ada imbas biaya tambahan untuk memproduksi tiap liter BBM subsidi. Kita konversikan satuan kenaikan ini ke Rupiah per Kiloliter (KL) terlebih dahulu, lalu dikalikan dengan kuota volume masing-masing jenis BBM.
    2. **Menghitung Pendapatan (Windfall):** Di sisi lain, sebagai negara produsen, kita juga mendapat tambahan penerimaan dari hasil lifting minyak. Kita hitung nilai tambah brutonya selama setahun penuh (365 hari), lalu negara mengambil porsi penerimaan melalui PNBP SDA (31,2%) dan PPh Migas (21,5%).
    3. **Mencari Defisit Bersih:** Terakhir, kita bandingkan: apakah tambahan pendapatan sanggup menutup tambahan beban? Caranya dengan mengurangkan Beban dengan Pendapatan.

    **Rumus Matematis Dasarnya:**
    * **Biaya Tambahan per KL:** $\Delta \text{Biaya} = 6,2898 \times \text{Kurs}$
    * **Beban Subsidi:** $\text{Beban} = \text{Volume (KL)} \times \Delta \text{Biaya}$
    * **Pendapatan Bruto Setahun:** $\text{Bruto} = \text{Lifting} \times 365 \times \text{Kurs}$
    * **Defisit per \$1:** $\text{Total Beban} - (\text{PNBP SDA} + \text{PPh Migas})$
    """)

st.divider()

# --- INPUT PARAMETER DI BAGIAN UTAMA ---
st.header("⚙️ Parameter Asumsi (Silakan Ubah Angkanya)")
col_input1, col_input2 = st.columns(2)

with col_input1:
    st.subheader("Indikator Makroekonomi")
    kurs = st.number_input("Kurs Rupiah (Rp/USD)", value=16500, step=100)
    icp_asumsi = st.number_input("Harga Asumsi ICP (USD/barel)", value=70, step=1)
    icp_skenario = st.number_input("Harga Skenario Ekstrem ICP (USD/barel)", value=200, step=10)
    lifting = st.number_input("Lifting Minyak (barel/hari)", value=610000, step=10000)

with col_input2:
    st.subheader("Volume Kuota BBM (KL)")
    st.info("💡 Angka di bawah menggunakan satuan raw. Saat ditampilkan, hasilnya akan otomatis menggunakan titik ribuan.")
    vol_pertalite = st.number_input("Kuota Pertalite (KL)", value=29267947, step=500000)
    vol_solar = st.number_input("Kuota Solar Subsidi (KL)", value=18636500, step=500000)
    vol_mitan = st.number_input("Kuota Minyak Tanah (KL)", value=526000, step=10000)

# --- PERHITUNGAN MATEMATIKA ---
konversi_kl = 6.2898  
biaya_per_kl = konversi_kl * kurs

# Beban per USD 1 (dalam Triliun)
beban_pertalite = (vol_pertalite * biaya_per_kl) / 1e12
beban_solar = (vol_solar * biaya_per_kl) / 1e12
beban_mitan = (vol_mitan * biaya_per_kl) / 1e12
total_beban = beban_pertalite + beban_solar + beban_mitan

# Pendapatan per USD 1 (dalam Triliun)
nilai_tambah_bruto = (lifting * 365 * kurs) / 1e12
pnbp_sda = nilai_tambah_bruto * 0.312  
pph_migas = nilai_tambah_bruto * 0.215 
total_pendapatan = pnbp_sda + pph_migas

net_defisit_per_dolar = total_beban - total_pendapatan
delta_harga = icp_skenario - icp_asumsi
total_defisit_skenario = net_defisit_per_dolar * delta_harga

# Fungsi pembantu untuk format angka ala Indonesia (titik untuk ribuan)
def fmt_id(angka, desimal=2):
    return f"{angka:,.{desimal}f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- UI HASIL HITUNGAN ---
st.divider()
st.header(f"📊 Dampak Kenaikan Setiap USD 1 / barel")

col_hasil1, col_hasil2, col_hasil3 = st.columns(3)

with col_hasil1:
    st.error(f"**🔴 Tambahan Beban**\n# Rp {fmt_id(total_beban)} T")
    st.write(f"- Pertalite: Rp {fmt_id(beban_pertalite)} T")
    st.write(f"- Solar: Rp {fmt_id(beban_solar)} T")
    st.write(f"- Minyak Tanah: Rp {fmt_id(beban_mitan, 3)} T")

with col_hasil2:
    st.success(f"**🟢 Tambahan Pendapatan**\n# Rp {fmt_id(total_pendapatan)} T")
    st.write(f"- PNBP SDA: Rp {fmt_id(pnbp_sda)} T")
    st.write(f"- PPh Migas: Rp {fmt_id(pph_migas)} T")

with col_hasil3:
    st.warning(f"**⚠️ Pembengkakan Defisit**\n# Rp {fmt_id(net_defisit_per_dolar)} T")
    st.write(f"*Didapat dari Total Beban dikurangi Total Pendapatan.*")

# --- VISUALISASI GRAFIK ---
st.divider()
st.header("📈 Visualisasi Laju Defisit Anggaran")
st.markdown(f"Grafik ini menunjukkan akumulasi defisit jika harga merangkak naik dari asumsi dasar (**USD {icp_asumsi}**) menuju skenario ekstrem (**USD {icp_skenario}**).")

# Membuat deret data untuk grafik
rentang_harga = np.arange(icp_asumsi, icp_skenario + 1, max(1, (icp_skenario - icp_asumsi) // 20))
akumulasi_defisit = (rentang_harga - icp_asumsi) * net_defisit_per_dolar

df_chart = pd.DataFrame({
    "Harga ICP (USD/barel)": rentang_harga,
    "Defisit (Triliun Rp)": akumulasi_defisit
}).set_index("Harga ICP (USD/barel)")

# Menampilkan grafik area
st.area_chart(df_chart, color="#ff4b4b")

st.info(f"💡 **Kesimpulan Akhir:** Jika harga minyak mentah benar-benar menyentuh **USD {icp_skenario}/barel**, ketahanan fiskal RAPBN 2026 akan terbebani tambahan defisit hingga **Rp {fmt_id(total_defisit_skenario)} Triliun**.")
