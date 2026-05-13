import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts

st.set_page_config(page_title="Requirement Architect", layout="wide")

st.title("🧩 ダイナミック要求デザイン（A, B, C設計）")
st.info("💡 図の中の丸印を **【ダブルクリック】** すると、そのノードを選択・編集できます。")

# --- 1. データの初期化 ---
if 'tree_df' not in st.session_state:
    st.session_state.tree_df = pd.DataFrame([
        {"ID": "1", "Parent": "", "Name": "要求A"}
    ]).astype(str)

if 'selected_id' not in st.session_state:
    st.session_state.selected_id = "1"

# --- 2. 階層データの変換ロジック ---
def build_tree(df, selected_id):
    nodes = {}
    for _, row in df.iterrows():
        is_selected = (row['ID'] == selected_id)
        # 選択されているノードの色を変える設定を追加
        nodes[row['ID']] = {
            "id": row['ID'], 
            "name": row['Name'], 
            "children": [],
            "itemStyle": {"color": "#ff4b4b" if is_selected else "#6366f1"}, # 選択中なら赤
            "label": {"fontWeight": "bold" if is_selected else "normal"}
        }
    
    root_nodes = []
    for _, row in df.iterrows():
        node = nodes[row['ID']]
        p_id = row['Parent']
        if p_id and p_id in nodes:
            nodes[p_id]["children"].append(node)
        else:
            root_nodes.append(node)
    return root_nodes[0] if root_nodes else {"name": "Empty"}

# --- 3. メインレイアウト ---
col_graph, col_edit = st.columns([2, 1])

with col_graph:
    tree_data = build_tree(st.session_state.tree_df, st.session_state.selected_id)
    
    options = {
        "series": [{
            "type": "tree",
            "data": [tree_data],
            "top": "10%", "left": "10%", "bottom": "10%", "right": "20%",
            "symbolSize": 26,
            "initialTreeDepth": 10,
            "label": {"position": "top", "fontSize": 14},
            "leaves": {"label": {"position": "right", "align": "left"}},
            "expandAndCollapse": True,
            "animationDuration": 300,
        }]
    }
    
    # 🌟 ここで 'dblclick' (ダブルクリック) イベントを指定します
    events = {"dblclick": "function(params) { return params.data.id; }"}
    res = st_echarts(options, events=events, height="600px", key="tree_editor")
    
    # ダブルクリックされた時の処理
    if res:
        new_sel_id = str(res[0]) if isinstance(res, list) else str(res)
        if new_sel_id != st.session_state.selected_id:
            st.session_state.selected_id = new_sel_id
            st.rerun()

with col_edit:
    st.subheader("🛠️ ノード編集")
    
    sel_id = st.session_state.selected_id
    df = st.session_state.tree_df
    current_node = df[df['ID'] == sel_id]
    
    if not current_node.empty:
        with st.form(key="edit_form"):
            st.write(f"📍 選択中のID: **{sel_id}**")
            new_name = st.text_input("ラベル名の変更:", value=current_node.iloc[0]['Name'])
            if st.form_submit_button("✅ 名前を確定"):
                st.session_state.tree_df.loc[df['ID'] == sel_id, 'Name'] = new_name
                st.rerun()

        st.divider()
        
        if st.button("➕ この下に子を追加", use_container_width=True):
            children = df[df['Parent'] == sel_id]
            new_id = f"{sel_id}.{len(children) + 1}"
            new_row = pd.DataFrame([{"ID": new_id, "Parent": sel_id, "Name": "新しい子"}]).astype(str)
            st.session_state.tree_df = pd.concat([df, new_row], ignore_index=True)
            st.session_state.selected_id = new_id # 追加した子をそのまま選択
            st.rerun()
            
        if sel_id != "1":
            if st.button("🗑️ このノードを削除", type="secondary", use_container_width=True):
                st.session_state.tree_df = df[~df['ID'].str.startswith(sel_id)]
                st.session_state.selected_id = "1"
                st.rerun()
    else:
        st.info("図の丸印をダブルクリックしてください。")
