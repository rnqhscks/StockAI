from kiwoom.kiwoom import *
from PyQt5.QtWidgets import *
import sys


class Ui_class:
    def __init__(self):
        print("UI클래스 입니다.")

        self.app = QApplication(sys.argv)  # 프로그램의 변수 등을 초기화시켜주고 app 변수에 넣어서 app을 프로그램처럼 쓸 수 있게 해줌

        self.kiwoom = Kiwoom()  # 본격적인 프로그램 시작

        self.app.exec_()  # 프로그램이 끝나지 않게 대기