import streamlit as st
import pandas as pd
from datetime import datetime
import pytz # タイムゾーン
import io # CSVをメモリ上で扱うため

# --- 1. アプリのタイトル ---
st.set_page_config(page_title="Survey (55 Sliders)")
st.title("モダリティ　アンケートフォーム")
st.write("各項目の明るさを-10から10で評価してください。")

# --- 2. 質問リストの定義 ---
# (ここで55個の質問名を定義します)
# (例として "Item 1", "Item 2", ... と自動生成します)


f_allconb_list = []
for i in range( 1 , 11 ):
  for j in range( 1 , 12 - i ):
    f_allconb_list.append([i,j])

num_questions = 55
questions = [f"{f_allconb_list[i]} " for i in range(num_questions)]

# --- 3. 入力フォーム ---
with st.form(key="survey_form", clear_on_submit=False):
    
    st.info("このフォームの回答はサーバーに保存されません。")
    
    # ユーザー情報
    name = st.text_input("お名前 (任意)")

    st.divider() # 罫線
    
    # --- ★ 55個のスライダーをループで生成 ---
    slider_values = [] # 55個の回答を保存するリスト
    
    for i, question_label in enumerate(questions):
        value = st.slider(
            question_label,
            min_value=-10.0,
            max_value=10.0,
            value=0.0,  # デフォルト値
            step=0.01,
            key=f"slider_{i}" # ★ 必須: 固有のキー
        )
        slider_values.append(value)
    # --- ★ ループここまで ---

    st.divider() # 罫線

    # 感想
    feedback = st.text_area(
        "全体的なご意見・ご感想",
        placeholder="ご自由にお書きください"
    )
    
    # 送信ボタン
    submit_button = st.form_submit_button(label='回答を確定')

# --- 4. 送信ボタンが押された後の処理 ---
if submit_button:
    
    
    # 4b. タイムスタンプの取得
    jst = pytz.timezone('Asia/Tokyo')
    timestamp = datetime.now(jst).strftime("%Y-%m-%d %H:%M:%S")

    # 4c. ダウンロード用のデータ（辞書）を作成
    response_data = {
        "名前": [name],
        "感想": [feedback],
        "タイムスタンプ": [timestamp]
    }
    
    # 4d. スライダーの回答を辞書に追加
    # CSVの列名を "Item_1", "Item_2", ... にする
    slider_column_names = [f"Item_{i+1}" for i in range(num_questions)]
    
    for i, col_name in enumerate(slider_column_names):
        response_data[col_name] = [slider_values[i]] # 1行のDFにするためリストに入れる

    # 4e. Pandas DataFrame に変換
    # (1行 x (3 + 55)列 のDataFrameが完成)
    df_response = pd.DataFrame(response_data)
    
    # 4f. DataFrame を CSV 形式のテキストデータに変換
    csv_data = df_response.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')

    # 4g. 完了メッセージとダウンロードボタンを表示
    st.success("ご回答ありがとうございます！")
    st.info("以下のボタンを押して、回答の控え（CSVファイル）をダウンロードしてください。")
    
    st.download_button(
        label="【自分の全回答】をCSVでダウンロード",
        data=csv_data,
        file_name=f"my_survey_response_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )
