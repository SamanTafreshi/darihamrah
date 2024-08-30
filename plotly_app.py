import numpy as np
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State

from plotly_factories import MajorPlotFactory, PlotManager
from repositories import amazon_csv
from forms import filter_name

def create_dash_app():
    app = dash.Dash(__name__)

    # Initialize the data once
    initial_x, initial_y = amazon_csv(None)  # No filter applied initially

    # Get filter options from the data
    names = filter_name()  # This returns a list of unique names
    dropdown_options = [{'label': name, 'value': name} for name in names]

    def create_figure(x, y):
        plot_manager = create_plot_manager(x, y)
        layout = customize_layout(plot_manager, x)
        return {'data': plot_manager.fig.data, 'layout': layout}

    def create_plot_manager(x, y):
        plot_factory = MajorPlotFactory(x, y)
        plot_manager = PlotManager(
            plot_factory,
            labels=['discount<br>price', 'actual<br>price'],
            colors=['red', 'green'],
        )
        return plot_manager

    def customize_layout(plot_manager, x):
        layout = plot_manager.create_layout()

        # Limit count of display x_ticks
        if len(list(x)) > 20:
            x = list(x)
            num_ticks = 20  # Number of ticks to show, adjust as needed
            tick_indices = [int(i * (len(x) - 1)) for i in np.linspace(0, 1, num_ticks)]
            x_subset = [x[idx] for idx in tick_indices]
            layout['xaxis']['tickvals'] = x_subset
            layout['xaxis']['ticktext'] = x_subset  # You may adjust ticktext as needed

        return layout

    # Define the layout of the Dash app
    app.layout = html.Div([
        dcc.Dropdown(
            id='dropdown-filter',
            options=dropdown_options,
            value=[],  # Default value is an empty list (no filters applied initially)
            multi=True  # Enable multi-select
        ),
        html.Button('Filter Names', id='filter-button', n_clicks=0),
        dcc.Graph(
            id='graph1',
            config={'displayModeBar': True, 'displaylogo': False},
            figure=create_figure(initial_x, initial_y)  # Load initial figure
        )
    ])

    @app.callback(
        Output('graph1', 'figure'),
        [Input('filter-button', 'n_clicks')],
        [State('dropdown-filter', 'value')]
    )
    def update_figure(n_clicks, selected_filters):
        # Filtered data or initial data based on user interaction
        x, y = amazon_csv(selected_filters if n_clicks > 0 and selected_filters else None)
        return create_figure(x, y)

    return app