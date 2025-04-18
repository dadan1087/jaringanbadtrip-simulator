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
green_level = st.sidebar.number_input("Level Matriks Sempurna untuk GREEN", min_value=1, max_value=10, value=3)
silver_threshold = st.sidebar.number_input("Jumlah Green untuk SILVER", min_value=1, value=14)
red_threshold = st.sidebar.number_input("Jumlah Silver untuk RED", min_value=1, value=14)

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
    if n in red:
        return "RED"
    elif n in silver:
        return "SILVER"
    elif n in green:
        return "GREEN"
    return "-"

# --- Status Calculation ---
@st.cache_data(show_spinner=False)
def calculate_statuses(all_members, max_index, green_level, silver_threshold, red_threshold):
    green, silver, red = set(), set(), set()
    # compute required children per side
    req_children = 2 ** green_level - 1
    
    # find Greens
    for m in all_members:
        left, right = get_children(m)
        if left <= max_index and right <= max_index:
            def collect(root, depth):
                nodes, queue = [], [(root, 0)]
                while queue:
                    cur, d = queue.pop(0)
                    if d > depth:
                        continue
                    nodes.append(cur)
                    l, r = get_children(cur)
                    if l <= max_index:
                        queue.append((l, d+1))
                    if r <= max_index:
                        queue.append((r, d+1))
                return nodes
            left_count = len(collect(left, green_level - 1))
            right_count = len(collect(right, green_level - 1))
            if left_count >= req_children and right_count >= req_children:
                green.add(m)
    
    # cache descendants
    desc_cache = {m: count_descendants(m, max_index) for m in all_members}
    # find Silvers
    for m in all_members:
        if len([d for d in green if d in desc_cache[m]]) >= silver_threshold:
            silver.add(m)
    # find Reds
    for m in all_members:
        if len([d for d in silver if d in desc_cache[m]]) >= red_threshold:
            red.add(m)
    return green, silver, red

# --- Build & Simulate ---
tree = build_binary_tree(level_simulasi)
all_members = [n for lvl in tree.values() for n in lvl]
max_idx = max(all_members)

green, silver, red = calculate_statuses(
    tuple(all_members),
    max_idx,
    green_level,
    silver_threshold,
    red_threshold
)

# --- Eligible Members (Upline penerima bonus) ---
eligible_green = set(green)
eligible_silver = set(silver)
eligible_red = set(red)

# --- Financial Calculations ---
jm = len(all_members)
TotalBelanja = jm * belanja
CashIn = jm * alokasi_belanja
TotGreen = len(eligible_green) * bonus_green
TotSilver = len(eligible_silver) * bonus_silver
TotRed = len(eligible_red) * bonus_red
CashOut = TotGreen + TotSilver + TotRed
Nett = CashIn - CashOut

# --- Output Ringkasan Simulasi ---
st.subheader("📊 Ringkasan Simulasi")
jm = len(all_members)
st.markdown(f"**Total Member:** {jm:,}")
st.markdown(f"**Green (lvl {green_level}):** {len(green):,}")
st.markdown(f"**Silver (≥{silver_threshold} Green):** {len(silver):,}")
st.markdown(f"**Red (≥{red_threshold} Silver):** {len(red):,}")

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
# format currency
currency_idx = [0,1,5,6,7,8,9]
df_summary["Jumlah"] = df_summary["Jumlah"].apply(
    lambda x: f"Rp{x:,.0f}" if isinstance(x,(int,float)) and df_summary["Jumlah"].tolist().index(x) in currency_idx else f"{x:,}"
)
st.table(df_summary)

# alert
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
    queue = [(node, 0)]
    while queue:
        n, d = queue.pop(0)
        if d > depth or n > max_idx:
            continue
        lbl = f"#{n}"
        if n in eligible_red:
            lbl = f"🔴{lbl}"
        elif n in eligible_silver:
            lbl = f"⚪{lbl}"
        elif n in eligible_green:
            lbl = f"🟢{lbl}"
        g.node(str(n), lbl)
        l, r = get_children(n)
        if l <= max_idx:
            g.edge(str(n), str(l))
            queue.append((l, d+1))
        if r <= max_idx:
            g.edge(str(n), str(r))
            queue.append((r, d+1))
    return g

st.graphviz_chart(draw(0, min(level_simulasi, 6)))

# --- Subtree Viewer ---
st.subheader("🔍 Subjaringan Member")
sel = st.number_input("Pilih Member:", 0, max_idx, 0)
st.markdown(f"Status: **{get_status(sel, green, silver, red)}**")
st.markdown(f"Downline Green: {len(count_descendants(sel, max_idx) & green)}")
st.markdown(f"Downline Silver: {len(count_descendants(sel, max_idx) & silver)}")
st.graphviz_chart(draw(sel, 3))
