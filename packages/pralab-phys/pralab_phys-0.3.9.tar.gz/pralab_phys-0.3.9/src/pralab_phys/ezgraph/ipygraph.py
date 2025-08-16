import pandas as pd
from ipywidgets import interact, Select, IntSlider, Checkbox

from .ezgraph_2d import EZGraph

class EZGraphDisplay:
    """DataFrameを受け取り、2次元グラフを描画するためのクラス
    """

    def _gen_graph(self, x_axis, y_axis, y_axis2, logx, logy, width):
        graph = EZGraph(xax_title=self.x_axis.value, yax_title=self.y_axis.value, width=width)
        graph.add_lines_markers(self.df[x_axis], self.df[y_axis])
        if y_axis2 != "なし":
            import plotly.graph_objects as go
            graph.add_trace(
                go.Scatter(
                    x=self.df[x_axis],
                    y=self.df[y_axis2],
                    mode="lines+markers",
                    name=str(y_axis2),
                    marker=dict(size=7),
                    line=dict(width=3.5),
                    yaxis="y2"
                )
            )
            graph.update_layout(yaxis2=dict(overlaying='y', side='right'))
        if logx:
            graph.logx()
        if logy:
            graph.logy()
        graph.show()

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.x_axis = Select(options=df.columns, description='X軸', rows=4)
        self.y_axis = Select(options=df.columns, description='Y軸', rows=4)
        self.y_axis2 = Select(options=["なし"] + list(df.columns), description='Y2軸', rows=4)
        self.width = IntSlider(value=800, min=400, max=1200, step=500, description='Width')
        self.logx_checkbox = Checkbox(value=False, description="X対数")
        self.logy_checkbox = Checkbox(value=False, description="Y対数")
        interact(
            self._gen_graph,
            x_axis=self.x_axis,
            y_axis=self.y_axis,
            y_axis2=self.y_axis2,
            logx=self.logx_checkbox,
            logy=self.logy_checkbox,
            width=self.width
        )
