import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, ctx
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

# Load dataset
df = pd.read_csv(r'input.csv')

impact_order = ['critical', 'serious', 'moderate', 'minor']
df['Impact'] = pd.Categorical(df['Impact'], categories=impact_order, ordered=True)

# Define rule categories mapping
rule_categories = {
    # ARIA-related Issues
    'aria-role-missing': 'ARIA Issues', 'aria-state-property-missing': 'ARIA Issues',
    'aria-name-missing-incorrect': 'ARIA Issues', 'aria-required-missing': 'ARIA Issues',
    'aria-dialog-name': 'ARIA Issues', 'aria-allowed-attr': 'ARIA Issues', 'aria-required-parent': 'ARIA Issues',
    'aria-role-invalid': 'ARIA Issues', 'aria-allowed-role': 'ARIA Issues', 'nested-interactive': 'ARIA Issues',
    'presentation-role-conflict': 'ARIA Issues',

    # Contrast and Color-related Issues
    'contrast-link-infocus-4.5-1': 'Contrast and Color', 'contrast-text-4.5-1': 'Contrast and Color',
    'contrast-text-4.5-1-placeholder': 'Contrast and Color', 'color-contrast': 'Contrast and Color',
    'form-errors-color-only': 'Contrast and Color',

    # Focus and Keyboard Accessibility
    'keyboard-inaccessible': 'Focus and Keyboard', 'focus-on-hidden-item': 'Focus and Keyboard',
    'focus-indicator-missing': 'Focus and Keyboard', 'focus-modal-moves-outside': 'Focus and Keyboard',
    'focus-modal-none': 'Focus and Keyboard', 'focus-modal-not-returned': 'Focus and Keyboard',
    'tab-order-illogical': 'Focus and Keyboard',

    # Headings and Semantic Structure
    'semantic-heading': 'Headings and Structure', 'semantic-incorrect': 'Headings and Structure',
    'semantic-list': 'Headings and Structure', 'semantic-hidden': 'Headings and Structure',
    'heading-order': 'Headings and Structure', 'heading-level-increase': 'Headings and Structure',
    'heading-level-order': 'Headings and Structure', 'semantic-heading-misused': 'Headings and Structure',
    'heading-not-descriptive': 'Headings and Structure',

    # Image and Alt-text Issues
    'alt-text-decorative-inappropriate': 'Image and Alt-text', 'alt-text-missing': 'Image and Alt-text',
    'alt-text-short-text-not-meaningful': 'Image and Alt-text', 'image-alt': 'Image and Alt-text',
    'image-of-text': 'Image and Alt-text', 'input-image-alt': 'Image and Alt-text',

    # Landmarks and Structural Issues
    'landmark-complementary-is-top-level': 'Landmarks and Structure', 'landmark-one-main': 'Landmarks and Structure',
    'landmark-unique': 'Landmarks and Structure', 'landmark-no-duplicate-banner': 'Landmarks and Structure',
    'landmark-no-duplicate-contentinfo': 'Landmarks and Structure',

    # Form and Labeling Issues
    'button-name': 'Forms and Labeling', 'label': 'Forms and Labeling', 'title-not-meaningful': 'Forms and Labeling',
    'title-not-unique': 'Forms and Labeling', 'label-is-placeholder': 'Forms and Labeling',
    'label-programmatic-not-descriptive': 'Forms and Labeling', 'label-group-not-associated': 'Forms and Labeling',
    'label-group-radio-not-associated': 'Forms and Labeling',

    # Dialog, Modal, and Timeout Issues
    'custom-dialog': 'Dialogs and Modals', 'modal-no-esc': 'Dialogs and Modals',
    'timeout-no-warning': 'Dialogs and Modals', 'timeout-not-announced': 'Dialogs and Modals',

    # Navigation and Unexpected Behavior
    'custom-navigation': 'Navigation', 'semantic-nav': 'Navigation',
    'link-in-text-block': 'Navigation', 'unexpected-change-on-focus': 'Navigation'
}

df['Rule Category'] = df['Rule ID'].map(rule_categories).fillna('Other')

# Initialize Dash App
app = dash.Dash(__name__)

# Custom Styling
app.layout = html.Div([
    html.H1("Accessibility Audit Dashboard", style={'text-align': 'center', 'color': '#2c3e50', 'font-family': 'Arial, sans-serif', 'font-weight': 'bold'}),

    html.Div([
        dcc.Dropdown(
            id='test-title-dropdown',
            options=[{'label': 'All', 'value': 'All'}] + [{'label': t, 'value': t} for t in df['Test Title'].unique()],
            value=['All'], multi=True,
            placeholder="Select Test Titles",
            style={'width': '50%', 'margin': 'auto', 'font-family': 'Arial, sans-serif'}
        ),
    ], style={'text-align': 'center', 'margin-bottom': '20px'}),

    dcc.Store(id='selected-categories', data=[]),

    html.Div(id="total-issues-summary", style={'text-align': 'center', 'font-size': '18px', 'font-weight': 'bold', 'font-family': 'Arial, sans-serif', 'margin-bottom': '15px'}),

    dcc.Graph(id='category-bar-chart', style={'margin': 'auto', 'padding': '20px'}),

    html.Div([
        dcc.Dropdown(
            id='category-selector',
            options=[{'label': cat, 'value': cat} for cat in df['Rule Category'].unique()],
            value=[], multi=True,
            placeholder="Select Categories",
            style={'width': '50%', 'margin': 'auto', 'margin-top': '20px', 'margin-bottom': '30px', 'font-family': 'Arial, sans-serif'}
        ),
    ]),

    html.Div(id="rule-breakdown", style={'margin': 'auto', 'font-family': 'Arial, sans-serif'}),

    html.Div(id="selected-summary", style={'text-align': 'center', 'font-size': '16px', 'color': '#333', 'font-family': 'Arial, sans-serif'})
])

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

    fig = px.bar(
        grouped_df,
        x="Rule Category",
        y="count",
        color="Impact",
        title="Accessibility Issues Overview" if "All" in selected_tests else f"Issues for {', '.join(selected_tests)}",
        color_discrete_map={
            "critical": "#e74c3c",  # Red
            "serious": "#e67e22",   # Orange
            "moderate": "#f1c40f",  # Yellow
            "minor": "#95a5a6"      # Grey
        }
    )

    return fig, total_summary

@app.callback(
    Output('selected-categories', 'data'),
    Input('category-selector', 'value')
)
def store_selected_categories(dropdown_categories):
    return dropdown_categories  


@app.callback(
    [Output('rule-breakdown', 'children'),
     Output('selected-summary', 'children')],
    Input('selected-categories', 'data')
)
def display_selected_categories(selected_categories):
    if not selected_categories:
        return html.Div("Select categories via dropdown.", style={'text-align': 'center', 'font-style': 'italic', 'font-family': 'Arial, sans-serif'}), ""

    # Filter dataframe based on selected categories
    filtered_df = df[df['Rule Category'].isin(selected_categories)]
    
    # Group by Rule ID and Severity (Impact) while removing rows with count == 0
    grouped_data = filtered_df.groupby(['Rule ID', 'Impact']).size().reset_index(name='count')
    grouped_data = grouped_data[grouped_data['count'] > 0]  # Only keep rows with count > 0

    total_selected_issues = len(filtered_df)
    total_selected_percentage = (total_selected_issues / len(df)) * 100

    selected_summary = f"Total Selected Issues:\n{total_selected_issues}\n{total_selected_percentage:.2f}% of all issues"

    breakdown_table = html.Table([
        html.Tr([
            html.Th("Rule ID", style={'padding': '15px', 'text-align': 'center', 'background-color': '#2c3e50', 'color': 'white', 'font-family': 'Arial, sans-serif'}),
            html.Th("Severity", style={'padding': '15px', 'text-align': 'center', 'background-color': '#2c3e50', 'color': 'white', 'font-family': 'Arial, sans-serif'}),
            html.Th("Count", style={'padding': '15px', 'text-align': 'center', 'background-color': '#2c3e50', 'color': 'white', 'font-family': 'Arial, sans-serif'})
        ])
    ] + [
        html.Tr([
            html.Td(row["Rule ID"], style={'padding': '15px', 'text-align': 'center', 'border': '1px solid #ddd', 'font-family': 'Arial, sans-serif'}),
            html.Td(row["Impact"], style={'padding': '15px', 'text-align': 'center', 'border': '1px solid #ddd', 'font-family': 'Arial, sans-serif'}),
            html.Td(row["count"], style={'padding': '15px', 'text-align': 'center', 'border': '1px solid #ddd', 'font-family': 'Arial, sans-serif'})
        ])
        for _, row in grouped_data.iterrows()
    ], style={'margin': 'auto', 'border-collapse': 'collapse', 'width': '80%', 'font-size': '18px'})

    return breakdown_table, selected_summary


server = app.server

if __name__ == "__main__":
    app.run(debug=True)
