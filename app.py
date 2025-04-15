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
bonus_silver = st.sidebar.number_input("Bonus SILVER", min_value=0, step=100000, value=10000000)
bonus_red = st.sidebar.number_input("Bonus RED", min_value=0, step=100000, value=50000000)

# --- Simulate Binary Tree Growth ---
def simulate_binary_growth(levels):
    network = {}
    index = 0
    for level in range(levels + 1):
        num_nodes = 2 ** level
        for i in range(num_nodes):
            network[index] = {
                'level': level,
                'left': 2 * index + 1,
                'right': 2 * index + 2,
                'status': '-',
                'bonus': 0,
                'green_downlines': 0,
                'silver_downlines': 0
            }
            index += 1
    return network

# --- Check if a member has a perfect matrix ---
def has_perfect_matrix(network, node_id):
    def count_descendants(nid, level=0):
        if nid not in network or level == 3:
            return 0
        left = network[nid]['left']
        right = network[nid]['right']
        return 1 + count_descendants(left, level + 1) + count_descendants(right, level + 1)

    def is_perfect(nid, depth):
        if depth == 0:
            return True
        if nid not in network:
            return False
        return is_perfect(network[nid]['left'], depth - 1) and is_perfect(network[nid]['right'], depth - 1)

    return is_perfect(node_id, 3)

network = simulate_binary_growth(minggu)
total_members = len(network)

# --- Assign status and calculate bonuses ---
green_bonus_total = 0
silver_bonus_total = 0
red_bonus_total = 0

# Determine Green Status
for node_id in sorted(network.keys(), reverse=True):
    if has_perfect_matrix(network, node_id):
        network[node_id]['status'] = 'Green'
        network[node_id]['bonus'] += bonus_green
        green_bonus_total += bonus_green

# Count Green downlines for each node
for node_id in sorted(network.keys(), reverse=True):
    left = network[node_id]['left']
    right = network[node_id]['right']
    green_count = 0
    if left in network and network[left]['status'] == 'Green':
        green_count += 1
    if right in network and network[right]['status'] == 'Green':
        green_count += 1
    if left in network:
        green_count += network[left]['green_downlines']
    if right in network:
        green_count += network[right]['green_downlines']
    network[node_id]['green_downlines'] = green_count
    if green_count >= 14:
        network[node_id]['status'] = 'Silver'
        network[node_id]['bonus'] += bonus_silver
        silver_bonus_total += bonus_silver

# Count Silver downlines for Red qualification
for node_id in sorted(network.keys(), reverse=True):
    left = network[node_id]['left']
    right = network[node_id]['right']
    silver_count = 0
    if left in network and network[left]['status'] == 'Silver':
        silver_count += 1
    if right in network and network[right]['status'] == 'Silver':
        silver_count += 1
    if left in network:
        silver_count += network[left]['silver_downlines']
    if right in network:
        silver_count += network[right]['silver_downlines']
    network[node_id]['silver_downlines'] = silver_count
    if silver_count >= 14:
        network[node_id]['status'] = 'Red'
        network[node_id]['bonus'] += bonus_red
        red_bonus_total += bonus_red

# --- Output Summary ---
st.subheader("\U0001F4CA Ringkasan Simulasi")
st.markdown(f"**Total Member:** {total_members}")
st.markdown(f"**Status Member 0:** {network[0]['status']}")
st.markdown(f"**Bonus Member 0:** Rp{network[0]['bonus']:,.0f}")

# --- Alokasi Bonus Table ---
st.subheader("\U0001F4B0 Alokasi Bonus")
data_bonus = {
    "Kategori": ["GREEN", "SILVER", "RED"],
    "Total Bonus (Rp)": [green_bonus_total, silver_bonus_total, red_bonus_total]
}
df_bonus = pd.DataFrame(data_bonus)
st.dataframe(df_bonus, use_container_width=True)

# --- Grafik Pertumbuhan ---
st.subheader("\U0001F4C8 Grafik Pertumbuhan Jaringan")
fig, ax = plt.subplots()
level_counts = {}
for node in network.values():
    level = node['level']
    level_counts[level] = level_counts.get(level, 0) + 1
levels = list(level_counts.keys())
members = list(level_counts.values())
ax.plot(levels, members, marker='o', linestyle='-', color='green')
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

def draw_binary_tree_custom(network):
    dot = graphviz.Digraph()
    for node_id, node in network.items():
        label = f"#{node_id}\n{node['status']}"
        dot.node(str(node_id), label)
        if node['left'] in network:
            dot.edge(str(node_id), str(node['left']))
        if node['right'] in network:
            dot.edge(str(node_id), str(node['right']))
    return dot

st.graphviz_chart(draw_binary_tree_custom(network))

# --- Interaktif Pilih Node untuk Lihat Detail ---
st.subheader("\U0001F50D Lihat Detail Member")
selected_node = st.number_input("Masukkan nomor member:", min_value=0, max_value=total_members - 1, step=1)
st.markdown(f"**Status:** {network[selected_node]['status']}")
st.markdown(f"**Bonus:** Rp{network[selected_node]['bonus']:,.0f}")
st.markdown(f"**Green Downlines:** {network[selected_node]['green_downlines']}")
st.markdown(f"**Silver Downlines:** {network[selected_node]['silver_downlines']}")

st.markdown("---")
st.caption("Simulasi ini berdasarkan pertumbuhan binary sempurna dan aturan MLM yang ditetapkan.")
