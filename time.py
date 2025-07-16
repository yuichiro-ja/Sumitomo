import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Load data and perform initial filtering for Sakai City
df = pd.read_csv('merged_final_data.csv')
sakai_lat_min, sakai_lat_max = 34.45, 34.60
sakai_lon_min, sakai_lon_max = 135.40, 135.60
df_sakai = df[
    (df['latitude'] >= sakai_lat_min) & (df['latitude'] <= sakai_lat_max) &
    (df['longitude'] >= sakai_lon_min) & (df['longitude'] <= sakai_lon_max)
].copy()

# --- Data Preprocessing ---
# Convert timestamp to datetime objects
df_sakai['timestamp'] = pd.to_datetime(df_sakai['timestamp'], errors='coerce')

# Define a function to categorize time slots
def get_time_slot(hour):
    if 7 <= hour < 10:
        return '朝 (7-9時)'
    elif 10 <= hour < 17:
        return '日中 (10-16時)'
    elif 17 <= hour < 20:
        return '夕方 (17-19時)'
    elif 22 <= hour or hour < 5:
        return '夜間 (22-4時)'
    else:
        return 'その他'

# Create time_slot and weather_category columns
df_sakai['time_slot'] = df_sakai['timestamp'].dt.hour.apply(get_time_slot)
df_sakai['weather_category'] = np.where(df_sakai['降水量(mm)'] > 0, '雨', '晴れ・曇り')

# Filter out 'その他' time slot and NaN timestamps
df_sakai = df_sakai[df_sakai['time_slot'] != 'その他'].dropna(subset=['timestamp'])

# --- Analysis per Time Slot ---
results = {}

time_slots_to_analyze = ['朝 (7-9時)', '日中 (10-16時)', '夕方 (17-19時)', '夜間 (22-4時)']

for slot in time_slots_to_analyze:
    df_slot = df_sakai[df_sakai['time_slot'] == slot]

    # Find locations with data for both weather conditions within the time slot
    df_filtered_locations = df_slot.groupby(['latitude', 'longitude']).filter(lambda x: x['weather_category'].nunique() > 1)

    if not df_filtered_locations.empty:
        # Calculate average deceleration at these specific locations
        avg_deceleration = df_filtered_locations.groupby('weather_category')['deceleration_G'].mean()
        results[slot] = avg_deceleration.to_dict()
    else:
        results[slot] = {'晴れ・曇り': np.nan, '雨': np.nan} # No matching locations found

# --- Display Results ---
results_df = pd.DataFrame(results).T.rename_axis('時間帯').reset_index()
print("時間帯・天候別の平均急減速率（同一地点での比較）:")
print(results_df)


# --- Visualization ---
plt.style.use('default')
plt.rcParams['font.family'] = 'Hiragino Sans'
plt.rcParams['figure.figsize'] = (12, 7)

plot_df = results_df.melt(id_vars='時間帯', var_name='天候', value_name='平均急減速率 (G)')

sns.barplot(data=plot_df, x='時間帯', y='平均急減速率 (G)', hue='天候', order=time_slots_to_analyze, hue_order=['晴れ・曇り', '雨'])
plt.title('【分析結果】時間帯・天候別の平均急減速率', fontsize=16, pad=20)
plt.ylabel('平均急減速率 (G)', fontsize=12)
plt.xlabel('時間帯', fontsize=12)
plt.xticks(rotation=0)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.legend(title='天候')
plt.tight_layout()

# Save the plot
plt.savefig('sakai_deceleration_timeslot_weather.png')
print("\nグラフを 'sakai_deceleration_timeslot_weather.png' として保存しました。")