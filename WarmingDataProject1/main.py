import sys
from PyQt5.QtWidgets import QApplication
from data_manager import DataManager
from ui_components import MainWindow


def main():
    # 프로그램 시작
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # 데이터 불러오기
    data_manager = DataManager()

    # 메인 화면 보여주기
    window = MainWindow(data_manager)
    window.show()

    # 프로그램 종료될 때까지 대기
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()