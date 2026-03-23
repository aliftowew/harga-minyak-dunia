import streamlit as st
import pandas as pd

# Konfigurasi Halaman
st.set_page_config(page_title="Simulasi APBN & Harga Minyak", layout="wide")

st.title("🛢️ Dashboard Simulasi Dampak Harga Minyak thd RAPBN")
st.markdown("Ubah asumsi makro dan volume kuota BBM di sidebar untuk melihat perubahan dampak ke APBN secara *real-time*.")

# --- SIDEBAR INPUTS ---
st.sidebar.header("⚙️ Asumsi Makro & Skenario")
kurs = st.sidebar.number_input("Kurs Rupiah (Rp/USD)", value=16500, step=100)
icp_asumsi = st.sidebar.number_input("Harga Asumsi ICP (USD/barel)", value=70, step=1)
icp_skenario = st.sidebar.number_input("Harga Skenario ICP (USD/barel)", value=200, step=5)
lifting = st.sidebar.number_input("Lifting Minyak (barel/hari)", value=610000, step=10000)

st.sidebar.header("⛽ Volume Kuota BBM (KL)")
vol_pertalite = st.sidebar.number_input("Pertalite", value=29267947, step=500000)
vol_solar = st.sidebar.number_input("Solar Subsidi", value=18636500, step=500000)
vol_mitan = st.sidebar.number_input("Minyak Tanah", value=526000, step=10000)

# --- CALCULATIONS ---
# 1. Konversi Biaya per Kenaikan USD 1/barel
konversi_kl = 6.2898  # Konstanta dari barel ke KL
biaya_per_kl = konversi_kl * kurs

# Beban per USD 1
beban_pertalite = (vol_pertalite * biaya_per_kl) / 1e12
beban_solar = (vol_solar * biaya_per_kl) / 1e12
beban_mitan = (vol_mitan * biaya_per_kl) / 1e12
total_beban = beban_pertalite + beban_solar + beban_mitan

# 2. Pendapatan per Kenaikan USD 1/barel
nilai_tambah_bruto = (lifting * 365 * kurs) / 1e12
pnbp_sda = nilai_tambah_bruto * 0.312  # 31.2%
pph_migas = nilai_tambah_bruto * 0.215 # 21.5%
total_pendapatan = pnbp_sda + pph_migas

# 3. Defisit
net_defisit_per_dolar = total_beban - total_pendapatan
delta_harga = icp_skenario - icp_asumsi
total_defisit_skenario = net_defisit_per_dolar * delta_harga

# --- UI DASHBOARD ---
st.header("📊 Dampak Kenaikan Setiap USD 1 / barel")
col1, col2, col3 = st.columns(3)

with col1:
    st.info("🔴 **Tambahan Beban Subsidi**")
    st.metric(label="Total Beban", value=f"Rp {total_beban:.2f} T")
    st.caption(f"- Pertalite: Rp {beban_pertalite:.2f} T\n- Solar: Rp {beban_solar:.2f} T\n- Mitan: Rp {beban_mitan:.3f} T")

with col2:
    st.success("🟢 **Tambahan Pendapatan Negara**")
    st.metric(label="Total Pendapatan", value=f"Rp {total_pendapatan:.2f} T")
    st.caption(f"- PNBP SDA (31.2%): Rp {pnbp_sda:.2f} T\n- PPh Migas (21.5%): Rp {pph_migas:.2f} T")

with col3:
    st.warning("⚠️ **Net Defisit Negara**")
    st.metric(label="Defisit per USD 1", value=f"Rp {net_defisit_per_dolar:.2f} T")
    st.caption(f"Tiap kelipatan USD 10/barel = Rp {(net_defisit_per_dolar * 10):.1f} T")

st.divider()

# --- SCENARIO HIGHLIGHT ---
st.header("🚨 Simulasi Skenario Ekstrem")
st.markdown(f"Jika harga minyak melonjak dari **USD {icp_asumsi}** ke **USD {icp_skenario}** (selisih USD {delta_harga}):")

col_skenario1, col_skenario2 = st.columns(2)
with col_skenario1:
    st.error(f"### Tambahan Defisit RAPBN:\n# Rp {total_defisit_skenario:.1f} Triliun")

with col_skenario2:
    st.write("**Rincian Skenario Ekstrem:**")
    df_skenario = pd.DataFrame({
        "Komponen": ["Lonjakan Beban Subsidi", "Lonjakan Pendapatan Negara", "Net Defisit Pembengkakan"],
        "Nilai (Triliun Rp)": [total_beban * delta_harga, total_pendapatan * delta_harga, total_defisit_skenario]
    })
    st.dataframe(df_skenario, use_container_width=True, hide_index=True)
