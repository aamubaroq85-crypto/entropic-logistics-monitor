import streamlit as st
import pandas as pd
import math
import numpy as np
import plotly.graph_objects as go

# ==========================================
# KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(page_title="Entropic Logistics Monitor", layout="wide")

st.title("🌍 Global Mining Entropic Logistics Monitor")
st.markdown("""
Dashboard interaktif pengambilan keputusan rute armada tambang berbasis **Zero-Loss Routing Protoco**. 
Sistem ini mengevaluasi rute dengan jejak entropi minimum untuk memaksimalkan efisiensi bahan bakar.
""")

# ==========================================
# SIDEBAR: KONTROL PARAMETER INTERAKTIF
# ==========================================
st.sidebar.header("⚙️ Parameter Geometris")
pi_eff = st.sidebar.number_input("Konstanta Zuhri (π_eff)", value=1.618, format="%.3f")
G = 9.81

st.sidebar.markdown("---")
st.sidebar.subheader("🛣️ Kondisi Rute A")
route_a_theta = st.sidebar.slider("Kemiringan Rute A (Derajat)", 0.0, 25.0, 5.0)
route_a_mu = st.sidebar.slider("Gesekan Rute A (μ) - (Makin besar makin licin/berlumpur)", 0.1, 1.0, 0.4)

st.sidebar.markdown("---")
st.sidebar.subheader("🛣️ Kondisi Rute B")
route_b_theta = st.sidebar.slider("Kemiringan Rute B (Derajat)", 0.0, 25.0, 12.0)
route_b_mu = st.sidebar.slider("Gesekan Rute B (μ) - (Kering/Berbatu)", 0.1, 1.0, 0.15)

# ==========================================
# FUNGSI KALKULASI & DUMMY DATA
# ==========================================
def calculate_entropic_loss(weight_ton, speed_ms, theta_deg, mu_friction, pi_val):
    weight_kg = weight_ton * 1000
    theta_rad = math.radians(theta_deg)
    force_gravity = weight_kg * G * math.sin(theta_rad)
    force_friction = mu_friction * weight_kg * G * math.cos(theta_rad)
    return ((force_gravity + force_friction) * speed_ms) / pi_val

# Menggunakan np.random.seed agar data truk tidak berubah-ubah saat slider digeser
np.random.seed(42)
num_trucks = 10
truck_ids = [f"TRK-{100+i}" for i in range(1, num_trucks + 1)]
weights = np.random.randint(80, 150, size=num_trucks)
speeds = np.random.uniform(5.0, 10.0, size=num_trucks)

df_trucks = pd.DataFrame({
    "ID_Truk": truck_ids,
    "Muatan_Ton": weights,
    "Kecepatan_ms": speeds
})

# ==========================================
# PROSES EVALUASI ALGORITMA
# ==========================================
results = []
for index, row in df_trucks.iterrows():
    w = row["Muatan_Ton"]
    v = row["Kecepatan_ms"]
    
    e_a = calculate_entropic_loss(w, v, route_a_theta, route_a_mu, pi_eff)
    e_b = calculate_entropic_loss(w, v, route_b_theta, route_b_mu, pi_eff)
    
    best_route = "Rute A" if e_a < e_b else "Rute B"
    saved = abs(e_a - e_b)
    
    results.append({
        "ID_Truk": row["ID_Truk"],
        "E_Loss_Rute_A": round(e_a, 2),
        "E_Loss_Rute_B": round(e_b, 2),
        "Rekomendasi": best_route,
        "Energi_Diselamatkan": round(saved, 2)
    })

df_hasil = pd.DataFrame(results)

# ==========================================
# VISUALISASI DASHBOARD
# ==========================================
# 1. Metrik Utama (KPI)
total_saved = df_hasil['Energi_Diselamatkan'].sum()
total_loss_if_wrong = df_hasil[['E_Loss_Rute_A', 'E_Loss_Rute_B']].max(axis=1).sum()
efficiency_gain = (total_saved / total_loss_if_wrong) * 100

col1, col2, col3 = st.columns(3)
col1.metric("Total Armada Beroperasi", f"{num_trucks} Unit")
col2.metric("Total Energi Diselamatkan", f"{total_saved:,.0f} Joule/s", "Real-time")
col3.metric("Estimasi Peningkatan Efisiensi", f"{efficiency_gain:.1f}%", "BBM Saved")

st.markdown("---")

# 2. Grafik Plotly Interaktif
st.subheader("📊 Perbandingan Entropi per Unit Armada")
fig = go.Figure()
fig.add_trace(go.Bar(x=df_hasil['ID_Truk'], y=df_hasil['E_Loss_Rute_A'], name='Rute A', marker_color='#E55451'))
fig.add_trace(go.Bar(x=df_hasil['ID_Truk'], y=df_hasil['E_Loss_Rute_B'], name='Rute B', marker_color='#2E8B57'))

fig.update_layout(
    barmode='group',
    xaxis_title='ID Truk',
    yaxis_title='Kehilangan Energi (E_loss)',
    plot_bgcolor='rgba(0,0,0,0)',
    legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.5)')
)
st.plotly_chart(fig, use_container_width=True)

# 3. Tabel Data Detail
st.subheader("📋 Log Keputusan Sistem Rekomendasi")
# Memberikan warna pada kolom rekomendasi
def highlight_recommendation(val):
    color = '#c6efce' if val == 'Rute A' else '#ffc7ce'
    return f'background-color: {color}; color: black'

st.dataframe(df_hasil.style.map(highlight_recommendation, subset=['Rekomendasi']), use_container_width=True)

