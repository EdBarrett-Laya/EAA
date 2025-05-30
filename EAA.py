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
    Output('rule-breakdown.callback(
    Output('rule-breakdown', 'children'),
    Input('category', 'children'),
    Input('category-bar-chart', 'click-bar-chart', 'clickData'),
    InputData'),
    Input('test-title-dropdown', 'value')
)
def display_rule_breakdown(clickData, selected_tests):
    if not clickData:
       ('test-title-dropdown', 'value')
)
def display_rule_breakdown(clickData, selected_tests):
    if not clickData:
        return "Click on a bar to see individual rules."

    clicked return "Click on a bar to see individual rules."

    clicked_category = click_category = clickData['points'][0]['x']
    filteredData['points'][0]['x']
    filtered_df = df[df['Rule Category'] ==_df = df[df['Rule Category'] == clicked_category clicked_category]

    if "All" not]

    if "All" not in selected_tests:
        filtered in selected_tests:
        filtered_df = filtered_df_df = filtered_df[filtered_df['Test Title'].isin(selected_tests[filtered_df['Test Title'].isin(selected_tests)]

    grouped_data = filtered_df.groupby(['Rule ID', 'Impact']).size().reset_index(name='count')

)]

    grouped_data = filtered_df.groupby(['Rule ID', 'Impact']).size().reset_index(name='count')

    # Filter out    # Filter out rows where count rows where count == 0
    grouped == 0
    grouped_data = grouped_data[grouped_data['count'] > 0]

    breakdown_data = grouped_data[grouped_data['count'] > 0]

    breakdown_table = html.Table_table = html.Table([
        html.Tr([html.Th("Rule ID"), html.Th("Impact"), html.Th("Count")])
   ([
        html.Tr([html.Th("Rule ID"), html.Th("Impact"), html.Th("Count")])
    ] + [
        html.Tr([html.Td(rule), html.Td(impact), html.Td(count)])
        ] + [
        html.Tr([html.Td(rule), html.Td(impact), html.Td(count)])
        for rule, impact for rule, impact, count in grouped, count in grouped_data.values
    ])

    return breakdown_data.values
    ])

    return breakdown_table

server = app.server  # ✅ Gunicorn needs this!

if __name__ == "__main__":
    app.run(debug=True)
