import streamlit as st
import pandas as pd

# Konfigurasi Halaman
st.set_page_config(page_title="Kalkulator Dampak ICP ke RAPBN", layout="wide")

st.title("🛢️ Kalkulator Dampak Harga Minyak thd RAPBN 2026")
st.markdown("Ubah parameter di bawah ini untuk melihat simulasi dampak pergerakan harga minyak dunia terhadap ketahanan fiskal kita secara *real-time*.")

# --- 1. LOGIKA BERPIKIR (Di Atas, Terbuka Otomatis, Di-Highlight) ---
with st.expander("🧠 Logika Berpikir Kalkulator Ini", expanded=True):
    st.info("""
    **Bagaimana Alur Hitungannya?**
    1. **Menghitung Beban Negara:** Setiap ada kenaikan harga minyak mentah $1/barel, ada imbas biaya tambahan untuk memproduksi tiap liter BBM subsidi. Kita konversikan satuan kenaikan ini ke Rupiah per Kiloliter (KL) terlebih dahulu, lalu dikalikan dengan kuota volume masing-masing jenis BBM.
    2. **Menghitung Pendapatan (Windfall):** Di sisi lain, sebagai negara produsen, kita juga mendapat tambahan penerimaan dari hasil lifting minyak. Kita hitung nilai tambah brutonya selama setahun penuh (365 hari), lalu negara mengambil porsi penerimaan melalui PNBP SDA (31,2%) dan PPh Migas (21,5%).
    3. **Mencari Defisit Bersih:** Terakhir, kita bandingkan: apakah tambahan pendapatan sanggup menutup tambahan beban? Caranya dengan mengurangkan total Beban dengan total Pendapatan.
    """)

st.divider()

# --- 2. INPUT PARAMETER ---
st.header("⚙️ Parameter Asumsi")
st.caption("📌 **Catatan:** Data asumsi dasar ekonomi makro dan volume kuota BBM subsidi di bawah ini secara default merujuk pada postur **RAPBN 2026**.")

col_input1, col_input2 = st.columns(2)

with col_input1:
    st.subheader("Indikator Makroekonomi")
    kurs = st.number_input("Kurs Rupiah (Rp/USD)", value=16500, step=100)
    icp_asumsi = st.number_input("Harga Asumsi ICP (USD/barel)", value=70, step=1)
    icp_skenario = st.number_input("Harga Skenario Ekstrem ICP (USD/barel)", value=200, step=10)
    lifting = st.number_input("Lifting Minyak (barel/hari)", value=610000, step=10000)

with col_input2:
    st.subheader("Volume Kuota BBM (KL)")
    vol_pertalite = st.number_input("Kuota Pertalite (KL)", value=29267947, step=500000)
    vol_solar = st.number_input("Kuota Solar Subsidi (KL)", value=18636500, step=500000)
    vol_mitan = st.number_input("Kuota Minyak Tanah (KL)", value=526000, step=10000)

# --- PERHITUNGAN MATEMATIKA BEKEND ---
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

def fmt_id(angka, desimal=2):
    return f"{angka:,.{desimal}f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- 3. UI HASIL HITUNGAN ---
st.divider()
st.header("📊 Hasil Simulasi per Kenaikan USD 1 / barel")

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
    st.warning(f"**⚠️ Net Defisit Pembengkakan**\n# Rp {fmt_id(net_defisit_per_dolar)} T")
    st.write(f"*Total Beban dikurangi Total Pendapatan.*")

# --- 4. RUMUS MATEMATIS (Di Bawah Angka, Terbuka Otomatis, Di-Highlight) ---
with st.expander("📐 Rumus Matematis yang Digunakan", expanded=True):
    st.warning("""
    **Detail Rumus:**
    * **Biaya Tambahan per KL** = 6,2898 × Kurs Rupiah
    * **Beban Subsidi** = Volume BBM (KL) × Biaya Tambahan per KL
    * **Pendapatan Bruto Setahun** = Lifting Harian × 365 Hari × Kurs Rupiah
    * **Pendapatan Bersih Negara** = PNBP SDA (31,2% dari Bruto) + PPh Migas (21,5% dari Bruto)
    * **Defisit per Kenaikan $1** = Total Beban Subsidi - Pendapatan Bersih Negara
    """)

# --- 5. VISUALISASI GRAFIK BARU (Positif/Negatif) ---
st.divider()
st.header("📈 Visualisasi Data")

col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("Perbandingan Volume Kuota BBM (Juta KL)")
    df_vol = pd.DataFrame({
        "Jenis BBM": ["Pertalite", "Solar Subsidi", "Minyak Tanah"],
        "Volume (Juta KL)": [vol_pertalite/1e6, vol_solar/1e6, vol_mitan/1e6]
    })
    st.bar_chart(df_vol.set_index("Jenis BBM"))

with col_chart2:
    st.subheader("Beban vs Pendapatan per $1 (Triliun Rp)")
    # Beban dan Defisit dibuat negatif agar grafik mengarah ke bawah (merah)
    # Pendapatan dibuat positif agar grafik mengarah ke atas (hijau)
    df_fin = pd.DataFrame({
        "Komponen": ["Beban Pertalite", "Beban Solar", "Beban Mitan", "PNBP SDA", "PPh Migas", "Selisih (Defisit)"],
        "Nilai (Triliun Rp)": [-beban_pertalite, -beban_solar, -beban_mitan, pnbp_sda, pph_migas, -net_defisit_per_dolar],
        "Warna": ["#ff4b4b", "#ff4b4b", "#ff4b4b", "#2ecc71", "#2ecc71", "#ff9900"] 
    })
    # Streamlit versi terbaru mendukung parameter 'color' untuk mewarnai bar chart secara spesifik
    st.bar_chart(df_fin.set_index("Komponen"), y="Nilai (Triliun Rp)", color="Warna")

st.divider()
st.info(f"🚨 **KESIMPULAN SKENARIO EKSTREM:** Jika harga minyak mentah benar-benar menyentuh **USD {icp_skenario}/barel**, ketahanan fiskal RAPBN 2026 akan terbebani tambahan defisit hingga **Rp {fmt_id(total_defisit_skenario)} Triliun**.")
