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

# --- Utility Functions ---
def is_perfect_matrix(member_index, member_status):
    left = 2 * member_index + 1
    right = 2 * member_index + 2
    if left not in member_status or right not in member_status:
        return False

    left_subtree = get_subtree(left, member_status)
    right_subtree = get_subtree(right, member_status)
    return len(left_subtree) >= 7 and len(right_subtree) >= 7

def get_subtree(index, member_status):
    nodes = []
    def dfs(i):
        if i not in member_status:
            return
        nodes.append(i)
        dfs(2 * i + 1)
        dfs(2 * i + 2)
    dfs(index)
    return nodes

# --- Simulate Binary Tree ---
def simulate_binary_tree(levels):
    total_nodes = 2 ** (levels + 1) - 1
    member_status = {}
    member_bonus = {}
    member_green_downline = {}
    member_silver_downline = {}

    for i in range(total_nodes):
        member_status[i] = "-"
        member_bonus[i] = 0
        member_green_downline[i] = []
        member_silver_downline[i] = []

    green_members = set()
    silver_members = set()
    red_members = set()

    for i in reversed(range(total_nodes)):
        if is_perfect_matrix(i, member_status):
            member_status[i] = "Green"
            member_bonus[i] = bonus_green
            green_members.add(i)

    for i in range(total_nodes):
        for g in green_members:
            if g in get_subtree(i, member_status) and g != i:
                member_green_downline[i].append(g)

        if len(member_green_downline[i]) >= 14:
            member_status[i] = "Silver"
            member_bonus[i] = bonus_silver
            silver_members.add(i)

    for i in range(total_nodes):
        for s in silver_members:
            if s in get_subtree(i, member_status) and s != i:
                member_silver_downline[i].append(s)

        if len(member_silver_downline[i]) >= 14:
            member_status[i] = "Red"
            member_bonus[i] = bonus_red
            red_members.add(i)

    return total_nodes, member_status, member_bonus, member_green_downline, member_silver_downline

# --- Simulasi ---
total_members, member_status, member_bonus, green_downlines, silver_downlines = simulate_binary_tree(minggu)

total_bonus_green = sum(b for i, b in member_bonus.items() if member_status[i] == "Green")
total_bonus_silver = sum(b for i, b in member_bonus.items() if member_status[i] == "Silver")
total_bonus_red = sum(b for i, b in member_bonus.items() if member_status[i] == "Red")

# --- Output Section ---
st.subheader("\U0001F4CA Ringkasan Simulasi")
st.markdown(f"**Total Member:** {total_members}")
st.markdown(f"**Status Member 0:** {member_status[0]}")
st.markdown(f"**Bonus Member 0:** Rp{member_bonus[0]:,.0f}")

# --- Tabel Alokasi Bonus ---
st.subheader("\U0001F4B0 Tabel Alokasi Bonus")
df_bonus = pd.DataFrame({
    "Kategori": ["GREEN", "SILVER", "RED"],
    "Total Bonus (Rp)": [total_bonus_green, total_bonus_silver, total_bonus_red]
})
st.dataframe(df_bonus, use_container_width=True)

# --- Visualisasi Binary Tree ---
st.subheader("\U0001F333 Struktur Jaringan Binary")

def draw_binary_tree(levels, member_status):
    dot = graphviz.Digraph()

    def get_label(n):
        status = member_status.get(n, "-")
        return f"#{n}\n{status}"

    def add_nodes(parent, current, current_level):
        if current_level > levels:
            return
        left = 2 * current + 1
        right = 2 * current + 2
        dot.node(str(current), get_label(current))
        if left < 2 ** (levels + 1) - 1:
            dot.node(str(left), get_label(left))
            dot.edge(str(current), str(left))
            add_nodes(current, left, current_level + 1)
        if right < 2 ** (levels + 1) - 1:
            dot.node(str(right), get_label(right))
            dot.edge(str(current), str(right))
            add_nodes(current, right, current_level + 1)

    add_nodes(None, 0, 0)
    return dot

st.graphviz_chart(draw_binary_tree(minggu, member_status))

# --- Interaktif Pilih Node untuk Lihat Detail ---
st.subheader("\U0001F50D Detail Member Tertentu")
selected_node = st.number_input("Masukkan nomor member:", min_value=0, max_value=total_members - 1, step=1)

st.markdown(f"**Status:** {member_status[selected_node]}")
st.markdown(f"**Bonus:** Rp{member_bonus[selected_node]:,.0f}")
st.markdown(f"**Green Downlines:** {len(green_downlines[selected_node])}")
st.markdown(f"**Silver Downlines:** {len(silver_downlines[selected_node])}")

st.markdown("---")
st.caption("Simulasi ini berbasis jaringan binary sempurna. Dalam implementasi nyata, hasil bisa berbeda tergantung struktur jaringan dan aktivitas member.")
