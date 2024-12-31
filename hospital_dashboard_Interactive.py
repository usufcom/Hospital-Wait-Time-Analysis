import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

# Load and preprocess the data
df = pd.read_excel('hospital_data_sampleee.xlsx')
df.columns = df.columns.str.strip()

# Convert time columns to datetime by combining date and time strings
time_columns = ['Entry Time', 'Post-Consultation Time', 'Completion Time']
for col in time_columns:
    df[col] = pd.to_datetime(df['Date'].dt.strftime('%Y-%m-%d') + ' ' + df[col].astype(str))

# Calculate waiting and consultation times
df['Wait Time'] = (df['Post-Consultation Time'] - df['Entry Time']).dt.total_seconds() / 60
df['Consultation Duration'] = (df['Completion Time'] - df['Post-Consultation Time']).dt.total_seconds() / 60
df['Hour'] = df['Entry Time'].dt.hour
df['Day of Week'] = df['Date'].dt.day_name()

# Calculate metrics
average_wait_time = df['Wait Time'].mean()
total_patients = df['Patient ID'].nunique()

# Initialize the Dash app
app = Dash(__name__)

# Layout of the dashboard
app.layout = html.Div([
    html.Div([
        html.H1("Hospital Wait Time Analysis",
                style={'textAlign': 'center', 'color': 'white', 'padding': '10px',
                       'borderBottom': '2px solid #FF5733', 'marginBottom': '5px'}),
        html.H4("Designed by Youssoufa M.",
                style={'textAlign': 'center', 'color': '#AAAAAA', 'marginTop': '0px',
                       'fontStyle': 'italic'}),
    ], style={'backgroundColor': '#1E1E1E', 'padding': '20px', 'border': '3px solid #FF5733',
              'borderRadius': '10px', 'marginBottom': '30px'}),

    # Dropdown Filters
    html.Div([
        dcc.Dropdown(
            id='day-filter',
            options=[{'label': day, 'value': day} for day in df['Day of Week'].unique()],
            multi=True,
            placeholder="Filter by Day of Week"
        ),
        dcc.Dropdown(
            id='doctor-filter',
            options=[{'label': doc, 'value': doc} for doc in df['Doctor Type'].unique()],
            multi=True,
            placeholder="Filter by Doctor Type"
        ),
    ], style={'display': 'flex', 'justify-content': 'space-around', 'margin-bottom': '30px'}),

    html.Div([
        html.Div([
            html.H3("Average Wait Time (mins):",
                    style={'textAlign': 'center', 'color': 'white', 'margin': '0'}),
            html.H2(f"{average_wait_time:.2f}",
                    id='avg-wait-output',
                    style={'textAlign': 'center', 'color': 'white', 'margin': '0'}),
        ], className='box',
           style={'border': '3px solid #C0392B', 'width': '45%', 'padding': '20px',
                  'backgroundColor': '#922B21', 'borderRadius': '10px'}),

        html.Div([
            html.H3("Total Patients:",
                    style={'textAlign': 'center', 'color': 'white', 'margin': '0'}),
            html.H2(f"{total_patients}",
                    id='total-patient-output',
                    style={'textAlign': 'center', 'color': 'white', 'margin': '0'}),
        ], className='box',
           style={'border': '3px solid #27AE60', 'width': '45%', 'padding': '20px',
                  'backgroundColor': '#1D7D4D', 'borderRadius': '10px'}),
    ], style={'display': 'flex', 'justify-content': 'space-around', 'margin-bottom': '20px'}),

    # Graphs Section
    html.Div([
        html.Div([
            dcc.Graph(id='busy-days'),
        ], className='box', style={'border': '3px solid #3498db', 'width': '48%',
                                   'backgroundColor': '#2C3E50', 'borderRadius': '10px'}),

        html.Div([
            dcc.Graph(id='doctor-type-pie'),
        ], className='box', style={'border': '3px solid #9b59b6', 'width': '48%',
                                   'backgroundColor': '#5D3C70', 'borderRadius': '10px'}),
    ], style={'display': 'flex', 'justify-content': 'space-between'}),

    html.Div([
        html.Div([
            dcc.Graph(id='wait-time-hour'),
        ], className='box', style={'border': '3px solid #e74c3c', 'width': '48%',
                                   'backgroundColor': '#7B241C', 'borderRadius': '10px'}),

        html.Div([
            dcc.Graph(id='financial-class'),
        ], className='box', style={'border': '3px solid #f1c40f', 'width': '48%',
                                   'backgroundColor': '#7D6608', 'borderRadius': '10px'}),
    ], style={'display': 'flex', 'justify-content': 'space-between'}),
], style={'backgroundColor': '#121212', 'padding': '20px'})


# Callback to update graphs and KPIs based on filters
@app.callback(
    [Output('busy-days', 'figure'),
     Output('doctor-type-pie', 'figure'),
     Output('wait-time-hour', 'figure'),
     Output('financial-class', 'figure'),
     Output('avg-wait-output', 'children'),
     Output('total-patient-output', 'children')],
    [Input('day-filter', 'value'),
     Input('doctor-filter', 'value')]
)
def update_graphs(selected_days, selected_doctors):
    filtered_df = df.copy()

    if selected_days:
        filtered_df = filtered_df[filtered_df['Day of Week'].isin(selected_days)]
    if selected_doctors:
        filtered_df = filtered_df[filtered_df['Doctor Type'].isin(selected_doctors)]

    avg_wait = filtered_df['Wait Time'].mean()
    total_patients = filtered_df['Patient ID'].nunique()

    busy_days_fig = px.bar(
        filtered_df.groupby('Day of Week')['Wait Time'].mean().sort_index(),
        title='Average Wait Time by Day of the Week'
    )

    doc_pie_fig = px.pie(
        filtered_df.groupby('Doctor Type')['Wait Time'].mean().reset_index(),
        values='Wait Time',
        names='Doctor Type',
        title='Average Wait Time by Doctor Type'
    )

    wait_hour_fig = px.line(
        filtered_df.groupby('Hour')['Wait Time'].mean().reset_index(),
        x='Hour',
        y='Wait Time',
        title='Average Wait Time by Hour of Day',
        markers=True
    )

    fin_class_fig = px.bar(
        filtered_df.groupby('Financial Class')['Wait Time'].mean().reset_index(),
        x='Financial Class',
        y='Wait Time',
        title='Average Wait Time by Financial Class'
    )

    return busy_days_fig, doc_pie_fig, wait_hour_fig, fin_class_fig, f"{avg_wait:.2f}", f"{total_patients}"


if __name__ == '__main__':
    app.run_server(debug=True)
