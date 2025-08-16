import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

class RealTimePlot:
    def __init__(self, x_label, y_label, interval=1000):
        # 軸ラベルの初期化
        self.x_label = x_label
        self.y_label = y_label
        # データを格納するリスト
        self.x_data = []
        self.y_data = []
        
        # Dash アプリケーションの設定
        self.app = dash.Dash(__name__)
        self.app.layout = html.Div([
            dcc.Graph(id='live-graph'),
            dcc.Interval(
                id='graph-update',
                interval=interval,  # 更新間隔（ミリ秒）
                n_intervals=0
            )
        ])
        
        # グラフ更新用のコールバックを設定
        self.app.callback(
            Output('live-graph', 'figure'),
            [Input('graph-update', 'n_intervals')]
        )(self.update_graph)

    def update_graph(self, n):
        # X軸とY軸の範囲を決定
        if self.x_data:
            x_range = [min(self.x_data), max(self.x_data)]
        else:
            x_range = [0, 1]
        if self.y_data:
            y_range = [min(self.y_data), max(self.y_data)]
        else:
            y_range = [0, 1]

        # プロット用のデータ作成
        data = go.Scatter(
            x=self.x_data,
            y=self.y_data,
            mode='lines+markers'
        )
        figure = {
            'data': [data],
            'layout': go.Layout(
                xaxis={'title': self.x_label, 'range': x_range},
                yaxis={'title': self.y_label, 'range': y_range}
            )
        }
        return figure

    def add(self, x, y):
        # 受け取ったデータを追加
        self.x_data.append(x)
        self.y_data.append(y)

    def run(self, debug=True):
        # Dash サーバーを起動
        self.app.run(debug=debug)

if __name__ == '__main__':
    # サンプル実行: X軸とY軸のラベルを指定してサーバーを起動
    rtp = RealTimePlot("X 軸", "Y 軸")
    rtp.run()
