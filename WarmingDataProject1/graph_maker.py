import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import *
import pandas as pd
import numpy as np

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False


class GraphCanvas(FigureCanvas):
    """그래프를 그리는 캔버스"""

    def __init__(self):
        self.figure = Figure(figsize=(10, 6))
        super().__init__(self.figure)

    def draw_scatter_plot(self, x_data, y_data, x_name, y_name):
        """산점도 그리기"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # 데이터 정리 (빈 값 제거)
        clean_data = pd.DataFrame({'x': x_data, 'y': y_data}).dropna()

        if len(clean_data) > 1:
            # 점 찍기
            ax.scatter(clean_data['x'], clean_data['y'],
                       color='blue', alpha=0.7, s=50)

            # 추세선 그리기
            z = np.polyfit(clean_data['x'], clean_data['y'], 1)
            line = np.poly1d(z)
            ax.plot(clean_data['x'], line(clean_data['x']),
                    "r--", alpha=0.8, linewidth=2)

            # 상관계수 표시
            correlation = clean_data['x'].corr(clean_data['y'])
            ax.text(0.05, 0.95, f'상관계수: {correlation:.3f}',
                    transform=ax.transAxes, fontsize=12,
                    bbox=dict(boxstyle="round", facecolor='yellow', alpha=0.7))

        ax.set_xlabel(x_name, fontsize=12)
        ax.set_ylabel(y_name, fontsize=12)
        ax.set_title(f'{x_name} vs {y_name}', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)

        self.figure.tight_layout()
        self.draw()

    def draw_line_plot(self, data, columns, title):
        """선 그래프 그리기"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown']

        for i, col in enumerate(columns[:6]):  # 최대 6개까지
            if col in data.columns and col != '연도':
                color = colors[i % len(colors)]
                ax.plot(data['연도'], data[col],
                        marker='o', label=col, color=color, linewidth=2)

        ax.set_xlabel('연도', fontsize=12)
        ax.set_ylabel('값', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)

        self.figure.tight_layout()
        self.draw()


class GraphWidget(QWidget):
    """그래프 탭의 내용"""

    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # 컨트롤 패널
        control_panel = QGroupBox("그래프 설정")
        control_layout = QGridLayout()

        # 데이터 선택
        control_layout.addWidget(QLabel("데이터:"), 0, 0)
        self.data_combo = QComboBox()
        self.data_combo.addItems(list(self.data_manager.data.keys()))
        control_layout.addWidget(self.data_combo, 0, 1)

        # 그래프 그리기 버튼
        self.plot_button = QPushButton("📊 그래프 그리기")
        self.plot_button.clicked.connect(self.draw_graph)
        control_layout.addWidget(self.plot_button, 0, 2)

        control_panel.setLayout(control_layout)
        layout.addWidget(control_panel)

        # 그래프 캔버스
        self.canvas = GraphCanvas()
        layout.addWidget(self.canvas)

        self.setLayout(layout)

    def draw_graph(self):
        """선택된 데이터로 그래프 그리기"""
        selected_data = self.data_combo.currentText()
        if selected_data in self.data_manager.data:
            data = self.data_manager.data[selected_data]
            columns = [col for col in data.columns if col != '연도']

            self.canvas.draw_line_plot(data, columns, f'{selected_data} 시간별 변화')