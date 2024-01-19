import pandas as pd
import scipy.stats as stats
from datetime import datetime

# Load the dataset
file_path = r"C:\Users\LENOVO\Downloads\Last One\Streaming_History_NF_Included_Updated Final.json"  # Replace with your actual file path
data = pd.read_json(file_path)

# Convert 'endTime' to datetime and extract week number and year
data['endTime'] = pd.to_datetime(data['endTime'])
data['year'] = data['endTime'].dt.isocalendar().year
data['week'] = data['endTime'].dt.isocalendar().week

# Specify the desired date and find its corresponding week number
desired_date = datetime(2023, 2, 27)
desired_year = desired_date.isocalendar()[0]
desired_week = desired_date.isocalendar()[1]

# Remove NaN values from valence
data = data.dropna(subset=['tempo'])

# Extract valence values for the specific weeks
valence_week_8 = data[(data['year'] == desired_year) & (data['week'] == desired_week - 1)]['tempo']
valence_week_9 = data[(data['year'] == desired_year) & (data['week'] == desired_week)]['tempo']
valence_week_10 = data[(data['year'] == desired_year) & (data['week'] == desired_week + 1)]['tempo']

# Mann-Whitney U Test
# Comparing week 9 with week 8
u_statistic_8_9, p_value_8_9 = stats.mannwhitneyu(valence_week_8, valence_week_9, alternative='two-sided')

# Comparing week 9 with week 10
u_statistic_9_10, p_value_9_10 = stats.mannwhitneyu(valence_week_9, valence_week_10, alternative='two-sided')

# Print the p-values
print(f'P-value for comparison between Target Date and One Week Before it: {p_value_8_9}')
print(f'P-value for comparison between Target Date and One Week After it: {p_value_9_10}')

# Interpretation of results
alpha = 0.05
if p_value_8_9 < alpha:
    print("Significant difference between Target Date and One Week Before it")
else:
    print("No significant difference between Target Date and One Week Before it")

if p_value_9_10 < alpha:
    print("Significant difference between Target Date and One Week After it")
else:
    print("No significant difference between Target Date and One Week After it")
