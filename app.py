import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math

st.set_page_config(page_title="MLM Binary Simulator", layout="wide")
st.title("MLM Binary Network Simulator")

# --- Input Section ---
st.sidebar.header("Input Member Details")
belanja = st.sidebar.number_input("Belanja (Rp)", min_value=0, step=100000, value=2000000)
minggu = st.sidebar.slider("Simulasi Pertumbuhan (minggu)", 1, 10, 3)

# --- Define Bonus & Status Rules ---
def get_status_and_bonus(total_downline, silver_downline):
    if total_downline == 14 and silver_downline < 14:
        return "Green", 5_000_000
    elif total_downline == 14 and silver_downline == 14:
        return "Red", 30_000_000
    elif total_downline >= 14:
        return "Silver", 10_000_000
    return "-", 0

# --- Simulate Binary Tree Growth ---
def simulate_binary_growth(levels):
    network = {0: 1}  # root level has 1 person
    for i in range(1, levels + 1):
        network[i] = network[i - 1] * 2
    return network

network = simulate_binary_growth(minggu)
total_members = sum(network.values())
total_downline = total_members - 1

# --- Dummy silver simulation ---
silver_downline = 14 if minggu >= 4 else 0
status, bonus = get_status_and_bonus(total_downline, silver_downline)

# --- Output Section ---
st.subheader("\U0001F4CA Ringkasan Simulasi")
st.markdown(f"**Total Member:** {total_members}")
st.markdown(f"**Downline:** {total_downline}")
st.markdown(f"**Status:** {status}")
st.markdown(f"**Bonus:** Rp{bonus:,.0f}")

# --- Grafik Pertumbuhan ---
st.subheader("\U0001F4C8 Grafik Pertumbuhan Jaringan")
fig, ax = plt.subplots()
levels = list(network.keys())
members = list(network.values())
ax.plot(levels, members, marker='o', linestyle='-', color='green')
ax.set_xlabel("Level")
ax.set_ylabel("Jumlah Member")
ax.set_title("Pertumbuhan Jaringan Binary")
ax.grid(True)
st.pyplot(fig)

# --- Tabel Detail ---
st.subheader("\U0001F4C3 Tabel Jumlah Member per Level")
df = pd.DataFrame({"Level": levels, "Member Baru": members})
st.dataframe(df, use_container_width=True)

st.markdown("---")
st.caption("Simulasi ini berdasarkan pertumbuhan binary sempurna. Untuk hasil aktual bisa berbeda tergantung perilaku member dan kondisi jaringan.")

import streamlit as st
import graphviz

def draw_binary_tree(levels):
    dot = graphviz.Digraph()
    dot.node("0", "🟢")

    node_id = 1
    def add_nodes(parent, current_level):
        nonlocal node_id
        if current_level > levels:
            return
        left = str(node_id)
        dot.node(left, "🟢")
        dot.edge(parent, left)
        node_id += 1

        right = str(node_id)
        dot.node(right, "🟢")
        dot.edge(parent, right)
        node_id += 1

        add_nodes(left, current_level + 1)
        add_nodes(right, current_level + 1)

    add_nodes("0", 1)
    return dot

# Tampilkan visualisasi binary tree
st.subheader("🌳 Struktur Jaringan Binary")
tree = draw_binary_tree(minggu)
st.graphviz_chart(tree)

