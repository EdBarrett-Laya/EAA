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
    
    html.Br(),
    
    html.Div(id="total-issues-summary", style={'text-align': 'center', 'font-size': '18px', 'font-weight': 'bold'}),
    
    dcc.Graph(id='category-bar-chart', style={'margin': 'auto'}),
    
    html.Div(id="rule-breakdown", style={'margin': 'auto'}),
    
    html.Div(id="selected-summary", style={'text-align': 'center', 'font-size': '16px', 'color': '#333'})
])

@app.callback(
    [Output('rule-breakdown', 'children'),
     Output('selected-summary', 'children')],
    Input('category-bar-chart', 'clickData'),
    Input('test-title-dropdown', 'value'),
    Input('column-dropdown', 'value')
)
def display_rule_breakdown(clickData, selected_tests, selected_columns):
    if not clickData:
        return html.Div("Click on a bar to see individual rules.", style={'text-align': 'center', 'font-style': 'italic'}), ""

    clicked_category = clickData['points'][0]['x']
    filtered_df = df[df['Rule Category'] == clicked_category]

    if "All" not in selected_tests:
        filtered_df = filtered_df[filtered_df['Test Title'].isin(selected_tests)]

    selected_columns = [col for col in selected_columns if col in filtered_df.columns]
    grouped_data = filtered_df[selected_columns].groupby(selected_columns).size().reset_index(name='count')
    grouped_data = grouped_data[grouped_data['count'] > 0]

    total_selected_issues = len(filtered_df)
    total_selected_percentage = (total_selected_issues / len(df[df['Test Title'].isin(selected_tests)])) * 100 if selected_tests else 0
    total_overall_percentage = (total_selected_issues / len(df)) * 100

    selected_summary = f"Total Issues:\n{total_selected_issues}\n{total_selected_percentage:.2f}% of test categories\n{total_overall_percentage:.2f}% of all issues"

    breakdown_table = html.Table([
        html.Tr([html.Th(col, style={'padding': '15px', 'text-align': 'center', 'background-color': '#4a90e2', 'color': 'white'}) for col in selected_columns] + 
                [html.Th("Count", style={'padding': '15px', 'text-align': 'center', 'background-color': '#4a90e2', 'color': 'white'})])
    ] + [
        html.Tr([html.Td(row[col], style={'padding': '15px', 'text-align': 'center', 'border': '1px solid #ddd'}) for col in selected_columns] + 
                [html.Td(row["count"], style={'padding': '15px', 'text-align': 'center', 'border': '1px solid #ddd'})])
        for _, row in grouped_data.iterrows()
    ], style={'margin': 'auto', 'border-collapse': 'collapse', 'width': '80%', 'font-size': '16px'})

    return breakdown_table, selected_summary

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

server = app.server  # Gunicorn needs this!

if __name__ == "__main__":
    app.run(debug=True)
