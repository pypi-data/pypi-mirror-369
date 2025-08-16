"""
RealtimePlot_fixed.py
このファイルは、Plotly Dash を利用してグローバルコンテナ経由でリアルタイムに複数グラフを管理する実装です。

【仕様】
- コンストラクタでは、更新間隔 (interval, ms) のみを指定。
- グローバルコンテナ（Dash アプリとレイアウト）は、初回 RealtimePlot インスタンス生成時に作成・起動。
- グラフは、ユーザーが register_graph() メソッドを呼び出して追加します。
  登録時の引数： name (必須), title (オプション)、個別軸ラベル x_label, y_label（それぞれデフォルトは 'X', 'Y'）。
- add_data(graph_name, x, y) で、指定グラフにデータ点を追加。
- remove_graph(graph_name) で、グローバルコンテナからグラフを削除可能。
- run() メソッドでサーバー起動、persist_display() で現在の表示を固定表示（軽量実装）。
- Dash の Interval コンポーネントとパターンマッチングコールバックを利用し、全グラフを定期的に更新します。
"""

import dash
from dash import dcc, html, Input, Output, ALL
import plotly.graph_objs as go
import threading
import time

# グローバル変数（モジュールレベル）
global_app = None        # Dash アプリケーション
global_layout = None     # 主レイアウト（全グラフ配置用）
global_server = None     # サーバーインスタンス
_GLOBAL_GRAPHS = {}      # 登録されたグラフの管理辞書
# _GLOBAL_GRAPHS 形式：
# {
#    graph_name: {
#         "title": title,
#         "x_label": x_label,
#         "y_label": y_label,
#         "x_data": [],
#         "y_data": []
#    },
#    ...
# }

def initialize_global_app(interval):
    """
    グローバル Dash アプリ、レイアウト、Interval コンポーネントの初期化を行う。
    """
    global global_app, global_layout, global_server

    global_app = dash.Dash(__name__)
    # グローバルレイアウトは Div で、子要素としてグラフを後から追加
    global_layout = html.Div([
        html.H2("Realtime Plot Dashboard"),
        html.Div(id="global-graph-container", children=[]),
        dcc.Interval(id="realtime-interval", interval=interval, n_intervals=0)
    ])
    global_app.layout = global_layout

    # Dash のパターンマッチングコールバックで、すべてのグラフコンポーネントを更新
    @global_app.callback(
        Output({'type': 'realtime-graph', 'index': ALL}, 'figure'),
        Input("realtime-interval", "n_intervals")
    )
    def update_all_graphs(n_intervals):
        figures = []
        # _GLOBAL_GRAPHS の順番は各グラフ登録順（不定順の場合もある）
        for graph_key in _GLOBAL_GRAPHS:
            data_dict = _GLOBAL_GRAPHS[graph_key]
            x_vals = data_dict["x_data"]
            y_vals = data_dict["y_data"]
            # 自動軸レンジ計算
            if x_vals:
                x_range = [min(x_vals), max(x_vals)]
            else:
                x_range = [0, 1]
            if y_vals:
                y_range = [min(y_vals), max(y_vals)]
            else:
                y_range = [0, 1]
            fig = {
                "data": [
                    go.Scatter(
                        x=x_vals,
                        y=y_vals,
                        mode="lines+markers",
                        name=data_dict["title"]
                    )
                ],
                "layout": go.Layout(
                    title=data_dict["title"],
                    xaxis={"title": data_dict["x_label"], "range": x_range},
                    yaxis={"title": data_dict["y_label"], "range": y_range}
                )
            }
            figures.append(fig)
        return figures

class RealtimePlot:
    def __init__(self, interval=1000):
        """
        interval: 更新間隔（ミリ秒）
        グローバル Dash アプリが存在しなければ作成・起動します。
        """
        self.interval = interval
        # このインスタンスで個別に管理したグラフは、グローバル辞書 _GLOBAL_GRAPHS を使用するため、
        # インスタンス独自の辞書は不要です。
        global global_app
        if global_app is None:
            initialize_global_app(interval)

    def register_graph(self, name, title=None, x_label='X', y_label='Y'):
        """
        グローバルコンテナにグラフを登録します。
        引数:
          name: グラフの識別子（必須）
          title: 表示タイトル（指定がなければ name を使用）
          x_label, y_label: 軸ラベル（デフォルト 'X', 'Y'）
        登録時、Dash の Graph コンポーネントを global_layout の "global-graph-container" に追加し、
        _GLOBAL_GRAPHS に初期状態 (空のデータ) を登録します。
        """
        global global_layout, _GLOBAL_GRAPHS
        if name in _GLOBAL_GRAPHS:
            raise ValueError(f"Graph '{name}' は既に登録されています。")
        if title is None:
            title = name
        # 初期データは空リスト
        _GLOBAL_GRAPHS[name] = {
            "title": title,
            "x_label": x_label,
            "y_label": y_label,
            "x_data": [],
            "y_data": []
        }
        # Dash Graph コンポーネントの id にはパターンマッチング用の dict を使用
        new_graph = dcc.Graph(id={'type': 'realtime-graph', 'index': name})
        # global_layout の子要素 "global-graph-container" に追加
        container = global_layout.children[1]
        container.children.append(new_graph)

    def remove_graph(self, name):
        """
        指定された識別子のグラフを、global コンテナと _GLOBAL_GRAPHS から削除します。
        """
        global global_layout, _GLOBAL_GRAPHS
        if name not in _GLOBAL_GRAPHS:
            raise ValueError(f"Graph '{name}' は登録されていません。")
        # Remove from the container: 2番目の要素が "global-graph-container"
        container = global_layout.children[1]
        # container.children はリストなので、フィルタリング
        container.children = [child for child in container.children
                              if not (isinstance(child.id, dict) and child.id.get('index') == name)]
        # Remove from the registry dictionary
        del _GLOBAL_GRAPHS[name]

    def add_data(self, graph_name, x, y):
        """
        graph_name で登録されたグラフにデータ点 (x, y) を追加します。
        """
        global _GLOBAL_GRAPHS
        if graph_name not in _GLOBAL_GRAPHS:
            raise ValueError(f"Graph '{graph_name}' は登録されていません。")
        _GLOBAL_GRAPHS[graph_name]["x_data"].append(x)
        _GLOBAL_GRAPHS[graph_name]["y_data"].append(y)

    def run(self, port=8050, debug=True):
        """
        グローバル Dash サーバーを起動します。
        このメソッドを呼び出すと、Notebook内またはブラウザでリアルタイム表示が可能になります。
        """
        global global_app, global_server
        if global_app is None:
            raise RuntimeError("Dash アプリケーションが初期化されていません。")
        # サーバーをバックグラウンドスレッドで起動
        def run_server():
            global_app.run_server(port=port, debug=debug, use_reloader=False)
        # 既にサーバーが起動しているかチェック（ここでは単純に global_server があるか）
        if global_server is None:
            global_server = threading.Thread(target=run_server, daemon=True)
            global_server.start()
            if debug:
                print(f"Dash server が http://localhost:{port} で起動しました。")

    def persist_display(self):
        """
        Dash の show() に相当する機能です。
        サーバーで表示中の状態を固定表示するため、IFrame 用の HTML を返します。
        ここではシンプルな方法として、サーバー URL を埋め込む IFrame のコードを表示します。
        """
        # サーバー URL は固定と仮定 (例: http://localhost:8050)
        iframe_code = f'<iframe src="http://localhost:8050" width="100%" height="600"></iframe>'
        display_html = f"""
        <html>
          <head><title>Persisted Display</title></head>
          <body>
            {iframe_code}
          </body>
        </html>
        """
        # Notebook 上で表示させるために、出力 HTML を返す
        return display_html

# テスト用コード（必要に応じて Notebook やコンソールで実行してください）
if __name__ == "__main__":
    rp = RealtimePlot(interval=1000)
    # 例として、"A" と "B" という 2 つのグラフを登録
    rp.register_graph("A", title="Graph A", x_label="Time", y_label="Value")
    rp.register_graph("B", title="Graph B", x_label="Time", y_label="Measurement")
    
    # サーバー起動
    rp.run(port=8050, debug=True)
    
    # データ追加の例（ここでは 10 回点を追加）
    import random
    for i in range(10):
        rp.add_data("A", i, random.uniform(0, 10))
        rp.add_data("B", i, random.uniform(0, 20))
        time.sleep(1)
    
    # persist_display() を呼び出し、IFrame コードを出力（Notebook で使用するため）
    html_code = rp.persist_display()
    print("Persist display HTML:")
    print(html_code)
