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
    'aria-role-missing': 'ARIA Issues', 'contrast-text-4.5-1': 'Contrast and Color',
    'keyboard-inaccessible': 'Focus and Keyboard', 'semantic-heading': 'Headings and Structure',
    'alt-text-missing': 'Image and Alt-text', 'landmark-unique': 'Landmarks and Structure',
    'label': 'Forms and Labeling', 'custom-dialog': 'Dialogs and Modals',
    'custom-navigation': 'Navigation'
}

df['Rule Category'] = df['Rule ID'].map(rule_categories).fillna('Other')

# Initialize Dash App
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Accessibility Issue Dashboard"),
    
    dcc.Dropdown(
        id='test-title-dropdown',
        options=[{'label': t, 'value': t} for t in df['Test Title'].unique()],
        placeholder="Select a Test Title",
    ),
    
    dcc.Graph(id='category-bar-chart'),
    html.Div(id='rule-breakdown')
])

@app.callback(
    Output('category-bar-chart', 'figure'),
    Input('test-title-dropdown', 'value')
)
def update_chart(selected_test):
    filtered_df = df if selected_test is None else df[df['Test Title'] == selected_test]
    grouped_df = filtered_df.groupby(['Rule Category', 'Impact']).size().reset_index(name='count')

    fig = px.bar(grouped_df,
                 x="Rule Category",
                 y="count",
                 color="Impact",
                 title=f"Accessibility Issue Breakdown for {selected_test}" if selected_test else "Select a Test Title")

    return fig

@app.callback(
    Output('rule-breakdown', 'children'),
    Input('category-bar-chart', 'clickData'),
    Input('test-title-dropdown', 'value')
)
def display_rule_breakdown(clickData, selected_test):
    if not clickData:
        return "Click on a bar to see individual rules."

    clicked_category = clickData['points'][0]['x']
    print("Clicked Category:", clicked_category)  # Debugging Line

    filtered_df = df[df['Rule Category'] == clicked_category]

    if selected_test:
        filtered_df = filtered_df[filtered_df['Test Title'] == selected_test]

    breakdown_table = html.Table([
        html.Tr([html.Th("Rule ID"), html.Th("Impact"), html.Th("Count")])
    ] + [
        html.Tr([html.Td(rule), html.Td(impact), html.Td(count)])
        for rule, impact, count in filtered_df.groupby(['Rule ID', 'Impact']).size().reset_index(name='count').values
    ])

    return breakdown_table

server = app.server  # ✅ Gunicorn needs this!

if __name__ == "__main__":
    app.run(debug=True)
