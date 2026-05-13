import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts

st.set_page_config(page_title="Requirement Architect", layout="wide")

st.title("🧩 ダイナミック要求デザイン（A, B, C設計）")
st.markdown("ノード（丸印）をクリックして選択し、名前の変更や子の追加を行ってください。")

# --- 1. データの初期化（すべて文字列型で固定） ---
if 'tree_df' not in st.session_state:
    init_data = pd.DataFrame([
        {"ID": "1", "Parent": "", "Name": "新しい要求"}
    ])
    st.session_state.tree_df = init_data.astype(str)

if 'selected_id' not in st.session_state:
    st.session_state.selected_id = "1"

# --- 2. 階層データの変換ロジック ---
def build_tree(df):
    # IDをキーにした辞書を作成
    nodes = {row['ID']: {"id": row['ID'], "name": row['Name'], "children": []} for _, row in df.iterrows()}
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
    tree_data = build_tree(st.session_state.tree_df)
    
    options = {
        "series": [{
            "type": "tree",
            "data": [tree_data],
            "top": "10%", "left": "10%", "bottom": "10%", "right": "20%",
            "symbolSize": 24, # 少し大きくして押しやすくしました
            "initialTreeDepth": 10,
            "label": {"position": "top", "fontSize": 14, "fontWeight": "bold"},
            "leaves": {"label": {"position": "right", "align": "left"}},
            "emphasis": {"focus": "descendant"},
            "expandAndCollapse": True,
        }]
    }
    
    # クリックイベントの設定
    events = {"click": "function(params) { return params.data.id; }"}
    res = st_echarts(options, events=events, height="600px", key="tree_editor")
    
    # 🌟 クリックされたら即座に session_state を更新して再描画
    if res:
        new_sel_id = str(res[0]) if isinstance(res, list) else str(res)
        if new_sel_id != st.session_state.selected_id:
            st.session_state.selected_id = new_sel_id
            st.rerun()

with col_edit:
    st.subheader("🛠️ ノード編集")
    
    # 現在の選択状況を確認
    sel_id = st.session_state.selected_id
    df = st.session_state.tree_df
    current_node = df[df['ID'] == sel_id]
    
    if not current_node.empty:
        # 編集フォームを st.form にまとめて反映を確実にします
        with st.form(key="edit_form"):
            st.write(f"📍 選択中のID: **{sel_id}**")
            new_name = st.text_input("ラベル名の変更:", value=current_node.iloc[0]['Name'])
            submit_name = st.form_submit_button("名前を確定")
            
            if submit_name:
                st.session_state.tree_df.loc[df['ID'] == sel_id, 'Name'] = new_name
                st.rerun()

        st.divider()
        
        # 子の追加セクション
        if st.button("➕ この下に子を追加", use_container_width=True):
            children = df[df['Parent'] == sel_id]
            new_id = f"{sel_id}.{len(children) + 1}"
            new_row = pd.DataFrame([{"ID": new_id, "Parent": sel_id, "Name": "新しい子ラベル"}]).astype(str)
            st.session_state.tree_df = pd.concat([df, new_row], ignore_index=True)
            # 追加した子をそのまま選択状態にする
            st.session_state.selected_id = new_id
            st.rerun()
            
        if sel_id != "1":
            if st.button("🗑️ このノードを削除", type="secondary", use_container_width=True):
                # 子要素も一緒に削除する（簡易的な実装）
                st.session_state.tree_df = df[~df['ID'].str.startswith(sel_id)]
                st.session_state.selected_id = "1"
                st.rerun()
    else:
        st.info("図の中の丸印をクリックして選択してください。")

# デバッグ用（不要になったら消してください）
with st.expander("📝 内部データの状態"):
    st.write(f"現在の選択ID: {st.session_state.selected_id}")
    st.table(st.session_state.tree_df)
