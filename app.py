import streamlit as st
import google.generativeai as genai
from datetime import datetime

# --- 画面の設定 ---
st.set_page_config(page_title="AI機関投資家アナリスト Pro", layout="wide")
st.title("🚀 AI機関投資家アナリスト Pro (Enhanced)")
today = datetime.now().strftime("%Y/%m/%d")
st.caption(f"実行日: {today} | バリューチェーンを含めた広範なセクター分析を実施します。")

# --- 設定 ---
with st.sidebar:
    st.header("設定")
    api_key = st.text_input("Gemini API Keyを入力", type="password")
    st.info("分析にはAPIキーが必要です。")

sector = st.text_input("分析セクターを入力（例：半導体、サイバーセキュリティ）")

# ★さらに進化したプロンプト★
PROMPT_TEMPLATE = f"""
あなたは米国株、日本株、債権コモディティに非常に詳しい、15年以上のキャリアを持つ機関投資家レベルのシニアアナリストです。
現在日付は【{today}】です。最新の市場環境・業績・需給・株価水準を前提に、可能な限り一次情報を元に回答してください。

以下のセクターについて分析してください：【{{sector_name}}】
※判定の幅を広めに取り、関連するバリューチェーン（川上から川下まで）や、上場直後の銘柄、ADR銘柄も含めて総合的に判断してください。

【ステップ1】 セクターの中長期的な構造変化
直近3〜5年の成長ドライバー、景気感応度、為替、地政学、米中摩擦などを300〜500字で整理。

【ステップ2】 有力銘柄の選定（4〜7社）
米国市場（ADR含む）を中心に、時価総額・成長性・テーマ性から注目銘柄を選定。キオクシアのような上場済み注目銘柄も対象に含めること。

【ステップ3】 徹底比較（Markdownテーブル）
・株価、時価総額、PER(予)、PBR(予)、ROE
・売上/営業益成長率（来期・再来期予想）
・【理論株価の試算】（DCF法またはマルチプルに基づく妥当水準）
・【乖離率】現在の株価との差（％）
・主要製品の差別化ポイントとチャート上の位置（25/75日線など）

【ステップ4】 投資魅力ランキングと「資金循環ヒートマップ」
魅力度順にランク付けし根拠を詳述。
また、セクター内のどの領域（例：メモリ、ロジック、装置、素材など）に資金が集中しているか、ヒートマップ的な視点で分析せよ。

【ステップ5】 シナリオ分析（今後3年）
メインシナリオ＋サブシナリオ2種。相対パフォーマンス予想を含む。

【ステップ6】 目標株価予想とエントリー戦略
上位3銘柄の12ヶ月後目標株価（強気・弱気・ベースの3案）。発生確率と推奨エントリー価格帯を具体的に提示せよ。

回答は客観的な数値を重視し、プロフェッショナルなトーンで出力してください。
"""

# --- 実行ボタン ---
if st.button("プロフェッショナル分析を開始"):
    if not api_key:
        st.error("APIキーを入力してください。")
    elif not sector:
        st.warning("セクター名を入力してください。")
    else:
        try:
            genai.configure(api_key=api_key)
            available_model = next((m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods and 'gemini' in m.name), None)
            
            if not available_model:
                st.error("利用可能なモデルが見つかりません。")
            else:
                model = genai.GenerativeModel(available_model)
                with st.spinner(f'シニアアナリストが {today} 時点のバリューチェーンを精査中...'):
                    response = model.generate_content(PROMPT_TEMPLATE.format(sector_name=sector))
                    st.success(f"「{sector}」の高度分析が完了しました。")
                    st.markdown(response.text)
        except Exception as e:
            st.error(f"エラー: {e}")