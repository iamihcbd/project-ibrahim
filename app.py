import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Import your custom function from ibrahim-project-walmart-sales-forecasting.py
from ibrahim_project_walmart_sales_forecasting import load_data  # Adjust this import as necessary

# Load the dataset using the custom function
forecast_data = load_data()

# Load other CSV files into DataFrames
submission_df = pd.read_csv('Submission.csv')
supermarket_sales_df = pd.read_csv('supermarket_sales - Sheet1.csv')
test1_df = pd.read_csv('test(1).csv')
test2_df = pd.read_csv('test(2).csv')
train_df = pd.read_csv('Train.csv')
historical_demand_df = pd.read_csv('Historical Product Demand.csv')
stores_df = pd.read_csv('stores.csv')

# Ensure date columns are parsed correctly
train_df['Date'] = pd.to_datetime(train_df['Date'])
historical_demand_df['Date'] = pd.to_datetime(historical_demand_df['Date'])

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    html.H1("Walmart Sales Forecasting Dashboard"),
    
    # Dropdown to select a store from the stores.csv
    dcc.Dropdown(
        id='store-dropdown',
        options=[{'label': f"Store {i}", 'value': i} for i in stores_df['Store'].unique()],
        value=stores_df['Store'].unique()[0],  # Default value
        style={'width': '50%'}
    ),
    
    # Date picker range for filtering
    dcc.DatePickerRange(
        id='date-picker',
        start_date=train_df['Date'].min(),
        end_date=train_df['Date'].max()
    ),
    
    # Graph for weekly sales
    dcc.Graph(id='sales-graph'),

    # Another graph for historical demand data
    dcc.Graph(id='demand-graph'),

    # Summary of data
    html.Div(id='summary-text')
])

# Callback to update the sales graph and summary based on store selection and date range
@app.callback(
    [Output('sales-graph', 'figure'),
     Output('demand-graph', 'figure'),
     Output('summary-text', 'children')],
    [Input('store-dropdown', 'value'),
     Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date')]
)
def update_graph(selected_store, start_date, end_date):
    # Filter the training data based on selected store and date range
    filtered_train_df = train_df[(train_df['Store'] == selected_store) & 
                                 (train_df['Date'] >= start_date) & 
                                 (train_df['Date'] <= end_date)]
    
    # Create a line chart for sales over time
    sales_fig = px.line(filtered_train_df, x='Date', y='Weekly_Sales', 
                        title=f'Weekly Sales for Store {selected_store}')

    # Filter historical demand data based on selected store and date range
    filtered_demand_df = historical_demand_df[(historical_demand_df['Store'] == selected_store) & 
                                              (historical_demand_df['Date'] >= start_date) & 
                                              (historical_demand_df['Date'] <= end_date)]
    
    # Create a line chart for historical product demand over time
    demand_fig = px.line(filtered_demand_df, x='Date', y='Demand', 
                         title=f'Historical Demand for Store {selected_store}')
    
    # Calculate summary statistics
    total_sales = filtered_train_df['Weekly_Sales'].sum()
    avg_sales = filtered_train_df['Weekly_Sales'].mean()
    summary = f"Total Sales: ${total_sales:,.2f}, Average Weekly Sales: ${avg_sales:,.2f}"

    return sales_fig, demand_fig, summary

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
