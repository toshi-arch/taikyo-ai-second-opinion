import streamlit as st
import google.generativeai as genai
import os
import json
import tempfile
from dotenv import load_dotenv
from prompts import SYSTEM_PROMPT


# ------------------------
# 環境変数
# ------------------------

load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)


# ------------------------
# ページ設定
# ------------------------

st.set_page_config(
    page_title="退去費用セカンドオピニオンAI",
    page_icon="🏠",
    layout="centered"
)


# ------------------------
# サイドバー
# ------------------------

with st.sidebar:
    st.title("⚙️ 設定")
    st.markdown("PoC検証用の設定です")
    selected_model = st.selectbox(
        "AIモデルを選択",
        [
            "gemini-3.1-pro-preview",
            "gemini-3.1-flash-lite-preview"
        ],
        help="""
            flash:
            高速・低コスト
            pro:
            高精度
            表の読み取りに強い
            """
    )
    st.markdown("---")
    st.caption("APIキーは .env から読み込まれます")


# ------------------------
# Gemini用関数
# ------------------------
def upload_pdf_to_gemini(uploaded_file):
    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    ) as tmp_file:
        tmp_file.write(
            uploaded_file.getvalue()
        )
        tmp_path = tmp_file.name
        
    gemini_file = genai.upload_file(
        path=tmp_path,
        mime_type="application/pdf"
    )
    os.remove(tmp_path)

    return gemini_file

# ------------------------
# UI
# ------------------------

st.title("🏠 退去費用セカンドオピニオンAI")
st.markdown("""

退去費用の見積書が
国土交通省ガイドラインに照らして
妥当かどうかの参考情報を表示します
""")

# ------------------------
# 入力フォーム
# ------------------------
with st.form("form"):
    st.subheader("入居期間")
    col1, col2 = st.columns(2)
    with col1:
        years = st.number_input(
            "年",
            min_value=0,
            max_value=50,
            value=2
        )
    with col2:
        months = st.number_input(
            "ヶ月",
            min_value=0,
            max_value=11,
            value=0
        )
    st.subheader("書類アップロード")
    estimate_pdf = st.file_uploader(
        "退去費用見積書（必須）",
        type=["pdf"]
    )
    contract_pdf = st.file_uploader(
        "契約書（任意）",
        type=["pdf"]
    )

    submitted = st.form_submit_button(
        "AIでチェック",
        type="primary"
    )

# ------------------------
# 実行
# ------------------------

if submitted:
    if not api_key:
        st.error(
            ".env に GEMINI_API_KEY を設定してください"
        )
    elif not estimate_pdf:
        st.error(
            "見積書PDFをアップロードしてください"
        )
    else:
        with st.spinner("分析中..."):
            try:
                # 入力まとめ
                contents = [
                    f"入居期間: {years}年 {months}ヶ月"
                ]
                # 見積書
                estimate_file = upload_pdf_to_gemini(
                    estimate_pdf
                )
                contents.append(
                    "退去費用見積書"
                )
                contents.append(
                    estimate_file
                )
                # 契約書
                if contract_pdf:
                    contract_file = upload_pdf_to_gemini(
                        contract_pdf
                    )
                    contents.append(
                        "契約書"
                    )
                    contents.append(
                        contract_file
                    )
                else:
                    contents.append(
                        "契約書: 不明"
                    )
                # モデル
                model = genai.GenerativeModel(
                    model_name=selected_model,
                    system_instruction=SYSTEM_PROMPT,
                    generation_config=genai.GenerationConfig(
                        response_mime_type="application/json",
                        temperature=1.0
                    )
                )
                response = model.generate_content(
                    contents
                )
                # JSON変換
                raw_text = response.text.strip()
                result = json.loads(
                    raw_text
                )
                
                # ------------------------
                # 表示
                # ------------------------
                st.success("分析完了")
                # summary
                st.header("総合コメント")
                st.info(
                    result.get(
                        "summary",
                        "なし"
                    )
                )
                # evaluations
                st.header("項目別チェック")
                evaluations = result.get(
                    "evaluations",
                    []
                )
                if not evaluations:
                    st.warning(
                        "項目が検出されませんでした"
                    )
                for item in evaluations:
                    title = item.get(
                        "category",
                        "項目"
                    )
                    with st.expander(title):
                        st.markdown("### 請求内容")
                        st.write(
                            item.get(
                                "billed_amount",
                                "不明"
                            )
                        )
                        st.markdown("### ガイドライン上の考え方")
                        st.write(
                            item.get(
                                "guideline_principle",
                                "不明"
                            )
                        )
                        st.markdown("### 特約の確認結果")
                        st.write(
                            item.get(
                                "special_contract_check",
                                "不明"
                            )
                        )
                        st.markdown("### アドバイス")
                        st.success(
                            item.get(
                                "advice",
                                "なし"
                            )
                        )
                # disclaimer
                st.header("注意事項")
                st.caption(
                    result.get(
                        "disclaimer",
                        ""
                    )
                )
                # debug
                with st.expander("JSON"):
                    st.json(result)
            except Exception as e:
                st.error("エラーが発生しました")
                st.exception(e)