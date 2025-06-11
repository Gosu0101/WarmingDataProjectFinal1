from PyQt5.QtWidgets import *
from PyQt5 import uic
from graph_maker import GraphCanvas
from calculator import Calculator
import os


class MainWindow(QMainWindow):
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager

        # .ui 파일 로드
        ui_path = os.path.join(os.path.dirname(__file__), 'main_window.ui')
        try:
            uic.loadUi(ui_path, self)
        except FileNotFoundError:
            print("UI 파일을 찾을 수 없습니다.")
            return

        self.setup_ui_connections()

    def setup_ui_connections(self):
        """UI 파일에서 로드된 위젯들과 기능 연결"""

        # 그래프 탭 설정
        self.setup_graph_tab()

        # 분석 탭 설정
        self.setup_analysis_tab()

        # 데이터 탭 설정
        self.setup_data_tab()

    def setup_graph_tab(self):
        """그래프 탭 설정 - GraphCanvas 모듈 활용"""
        # 콤보박스에 데이터 추가
        self.graph_data_combo.addItems(list(self.data_manager.data.keys()))

        # GraphCanvas 클래스 사용
        self.graph_canvas = GraphCanvas()

        # 기존 위젯의 레이아웃에 캔버스 추가
        canvas_layout = QVBoxLayout()
        canvas_layout.addWidget(self.graph_canvas)
        self.graph_canvas_widget.setLayout(canvas_layout)

        # 버튼 연결
        self.graph_plot_button.clicked.connect(self.draw_graph)

    def setup_analysis_tab(self):
        """분석 탭 설정 - Calculator와 GraphCanvas 모듈 활용"""
        # Calculator 인스턴스 생성
        self.calculator = Calculator()

        # 콤보박스들에 데이터 추가
        data_names = list(self.data_manager.data.keys())
        self.x_data_combo.addItems(data_names)
        self.y_data_combo.addItems(data_names)

        # GraphCanvas 클래스 사용 (분석용)
        self.analysis_canvas = GraphCanvas()

        # 캔버스를 위젯에 추가
        canvas_layout = QVBoxLayout()
        canvas_layout.addWidget(self.analysis_canvas)
        self.analysis_canvas_widget.setLayout(canvas_layout)

        # 콤보박스 연결
        self.x_data_combo.currentTextChanged.connect(self.update_x_columns)
        self.y_data_combo.currentTextChanged.connect(self.update_y_columns)
        self.analyze_button.clicked.connect(self.do_analysis)

        # 초기 컬럼 업데이트
        self.update_x_columns()
        self.update_y_columns()

    def setup_data_tab(self):
        """데이터 탭 설정"""
        # 콤보박스에 데이터 추가
        self.data_combo.addItems(list(self.data_manager.data.keys()))

        # 버튼 연결
        self.refresh_button.clicked.connect(self.refresh_data)
        self.export_button.clicked.connect(self.export_data)
        self.data_combo.currentTextChanged.connect(self.update_data_table)

        # 처음 로드시 테이블 업데이트
        self.update_data_table()

    def draw_graph(self):
        """선택된 데이터로 그래프 그리기 - GraphCanvas의 draw_line_plot 메서드 활용"""
        selected_data = self.graph_data_combo.currentText()
        if selected_data in self.data_manager.data:
            data = self.data_manager.data[selected_data]
            columns = [col for col in data.columns if col != '연도']

            # GraphCanvas의 메서드 사용
            self.graph_canvas.draw_line_plot(data, columns, f'{selected_data} 시간별 변화')

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
        """상관관계 분석 수행 - Calculator 모듈 활용"""
        # 선택된 데이터 가져오기
        x_data_name = self.x_data_combo.currentText()
        y_data_name = self.y_data_combo.currentText()
        x_column = self.x_column_combo.currentText()
        y_column = self.y_column_combo.currentText()

        if not all([x_data_name, y_data_name, x_column, y_column]):
            self.result_text.setText("데이터를 모두 선택해주세요!")
            return

        # 데이터 합치기
        import pandas as pd
        x_df = self.data_manager.data[x_data_name][['연도', x_column]]
        y_df = self.data_manager.data[y_data_name][['연도', y_column]]
        merged = pd.merge(x_df, y_df, on='연도', how='inner')

        if len(merged) < 2:
            self.result_text.setText("분석할 데이터가 부족합니다!")
            return

        # Calculator 클래스의 메서드 사용
        correlation = self.calculator.calc_correlation(
            merged[x_column], merged[y_column])

        # GraphCanvas의 산점도 그리기 메서드 사용
        self.analysis_canvas.draw_scatter_plot(
            merged[x_column], merged[y_column], x_column, y_column)

        # Calculator 클래스의 해석 메서드 사용
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

    def update_data_table(self):
        """선택된 데이터로 테이블 업데이트"""
        selected = self.data_combo.currentText()
        if selected in self.data_manager.data:
            df = self.data_manager.data[selected]

            # 테이블 설정
            self.data_table.setRowCount(len(df))
            self.data_table.setColumnCount(len(df.columns))
            self.data_table.setHorizontalHeaderLabels(df.columns.tolist())

            # 데이터 채우기
            for i in range(len(df)):
                for j in range(len(df.columns)):
                    item = QTableWidgetItem(str(df.iloc[i, j]))
                    self.data_table.setItem(i, j, item)

            # 상태 레이블 업데이트
            self.status_label.setText(f"{selected} - {len(df)}행 {len(df.columns)}열")

    def refresh_data(self):
        """데이터 새로고침"""
        self.data_manager.load_data()

        # 모든 콤보박스 업데이트
        data_names = list(self.data_manager.data.keys())

        self.data_combo.clear()
        self.data_combo.addItems(data_names)

        self.graph_data_combo.clear()
        self.graph_data_combo.addItems(data_names)

        self.x_data_combo.clear()
        self.x_data_combo.addItems(data_names)

        self.y_data_combo.clear()
        self.y_data_combo.addItems(data_names)

        self.update_data_table()

    def export_data(self):
        """현재 선택된 데이터를 CSV로 내보내기"""
        selected = self.data_combo.currentText()
        if selected in self.data_manager.data:
            filename, _ = QFileDialog.getSaveFileName(
                self, "CSV 파일 저장", f"{selected}.csv", "CSV files (*.csv)")
            if filename:
                self.data_manager.data[selected].to_csv(filename, index=False, encoding='utf-8-sig')
                QMessageBox.information(self, "성공", f"{filename}에 저장되었습니다!")