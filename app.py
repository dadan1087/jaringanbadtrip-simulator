import streamlit as st 
import pandas as pd
import matplotlib.pyplot as plt
import graphviz
from functools import lru_cache

st.set_page_config(page_title="MLM Binary Simulator", layout="wide")
st.title("Badtrips Binary Network Simulator")

# --- Input Section ---
st.sidebar.header("Input Member Details")
belanja = st.sidebar.number_input("Belanja (Rp)", min_value=0, step=100000, value=2000000)
level_simulasi = st.sidebar.slider("Simulasi Pertumbuhan (Level)", 1, 22, 6)

# --- Bonus Settings ---
st.sidebar.header("💸 Setting Alokasi Bonus")
alokasi_belanja = st.sidebar.number_input("Alokasi dari Belanja (Rp)", min_value=0, step=100000, value=1000000)
bonus_green = st.sidebar.number_input("Bonus GREEN", min_value=0, step=100000, value=5000000)
bonus_silver = st.sidebar.number_input("Bonus SILVER", min_value=0, step=100000, value=10000000)
bonus_red = st.sidebar.number_input("Bonus RED", min_value=0, step=100000, value=50000000)

# --- Helper Functions ---
def build_binary_tree(levels):
    tree = {}
    index = 0
    for level in range(levels + 1):
        nodes = 2 ** level
        tree[level] = list(range(index, index + nodes))
        index += nodes
    return tree

def get_children(index):
    return 2 * index + 1, 2 * index + 2

@lru_cache(maxsize=None)
def count_descendants(member, max_index):
    descendants = set()
    stack = [member]
    while stack:
        node = stack.pop()
        left, right = get_children(node)
        if left <= max_index:
            descendants.add(left)
            stack.append(left)
        if right <= max_index:
            descendants.add(right)
            stack.append(right)
    return descendants

def count_type_descendants(member, max_index, target_members):
    desc = count_descendants(member, max_index)
    return len([d for d in desc if d in target_members])

@st.cache_data(show_spinner=False)
def calculate_statuses(all_members, max_index):
    green_members = []
    silver_members = []
    red_members = []

    # Green: 7 kiri dan 7 kanan
    for member in all_members:
        left, right = get_children(member)
        def collect_subtree(root):
            result = []
            queue = [root]
            while queue:
                current = queue.pop(0)
                result.append(current)
                c_left, c_right = get_children(current)
                if c_left <= max_index:
                    queue.append(c_left)
                if c_right <= max_index:
                    queue.append(c_right)
            return result

        if left <= max_index and right <= max_index:
            left_desc = collect_subtree(left)
            right_desc = collect_subtree(right)
            if len(left_desc) >= 7 and len(right_desc) >= 7:
                green_members.append(member)

    for member in all_members:
        desc = count_descendants(member, max_index)
        green_count = len([d for d in green_members if d in desc])
        if green_count >= 14:
            silver_members.append(member)

    for member in all_members:
        desc = count_descendants(member, max_index)
        silver_count = len([d for d in silver_members if d in desc])
        if silver_count >= 14:
            red_members.append(member)

    return green_members, silver_members, red_members

def get_status(member, green_members, silver_members, red_members):
    if member in red_members:
        return "Red"
    elif member in silver_members:
        return "Silver"
    elif member in green_members:
        return "Green"
    return "-"

def format_rupiah(amount):
    return f"Rp{amount:,.0f}".replace(",", ".")

# --- Simulate Tree ---
tree_dict = build_binary_tree(level_simulasi)
all_members = [m for level in tree_dict.values() for m in level]
max_index = max(all_members)

green_members, silver_members, red_members = calculate_statuses(all_members, max_index)

bonus_green_total = len(green_members) * bonus_green
bonus_silver_total = len(silver_members) * bonus_silver
bonus_red_total = len(red_members) * bonus_red

# --- Output Section ---
st.subheader("📊 Ringkasan Simulasi")
st.markdown(f"**Total Member:** {len(all_members)}")

# --- Tabel Alokasi Bonus + Cashflow Lengkap ---
st.subheader("💰 Simulasi Cashflow dan Bonus Alokasi")

jumlah_member = len(all_members)
total_belanja = jumlah_member * belanja
cash_in = jumlah_member * alokasi_belanja
cash_out = bonus_green_total + bonus_silver_total + bonus_red_total
nett_cash = cash_in - cash_out

if nett_cash < 0:
    st.error("⚠️ Pengaturan bonus menyebabkan kerugian! Cash Out melebihi Cash In. Harap sesuaikan Alokasi atau Bonus agar tidak rugi.")

data_bonus = {
    "Deskripsi": [
        "Jumlah Member",
        "Total Belanja (Rp)",
        "Total Cash In (Rp)",
        "Jumlah Member Green",
        "Jumlah Member Silver",
        "Jumlah Member Red",
        "Total Bonus Green (Rp)",
        "Total Bonus Silver (Rp)",
        "Total Bonus Red (Rp)",
        "Total Cash Out (Bonus) (Rp)",
        "Nett (Cash In - Out) (Rp)"
    ],
    "Nilai": [
        f"{jumlah_member:,}",
        format_rupiah(total_belanja),
        format_rupiah(cash_in),
        f"{len(green_members):,}",
        f"{len(silver_members):,}",
        f"{len(red_members):,}",
        format_rupiah(bonus_green_total),
        format_rupiah(bonus_silver_total),
        format_rupiah(bonus_red_total),
        format_rupiah(cash_out),
        format_rupiah(nett_cash)
    ]
}

df_bonus = pd.DataFrame(data_bonus)
st.dataframe(df_bonus, use_container_width=True)

# --- Grafik Pertumbuhan ---
st.subheader("📈 Grafik Pertumbuhan Jaringan")
fig, ax = plt.subplots()
level_keys = list(tree_dict.keys())
members_per_level = [len(tree_dict[k]) for k in level_keys]
ax.plot(level_keys, members_per_level, marker='o')
ax.set_xlabel("Level")
ax.set_ylabel("Jumlah Member")
ax.set_title("Pertumbuhan Jaringan Binary")
ax.grid(True)
st.pyplot(fig)

# --- Struktur Binary ---
st.subheader("🌳 Struktur Jaringan Binary")
def draw_binary(start, max_depth):
    dot = graphviz.Digraph()
    queue = [(start, 0)]
    while queue:
        node, level = queue.pop(0)
        if level > max_depth:
            continue
        label = f"#{node}"
        if node in red_members:
            label = f"🔴 {label}"
        elif node in silver_members:
            label = f"⚪ {label}"
        elif node in green_members:
            label = f"🟢 {label}"
        dot.node(str(node), label)
        left, right = get_children(node)
        if left <= max_index:
            dot.edge(str(node), str(left))
            queue.append((left, level + 1))
        if right <= max_index:
            dot.edge(str(node), str(right))
            queue.append((right, level + 1))
    return dot

st.graphviz_chart(draw_binary(0, level_simulasi if level_simulasi <= 6 else 4))

# --- Subtree ---
st.subheader("🔍 Lihat Subjaringan dari Member Tertentu")
selected_node = st.number_input("Masukkan nomor member:", min_value=0, max_value=max_index, step=1)
st.markdown(f"**Status:** {get_status(selected_node, green_members, silver_members, red_members)}")
st.markdown(f"**Bonus:** {format_rupiah(bonus_green) if selected_node in green_members else format_rupiah(bonus_silver) if selected_node in silver_members else format_rupiah(bonus_red) if selected_node in red_members else 'Rp0'}")
st.markdown(f"**Green Downlines:** {count_type_descendants(selected_node, max_index, green_members)}")
st.markdown(f"**Silver Downlines:** {count_type_descendants(selected_node, max_index, silver_members)}")
st.graphviz_chart(draw_binary(selected_node, 3))
