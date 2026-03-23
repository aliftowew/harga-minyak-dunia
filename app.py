import streamlit as st
import pandas as pd
import altair as alt
import os

# Konfigurasi Halaman
st.set_page_config(page_title="Kalkulator Dampak ICP ke RAPBN", layout="wide")

st.title("🛢️ Kalkulator Dampak Harga Minyak thd RAPBN 2026")
st.markdown("Ubah parameter di bawah ini untuk melihat simulasi dampak pergerakan harga minyak dunia terhadap ketahanan fiskal kita secara *real-time*.")

# --- 1. LOGIKA BERPIKIR & DOWNLOAD FILE PDF ---
with st.expander("🧠 Logika Berpikir Kalkulator Ini", expanded=True):
    st.info("""
    **Bagaimana Alur Hitungannya?**
    1. **Menghitung Beban Negara:** Setiap ada kenaikan harga minyak mentah $1/barel, ada imbas biaya tambahan untuk memproduksi tiap liter BBM subsidi. Kita konversikan satuan kenaikan ini ke Rupiah per Kiloliter (KL) terlebih dahulu, lalu dikalikan dengan kuota volume masing-masing jenis BBM.
    2. **Menghitung Pendapatan (Windfall):** Di sisi lain, sebagai negara produsen, kita juga mendapat tambahan penerimaan dari hasil lifting minyak. Kita hitung nilai tambah brutonya selama setahun penuh (365 hari), lalu negara mengambil porsi penerimaan melalui PNBP SDA (31,2%) dan PPh Migas (21,5%).
    3. **Mencari Defisit Bersih:** Terakhir, kita bandingkan: apakah tambahan pendapatan sanggup menutup tambahan beban? Caranya dengan mengurangkan total Beban dengan total Pendapatan.
    """)
    
    # Tombol Download PDF
    pdf_path = "Logika_Berpikir_Minyak_APBN.pdf"
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as pdf_file:
            st.download_button(
                label="📄 Download File Catatan Asli (PDF)",
                data=pdf_file,
                file_name="Logika_Berpikir_Minyak_APBN.pdf",
                mime="application/pdf"
            )
    else:
        st.warning("⚠️ Untuk Admin: File 'Logika_Berpikir_Minyak_APBN.pdf' belum diletakkan di folder yang sama dengan aplikasi ini.")

st.divider()

# --- FUNGSI BANTUAN UNTUK INPUT ANGKA ---
def bersihkan_input(teks):
    """Mengubah teks berformat titik kembali menjadi angka (float) agar bisa dihitung"""
    try:
        # Hapus titik pemisah ribuan
        angka_bersih = teks.replace(".", "")
        return float(angka_bersih)
    except ValueError:
        return 0.0

def fmt_id(angka, desimal=2):
    """Format output hasil hitungan menjadi titik ribuan"""
    return f"{angka:,.{desimal}f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- 2. INPUT PARAMETER (DENGAN TITIK RIBUAN) ---
st.header("⚙️ Parameter Asumsi")
st.caption("📌 **Catatan:** Data asumsi dasar ekonomi makro dan volume kuota BBM subsidi di bawah ini secara default merujuk pada postur **RAPBN 2026**. Anda bebas mengetik angka menggunakan titik pemisah ribuan.")

col_input1, col_input2 = st.columns(2)

with col_input1:
    st.subheader("Indikator Makroekonomi")
    kurs_input = st.text_input("Kurs Rupiah (Rp/USD)", value="16.500")
    icp_asumsi_input = st.text_input("Harga Asumsi ICP (USD/barel)", value="70")
    icp_skenario_input = st.text_input("Harga Skenario Ekstrem ICP (USD/barel)", value="200")
    lifting_input = st.text_input("Lifting Minyak (barel/hari)", value="610.000")

    # Konversi input teks kembali jadi angka
    kurs = bersihkan_input(kurs_input)
    icp_asumsi = bersihkan_input(icp_asumsi_input)
    icp_skenario = bersihkan_input(icp_skenario_input)
    lifting = bersihkan_input(lifting_input)

with col_input2:
    st.subheader("Volume Kuota BBM (KL)")
    vol_pertalite_input = st.text_input("Kuota Pertalite (KL)", value="29.267.947")
    vol_solar_input = st.text_input("Kuota Solar Subsidi (KL)", value="18.636.500")
    vol_mitan_input = st.text_input("Kuota Minyak Tanah (KL)", value="526.000")

    # Konversi input teks kembali jadi angka
    vol_pertalite = bersihkan_input(vol_pertalite_input)
    vol_solar = bersihkan_input(vol_solar_input)
    vol_mitan = bersihkan_input(vol_mitan_input)

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

# --- 4. RUMUS MATEMATIS ---
with st.expander("📐 Rumus Matematis yang Digunakan", expanded=True):
    st.warning("""
    **Detail Rumus:**
    * **Biaya Tambahan per KL** = 6,2898 × Kurs Rupiah
    * **Beban Subsidi** = Volume BBM (KL) × Biaya Tambahan per KL
    * **Pendapatan Bruto Setahun** = Lifting Harian × 365 Hari × Kurs Rupiah
    * **Pendapatan Bersih Negara** = PNBP SDA (31,2% dari Bruto) + PPh Migas (21,5% dari Bruto)
    * **Defisit per Kenaikan $1** = Total Beban Subsidi - Pendapatan Bersih Negara
    """)

# --- 5. VISUALISASI GRAFIK BARU (Altair) ---
st.divider()
st.header("📈 Visualisasi Data")

col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("Perbandingan Volume Kuota BBM (Juta KL)")
    df_vol = pd.DataFrame({
        "Jenis BBM": ["Pertalite", "Solar Subsidi", "Minyak Tanah"],
        "Volume (Juta KL)": [round(vol_pertalite/1e6, 2), round(vol_solar/1e6, 2), round(vol_mitan/1e6, 2)]
    })
    
    chart_vol = alt.Chart(df_vol).mark_bar(color='#3b71ca').encode(
        x=alt.X("Jenis BBM:N", sort=None, title=""),
        y=alt.Y("Volume (Juta KL):Q"),
        tooltip=[alt.Tooltip("Jenis BBM:N"), alt.Tooltip("Volume (Juta KL):Q")]
    )
    
    st.altair_chart(chart_vol, use_container_width=True)

with col_chart2:
    st.subheader("Beban vs Pendapatan per $1 (Triliun Rp)")
    
    df_fin = pd.DataFrame({
        "Komponen": ["Beban Mitan", "Beban Pertalite", "Beban Solar", "PNBP SDA", "PPh Migas", "Selisih (Defisit)"],
        "Nilai (Triliun Rp)": [round(-beban_mitan, 2), round(-beban_pertalite, 2), round(-beban_solar, 2), round(pnbp_sda, 2), round(pph_migas, 2), round(-net_defisit_per_dolar, 2)],
        "Kategori": ["Negatif (Beban)", "Negatif (Beban)", "Negatif (Beban)", "Positif (Pendapatan)", "Positif (Pendapatan)", "Defisit"]
    })
    
    color_scale = alt.Scale(
        domain=["Negatif (Beban)", "Positif (Pendapatan)", "Defisit"],
        range=["#ff4b4b", "#2ecc71", "#ff9900"]  
    )
    
    chart_fin = alt.Chart(df_fin).mark_bar().encode(
        x=alt.X("Komponen:N", sort=None, title=""),
        y=alt.Y("Nilai (Triliun Rp):Q"),
        color=alt.Color("Kategori:N", scale=color_scale, legend=None),
        tooltip=[alt.Tooltip("Komponen:N"), alt.Tooltip("Nilai (Triliun Rp):Q")]
    )
    
    st.altair_chart(chart_fin, use_container_width=True)

st.divider()
st.info(f"🚨 **KESIMPULAN SKENARIO EKSTREM:** Jika harga minyak mentah benar-benar menyentuh **USD {icp_skenario_input}/barel**, ketahanan fiskal RAPBN 2026 akan terbebani tambahan defisit hingga **Rp {fmt_id(total_defisit_skenario)} Triliun**.")

# --- FOOTER SIGNATURE ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        <h4>💡 Semua Bisa Dihitung</h4>
        <p>by Alif Towew</p>
    </div>
    """, 
    unsafe_allow_html=True
)
