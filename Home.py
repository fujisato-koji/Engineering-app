import streamlit as st

# ページ全体の基本設定
st.set_page_config(
    page_title="統合エンジニアリングポータル",
    page_icon="🚀",
    layout="wide"
)

# ヘッダー部分
st.title("🚀 統合エンジニアリングポータル")
st.markdown("---")

st.markdown("""
### 概要
本ポータルは、システム設計開発・保守運用に必要な各種エンジニアリングツールを集約したダッシュボードです。
左側のサイドバーから、使用したいツールを選択してください。

---
""")

# ツール群の紹介（カード風レイアウト）
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 予知保全・信頼性工学")
    st.info("""
    **極低温バルブ 寿命予測ダッシュボード**
    *   ワイブル分布を用いた生存時間解析
    *   稼働データからの故障モード自動判定
    *   最適な交換サイクルの算出
    """)

with col2:
    st.subheader("🔥 今後追加予定のツール")
    st.warning("""
    *   **安全距離シミュレータ** (Kingery-Bulmash式)
    *   **極低温配管 熱収縮計算ツール**
    *   **風況データ (ERA5) 解析ダッシュボード**
    """)

st.markdown("---")
st.caption("© 2026 Engineering Portal - Confidential")
