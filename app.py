import streamlit as st  
import pandas as pd
import matplotlib.pyplot as plt
import graphviz
from functools import lru_cache

# --- Streamlit Config ---
st.set_page_config(page_title="MLM Binary Simulator", layout="wide")
st.title("Badtrips Binary Network Simulator")

# --- Sidebar Inputs ---
st.sidebar.header("🔧 Pengaturan Simulasi")
belanja = st.sidebar.number_input("Belanja (Rp)", min_value=0, step=100000, value=2000000)
level_simulasi = st.sidebar.slider("Simulasi Pertumbuhan (Level)", 1, 22, 6)

st.sidebar.header("💸 Alokasi & Bonus")
alokasi_belanja = st.sidebar.number_input("Alokasi dari Belanja (Rp)", min_value=0, step=100000, value=1000000)
bonus_green = st.sidebar.number_input("Bonus GREEN", min_value=0, step=100000, value=5000000)
bonus_silver = st.sidebar.number_input("Bonus SILVER", min_value=0, step=100000, value=10000000)
bonus_red = st.sidebar.number_input("Bonus RED", min_value=0, step=100000, value=50000000)

st.sidebar.header("🎯 Syarat Status")
green_level = st.sidebar.number_input("Level Matriks Sempurna untuk GREEN", min_value=1, max_value=10, value=3, key="green_level")
silver_threshold = st.sidebar.number_input("Jumlah Green untuk SILVER", min_value=1, value=14, key="silver_threshold")
red_threshold = st.sidebar.number_input("Jumlah Silver untuk RED", min_value=1, value=14, key="red_threshold")

req_green_children = 2 ** green_level - 1

# --- Helper Functions ---
def build_binary_tree(levels):
    tree = {}
    index = 0
    for lvl in range(levels + 1):
        nodes = 2 ** lvl
        tree[lvl] = list(range(index, index + nodes))
        index += nodes
    return tree

def get_children(idx):
    return 2 * idx + 1, 2 * idx + 2

@lru_cache(maxsize=None)
def count_descendants(member, max_index):
    desc = set()
    stack = [member]
    while stack:
        node = stack.pop()
        left, right = get_children(node)
        if left <= max_index:
            desc.add(left)
            stack.append(left)
        if right <= max_index:
            desc.add(right)
            stack.append(right)
    return desc

def get_status(n, green, silver, red):
    if n in red: return "RED"
    elif n in silver: return "SILVER"
    elif n in green: return "GREEN"
    return "-"

# --- Status Calculation ---
def calculate_statuses(all_members, max_index):
    green, silver, red = set(), set(), set()
    for m in all_members:
        left, right = get_children(m)
        if left <= max_index and right <= max_index:
            def collect(root, depth):
                nodes, q = [], [(root,0)]
                while q:
                    cur, d = q.pop(0)
                    if d > depth: continue
                    nodes.append(cur)
                    l, r = get_children(cur)
                    if l <= max_index: q.append((l,d+1))
                    if r <= max_index: q.append((r,d+1))
                return nodes
            left_count = len(collect(left, green_level-1))
            right_count = len(collect(right, green_level-1))
            if left_count >= req_green_children and right_count >= req_green_children:
                green.add(m)

    cache_desc = {m: count_descendants(m, max_index) for m in all_members}
    for m in all_members:
        if len([d for d in green if d in cache_desc[m]]) >= silver_threshold:
            silver.add(m)
    for m in all_members:
        if len([d for d in silver if d in cache_desc[m]]) >= red_threshold:
            red.add(m)
    return green, silver, red

# --- Build & Simulate ---
tree = build_binary_tree(level_simulasi)
all_members = [n for lvl in tree.values() for n in lvl]
max_idx = max(all_members)
green, silver, red = calculate_statuses(tuple(all_members), max_idx)

# --- Eligible Members Only (yang terima bonus) ---
eligible_green = {m for m in green if m <= max_idx}
eligible_silver = {m for m in silver if m <= max_idx}
eligible_red = {m for m in red if m <= max_idx}

# --- Financial Calculations ---
jm = len(all_members)
TotalBelanja = jm * belanja
CashIn = jm * alokasi_belanja
TotGreen = len(eligible_green) * bonus_green
TotSilver = len(eligible_silver) * bonus_silver
TotRed = len(eligible_red) * bonus_red
CashOut = TotGreen + TotSilver + TotRed
Nett = CashIn - CashOut

# --- Ringkasan Keuangan Lengkap ---
st.subheader("💰 Ringkasan Keuangan Lengkap")

data = {
    "Deskripsi": [
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
    "Jumlah": [
        TotalBelanja,
        CashIn,
        len(eligible_green),
        len(eligible_silver),
        len(eligible_red),
        TotGreen,
        TotSilver,
        TotRed,
        CashOut,
        Nett
    ]
}

df_summary = pd.DataFrame(data)
df_summary["Jumlah"] = [
    f"Rp{val:,.0f}" if isinstance(val, (int, float)) and i not in [2,3,4] else f"{val:,}"
    for i, val in enumerate(df_summary["Jumlah"])
]

st.table(df_summary)

if Nett >= 0:
    st.success("✅ Cashflow positif - keuntungan")
else:
    st.error("⚠️ Cashflow negatif - kerugian")

# --- Growth Chart ---
st.subheader("📈 Grafik Pertumbuhan")
fig, ax = plt.subplots()
lv = list(tree.keys())
ax.plot(lv, [len(tree[l]) for l in lv], marker='o')
ax.set(xlabel="Level", ylabel="Member", title="Pertumbuhan Jaringan")
st.pyplot(fig)

# --- Binary Structure ---
st.subheader("🌳 Struktur Jaringan")
def draw(node, depth):
    g = graphviz.Digraph()
    q=[(node,0)]
    while q:
        n,d=q.pop(0)
        if d>depth or n>max_idx: continue
        lbl = f"#{n}"
        if n in red: lbl=f"🔴{lbl}" 
        elif n in silver: lbl=f"⚪{lbl}" 
        elif n in green: lbl=f"🟢{lbl}"
        g.node(str(n),lbl)
        l,r=get_children(n)
        if l<=max_idx: g.edge(str(n),str(l)); q.append((l,d+1))
        if r<=max_idx: g.edge(str(n),str(r)); q.append((r,d+1))
    return g
st.graphviz_chart(draw(0, min(level_simulasi,6)))

# --- Subtree Viewer ---
st.subheader("🔍 Subjaringan Member")
sel = st.number_input("Pilih Member:",0, max_idx,0)
st.markdown(f"Status: **{get_status(sel,green,silver,red)}**")
st.markdown(f"Downline Green: {count_descendants(sel,max_idx)&green}" )
st.markdown(f"Downline Silver: {count_descendants(sel,max_idx)&silver}")
st.graphviz_chart(draw(sel,3))
