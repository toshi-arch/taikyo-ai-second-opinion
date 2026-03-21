# app.py
import streamlit as st
import os

# ページ設定
st.set_page_config(page_title="退去費用セカンドオピニオンAI", page_icon="🏠", layout="centered")

# サイドバー（モデル選択）
with st.sidebar:
    st.title("⚙️ 設定")
    st.markdown("PoC検証用の設定です。")
    selected_model = st.selectbox(
        "AIモデルを選択", 
        ["gemini-1.5-flash", "gemini-1.5-pro"],
        help="flashは高速・低コスト、proは高精度（複雑な表の読み取りに強い）です。"
    )
    st.markdown("---")
    st.markdown("※APIキーは `.env` ファイルから自動で読み込まれます。")

# メイン画面ヘッダー
st.title("🏠 退去費用セカンドオピニオンAI")
st.markdown("""
退去費用の見積書が、国土交通省の「原状回復ガイドライン」に沿っているかAIがチェックします。
まずは以下の情報を入力・アップロードしてください。
""")

# 入力フォーム
with st.form("input_form"):
    st.subheader("1. 入居期間を入力")
    col1, col2 = st.columns(2)
    with col1:
        years = st.number_input("年", min_value=0, max_value=50, value=2)
    with col2:
        months = st.number_input("ヶ月", min_value=0, max_value=11, value=0)

    st.subheader("2. 書類のアップロード")
    st.info("PDF形式のファイルをアップロードしてください。")
    
    estimate_pdf = st.file_uploader("📄 退去費用見積書 【必須】", type=["pdf"])
    contract_pdf = st.file_uploader("📄 賃貸借契約書（特約事項） 【任意】", type=["pdf"])

    # 送信ボタン
    submit_btn = st.form_submit_button("AIでチェック開始", type="primary")


# ボタンが押された時の処理（今は確認用のモックアップ）
if submit_btn:
    if not estimate_pdf:
        st.error("⚠️ 退去費用見積書のPDFをアップロードしてください。")
    else:
        st.success("✅ ファイルの読み込みに成功しました！")
        st.write(f"**入居期間:** {years}年 {months}ヶ月")
        st.write(f"**選択モデル:** {selected_model}")
        if contract_pdf:
            st.write("**特約事項のファイル:** あり")
        else:
            st.write("**特約事項のファイル:** なし")
        
        st.info("次のステップで、ここにGemini APIの処理を組み込みます！")