import pandas as pd

def clean_and_merge_data_final():
    """
    堺市の急減速データと天候データを正しく読み込み、整形した上でマージする最終版の関数
    """
    # --- 1. データ読み込み (UTF-8 with BOM 対応) ---
    try:
        # エラーの原因である「UTF-8 with BOM」に対応するため、'utf-8-sig' を指定します
        weather_df_raw = pd.read_csv('sakai_weather.csv', encoding='utf-8-sig')
        deceleration_df = pd.read_csv('sorted_deceleration.csv', encoding='utf-8-sig')
    except FileNotFoundError:
        print("エラー: CSVファイルが見つかりません。スクリプトと同じフォルダにあるか確認してください。")
        return
    except Exception as e:
        print(f"ファイルの読み込み中に予期せぬエラーが発生しました: {e}")
        return

    # --- 2. 天候データの整形 (sakai_weather.csv) ---
    print("天候データを整形しています...")
    # 1行目を新しい列名として設定
    new_weather_columns = weather_df_raw.iloc[0].tolist()
    new_weather_columns[4] = '風向' # 5列目の列名を'風向'に修正
    
    # 不要な行(0-2行目)を削除し、インデックスをリセット
    weather_df = weather_df_raw.iloc[3:].reset_index(drop=True)
    weather_df.columns = new_weather_columns
    
    # 'timestamp'列を日付形式に変換
    weather_df['timestamp'] = pd.to_datetime(weather_df['timestamp'])

    # データ型を数値に変換（エラーは無視）
    numeric_cols = ['気温(℃)', '降水量(mm)', '風速(m/s)']
    weather_df[numeric_cols] = weather_df[numeric_cols].apply(pd.to_numeric, errors='coerce')
    
    print("天候データの整形が完了しました。")
    print("-" * 30)

    # --- 3. データの統合準備 ---
    print("データを統合する準備をしています...")
    # 急減速データの'timestamp'列も日付形式に変換
    deceleration_df['timestamp'] = pd.to_datetime(deceleration_df['timestamp'])

    # マージ用のキー列 'timestamp_hour' を作成（時刻を時間単位で切り捨て）
    deceleration_df['timestamp_hour'] = deceleration_df['timestamp'].dt.floor('h')
    
    print("統合準備が完了しました。")
    print("-" * 30)

    # --- 4. データの統合 ---
    print("データを統合しています...")
    # 急減速データを基準に天候データを結合
    merged_df = pd.merge(
        left=deceleration_df,
        right=weather_df,
        left_on='timestamp_hour',
        right_on='timestamp',
        how='left'
    )

    # 不要になった列と、重複したtimestamp列を整理
    merged_df = merged_df.drop(columns=['timestamp_hour', 'timestamp_y'])
    merged_df = merged_df.rename(columns={'timestamp_x': 'timestamp'})
    
    print("データの統合が完了しました。")
    print("-" * 30)

    # --- 5. 結果の保存 ---
    output_filename = 'merged_final_data.csv'
    merged_df.to_csv(output_filename, index=False, encoding='utf-8-sig')

    print(f"🎉 全ての処理が完了しました！")
    print(f"結果は '{output_filename}' として保存されました。")
    print("\n--- 最終的な統合データのサンプル ---")
    print(merged_df.head())


if __name__ == '__main__':
    clean_and_merge_data_final()