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
# Define a function to categorize speed
def get_speed_bin(speed):
    if speed < 30:
        return '低速 (30km/h未満)'
    elif 30 <= speed <= 60:
        return '中速 (30-60km/h)'
    else: # speed > 60
        return '高速 (60km/h超)'

# Create speed_bin and weather_category columns
df_sakai['speed_bin'] = df_sakai['speed_kmph'].apply(get_speed_bin)
df_sakai['weather_category'] = np.where(df_sakai['降水量(mm)'] > 0, '雨', '晴れ・曇り')

# --- Analysis per Speed Bin ---
results = {}
speed_bins_to_analyze = ['低速 (30km/h未満)', '中速 (30-60km/h)', '高速 (60km/h超)']

for bin_name in speed_bins_to_analyze:
    df_bin = df_sakai[df_sakai['speed_bin'] == bin_name]

    # Find locations with data for both weather conditions within the speed bin
    df_filtered_locations = df_bin.groupby(['latitude', 'longitude']).filter(lambda x: x['weather_category'].nunique() > 1)

    if not df_filtered_locations.empty:
        # Calculate average deceleration at these specific locations
        avg_deceleration = df_filtered_locations.groupby('weather_category')['deceleration_G'].mean()
        results[bin_name] = avg_deceleration.to_dict()
    else:
        # No locations with both weather conditions found for this bin
        results[bin_name] = {'晴れ・曇り': np.nan, '雨': np.nan}

# --- Display Results ---
results_df = pd.DataFrame(results).T.rename_axis('速度域').reset_index()
print("速度域・天候別の平均急減速率（同一地点での比較）:")
print(results_df)

# --- Visualization ---
plt.style.use('default')
plt.rcParams['font.family'] = 'Hiragino Sans'
plt.rcParams['figure.figsize'] = (12, 7)

plot_df = results_df.melt(id_vars='速度域', var_name='天候', value_name='平均急減速率 (G)')

sns.barplot(data=plot_df, x='速度域', y='平均急減速率 (G)', hue='天候', order=speed_bins_to_analyze, hue_order=['晴れ・曇り', '雨'])
plt.title('【分析結果】速度域・天候別の平均急減速率', fontsize=16, pad=20)
plt.ylabel('平均急減速率 (G)', fontsize=12)
plt.xlabel('速度域', fontsize=12)
plt.xticks(rotation=0)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.legend(title='天候')
plt.tight_layout()

# Save the plot
plt.savefig('sakai_deceleration_speed_weather.png')
print("\nグラフを 'sakai_deceleration_speed_weather.png' として保存しました。")