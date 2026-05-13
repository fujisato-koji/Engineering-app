import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts

st.set_page_config(page_title="Requirement Architect", layout="wide")

st.title("🧩 ダイナミック要求デザイン")

# --- 1. データの初期化（型の不一致を防ぐため全て文字列で統一） ---
if 'tree_df' not in st.session_state:
    st.session_state.tree_df = pd.DataFrame([
        {"ID": "1", "Parent": "", "Name": "要求A"}
    ], dtype=str)

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
        "series": [{
            "type": "tree",
            "data": [tree_data],
            "top": "15%", "left": "10%", "bottom": "15%", "right": "20%",
            "symbolSize": 30,
            "initialTreeDepth": 10,
            "label": {"position": "top"},
            "leaves": {"label": {"position": "right"}},
            "expandAndCollapse": True,
        }]
    }
    
    # クリックイベント
    events = {"click": "function(params) { return params.data.id; }"}
    res = st_echarts(options, events=events, height="600px", key="tree_editor")
    
    # グラフクリック時の反応
    if res:
        new_id = str(res[0]) if isinstance(res, list) else str(res)
        if new_id != st.session_state.selected_id:
            st.session_state.selected_id = new_id
            st.rerun()

with col_edit:
    st.subheader("🛠️ ノード編集")
    
    # 最新のデータを取得
    df = st.session_state.tree_df
    all_ids = df['ID'].astype(str).tolist()
    
    # 現在の選択IDがリストに存在するか確認（なければルートに戻す）
    if st.session_state.selected_id not in all_ids:
        st.session_state.selected_id = all_ids[0]

    # バックアップ用の選択ボックス
    idx = all_ids.index(st.session_state.selected_id)
    choice = st.selectbox("ノードを直接選択:", all_ids, index=idx)
    if choice != st.session_state.selected_id:
        st.session_state.selected_id = choice
        st.rerun()

    st.divider()

    # 選択されている行を確実に抽出
    current_idx = df.index[df['ID'].astype(str) == st.session_state.selected_id].tolist()
    
    if current_idx:
        row_idx = current_idx[0]
        st.write(f"📍 ID: **{st.session_state.selected_id}** を編集中")
        
        # 名前変更
        new_name = st.text_input("ラベル名:", value=df.at[row_idx, 'Name'])
        if st.button("✅ 名前を保存"):
            st.session_state.tree_df.at[row_idx, 'Name'] = new_name
            st.success("保存しました")
            st.rerun()

        st.divider()
        
        # 子の追加
        if st.button("➕ この下に子を追加", use_container_width=True):
            parent_id = st.session_state.selected_id
            children_count = len(df[df['Parent'].astype(str) == parent_id])
            new_id = f"{parent_id}.{children_count + 1}"
            
            new_row = pd.DataFrame([{"ID": new_id, "Parent": parent_id, "Name": "新しい要素"}], dtype=str)
            st.session_state.tree_df = pd.concat([df, new_row], ignore_index=True)
            st.session_state.selected_id = new_id
            st.rerun()
            
        # 削除
        if st.session_state.selected_id != "1":
            if st.button("🗑️ 選択中のノードを削除", type="secondary", use_container_width=True):
                target = st.session_state.selected_id
                # 自分と、自分から始まるIDの子をすべて消す
                st.session_state.tree_df = df[~df['ID'].astype(str).str.startswith(target)]
                st.session_state.selected_id = "1"
                st.rerun()
    else:
        st.error("エラー: ノードが見つかりません。")
        if st.button("データをリセット"):
            del st.session_state.tree_df
            st.rerun()

# 診断用（問題がある時だけ開いてください）
with st.expander("🔍 診断ツール"):
    st.write(f"選択中のID: {st.session_state.selected_id}")
    st.write("現在のデータテーブル:")
    st.dataframe(st.session_state.tree_df)