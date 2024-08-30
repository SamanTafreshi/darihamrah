import numpy as np
import plotly.graph_objects as go
from abc import ABC, abstractmethod

class PlotFactory(ABC):
    def __init__(self, x, y_list):
        self.x = np.asarray(x)
        self.y_list = [np.asarray(y) for y in y_list]
        min_y = min(min(y) for y in self.y_list)
        max_y = max(max(y) for y in self.y_list)
        self.y_ticks = np.linspace(min_y, np.round(max_y, 0) + min_y, 21)
        self.formatted_y_ticks = [f'{int(val):,}' for val in self.y_ticks]
        # self.y_ticks_millions = np.round(np.linspace(0, np.round(max(max(y) for y in self.y_list), 0) + min(min(y) for y in self.y_list), 21) / 1e6).astype("int64")

    @abstractmethod
    def create_line_plot(self, y, name, color, visible):
        pass


class MajorPlotFactory(PlotFactory):
    def create_line_plot(self, y, name, color, visible=True):
        return go.Scatter(
            x=self.x,
            y=y,
            mode='lines+markers',  # lines
            name=name,
            visible=visible,
            line=dict(width=3, color=color),
            hovertemplate='%{x} <br> %{y:,}'
        )

class PlotManager:
    def __init__(self, plot_factory, labels, colors, show_line_plot=True):
        self.plot_factory = plot_factory
        self.labels = labels
        self.colors = colors

        line_visible = show_line_plot

        data = []
        for i, y in enumerate(self.plot_factory.y_list):
            data.append(self.plot_factory.create_line_plot(y, self.labels[i], self.colors[i], visible=line_visible))

        self.fig = go.Figure(
            data=data,
            layout=self.create_layout()
        )

    def create_layout(self):
        layout = go.Layout(
            xaxis=dict(
                tickmode='array',
                tickvals=self.plot_factory.x,
                ticktext=self.plot_factory.x
            ),
            yaxis=dict(
                tickvals=self.plot_factory.y_ticks,
                ticktext=[f'{val}' for val in self.plot_factory.formatted_y_ticks],
                tickformat=',.0f',
            ),
            legend=dict(
                x=1.05,
                y=1,
                traceorder='normal',
                font=dict(
                    family='sans-serif',
                    size=12,
                    color='black'
                ),
                bgcolor='rgba(0,0,0,0)',
                bordercolor='rgba(0,0,0,0)'
            ),
            autosize=True,
            margin=dict(l=70, r=100, t=30, b=100),  # Increase right margin to accommodate buttons
        )
        return layout