import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# Load dataset
df = pd.read_csv(r'input.csv')

impact_order = ['critical', 'serious', 'moderate', 'minor']
df['Impact'] = pd.Categorical(df['Impact'], categories=impact_order, ordered=True)

# Define rule categories mapping
rule_categories = { 
    'aria-role-missing': 'ARIA Issues', 'contrast-link-infocus-4.5-1': 'Contrast and Color',
    'keyboard-inaccessible': 'Focus and Keyboard', 'semantic-heading': 'Headings and Structure',
    'alt-text-missing': 'Image and Alt-text', 'landmark-unique': 'Landmarks and Structure',
    'label': 'Forms and Labeling', 'custom-dialog': 'Dialogs and Modals',
    'custom-navigation': 'Navigation'
}
df['Rule Category'] = df['Rule ID'].map(rule_categories).fillna('Other')

# Initialize Dash App
app = dash.Dash(__name__)

# Custom Styling
app.layout = html.Div([
    html.H1("Accessibility Issue Dashboard", style={'text-align': 'center', 'color': '#4a90e2'}),
    
    html.Div([
        dcc.Dropdown(
            id='test-title-dropdown',
            options=[{'label': 'All', 'value': 'All'}] + [{'label': t, 'value': t} for t in df['Test Title'].unique()],
            value=['All'], multi=True,
            placeholder="Select Test Titles",
            style={'width': '50%', 'margin': 'auto'}
        ),

        dcc.Dropdown(
            id='column-dropdown',
            options=[{'label': col, 'value': col} for col in df.columns],
            value=['Rule ID', 'Impact'], multi=True,
            placeholder="Select Columns to Display",
            style={'width': '50%', 'margin': 'auto', 'margin-top': '10px'}
        ),
    ], style={'text-align': 'center'}),
    
    dcc.Store(id='selected-categories', data=[])

    html.Br(),
    
    html.Div(id="total-issues-summary", style={'text-align': 'center', 'font-size': '18px', 'font-weight': 'bold'}),
    
    dcc.Graph(id='category-bar-chart', style={'margin': 'auto'}),
    
    html.Div(id="rule-breakdown", style={'margin': 'auto'}),
    
    html.Div(id="selected-summary", style={'text-align': 'center', 'font-size': '16px', 'color': '#333'})
])

@app.callback(
    Output('rule-breakdown', 'children'),
    Input('selected-categories', 'data')
)
def display_selected_categories(selected_categories):
    if not selected_categories:
        return html.Div("Click on bars to select categories.", style={'text-align': 'center', 'font-style': 'italic'})

    # Filter dataframe based on selected categories only
    filtered_df = df[df['Rule Category'].isin(selected_categories)]

    # Aggregate counts per category
    grouped_data = filtered_df.groupby(['Rule Category']).size().reset_index(name='count')

    breakdown_table = html.Table([
        html.Tr([
            html.Th("Rule Category", style={'padding': '15px', 'text-align': 'center', 'background-color': '#4a90e2', 'color': 'white'}),
            html.Th("Count", style={'padding': '15px', 'text-align': 'center', 'background-color': '#4a90e2', 'color': 'white'})
        ])
    ] + [
        html.Tr([
            html.Td(row["Rule Category"], style={'padding': '15px', 'text-align': 'center', 'border': '1px solid #ddd'}),
            html.Td(row["count"], style={'padding': '15px', 'text-align': 'center', 'border': '1px solid #ddd'})
        ])
        for _, row in grouped_data.iterrows()
    ], style={'margin': 'auto', 'border-collapse': 'collapse', 'width': '80%', 'font-size': '16px'})

    return breakdown_table


@app.callback(
    Output('category-bar-chart', 'figure'),
    Output('total-issues-summary', 'children'),
    Input('test-title-dropdown', 'value')
)
def update_chart(selected_tests):
    if "All" in selected_tests or not selected_tests:
        filtered_df = df
    else:
        filtered_df = df[df['Test Title'].isin(selected_tests)]

    total_issues_selected = len(filtered_df)
    total_issues_all = len(df)
    percentage_selected = (total_issues_selected / total_issues_all) * 100

    total_summary = f"Total Issues:\n{total_issues_selected}\n{percentage_selected:.2f}% of all issues"

    grouped_df = filtered_df.groupby(['Rule Category', 'Impact']).size().reset_index(name='count')

    fig = px.bar(grouped_df,
                x="Rule Category",
                y="count",
                color="Impact",
                title="Accessibility Issues Overview" if "All" in selected_tests else f"Issues for {', '.join(selected_tests)}")

    return fig, total_summary

@app.callback(
    Output('selected-categories', 'data'),
    Input('category-bar-chart', 'clickData'),
    State('selected-categories', 'data')
)
def store_selected_categories(clickData, stored_categories):
    if not clickData:
        return stored_categories  # Keep existing selections

    clicked_category = clickData['points'][0]['x']

    # Append new category only if it's not already selected
    if clicked_category not in stored_categories:
        stored_categories.append(clicked_category)

    return stored_categories


server = app.server  # Gunicorn needs this!

if __name__ == "__main__":
    app.run(debug=True)
