import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

# Load and process your data
data = pd.read_json(r"C:\Users\LENOVO\Downloads\Last One\Streaming_History_NF_Included_Updated Final.json")  # Replace with your file path
data['endTime'] = pd.to_datetime(data['endTime'])

# Process data for unique songs per week
unique_songs_per_week_data = pd.read_json(r"C:\Users\LENOVO\Downloads\Last One\Unique_Songs_Per_Month_UTF8.json")  # Replace with your file path
unique_songs_per_week_data['endTime'] = pd.to_datetime(unique_songs_per_week_data['endTime'])
unique_songs_per_week_data['YearWeek'] = unique_songs_per_week_data['endTime'].dt.to_period('W')

# Exclude non-numeric columns and calculate the average of each feature per week
numeric_columns = unique_songs_per_week_data.select_dtypes(include=['float64', 'int64'])
numeric_columns['YearWeek'] = unique_songs_per_week_data['YearWeek']
average_features_per_week = numeric_columns.groupby('YearWeek').mean().reset_index()
average_features_per_week['YearWeek'] = average_features_per_week['YearWeek'].astype(str)

# Available features
features = ['danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']

# Feature descriptions
feature_descriptions = {
    'acousticness': 'A confidence measure from 0.0 to 1.0 of whether the track is acoustic. 1.0 represents high confidence the track is acoustic.',
    'danceability': 'Danceability describes how suitable a track is for dancing based on a combination of musical elements including tempo, rhythm stability, beat strength, and overall regularity. A value of 0.0 is least danceable and 1.0 is most danceable.',
    'energy': 'Energy is a measure from 0.0 to 1.0 and represents a perceptual measure of intensity and activity. Typically, energetic tracks feel fast, loud, and noisy. For example, death metal has high energy, while a Bach prelude scores low on the scale. Perceptual features contributing to this attribute include dynamic range, perceived loudness, timbre, onset rate, and general entropy.',
    'instrumentalness': 'Predicts whether a track contains no vocals. "Ooh" and "aah" sounds are treated as instrumental in this context. Rap or spoken word tracks are clearly "vocal". The closer the instrumentalness value is to 1.0, the greater likelihood the track contains no vocal content. Values above 0.5 are intended to represent instrumental tracks, but confidence is higher as the value approaches 1.0.',
    'liveness': 'Detects the presence of an audience in the recording. Higher liveness values represent an increased probability that the track was performed live. A value above 0.8 provides strong likelihood that the track is live.',
    'loudness': 'The overall loudness of a track in decibels (dB). Loudness values are averaged across the entire track and are useful for comparing relative loudness of tracks. Loudness is the quality of a sound that is the primary psychological correlate of physical strength (amplitude). Values typically range between -60 and 0 db.',
    'speechiness': 'Speechiness detects the presence of spoken words in a track. The more exclusively speech-like the recording (e.g. talk show, audio book, poetry), the closer to 1.0 the attribute value. Values above 0.66 describe tracks that are probably made entirely of spoken words. Values between 0.33 and 0.66 describe tracks that may contain both music and speech, either in sections or layered, including such cases as rap music. Values below 0.33 most likely represent music and other non-speech-like tracks.',
    'tempo': 'The overall estimated tempo of a track in beats per minute (BPM). In musical terminology, tempo is the speed or pace of a given piece and derives directly from the average beat duration.',
    'valence': 'A measure from 0.0 to 1.0 describing the musical positiveness conveyed by a track. Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric), while tracks with low valence sound more negative (e.g. sad, depressed, angry).'
}

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    dcc.DatePickerRange(
        id='date-picker-range',
        start_date=data['endTime'].min(),
        end_date=data['endTime'].max(),
        display_format='YYYY-MM-DD',
    ),
    dcc.Dropdown(
        id='y-axis-dropdown',
        options=[{'label': i, 'value': i} for i in features],
        value='energy',
        style={'width': '48%', 'display': 'inline-block'}
    ),
    dcc.Graph(id='feature-graph'),
    dcc.Graph(id='song-count-graph'),
    dcc.Graph(id='average-feature-graph'),
    html.Div(id='feature-description')  # Div to display feature descriptions
])

# Callback for updating graphs
@app.callback(
    [Output('feature-graph', 'figure'),
     Output('song-count-graph', 'figure'),
     Output('average-feature-graph', 'figure')],
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('y-axis-dropdown', 'value')]
)
def update_graphs(start_date, end_date, y_axis_name):
    filtered_data = data[(data['endTime'] >= start_date) & (data['endTime'] <= end_date)]

    # Scatter plot
    scatter_plot = px.scatter(filtered_data, x='endTime', y=y_axis_name, hover_data=['trackName', 'artistName'])

    # Count the number of songs per day
    song_count_per_day = filtered_data['endTime'].dt.date.value_counts().sort_index()
    bar_chart = go.Figure(data=[go.Bar(x=song_count_per_day.index, y=song_count_per_day.values)])
    bar_chart.update_layout(title='Number of Songs Played Per Day', xaxis_title='Date', yaxis_title='Song Count')

    # Filter weekly average data based on selected date range
    start_period = pd.Period(start_date, freq='W')
    end_period = pd.Period(end_date, freq='W')
    weekly_filtered_data = average_features_per_week[(average_features_per_week['YearWeek'] >= str(start_period)) & (average_features_per_week['YearWeek'] <= str(end_period))]

    # Average feature graph
    average_feature_graph = px.line(weekly_filtered_data, x='YearWeek', y=y_axis_name, title=f'Weekly Average of {y_axis_name.capitalize()}')

    return scatter_plot, bar_chart, average_feature_graph

# Callback for updating feature descriptions
@app.callback(
    Output('feature-description', 'children'),
    [Input('y-axis-dropdown', 'value')]
)
def update_feature_description(selected_feature):
    return feature_descriptions.get(selected_feature, '')

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)