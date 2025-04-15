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

# --- Simulasi Pertumbuhan Binary Tree ---
def generate_members(levels):
    members = []
    for level in range(levels + 1):
        for i in range(2 ** level):
            member_id = len(members)
            parent_id = (member_id - 1) // 2 if member_id != 0 else None
            members.append({
                "id": member_id,
                "parent": parent_id,
                "level": level,
                "status": "Green",
                "bonus": 0,
                "green_downline": 0,
                "silver_downline": 0
            })
    return members

members = generate_members(minggu)

# --- Hitung Bonus Green ---
def assign_green_bonus(members):
    bonus_total = 0
    awarded_ids = set()
    for m in members[::-1]:
        if m["id"] == 0:
            continue
        parent = members[m["parent"]]
        if parent["id"] in awarded_ids:
            continue
        siblings = [x for x in members if x["parent"] == parent["id"]]
        if len(siblings) >= 2:
            children = [x for x in members if x["parent"] in [s["id"] for s in siblings]]
            if len(children) >= 4:
                grand = [x for x in members if x["parent"] in [c["id"] for c in children]]
                if len(grand) >= 8:
                    parent["bonus"] += bonus_green
                    parent["status"] = "Green"
                    awarded_ids.add(parent["id"])
                    bonus_total += bonus_green
    return bonus_total

bonus_green_total = assign_green_bonus(members)

# --- Hitung Bonus Silver ---
def assign_silver_bonus(members):
    bonus_total = 0
    for m in members:
        downlines = [x for x in members if x["parent"] == m["id"] and x["status"] == "Green"]
        if len(downlines) >= 14:
            m["status"] = "Silver"
            m["bonus"] += bonus_silver
            bonus_total += bonus_silver
    return bonus_total

bonus_silver_total = assign_silver_bonus(members)

# --- Hitung Bonus Red ---
def assign_red_bonus(members):
    bonus_total = 0
    for m in members:
        downlines = [x for x in members if x["parent"] == m["id"] and x["status"] == "Silver"]
        if len(downlines) >= 14:
            m["status"] = "Red"
            m["bonus"] += bonus_red
            bonus_total += bonus_red
    return bonus_total

bonus_red_total = assign_red_bonus(members)

# --- Ringkasan ---
jumlah_member = len(members)

st.subheader("\U0001F4CA Ringkasan Simulasi")
st.markdown(f"**Total Member:** {jumlah_member}")
st.markdown(f"**Total Bonus GREEN:** Rp{bonus_green_total:,.0f}")
st.markdown(f"**Total Bonus SILVER:** Rp{bonus_silver_total:,.0f}")
st.markdown(f"**Total Bonus RED:** Rp{bonus_red_total:,.0f}")

# --- Tabel Bonus Alokasi ---
st.subheader("\U0001F4B0 Alokasi Bonus")
data_bonus = {
    "Kategori": ["Alokasi dari Belanja", "GREEN", "SILVER", "RED"],
    "Jumlah (Rp)": [alokasi_belanja, bonus_green, bonus_silver, bonus_red]
}
df_bonus = pd.DataFrame(data_bonus)
st.dataframe(df_bonus, use_container_width=True)

# --- Grafik Pertumbuhan ---
st.subheader("\U0001F4C8 Grafik Pertumbuhan Jaringan")
level_count = {}
for m in members:
    level = m["level"]
    level_count[level] = level_count.get(level, 0) + 1

fig, ax = plt.subplots()
ax.plot(list(level_count.keys()), list(level_count.values()), marker='o', linestyle='-', color='green')
for x, y in level_count.items():
    ax.text(x, y + 0.5, str(y), ha='center', fontsize=9, color='black')

ax.set_xlabel("Level")
ax.set_ylabel("Jumlah Member")
ax.set_title("Pertumbuhan Jaringan Binary")
ax.grid(True)
st.pyplot(fig)

# --- Struktur Binary Visual ---
st.subheader("\U0001F333 Struktur Jaringan Binary")
def draw_binary_tree(members):
    dot = graphviz.Digraph()
    for m in members:
        label = f"{m['status']}\n#{m['id']}\nBonus: {m['bonus']//1_000_000}jt"
        dot.node(str(m['id']), label)
        if m['parent'] is not None:
            dot.edge(str(m['parent']), str(m['id']))
    return dot

st.graphviz_chart(draw_binary_tree(members))

st.markdown("---")
st.caption("Simulasi ini berdasarkan struktur binary sempurna. Bonus hanya diberikan ke upline tertinggi per formasi.")
