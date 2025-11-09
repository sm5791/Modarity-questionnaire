import streamlit as st
import pandas as pd
from datetime import datetime
import pytz # タイムゾーン
import io # CSVをメモリ上で扱うため
import matplotlib.pyplot as plt # ★ グラフ描画のために追加
import numpy as np # ★ グラフ描画のために追加

# --- 1. アプリのタイトル ---
st.set_page_config(page_title="Survey Plot App")
st.title("モダリティ　アンケートフォーム")
st.markdown(r"各項目の明るさを$-10$から$10$で評価してください。")

# --- 2. グラフ描画用の関数を定義 ---
# (以前のプロットコードを関数化)
def create_scatter_plot(x_data, y_data, z_data):
    # fig (図全体) と ax (軸) を取得
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # 散布図を描画
    scatter = ax.scatter(
        x_data, 
        y_data, 
        c=z_data,         # ★ 回答者の回答 (z_data) を色に指定
        cmap='coolwarm',  # カラーマップ
        s=400           # 点のサイズ
    )
    
    # 軸とタイトルの設定 (英語/豆腐回避)
    ax.set_xticks(range(1, 11))
    ax.set_yticks(range(1, 11))
    fig.colorbar(scatter, ax=ax, label='Response Value (Z-data)') # カラーバー
    ax.set_xlabel("first interval")
    ax.set_ylabel("second interval")
    ax.set_title("Survey Responses Heatmap (Scatter Plot)")
    ax.grid(True, linestyle='--', alpha=0.5)
    
    return fig # 描画したグラフのFigureオブジェクトを返す

# --- 3. 質問リストと座標の定義 ---
f_allconb_list = []
for i in range( 1 , 11 ):
  for j in range( 1 , 12 - i ):
    f_allconb_list.append([i,j]) # [i, j] のペア

# ★ グラフ描画用に、x と y の座標リストを分離して作成
x_data_coords = [pair[0] for pair in f_allconb_list]
y_data_coords = [pair[1] for pair in f_allconb_list]

num_questions = 55
questions = [f"{f_allconb_list[i]} " for i in range(num_questions)]

# --- 4. 入力フォーム ---
with st.form(key="survey_form", clear_on_submit=False):
    
    st.info("このフォームの回答はサーバーに保存されません。")
    
    # ユーザー情報
    name = st.text_input("お名前 (任意)")

    st.divider() # 罫線
    
    # --- 55個のスライダーをループで生成 ---
    slider_values = [] # 55個の回答(z_data)を保存するリスト
    
    for i, question_label in enumerate(questions):
        value = st.slider(
            question_label,
            min_value=-10.0,
            max_value=10.0,
            value=0.0,  # デフォルト値
            step=0.01,
            key=f"slider_{i}" # 必須: 固有のキー
        )
        slider_values.append(value)
    # --- ループここまで ---

    st.divider() # 罫線

    # 感想
    feedback = st.text_area(
        "全体的なご意見・ご感想",
        placeholder="ご自由にお書きください"
    )
    
    # 送信ボタン
    submit_button = st.form_submit_button(label='回答を確定')

# --- 5. 送信ボタンが押された後の処理 ---
if submit_button:
    
    # 5a. タイムスタンプの取得
    jst = pytz.timezone('Asia/Tokyo')
    timestamp = datetime.now(jst).strftime("%Y-%m-%d %H:%M:%S")

    # 5b. ダウンロード用のデータ（辞書）を作成
    response_data = {
        "名前": [name],
        "感想": [feedback],
        "タイムスタンプ": [timestamp]
    }
    
    # 5c. スライダーの回答を辞書に追加
    slider_column_names = [f"Item_{i+1}" for i in range(num_questions)]
    
    for i, col_name in enumerate(slider_column_names):
        response_data[col_name] = [slider_values[i]]

    # 5d. Pandas DataFrame に変換
    df_response = pd.DataFrame(response_data)
    
    # 5e. DataFrame を CSV 形式のテキストデータに変換
    csv_data = df_response.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')

    # --- 5f. 完了メッセージと「グラフ表示」 ---
    st.success("ご回答ありがとうございます！")
    
    st.header("回答の視覚化グラフ")
    st.write("あなたの回答プロットされています。")
    
    # (x, y) 座標と、回答 (z) を渡してグラフを作成
    fig = create_scatter_plot(x_data_coords, y_data_coords, slider_values)
    st.pyplot(fig) # ★ Streamlit にグラフを表示

    # --- 5g. ダウンロードボタンの表示 ---
    st.header("回答のダウンロード")
    st.info("以下のボタンを押して、回答の控え（CSVファイル）をダウンロードしてください。")
    
    st.download_button(
        label="Download csv",
        data=csv_data,
        file_name=f"my_survey_response_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )
