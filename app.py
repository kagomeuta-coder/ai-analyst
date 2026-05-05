import streamlit as st
import google.generativeai as genai
from datetime import datetime

# --- 画面の設定 ---
st.set_page_config(page_title="AI機関投資家アナリスト", layout="wide")
st.title("🚀 AI機関投資家アナリスト Pro")
today = datetime.now().strftime("%Y/%m/%d")
st.caption(f"現在日付: {today} | 最新の市場データに基づき、シニアアナリストが分析します。")

# --- 設定（APIキーの入力） ---
with st.sidebar:
    st.header("設定")
    api_key = st.text_input("Gemini API Keyを入力", type="password")
    st.info("APIキーを入力して分析を開始してください。")

# --- メイン入力エリア ---
sector = st.text_input("分析したいセクターを入力（例：半導体製造装置、生成AIインフラ、日本のメガバンク）")

# ★進化した最強プロンプト★
PROMPT_TEMPLATE = f"""
あなたは米国株、日本株、債権コモディティに非常に詳しい、15年以上のキャリアを持つ機関投資家レベルのシニアアナリストです。
現在日付は【{today}】です。最新の市場環境・業績・需給・株価水準を前提に、可能な限り一次情報を元に回答してください。
わからないことや不明確なことは無理に答えを出さず「わからない」または「仮説としては〜」とはっきり答えてください。

以下のセクターについて分析してください：【{{sector_name}}】

【ステップ1】 セクターの構造変化
直近3〜5年の中長期的な構造変化・成長ドライバー・リスク要因を300〜500字程度で整理してください。（為替、地政学、設備投資サイクル、米中摩擦を含む）

【ステップ2】 有力銘柄の選定
現在最も注目すべき有力銘柄を4〜7社選び、選定理由を列挙してください。

【ステップ3】 徹底比較（Markdownテーブル形式）
以下の観点で比較表を作成してください：
・直近株価、時価総額
・PER(予)、PBR(予)、ROE
・売上・営業利益成長率（来期・再来期予想含む）
・【追加】理論株価の試算（DCF法またはPERマルチプルに基づく妥当水準）
・【追加】現在の株価との乖離率（アップサイド/ダウンサイド％）
・主力製品の差別化ポイント

【ステップ4】 投資魅力ランキングとヒートマップ分析
投資魅力が高い順にランキングし、根拠を述べてください。
あわせて、セクター内の「資金循環ヒートマップ」を言語化し、現在どのサブセクターに最も強い買い圧力がかかっているか（例：前工程、後工程、検査装置など）を分析してください。

【ステップ5】 シナリオ分析
今後3年のメインシナリオと、それが外れる場合のサブシナリオを2パターン挙げ、それぞれの場合の水準感を述べてください。

【ステップ6】 目標株価とエントリー戦略
上位3銘柄について、12ヶ月後の「目標株価予想」を、強気・弱気・ベースの3シナリオで提示してください。各シナリオの発生確率（仮説）と、エントリーする際の推奨価格帯（押し目買い水準）を具体的に提言してください。

回答は客観的かつ数値根拠を多く含め、プロ向けのトーンで出力してください。
"""

# --- 実行ボタン ---
if st.button("プロフェッショナル分析を開始"):
    if not api_key:
        st.error("左のメニューからAPIキーを入力してください。")
    elif not sector:
        st.warning("セクター名を入力してください。")
    else:
        try:
            genai.configure(api_key=api_key)
            
            # 使えるモデルを自動検索
            available_model = None
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    if 'gemini' in m.name:
                        available_model = m.name
                        break
            
            if not available_model:
                st.error("モデルが見つかりません。")
            else:
                model = genai.GenerativeModel(available_model)
                
                with st.spinner(f'シニアアナリストが {today} 時点のデータを精査中...'):
                    full_prompt = PROMPT_TEMPLATE.format(sector_name=sector)
                    response = model.generate_content(full_prompt)
                    
                    st.success(f"「{sector}」の高度分析が完了しました。")
                    st.markdown(response.text)
                    
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")