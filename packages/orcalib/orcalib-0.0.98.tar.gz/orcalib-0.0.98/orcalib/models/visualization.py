from typing import Any

import plotly.graph_objects as go
from plotly.subplots import make_subplots


class FinetunePlot:
    def __init__(self, show_running_mean: bool = False):
        self.fig = make_subplots(specs=[[{"secondary_y": False}]])

        # Add traces
        self.fig.add_trace(
            go.Scatter(
                name="Loss",
                mode="markers",
                marker={
                    "size": 5,
                    "color": "rgba(0,0,255,0.5)",
                },
            ),
        )
        self.fig.add_trace(
            go.Scatter(
                mode="lines",
                name="Mean Loss" if show_running_mean else "Trailing Mean Loss",
                line=dict(
                    color="blue",
                    width=2,
                ),
            ),
        )
        self.fig.add_trace(
            go.Scatter(
                mode="lines",
                name="Validation Loss",
                line=dict(
                    color="green",
                    width=2,
                ),
            ),
        )

        # Update layout
        self.fig.update_layout(
            height=600,
            xaxis=dict(title="Epoch"),
            yaxis=dict(title="Loss"),
            title="Training Loss per Epoch",
            legend=dict(x=0.01, y=0.99),
        )

        self.fig_widget = go.FigureWidget(self.fig)

    def update(
        self,
        fractional_epochs: list[float],
        loss_values: list[float],
        mean_loss_values: list[float],
        validation_scores: list[float],
        batch_count: int,
        num_batches: int,
        epoch: int,
        total_epochs: int,
    ):
        # Add vertical line to indicate the start of a new epoch
        if (batch_count + 1) % num_batches == 0 and batch_count != 0:
            self.fig_widget.add_vline(
                x=int((batch_count + 1) / num_batches),
                line_color="rgba(0,0,0,0.25)",
            )

        with self.fig_widget.batch_update():
            d: Any = self.fig_widget.data
            d[0].x = fractional_epochs
            d[0].y = loss_values
            d[1].x = fractional_epochs
            d[1].y = mean_loss_values
            d[2].x = list(range(0, len(validation_scores)))
            d[2].y = validation_scores
            self.fig_widget.update_layout(xaxis=dict(title=f"Epoch: {epoch + 1}/{total_epochs}"))

    def get_widget(self):
        return self.fig_widget
