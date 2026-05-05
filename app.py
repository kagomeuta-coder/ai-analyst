import streamlit as st
import google.generativeai as genai

# --- 画面の設定 ---
st.set_page_config(page_title="AI機関投資家アナリスト", layout="wide")
st.title("🚀 AI機関投資家セクター分析ツール")
st.caption("あなたが指定したセクターを、シニアアナリストの視点で徹底分析します。")

# --- 設定（APIキーの入力） ---
with st.sidebar:
    st.header("設定")
    api_key = st.text_input("Gemini API Keyを入力", type="password")
    st.info("APIキーは Google AI Studio から無料で取得できます。")

# --- メイン入力エリア ---
sector = st.text_input("分析したいセクターを入力（例：半導体製造装置、サイバーセキュリティ、メガバンク）")

# ★あなたの最強プロンプト★
PROMPT_TEMPLATE = """
あなたは米国株、日本株、債権コモディティに非常に詳しい、15年以上のキャリアを持つ機関投資家レベルのシニアアナリストです。
現在日付は2026/3/12です。最新の市場環境・業績・需給・株価水準を前提に可能な限り一次情報を元に回答してください。わからないことや不明確なことは無理に答えを出さず「わからない」または「仮説としては〜」とはっきり答えてください。

以下のセクターについて分析してください：【{sector_name}】

手順に従って厳密に進めてください。

【ステップ1】 そのセクターの直近3〜5年の中長期的な構造変化・成長ドライバー・リスク要因・景気感応度を300〜500字程度で整理してください。（円安/円高、AI需要、地政学、設備投資サイクル、中国依存度、米中摩擦なども含む）
【ステップ2】 米国株市場において、現在（2026年時点）最も注目すべき有力銘柄を4〜7社選び、選定理由を簡潔に列挙してください。（時価総額上位だけでなく、成長性・バリュエーション・テーマ性・需給の観点も考慮）
【ステップ3】 上記で挙げた銘柄群を以下の観点で比較表形式（Markdownテーブル）で比較してください。
・直近株価、時価総額
・PER（予）、PBR（予）、EV/EBITDA
・ROE、営業利益率（直近or予想）
・売上・営業利益成長率（直近決算＋来期・再来期予想）
・配当利回り・自社株買い動向
・主力製品/サービスの差別化ポイント
・中国・米国売上比率（概算でも可）
・株価チャート上の位置（25日・75日線、52週高値更新かどうかなど簡潔に）
【ステップ4】 現時点で最も投資魅力が高い順にランキングし、各順位の根拠を簡潔に述べてください。
【ステップ5】 このセクター全体として、今後3年のメインシナリオとメインシナリオが外れる場合のサブシナリオを2パターン挙げ、それぞれの場合にセクター全体として強気・弱気になる水準感（日経平均に対する相対パフォーマンス予想）を述べてください。

回答は客観的かつ数値根拠をできるだけ多く含め、感情的な表現は避けてください。
"""

# --- 実行ボタン ---
if st.button("分析を開始する"):
    if not api_key:
        st.error("左のメニューからAPIキーを入力してください。")
    elif not sector:
        st.warning("セクター名を入力してください。")
    else:
        try:
            # APIキーの設定
            genai.configure(api_key=api_key)
            
            # ★404エラー回避策：使えるモデルを自動検索する★
            available_model = None
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    if 'gemini' in m.name:
                        available_model = m.name
                        break # 最初に見つかったモデルを採用
            
            if not available_model:
                st.error("使えるAIモデルが見つかりませんでした。APIキーが間違っているか、制限されている可能性があります。")
            else:
                # 自動で見つけたモデルをセット
                model = genai.GenerativeModel(available_model)
                
                with st.spinner(f'シニアアナリストが分析中...（裏側で {available_model} が稼働中）'):
                    # プロンプトの組み立て
                    full_prompt = PROMPT_TEMPLATE.format(sector_name=sector)
                    
                    # AIへ送信
                    response = model.generate_content(full_prompt)
                    
                    # 結果の表示
                    st.success(f"「{sector}」の分析が完了しました！")
                    st.markdown(response.text)
                    
        except Exception as e:
            st.error(f"通信エラーが発生しました: {e}")