import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import graphviz

st.set_page_config(page_title="Simulasi MLM Binary", layout="wide")
st.title("Simulasi Binary MLM - Cashflow dan Bonus")

# --- Sidebar Setting ---
st.sidebar.header("⚖️ Setting Simulasi")
belanja_per_member = st.sidebar.number_input("Belanja per Member (Rp)", value=2000000, step=100000)
alokasi_bonus_per_member = st.sidebar.number_input("Alokasi Bonus per Member (Rp)", value=1000000, step=100000)
bonus_green = st.sidebar.number_input("Bonus GREEN (Rp)", value=5000000, step=500000)
bonus_silver = st.sidebar.number_input("Bonus SILVER (Rp)", value=10000000, step=1000000)
bonus_red = st.sidebar.number_input("Bonus RED (Rp)", value=50000000, step=5000000)
jumlah_minggu = st.sidebar.slider("Simulasi Pertumbuhan (minggu)", 1, 5, 3)

# --- Fungsi Hitung Pertumbuhan Jaringan ---
def hitung_jaringan(minggu):
    jaringan = {}
    total_member = 0
    for i in range(minggu + 1):
        jumlah = 2**i
        jaringan[i] = jumlah
        total_member += jumlah
    return jaringan, total_member

jaringan, total_member = hitung_jaringan(jumlah_minggu)
total_downline = total_member - 1

# --- Fungsi Hitung Bonus ---
def hitung_bonus(jumlah_member):
    bonus_green_total = 0
    bonus_silver_total = 0
    bonus_red_total = 0

    # Anggap member pertama (#0) eligible GREEN jika downline 14
    if jumlah_member >= 15:
        bonus_green_total = bonus_green

    # SILVER dan RED dihitung berdasarkan kondisi bahwa perlu 14 GREEN dan 14 SILVER berturut-turut
    total_green = 1 if jumlah_member >= 15 else 0
    total_silver = 0
    total_red = 0

    if total_green >= 14:
        bonus_silver_total = bonus_silver
        total_silver = 1

    if total_silver >= 14:
        bonus_red_total = bonus_red

    return bonus_green_total, bonus_silver_total, bonus_red_total, total_green, total_silver

bonus_green_total, bonus_silver_total, bonus_red_total, total_green, total_silver = hitung_bonus(total_member)

# --- Cashflow & Alokasi Bonus ---
total_cashin = total_member * alokasi_bonus_per_member
total_bonus = bonus_green_total + bonus_silver_total + bonus_red_total
saldo = total_cashin - total_bonus

# --- Tabel Cashflow ---
st.subheader(":moneybag: Simulasi Cashflow dan Alokasi Bonus")
data_cashflow = {
    "Kategori": [
        "Total Member",
        "Total Cash-in dari Alokasi Belanja",
        "Total Bonus GREEN",
        "Total Bonus SILVER",
        "Total Bonus RED",
        "Saldo Akhir"
    ],
    "Jumlah (Rp)": [
        total_member,
        total_cashin,
        bonus_green_total,
        bonus_silver_total,
        bonus_red_total,
        saldo
    ]
}
df_cashflow = pd.DataFrame(data_cashflow)
st.dataframe(df_cashflow, use_container_width=True)

# --- Grafik Pertumbuhan ---
st.subheader(":chart_with_upwards_trend: Grafik Pertumbuhan Jaringan")
fig, ax = plt.subplots()
level = list(jaringan.keys())
jumlah = list(jaringan.values())
ax.plot(level, jumlah, marker='o', linestyle='-', color='green')
for i, (x, y) in enumerate(zip(level, jumlah)):
    ax.text(x, y + 0.3, str(y), ha='center', fontsize=9)
ax.set_xlabel("Level")
ax.set_ylabel("Jumlah Member")
ax.set_title("Pertumbuhan Jaringan Binary")
ax.grid(True)
st.pyplot(fig)

# --- Tabel Jumlah Member per Level ---
st.subheader(":bar_chart: Jumlah Member per Level")
df_jaringan = pd.DataFrame({"Level": level, "Jumlah Member": jumlah})
st.dataframe(df_jaringan, use_container_width=True)

st.caption("Simulasi berdasarkan pertumbuhan jaringan binary sempurna. Untuk hasil aktual, struktur jaringan bisa berbeda.")
