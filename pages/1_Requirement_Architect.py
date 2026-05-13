import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts

st.set_page_config(page_title="Requirement Architect", layout="wide")

st.title("🧩 高速ダイナミック要求デザイン")

# --- 1. データの初期化 ---
if 'tree_df' not in st.session_state:
    st.session_state.tree_df = pd.DataFrame([
        {"ID": "1", "Parent": "", "Name": "要求A"}
    ], dtype=str)

if 'selected_id' not in st.session_state:
    st.session_state.selected_id = "1"

# --- 2. データの変換 (高速化版) ---
def get_tree_json(df, selected_id):
    nodes = {row['ID']: {
        "id": row['ID'], "name": row['Name'], "children": [],
        "itemStyle": {"color": "#ff4b4b" if row['ID'] == selected_id else "#6366f1"},
        "label": {"fontWeight": "bold" if row['ID'] == selected_id else "normal"}
    } for _, row in df.iterrows()}
    
    root = None
    for _, row in df.iterrows():
        node = nodes[row['ID']]
        if row['Parent'] and row['Parent'] in nodes:
            nodes[row['Parent']]["children"].append(node)
        else:
            root = node
    return root or {"name": "Empty"}

# --- 3. 画面レイアウト ---
col_graph, col_edit = st.columns([2, 1])

# --- グラフ表示部分 (Fragmentで独立させる) ---
@st.fragment
def show_graph():
    tree_data = get_tree_json(st.session_state.tree_df, st.session_state.selected_id)
    options = {
        "series": [{
            "type": "tree", "data": [tree_data],
            "top": "15%", "left": "10%", "bottom": "15%", "right": "20%",
            "symbolSize": 30, "initialTreeDepth": 10,
            "label": {"position": "top", "fontSize": 14},
            "leaves": {"label": {"position": "right"}},
            "expandAndCollapse": True,
            "animationDuration": 200, # アニメーションを高速化
        }]
    }
    
    # クリックイベントの取得
    res = st_echarts(options, events={"click": "function(p){return p.data.id;}"}, height="600px", key="tree_viz")
    
    if res and res != st.session_state.selected_id:
        st.session_state.selected_id = str(res)
        st.rerun()

with col_graph:
    show_graph()

# --- 編集部分 ---
with col_edit:
    st.subheader("🛠️ ノード編集")
    df = st.session_state.tree_df
    all_ids = df['ID'].tolist()
    
    # セレクトボックスでも即座に切り替え可能に
    sel_id = st.selectbox("対象を選択:", all_ids, index=all_ids.index(st.session_state.selected_id) if st.session_state.selected_id in all_ids else 0)
    if sel_id != st.session_state.selected_id:
        st.session_state.selected_id = sel_id
        st.rerun()

    st.divider()
    
    # 選択中のデータの取得
    idx = df.index[df['ID'] == st.session_state.selected_id].tolist()
    if idx:
        curr_idx = idx[0]
        with st.container(border=True):
            st.write(f"📍 ID: **{st.session_state.selected_id}**")
            new_name = st.text_input("ラベル名:", value=df.at[curr_idx, 'Name'], key=f"input_{st.session_state.selected_id}")
            
            if st.button("✅ 保存", use_container_width=True):
                st.session_state.tree_df.at[curr_idx, 'Name'] = new_name
                st.rerun()

        st.divider()
        
        if st.button("➕ 子を追加", use_container_width=True, type="primary"):
            c_count = len(df[df['Parent'] == st.session_state.selected_id])
            new_id = f"{st.session_state.selected_id}.{c_count + 1}"
            new_row = pd.DataFrame([{"ID": new_id, "Parent": st.session_state.selected_id, "Name": "新しい要素"}], dtype=str)
            st.session_state.tree_df = pd.concat([df, new_row], ignore_index=True)
            st.session_state.selected_id = new_id
            st.rerun()
            
        if st.session_state.selected_id != "1":
            if st.button("🗑️ 削除", use_container_width=True):
                st.session_state.tree_df = df[~df['ID'].str.startswith(st.session_state.selected_id)]
                st.session_state.selected_id = "1"
                st.rerun()