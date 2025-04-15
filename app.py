import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import graphviz
import math

st.set_page_config(page_title="MLM Binary Simulator", layout="wide")
st.title("MLM Binary Network Simulator")

# --- Input Section ---
st.sidebar.header("Input Member Details")
belanja = st.sidebar.number_input("Belanja (Rp)", min_value=0, step=100000, value=2000000)
minggu = st.sidebar.slider("Simulasi Pertumbuhan (minggu)", 1, 5, 3)

# --- Bonus Settings ---
st.sidebar.header("\U0001F4B8 Setting Alokasi Bonus")
alokasi_belanja = st.sidebar.number_input("Alokasi dari Belanja (Rp)", min_value=0, step=100000, value=1000000)
bonus_green = st.sidebar.number_input("Bonus GREEN", min_value=0, step=100000, value=5000000)
bonus_silver = st.sidebar.number_input("Bonus SILVER", min_value=0, step=100000, value=15000000)
bonus_red = st.sidebar.number_input("Bonus RED", min_value=0, step=100000, value=50000000)

# --- Define Bonus & Status Rules ---
def get_status_and_bonus(total_downline, green_downline, silver_downline):
    # Cek jika ada 14 Silver di bawahnya, maka statusnya bisa jadi Red
    if silver_downline >= 14:  # Jika sudah ada 14 Silver di bawahnya
        return "Red", bonus_red
    # Cek jika ada 14 Green di bawahnya, maka statusnya bisa jadi Silver
    elif green_downline >= 14 and silver_downline == 0:  # Masih Green, belum ada Silver
        return "Silver", bonus_silver
    elif green_downline >= 14:  # Dapat Bonus Silver jika sudah punya 14 Green
        return "Silver", bonus_silver
    # Jika total downline sudah mencapai 14 dan green_downline < 14, status Green
    elif total_downline == 14 and green_downline < 14:
        return "Green", bonus_green
    elif total_downline < 14:
        return "-", 0
    return "-", 0

# --- Simulate Binary Tree Growth ---
def simulate_binary_growth(levels):
    network = {0: 1}  # root level has 1 person
    for i in range(1, levels + 1):
        network[i] = network[i - 1] * 2
    return network

# --- Simulate the network based on the number of weeks (levels) ---
network = simulate_binary_growth(minggu)
total_members = sum(network.values())
total_downline = total_members - 1

# --- Dummy simulation of Green and Silver downlines ---
green_downline = min(14, total_downline)  # For simplicity, we simulate green downlines to be up to 14
silver_downline = min(14, green_downline)  # For simplicity, we simulate silver downlines to be up to 14

status, bonus = get_status_and_bonus(total_downline, green_downline, silver_downline)

# --- Output Section ---
st.subheader("\U0001F4CA Ringkasan Simulasi")
st.markdown(f"**Total Member:** {total_members}")
st.markdown(f"**Downline:** {total_downline}")
st.markdown(f"**Status:** {status}")
st.markdown(f"**Bonus:** Rp{bonus:,.0f}")

# --- Alokasi Bonus Table ---
st.subheader("\U0001F4B0 Alokasi Bonus")
data_bonus = {
    "Kategori": ["Dari Belanja", "GREEN", "SILVER", "RED"],
    "Jumlah (Rp)": [alokasi_belanja, bonus_green, bonus_silver, bonus_red]
}
df_bonus = pd.DataFrame(data_bonus)
st.dataframe(df_bonus, use_container_width=True)

# --- Grafik Pertumbuhan ---
st.subheader("\U0001F4C8 Grafik Pertumbuhan Jaringan")
fig, ax = plt.subplots()
levels = list(network.keys())
members = list(network.values())
ax.plot(levels, members, marker='o', linestyle='-', color='green')

# Tambahkan label angka di tiap titik
for i, (x, y) in enumerate(zip(levels, members)):
    ax.text(x, y + 0.5, str(y), ha='center', fontsize=9, color='black')

ax.set_xlabel("Level")
ax.set_ylabel("Jumlah Member")
ax.set_title("Pertumbuhan Jaringan Binary")
ax.grid(True)
st.pyplot(fig)

# --- Tabel Detail ---
st.subheader("\U0001F4C3 Tabel Jumlah Member per Level")
df = pd.DataFrame({"Level": levels, "Member Baru": members})
st.dataframe(df, use_container_width=True)

# --- Visualisasi Struktur Binary Tree ---
st.subheader("\U0001F333 Struktur Jaringan Binary")

def draw_binary_tree(levels, start=0, node_limit=None):
    dot = graphviz.Digraph()

    def get_label(n):
        return f"🟢 #{n
