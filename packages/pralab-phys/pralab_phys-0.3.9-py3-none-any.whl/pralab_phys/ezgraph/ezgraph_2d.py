import plotly.graph_objects as go
from collections.abc import Collection

class EZGraph(go.Figure):
    '''2次元グラフを描画するためのクラス

    Args:
        dispname (str): グラフの表示名
        xax_title (str): x軸のタイトル
        yax_title (str): y軸のタイトル
        width (int): グラフの幅
        height (int): グラフの高さ
    '''

    def __init__(
        self, 
        dispname:str = "",
        xax_title:str = "",
        yax_title:str = "",
        width:int = 900, 
        height:int = 600,
    ):
        super().__init__()

        # plotly側の設定により、最初にアンダーバーを入れないとエラーを吐く
        # 修正を要検討
        self._dispname = dispname

        self.update_layout(
            title = dict(text = "<b>" + self._dispname, font = dict(size=22, color='gray'), y = 0.95),
            legend=dict(xanchor='left', yanchor='bottom', x=0.02, y=0.82),
            width=width, 
            height=height,
            xaxis=dict(title = xax_title),
            yaxis=dict(title = yax_title),
            plot_bgcolor='white')

        self.update_xaxes(
            showline=True,
            linewidth=2, mirror= True, tickfont_size = 20, title_font=dict(size=24), color='black',
            linecolor='grey',
            ticks='inside',
            ticklen=5,
            tickwidth=2,
            tickcolor='grey'
            )

        self.update_yaxes(
            showline=True,
            linewidth=2, mirror= True, tickfont_size = 20, title_font=dict(size=24), color='black',
            linecolor='grey',
            ticks='inside',
            ticklen=5,
            tickwidth=2,
            tickcolor='grey'
            )
    
    def add_lines_markers(
        self,
        xdata: Collection, 
        ydata: Collection, 
        name: str = "", 
        mode: str = "lines+markers", 
        color: str | None = None
    ):
        """Add a graph to the figure.

        Args:
            xdata (Collection):
                x-axis data

            ydata (Collection):
                y-axis data

            name (str, optional):
                name of the graph. Defaults to "".

            mode (str, optional):
                mode of the graph. Defaults to "lines+markers".

            color (str | None, optional): 
                plot color. Defaults to None (default color).
        """
        self.add_trace(
            go.Scatter(x=xdata, y=ydata, mode=mode, name=name, 
                marker=dict(size=7, color=color), line=dict(width=3.5, color=color)
                )
            )


    def add_markers(self, x: Collection, y: Collection, name: str = "", color: str | None = None, size: float = 7):
        """_summary_

        Args:
            x (Collection): _description_
            y (Collection): _description_
            name (str, optional): _description_. Defaults to "".
            color (str | None, optional): _description_. Defaults to None.
            size (int | float, optional): _description_. Defaults to 7.
        """

        self.add_trace(
            go.Scatter(x=x, y=y, mode="markers", name=name, 
                marker=dict(size=size, color=color)
                )
            )
        
    def add_line(self, x: Collection, y: Collection, name: str = "", color: str | None = None, width: float = 3.5):
        """Add a line to the figure.

        Args:
            x (Collection): 
                x-axis data
            y (Collection):
                y-axis data
            name (str, optional):
                Name of the line. Defaults to "".
            color (str | None, optional): _description_. Defaults to None.
            width (float, optional): _description_. Defaults to 3.5.
        """
        self.add_trace(
            go.Scatter(x=x, y=y, mode="lines", name=name, 
                line=dict(width=width, color=color)
                )
            )

    def logx(self):
        """x軸を対数軸にする
        """
        self.update_xaxes(type="log")
    
    def logy(self): 
        """y軸を対数軸にする
        """
        self.update_yaxes(type="log")

    def legand_loc(self, x: float = 1.02, y: float = 1):
        """凡例の位置を設定する

        Args:
            x (float, optional): . Defaults to 1.02.
            y (float, optional): _description_. Defaults to 1.
        """
        self.update_layout(legend=dict(x=x, y=y))

    def title_loc(self, y:float = 0.95):
        self.update_layout(title = dict(y=y))
    
    def print_methods(self):
        print([method for method in dir(self) if callable(getattr(self, method)) and not method.startswith("__")])