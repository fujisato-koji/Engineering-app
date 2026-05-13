import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts

st.set_page_config(page_title="Requirement Architect", layout="wide")

st.title("🧩 ダイナミック要求デザイン（A, B, C設計）")

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
        sid = str(row['ID'])
        is_selected = (sid == str(selected_id))
        nodes[sid] = {
            "id": sid, 
            "name": row['Name'], 
            "children": [],
            "itemStyle": {"color": "#ff4b4b" if is_selected else "#6366f1"},
            "label": {"fontWeight": "bold" if is_selected else "normal", "fontSize": 14}
        }
    
    root_nodes = []
    for _, row in df.iterrows():
        node = nodes[str(row['ID'])]
        p_id = str(row['Parent'])
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
        "tooltip": {"trigger": "item"},
        "series": [{
            "type": "tree",
            "data": [tree_data],
            "top": "15%", "left": "10%", "bottom": "15%", "right": "20%",
            "symbolSize": 28,
            "initialTreeDepth": 10,
            "label": {"position": "top"},
            "leaves": {"label": {"position": "right"}},
            "expandAndCollapse": True,
            "animationDuration": 400,
        }]
    }
    
    # 最も安定している 'click' を使用
    events = {"click": "function(params) { return params.data.id; }"}
    res = st_echarts(options, events=events, height="600px", key="tree_editor")
    
    # グラフがクリックされた場合の処理
    if res:
        new_id = str(res[0]) if isinstance(res, list) else str(res)
        if new_id != st.session_state.selected_id:
            st.session_state.selected_id = new_id
            st.rerun()

with col_edit:
    st.subheader("🛠️ ノード編集")
    
    df = st.session_state.tree_df
    
    # 【バックアップ機能】グラフが反応しないとき用のリスト選択
    id_list = df['ID'].tolist()
    # 現在の選択をリストのデフォルトにする
    try:
        default_idx = id_list.index(st.session_state.selected_id)
    except:
        default_idx = 0
        
    manual_sel = st.selectbox("ノードを選択（グラフ反応なし時の予備）:", id_list, index=default_idx)
    if manual_sel != st.session_state.selected_id:
        st.session_state.selected_id = manual_sel
        st.rerun()

    st.divider()

    # 選択中のデータの編集
    sel_id = st.session_state.selected_id
    current_node = df[df['ID'] == sel_id]
    
    if not current_node.empty:
        with st.form(key="edit_form"):
            st.write(f"📍 ID: **{sel_id}** を編集権限")
            new_name = st.text_input("ラベル名:", value=current_node.iloc[0]['Name'])
            if st.form_submit_button("✅ 名前を確定"):
                st.session_state.tree_df.loc[df['ID'] == sel_id, 'Name'] = new_name
                st.rerun()

        st.divider()
        
        if st.button("➕ この下に子を追加", use_container_width=True):
            children = df[df['Parent'] == sel_id]
            new_id = f"{sel_id}.{len(children) + 1}"
            new_row = pd.DataFrame([{"ID": new_id, "Parent": sel_id, "Name": "新しい要素"}]).astype(str)
            st.session_state.tree_df = pd.concat([df, new_row], ignore_index=True)
            st.session_state.selected_id = new_id
            st.rerun()
            
        if sel_id != "1":
            if st.button("🗑️ このノードを削除", type="secondary", use_container_width=True):
                st.session_state.tree_df = df[~df['ID'].str.startswith(sel_id)]
                st.session_state.selected_id = "1"
                st.rerun()