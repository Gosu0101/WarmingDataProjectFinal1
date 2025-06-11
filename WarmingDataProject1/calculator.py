from PyQt5.QtWidgets import *
from graph_maker import GraphCanvas
import pandas as pd


class Calculator:
    """계산 관련 함수들"""

    @staticmethod
    def calc_correlation(x_data, y_data):
        """상관계수 계산"""
        clean_data = pd.DataFrame({'x': x_data, 'y': y_data}).dropna()
        if len(clean_data) < 2:
            return 0
        return clean_data['x'].corr(clean_data['y'])

    @staticmethod
    def explain_correlation(correlation):
        """상관계수 해석"""
        r = abs(correlation)

        if r >= 0.8:
            strength = "매우 강한"
        elif r >= 0.6:
            strength = "강한"
        elif r >= 0.4:
            strength = "보통"
        elif r >= 0.2:
            strength = "약한"
        else:
            return "거의 관계없음"

        direction = "양의 관계" if correlation > 0 else "음의 관계"
        return f"{strength} {direction}"


class AnalysisWidget(QWidget):
    """분석 탭의 내용"""

    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.calculator = Calculator()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # 데이터 선택 패널
        selection_panel = QGroupBox("분석할 데이터 선택")
        selection_layout = QGridLayout()

        # X축 데이터
        selection_layout.addWidget(QLabel("X축 데이터:"), 0, 0)
        self.x_data_combo = QComboBox()
        self.x_data_combo.addItems(list(self.data_manager.data.keys()))
        selection_layout.addWidget(self.x_data_combo, 0, 1)

        self.x_column_combo = QComboBox()
        selection_layout.addWidget(self.x_column_combo, 0, 2)

        # Y축 데이터
        selection_layout.addWidget(QLabel("Y축 데이터:"), 1, 0)
        self.y_data_combo = QComboBox()
        self.y_data_combo.addItems(list(self.data_manager.data.keys()))
        selection_layout.addWidget(self.y_data_combo, 1, 1)

        self.y_column_combo = QComboBox()
        selection_layout.addWidget(self.y_column_combo, 1, 2)

        # 분석 버튼
        self.analyze_button = QPushButton("🔍 상관관계 분석하기")
        self.analyze_button.clicked.connect(self.do_analysis)
        selection_layout.addWidget(self.analyze_button, 2, 0, 1, 3)

        selection_panel.setLayout(selection_layout)
        layout.addWidget(selection_panel)

        # 결과 영역을 수평으로 나누기
        result_layout = QHBoxLayout()

        # 그래프
        self.canvas = GraphCanvas()
        result_layout.addWidget(self.canvas, 2)  # 비율 2

        # 결과 텍스트
        self.result_text = QTextEdit()
        self.result_text.setMaximumWidth(300)
        result_layout.addWidget(self.result_text, 1)  # 비율 1

        layout.addLayout(result_layout)
        self.setLayout(layout)

        # 콤보박스 업데이트 연결
        self.x_data_combo.currentTextChanged.connect(self.update_x_columns)
        self.y_data_combo.currentTextChanged.connect(self.update_y_columns)

        # 처음에 한번 업데이트
        self.update_x_columns()
        self.update_y_columns()

    def update_x_columns(self):
        """X축 컬럼 콤보박스 업데이트"""
        data_name = self.x_data_combo.currentText()
        self.x_column_combo.clear()
        if data_name in self.data_manager.data:
            columns = [col for col in self.data_manager.data[data_name].columns
                       if col != '연도']
            self.x_column_combo.addItems(columns)

    def update_y_columns(self):
        """Y축 컬럼 콤보박스 업데이트"""
        data_name = self.y_data_combo.currentText()
        self.y_column_combo.clear()
        if data_name in self.data_manager.data:
            columns = [col for col in self.data_manager.data[data_name].columns
                       if col != '연도']
            self.y_column_combo.addItems(columns)

    def do_analysis(self):
        """실제 분석 수행"""
        # 선택된 데이터 가져오기
        x_data_name = self.x_data_combo.currentText()
        y_data_name = self.y_data_combo.currentText()
        x_column = self.x_column_combo.currentText()
        y_column = self.y_column_combo.currentText()

        if not all([x_data_name, y_data_name, x_column, y_column]):
            self.result_text.setText("데이터를 모두 선택해주세요!")
            return

        # 데이터 합치기
        x_df = self.data_manager.data[x_data_name][['연도', x_column]]
        y_df = self.data_manager.data[y_data_name][['연도', y_column]]
        merged = pd.merge(x_df, y_df, on='연도', how='inner')

        if len(merged) < 2:
            self.result_text.setText("분석할 데이터가 부족합니다!")
            return

        # 상관관계 계산
        correlation = self.calculator.calc_correlation(
            merged[x_column], merged[y_column])

        # 그래프 그리기
        self.canvas.draw_scatter_plot(
            merged[x_column], merged[y_column], x_column, y_column)

        # 결과 해석
        explanation = self.calculator.explain_correlation(correlation)

        # 결과 텍스트 작성
        result = f"""
📊 분석 결과

🔢 상관계수: {correlation:.4f}

📝 해석: {explanation}

📈 의미:
"""

        if abs(correlation) > 0.6:
            result += "두 변수는 밀접한 관련이 있습니다."
        elif abs(correlation) > 0.3:
            result += "두 변수는 어느 정도 관련이 있습니다."
        else:
            result += "두 변수는 관련이 적습니다."

        result += f"""

📊 데이터 개수: {len(merged)}개
📅 분석 기간: {merged['연도'].min()}년 ~ {merged['연도'].max()}년
        """

        self.result_text.setText(result)