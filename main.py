import streamlit as st
import pandas as pd
from datetime import datetime
import pytz # タイムゾーン
import io # CSVをメモリ上で扱うため
import matplotlib.pyplot as plt # グラフ描画
import numpy as np # グラフ描画
import os # ★ MP3のファイル存在チェックのために追加

# --- 1. アプリのタイトル ---
st.set_page_config(page_title="Survey Plot App")
st.title("モダリティ　アンケートフォーム")
st.markdown(r"各音源を聞き、項目の明るさを$-10$から$10$で評価してください。お試し版なので、音源は３項目しか用意していません。") # ★ 説明文を修正

# --- 2. グラフ描画用の関数 (変更なし) ---
def create_scatter_plot(x_data, y_data, z_data):
    # ( ... グラフ描画のコードはそのまま ... )
    fig, ax = plt.subplots(figsize=(8, 6))
    scatter = ax.scatter(
        x_data, 
        y_data, 
        c=z_data,
        cmap='coolwarm',
        s=400,
        vmin=-10, # ★ vmin/vmax を追加
        vmax=10
    )
    ax.set_xticks(range(1, 11))
    ax.set_yticks(range(1, 11))
    fig.colorbar(scatter, ax=ax, label='Response Value (Z-data)')
    ax.set_xlabel("first interval (i)")
    ax.set_ylabel("second interval (j)")
    ax.set_title("Survey Responses Heatmap (Scatter Plot)")
    ax.grid(True, linestyle='--', alpha=0.5)
    return fig

# --- ★ 3. MP3読み込み用関数 (変更なし) ---
# st.cache_data を使い、一度読み込んだファイルはキャッシュする
#@st.cache_data
def load_audio_file(path):
    """MP3ファイルをバイナリとして読み込む"""
    if os.path.exists(path):
        with open(path, 'rb') as f:
            return f.read()
    return None

# --- 4. 質問リストと座標の定義 (変更なし) ---
f_allconb_list = []
for i in range( 1 , 11 ):
  for j in range( 1 , 12 - i ):
    f_allconb_list.append([i,j]) # [i, j] のペア

x_data_coords = [pair[0] for pair in f_allconb_list]
y_data_coords = [pair[1] for pair in f_allconb_list]

num_questions = 55
# 質問ラベル (例: "[1, 1]")
questions = [f"{f_allconb_list[i]} " for i in range(num_questions)]

# --- 5. 入力フォーム (元の 4.) ---
with st.form(key="survey_form", clear_on_submit=False):
    
    st.info("このフォームの回答はサーバーに保存されません。")
    name = st.text_input("お名前 (任意)")
    st.divider() # 罫線
    
    # --- ★ 55個のスライダーとMP3プレーヤーをループで生成 ---
    slider_values = [] # 55個の回答(z_data)を保存するリスト
    
    for i, question_label in enumerate(questions):
        
        # 1. 対応する (i, j) ペアを取得 (質問ラベル表示用)
        pair = f_allconb_list[i]
        
        # --- ★★★ ここを変更 ★★★ ---
        # 2. ファイル名を生成 (例: "audio00001.mp3")
        #    i は 0 から 54 なので、i+1 (1から55) を使います
        #    :05d は「5桁で、足りない分は0で埋める」という意味
        audio_path = f"audio{i+1:05d}.mp3"
        # --- ★★★ 変更ここまで ★★★ ---
        
        # 3. オーディオファイルをロード
        audio_bytes = load_audio_file(audio_path)
        
        # 4. 質問ラベルとプレーヤーを表示
        st.markdown(f"**質問 {i+1} / {num_questions} (**{question_label})**")
        if audio_bytes:
            st.audio(audio_bytes, format='audio/mp3')
        else:
            # MP3ファイルが見つからなかった場合
            st.caption(f"Audio file not found: {audio_path}")
        
        # 5. スライダーを表示
        value = st.slider(
            "評価:", # 質問ラベルは上で表示したので、ここは "評価" など簡潔に
            min_value=-10.0,
            max_value=10.0,
            value=0.0,  # デフォルト値
            step=0.01,
            key=f"slider_{i}" # 必須: 固有のキー
        )
        slider_values.append(value)
        st.markdown("---") # 各質問の間に区切り線

    # --- ★ ループここまで ---

    st.divider() # 罫線

    # 感想
    feedback = st.text_area(
        "全体的なご意見・ご感想",
        placeholder="ご自由にお書きください"
    )
    
    # 送信ボタン
    submit_button = st.form_submit_button(label='回答を確定')

# --- 6. 送信ボタンが押された後の処理 (元の 5.) ---
if submit_button:
    
    # タイムスタンプの取得
    jst = pytz.timezone('Asia/Tokyo')
    timestamp = datetime.now(jst).strftime("%Y-%m-%d %H:%M:%S")

    # ダウンロード用のデータ（辞書）を作成
    response_data = {
        "名前": [name],
        "感想": [feedback],
        "タイムスタンプ": [timestamp]
    }
    
    # --- ★★★ ここを変更 ★★★ ---
    # スライダーの回答を辞書に追加
    # CSVの列名を "Item_001", "Item_002"... に変更
    slider_column_names = [f"Item_{i+1:03d}" for i in range(num_questions)]
    # --- ★★★ 変更ここまで ★★★ ---
    
    for i, col_name in enumerate(slider_column_names):
        response_data[col_name] = [slider_values[i]]

    # Pandas DataFrame に変換
    df_response = pd.DataFrame(response_data)
    
    # DataFrame を CSV 形式のテキストデータに変換
    csv_data = df_response.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')

    # 完了メッセージと「グラフ表示」
    st.success("ご回答ありがとうございます！")
    
    st.header("回答の視覚化グラフ")
    st.write("あなたの回答がプロットされています。")
    
    # (x, y) 座標と、回答 (z) を渡してグラフを作成
    fig = create_scatter_plot(x_data_coords, y_data_coords, slider_values)
    st.pyplot(fig) # Streamlit にグラフを表示

    # ダウンロードボタンの表示
    st.header("回答のダウンロード")
    st.info("以下のボタンを押して、回答の控え（CSVファイル）をダウンロードしてください。")
    
    st.download_button(
        label="Download csv",
        data=csv_data,
        file_name=f"my_survey_response_{datetime.now().strftime('%Ym%d')}.csv",
        mime="text/csv",
    )
