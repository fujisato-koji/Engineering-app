import streamlit as st
import pandas as pd
import numpy as np
from lifelines import WeibullFitter
import plotly.graph_objects as go

# --- アプリの基本設定 ---
st.set_page_config(page_title="バルブ寿命予測API", layout="wide")
st.title("極低温バルブ 予知保全ダッシュボード")

# --- サイドバー：設定 ---
st.sidebar.header("パラメータ設定")
target_reliability = st.sidebar.slider("目標の安全基準（生存確率）", 0.80, 0.99, 0.95, 0.01)

# --- メイン：データ入力UI ---
st.subheader("1. 稼働データの入力")
st.write("現場の数値を直接入力するか、過去のCSVをアップロードしてください。")

input_method = st.radio("入力方法を選択:", ("直接入力（Excelライク）", "CSVアップロード"), horizontal=True)

df = None

if input_method == "直接入力（Excelライク）":
    st.info("💡 表のセルをクリックして直接数値を書き換えられます。一番下の行に入力すると新しい行が自動追加されます。")
    default_data = pd.DataFrame({
        "component_id": ["V-001", "V-002", "V-003", "V-004", "V-005"],
        "duration": [4250, 3000, 4500, 1500, 3800],
        "event_status": [1, 0, 1, 0, 1] 
    })
    df = st.data_editor(default_data, num_rows="dynamic", use_container_width=True)

else:
    uploaded_file = st.file_uploader("CSVファイルをアップロード (列: component_id, duration, event_status)", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("CSVファイルをアップロードしてください。")

# --- 解析の実行 ---
st.subheader("2. 寿命予測の実行")
if df is not None and st.button("🚀 このデータで解析を実行", type="primary"):
    try: # ★ここからエラー対策ブロック開始
        # --- 裏側のコアエンジン処理 ---
        wf = WeibullFitter()
        wf.fit(durations=df['duration'], event_observed=df['event_status'])

        m = wf.rho_
        eta = wf.lambda_
        
        if m < 1.0: failure_mode = "初期故障 (Early Failure)"
        elif 1.0 <= m < 1.2: failure_mode = "偶発故障 (Random Failure)"
        else: failure_mode = "摩耗故障 (Wear-out)"

        optimal_time = eta * ((-np.log(target_reliability)) ** (1/m))

        # --- 結果の表示 ---
        st.success("✅ 解析が完了しました！")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("形状パラメータ (m)", f"{m:.2f}", failure_mode)
        col2.metric("限界寿命の目安 (η)", f"{eta:.0f} 回")
        col3.metric("目標安全基準", f"{target_reliability*100:.0f} %")
        col4.metric("最適交換サイクル", f"{optimal_time:.0f} 回", "この基準を厳守", delta_color="inverse")

        # --- 稼働中の部品アラート表 ---
        st.subheader("🚨 稼働中の部品ステータス")
        active_components = df[df['event_status'] == 0].copy()
        
        if not active_components.empty:
            active_components['現在の生存確率'] = np.exp(-((active_components['duration'] / eta) ** m))
            active_components['残り寿命'] = optimal_time - active_components['duration']
            
            def get_status(remaining):
                if remaining > 500: return "🟢 SAFE"
                elif remaining > 0: return "🟡 WARNING (交換準備)"
                else: return "🔴 CRITICAL (直ちに交換)"

            active_components['ステータス'] = active_components['残り寿命'].apply(get_status)
            
            display_df = active_components[['component_id', 'duration', '現在の生存確率', '残り寿命', 'ステータス']].copy()
            display_df['現在の生存確率'] = (display_df['現在の生存確率'] * 100).round(1).astype(str) + " %"
            display_df['残り寿命'] = display_df['残り寿命'].round(0).astype(int).astype(str) + " 回"
            
            st.dataframe(display_df, use_container_width=True)
        else:
            st.info("現在稼働中の部品（event_status = 0）はありません。")

        # --- 生存確率カーブのグラフ描画 (Plotly版) ---
        st.subheader("📈 生存確率カーブ")
        
        max_time = max(eta * 1.5, df['duration'].max() * 1.2)
        t = np.linspace(0.1, max_time, 200)
        R = np.exp(-((t / eta) ** m))
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=t, y=R, 
            mode='lines', 
            name='生存確率',
            line=dict(color='#1f77b4', width=3)
        ))
        
        fig.add_hline(
            y=target_reliability, 
            line_dash="dash", line_color="#d62728",
            annotation_text=f"安全基準 ({target_reliability*100:.0f}%)", 
            annotation_position="bottom right"
        )
        
        fig.add_vline(
            x=optimal_time, 
            line_dash="dot", line_color="#ff7f0e",
            annotation_text=f"最適交換 ({optimal_time:.0f}回)", 
            annotation_position="top right"
        )
        
        fig.update_layout(
            xaxis_title="稼働サイクル (回)",
            yaxis_title="生存確率",
            yaxis_range=[0, 1.05],
            hovermode="x unified",
            margin=dict(l=0, r=0, t=30, b=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e: # ★ここが消えてしまっていた部分です！
        st.error(f"解析エラーが発生しました。\n\n詳細: {e}\n\n※入力データに『1つ以上の故障データ（event_status=1）』が含まれているか確認してください。")