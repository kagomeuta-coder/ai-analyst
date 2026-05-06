import streamlit as st
import google.generativeai as genai
from google.generativeai import protos  # ← ★最終奥義のパーツです
from datetime import datetime

# --- 画面の設定 ---
st.set_page_config(page_title="AI機関投資家アナリスト Pro", layout="wide")
st.title("🚀 AI機関投資家アナリスト Pro (Web検索対応版)")
today = datetime.now().strftime("%Y/%m/%d")
st.caption(f"実行日: {today} | リアルタイム検索（Search Grounding）を活用し、最新情報で分析します。")

# --- 設定メニュー ---
with st.sidebar:
    st.header("⚙️ 設定")
    api_key = st.text_input("Gemini API Keyを入力", type="password")
    st.info("分析を開始するにはAPIキーが必要です。")

# --- メイン入力エリア ---
sector = st.text_input("分析したいセクターを入力（例：日本の半導体、サイバーセキュリティ）")

# ★統合・進化した最強プロンプト★
PROMPT_TEMPLATE = f"""
あなたは米国株、日本株、債権コモディティに非常に詳しい、15年以上のキャリアを持つ機関投資家レベルのシニアアナリストです。
現在日付は【{today}】です。最新の市場環境・業績・需給・株価水準を前提に、可能な限り一次情報を元に回答してください。
わからないことや不明確なことは無理に答えを出さず「わからない」または「仮説としては〜」とはっきり答えてください。

以下のセクターについて分析してください：【{{sector_name}}】

【ステップ1：マクロ環境と構造変化】
そのセクターの直近3〜5年の中長期的な構造変化・成長ドライバー・リスク要因・景気感応度を300〜500字程度で整理してください。

【ステップ2：有力銘柄の選定】
指定された市場において、現在最も注目すべき有力銘柄を4〜7社選び、選定理由を簡潔に列挙してください。
※時価総額上位だけでなく、成長性・バリュエーション・テーマ性・需給の観点も考慮してください。
※セクター判定の幅を広めに取り、バリューチェーン全体や、ADR銘柄、上場直後の銘柄（キオクシア等）も柔軟に対象に含めてください。

【ステップ3：徹底比較テーブル】
上記で挙げた銘柄群を以下の観点で比較表形式（Markdownテーブル）で比較してください。
・直近株価、時価総額
・PER（予）、PBR（予）、EV/EBITDA
・ROE、営業利益率（直近or予想）
・売上・営業利益成長率（直近決算＋来期・再来期予想）
・理論株価の試算（DCF法またはマルチプルに基づく妥当水準）と、現在の株価との乖離率（アップサイド/ダウンサイド％）
・配当利回り・主力製品の差別化ポイント
・株価チャート上の位置（25日・75日線など簡潔に）

【ステップ4：ランキングとヒートマップ分析】
現時点で最も投資魅力が高い順にランキングし、各順位の根拠を簡潔に述べてください。
あわせて、セクター内の「資金循環ヒートマップ」を言語化し、現在どのサブセクターや領域に最も強い買い圧力がかかっているか分析してください。

【ステップ5：シナリオ分析】
今後3年のメインシナリオと、サブシナリオを2パターン挙げ、それぞれの場合にセクター全体として強気・弱気になる水準感（市場平均に対する相対パフォーマンス予想）を述べてください。

【ステップ6：目標株価とエントリー戦略】
上位3銘柄について、12ヶ月後の「目標株価予想」を、強気・弱気・ベースの3シナリオで提示してください。発生確率と、エントリーする際の推奨価格帯（押し目買い水準）を具体的に提言してください。

回答は客観的かつ数値根拠をできるだけ多く含め、プロ向けのトーンで出力してください。
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
            
            available_model = None
            models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            
            for m in models:
                if 'gemini-1.5' in m.name:
                    available_model = m.name
                    break
            if not available_model:
                for m in models:
                    if 'gemini' in m.name:
                        available_model = m.name
                        break
            
            if not available_model:
                st.error("利用可能なモデルが見つかりませんでした。")
            else:
                # ★最終修正箇所：Pythonの誤訳を防ぐため、Googleの生データ(protos)を直接渡す
                try:
                    search_tool = protos.Tool(google_search=protos.GoogleSearch())
                    tools_list = [search_tool]
                    status_text = f"シニアアナリストが最新データをWeb検索中...（{available_model} ＋ Google検索）"
                except AttributeError:
                    # Streamlitの環境が古すぎて検索機能が見つからない場合の安全装置
                    tools_list = None
                    status_text = f"シニアアナリストが分析中...（{available_model}）"
                    st.toast("⚠️ Google検索機能が未対応の環境のため、通常モードで実行します", icon="ℹ️")

                model = genai.GenerativeModel(
                    model_name=available_model,
                    tools=tools_list
                )
                
                with st.spinner(status_text):
                    full_prompt = PROMPT_TEMPLATE.format(sector_name=sector)
                    response = model.generate_content(full_prompt)
                    
                    st.success(f"「{sector}」の高度分析が完了しました。")
                    st.markdown(response.text)
                    
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
            st.info("※APIキーの入力ミスがないか、またはGoogle側のサーバー状況をご確認ください。")