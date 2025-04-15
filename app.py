import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import graphviz

st.set_page_config(page_title="MLM Binary Simulator", layout="wide")
st.title("MLM Binary Network Simulator")

# --- Input Section ---
st.sidebar.header("Input Member Details")
belanja = st.sidebar.number_input("Belanja (Rp)", min_value=0, step=100000, value=2000000)
minggu = st.sidebar.slider("Simulasi Pertumbuhan (minggu)", 1, 6, 4)

# --- Bonus Settings ---
st.sidebar.header("\U0001F4B8 Setting Alokasi Bonus")
alokasi_belanja = st.sidebar.number_input("Alokasi dari Belanja (Rp)", min_value=0, step=100000, value=1000000)
bonus_green = st.sidebar.number_input("Bonus GREEN", min_value=0, step=100000, value=5000000)
bonus_silver = st.sidebar.number_input("Bonus SILVER", min_value=0, step=100000, value=10000000)
bonus_red = st.sidebar.number_input("Bonus RED", min_value=0, step=100000, value=50000000)

# --- Simulate Binary Tree ---
def build_binary_tree(levels):
    tree = {}
    def add_node(index, level):
        if level > levels:
            return
        left = 2 * index + 1
        right = 2 * index + 2
        tree[index] = {
            "left": left,
            "right": right,
            "level": level,
            "status": "Green",
            "green_bonus_received": False,
            "silver_bonus_received": False,
            "red_bonus_received": False,
        }
        add_node(left, level + 1)
        add_node(right, level + 1)
    add_node(0, 1)
    return tree

def get_downlines(tree, index, level_limit=3):
    result = []
    def collect(idx, level):
        if idx not in tree or level > level_limit:
            return
        result.append(idx)
        collect(tree[idx]['left'], level + 1)
        collect(tree[idx]['right'], level + 1)
    collect(tree[index]['left'], 1)
    collect(tree[index]['right'], 1)
    return result

def count_green_and_silver(tree, idx):
    greens = 0
    silvers = 0
    for i in get_all_downlines(tree, idx):
        if tree[i]['status'] == 'Green':
            greens += 1
        elif tree[i]['status'] == 'Silver':
            silvers += 1
    return greens, silvers

def get_all_downlines(tree, index):
    result = []
    def collect(idx):
        if idx not in tree:
            return
        result.append(idx)
        collect(tree[idx]['left'])
        collect(tree[idx]['right'])
    collect(tree[index]['left'])
    collect(tree[index]['right'])
    return result

# --- Run Simulation ---
tree = build_binary_tree(minggu)
total_green_bonus = 0
total_silver_bonus = 0
total_red_bonus = 0
status_counter = {"Green": 0, "Silver": 0, "Red": 0}

def has_perfect_matrix(tree, idx):
    downlines = get_downlines(tree, idx, level_limit=3)
    return len(downlines) == 14  # 7 kiri + 7 kanan

for idx in tree:
    if has_perfect_matrix(tree, idx) and not tree[idx]['green_bonus_received']:
        tree[idx]['green_bonus_received'] = True
        total_green_bonus += bonus_green

for idx in tree:
    greens, silvers = count_green_and_silver(tree, idx)
    if greens >= 14 and not tree[idx]['silver_bonus_received']:
        tree[idx]['status'] = 'Silver'
        tree[idx]['silver_bonus_received'] = True
        total_silver_bonus += bonus_silver

for idx in tree:
    greens, silvers = count_green_and_silver(tree, idx)
    if silvers >= 14 and not tree[idx]['red_bonus_received']:
        tree[idx]['status'] = 'Red'
        tree[idx]['red_bonus_received'] = True
        total_red_bonus += bonus_red

for node in tree.values():
    status_counter[node['status']] += 1

# --- Output ---
st.subheader("\U0001F4CA Ringkasan Simulasi")
st.markdown(f"**Total Member:** {len(tree)}")
st.markdown(f"**Downline:** {len(tree)-1}")
st.markdown(f"**Total Bonus GREEN:** Rp{total_green_bonus:,.0f}")
st.markdown(f"**Total Bonus SILVER:** Rp{total_silver_bonus:,.0f}")
st.markdown(f"**Total Bonus RED:** Rp{total_red_bonus:,.0f}")

# --- Tabel Status ---
st.subheader("\U0001F465 Status Member")
st.markdown(f"🟢 Green: {status_counter['Green']} | 🥈 Silver: {status_counter['Silver']} | 🔴 Red: {status_counter['Red']}")

# --- Struktur Visualisasi ---
st.subheader("\U0001F333 Struktur Jaringan Binary")
def draw_binary_tree(tree):
    dot = graphviz.Digraph()
    for idx, node in tree.items():
        label = f"#{idx}"
        if node['status'] == 'Green':
            label = f"🟢 {label}"
        elif node['status'] == 'Silver':
            label = f"🥈 {label}"
        elif node['status'] == 'Red':
            label = f"🔴 {label}"
        dot.node(str(idx), label)
        if node['left'] in tree:
            dot.edge(str(idx), str(node['left']))
        if node['right'] in tree:
            dot.edge(str(idx), str(node['right']))
    return dot

st.graphviz_chart(draw_binary_tree(tree))

# --- Dataframe Detail ---
st.subheader("\U0001F4CB Data Member")
data = []
for idx, node in tree.items():
    greens, silvers = count_green_and_silver(tree, idx)
    data.append({
        "ID": idx,
        "Level": node['level'],
        "Status": node['status'],
        "Green Bonus": "✓" if node['green_bonus_received'] else "-",
        "Silver Bonus": "✓" if node['silver_bonus_received'] else "-",
        "Red Bonus": "✓" if node['red_bonus_received'] else "-",
        "Total Green Bawah": greens,
        "Total Silver Bawah": silvers
    })
df = pd.DataFrame(data)
st.dataframe(df, use_container_width=True)

st.markdown("---")
st.caption("Simulasi ini menggunakan struktur binary sempurna dan aturan bonus sesuai prioritas jaringan.")
