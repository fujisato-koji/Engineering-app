import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts

st.set_page_config(page_title="Requirement Architect", layout="wide")

st.title("🧩 ダイナミック要求デザイン（A, B, C設計）")
st.markdown("ノード（丸印）をクリックして選択し、名前の変更や子の追加を行ってください。")

# --- 1. データの初期化（最初は一つだけ） ---
if 'tree_df' not in st.session_state:
    st.session_state.tree_df = pd.DataFrame([
        {"ID": "1", "Parent": "", "Name": "新しい要求"}
    ])
if 'selected_id' not in st.session_state:
    st.session_state.selected_id = "1"

# --- 2. 階層データの変換ロジック ---
def build_tree(df):
    nodes = {row['ID']: {"id": row['ID'], "name": row['Name'], "children": []} for _, row in df.iterrows()}
    root_nodes = []
    for _, row in df.iterrows():
        node = nodes[row['ID']]
        if row['Parent'] and row['Parent'] in nodes:
            nodes[row['Parent']]["children"].append(node)
        else:
            root_nodes.append(node)
    return root_nodes[0] if root_nodes else {"name": "Empty"}

# --- 3. メインレイアウト ---
col_graph, col_edit = st.columns([2, 1])

with col_graph:
    tree_data = build_tree(st.session_state.tree_df)
    
    options = {
        "series": [{
            "type": "tree",
            "data": [tree_data],
            "top": "10%", "left": "10%", "bottom": "10%", "right": "20%",
            "symbolSize": 20,
            "initialTreeDepth": 10,
            "label": {"position": "top", "fontSize": 14, "fontWeight": "bold"},
            "leaves": {"label": {"position": "right", "align": "left"}},
            "emphasis": {"focus": "descendant"},
            "expandAndCollapse": True,
        }]
    }
    
    # クリックイベントを取得
    events = {"click": "function(params) { return params.data.id; }"}
    clicked_id = st_echarts(options, events=events, height="600px", key="tree_editor")
    
    if clicked_id:
        st.session_state.selected_id = clicked_id

with col_edit:
    st.subheader("🛠️ ノード編集")
    
    # 選択されたノードの情報を取得
    sel_id = st.session_state.selected_id
    current_node = st.session_state.tree_df[st.session_state.tree_df['ID'] == sel_id]
    
    if not current_node.empty:
        st.success(f"現在選択中: ID [{sel_id}]")
        
        # 名前を変更
        new_name = st.text_input("名前を変更:", value=current_node.iloc[0]['Name'])
        if st.button("✅ 名前を反映"):
            st.session_state.tree_df.loc[st.session_state.tree_df['ID'] == sel_id, 'Name'] = new_name
            st.rerun()
            
        st.divider()
        
        # 子を追加
        if st.button("➕ この下に子を追加"):
            new_id = f"{sel_id}.{len(st.session_state.tree_df[st.session_state.tree_df['Parent'] == sel_id]) + 1}"
            new_row = {"ID": new_id, "Parent": sel_id, "Name": "新しい子ラベル"}
            st.session_state.tree_df = pd.concat([st.session_state.tree_df, pd.DataFrame([new_row])], ignore_index=True)
            st.rerun()
            
        # 削除（ルート以外）
        if sel_id != "1":
            if st.button("🗑️ このノードを削除", type="secondary"):
                st.session_state.tree_df = st.session_state.tree_df[st.session_state.tree_df['ID'] != sel_id]
                st.session_state.selected_id = "1"
                st.rerun()
    else:
        st.info("図の中の丸印をクリックして選択してください。")

# デバッグ用：現在のデータ構造を表示
with st.expander("📝 内部データ構造の確認（Pandas DataFrame）"):
    st.write(st.session_state.tree_df)