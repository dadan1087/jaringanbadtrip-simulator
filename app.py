import streamlit as st
import pandas as pd
import graphviz

st.set_page_config(page_title="MLM Binary Network Simulator", layout="wide")
st.title("MLM Binary Network Simulator")

# --- Input Section ---
st.sidebar.header("Input Member Details")
belanja = st.sidebar.number_input("Belanja (Rp)", min_value=0, step=100000, value=2000000)
minggu = st.sidebar.slider("Simulasi Pertumbuhan (Level)", 1, 22, 6)

# --- Bonus Settings ---
st.sidebar.header("🎯 Setting Alokasi Bonus")
alokasi_belanja = st.sidebar.number_input("Alokasi dari Belanja (Rp)", min_value=0, step=100000, value=1000000)
bonus_green = st.sidebar.number_input("Bonus GREEN", min_value=0, step=100000, value=5000000)
bonus_silver = st.sidebar.number_input("Bonus SILVER", min_value=0, step=100000, value=10000000)
bonus_red = st.sidebar.number_input("Bonus RED", min_value=0, step=100000, value=50000000)

# --- Data Structures ---
class Member:
    def __init__(self, id, parent_id=None, level=0):
        self.id = id
        self.parent_id = parent_id
        self.left = None
        self.right = None
        self.level = level
        self.status = "-"
        self.bonus = 0
        self.green_downlines = 0
        self.silver_downlines = 0

# --- Binary Tree Generator ---
def build_binary_tree(levels):
    members = {}
    members[0] = Member(0, None, 0)
    queue = [members[0]]
    next_id = 1
    while queue:
        current = queue.pop(0)
        if current.level >= levels:
            continue
        # Add left child
        members[next_id] = Member(next_id, current.id, current.level + 1)
        current.left = next_id
        queue.append(members[next_id])
        next_id += 1
        # Add right child
        members[next_id] = Member(next_id, current.id, current.level + 1)
        current.right = next_id
        queue.append(members[next_id])
        next_id += 1
    return members

# --- Subtree size calculator ---
def count_subtree_members(members, member_id):
    count = 1
    member = members[member_id]
    for child_id in [member.left, member.right]:
        if child_id is not None:
            count += count_subtree_members(members, child_id)
    return count

# --- Status Evaluation ---
def evaluate_statuses(members):
    def count_green_silver_downlines(member_id):
        member = members[member_id]
        green = silver = 0
        children = [member.left, member.right]
        for cid in children:
            if cid is not None:
                child = members[cid]
                if child.status == "Green":
                    green += 1
                if child.status == "Silver":
                    silver += 1
                c_green, c_silver = count_green_silver_downlines(cid)
                green += c_green
                silver += c_silver
        return green, silver

    # Step 1: Assign Green
    for member_id in sorted(members.keys(), reverse=True):
        member = members[member_id]
        subtree_size = count_subtree_members(members, member_id)
        if subtree_size == 15:
            member.status = "Green"
            member.bonus = bonus_green

    # Step 2: Assign Silver and Red based on counted downlines
    for member in members.values():
        member.green_downlines, member.silver_downlines = count_green_silver_downlines(member.id)

    for member in members.values():
        if member.status == "Green" and member.green_downlines >= 14:
            member.status = "Silver"
            member.bonus = bonus_silver
        if member.status == "Silver" and member.silver_downlines >= 14:
            member.status = "Red"
            member.bonus = bonus_red

# --- Visual Binary Tree ---
def draw_binary_tree(members, max_level):
    dot = graphviz.Digraph()
    for member_id, member in members.items():
        if member.level > max_level:
            continue
        color = "white"
        if member.status == "Green":
            color = "lightgreen"
        elif member.status == "Silver":
            color = "skyblue"
        elif member.status == "Red":
            color = "red"
        dot.node(str(member_id), f"#{member_id}\n{member.status}", style="filled", fillcolor=color)
        if member.left is not None:
            dot.edge(str(member_id), str(member.left))
        if member.right is not None:
            dot.edge(str(member_id), str(member.right))
    return dot

# --- Simulate ---
members = build_binary_tree(minggu)
evaluate_statuses(members)

# --- Result Output ---
total_members = len(members)
bonus_total_green = sum(m.bonus for m in members.values() if m.status == "Green")
bonus_total_silver = sum(m.bonus for m in members.values() if m.status == "Silver")
bonus_total_red = sum(m.bonus for m in members.values() if m.status == "Red")

st.subheader("📊 Ringkasan Simulasi")
st.markdown(f"**Total Member:** {total_members}")
st.markdown(f"**Status Member 0:** {members[0].status}")
st.markdown(f"**Bonus Member 0:** Rp{members[0].bonus:,.0f}")

# --- Bonus Alokasi Table ---
st.subheader("💰 Simulasi Cashflow dan Bonus Alokasi")
bonus_data = {
    "Kategori": ["GREEN", "SILVER", "RED"],
    "Jumlah (Rp)": [bonus_total_green, bonus_total_silver, bonus_total_red],
    "Jumlah Member": [
        sum(1 for m in members.values() if m.status == "Green"),
        sum(1 for m in members.values() if m.status == "Silver"),
        sum(1 for m in members.values() if m.status == "Red")
    ]
}
st.dataframe(pd.DataFrame(bonus_data), use_container_width=True)

# --- Struktur Binary Tree ---
st.subheader("🌲 Struktur Jaringan Binary")
st.graphviz_chart(draw_binary_tree(members, max_level=minggu))

# --- Pilih Member untuk Lihat Detail ---
st.subheader("🔍 Lihat Detail Member")
selected_id = st.number_input("Masukkan nomor member:", min_value=0, max_value=total_members - 1, step=1)
selected_member = members[selected_id]

st.markdown(f"**Status:** {selected_member.status}")
st.markdown(f"**Bonus:** Rp{selected_member.bonus:,.0f}")
st.markdown(f"**Green Downlines:** {selected_member.green_downlines}")
st.markdown(f"**Silver Downlines:** {selected_member.silver_downlines}")

st.caption("Simulasi ini berdasarkan pertumbuhan binary sempurna. Hasil aktual bisa berbeda tergantung strategi dan struktur jaringan.")
