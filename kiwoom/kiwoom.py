import os
import time
import sys

import numpy as np

from kiwoom.ai import *

from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.errorCode import *
from PyQt5.QtTest import *
from config.kiwoomType import *
class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()  # 부모 클래스의 변수들을 사용하기 위해 실행

        self.realType = RealType()
        ####### event loop 모음
        self.login_event_loop = None
        self.detail_account_info_event_loop = QEventLoop()
        self.calculator_event_loop = QEventLoop()
        ############################

        ####### 스크린 번호 모음
        self.screen_my_info = "2000"
        self.screan_calculation_stock = "4000"
        self.screen_real_stock = "5000" # 종목별로 할당할 스크린 번호
        self.screen_meme_stock = "6000" # 종목별로 할당알 주문용 스크린 번호
        self.screen_start_stop_real = "1000"

        ####### 변수 모음
        self.account_num = None
        self.account_stock_dict = {}
        self.not_account_stock_dict = {}
        self.portfolio_stock_dict = {}
        self.jango_dict = {}
        #############################

        ####### 계좌 관련 변수
        self.use_money = 0
        self.use_money_percent = 0.5
        ############################

        ####### 종목 분석 용
        self.calcul_data = []
        self.selected_stock = []
        ############################

        ####### 알고리즘 조건 수치
        self.al1_last_time = 1
        self.al2_analyze_term = 0
        self.al3_soar_term = 10
        self.al3_soar_price_percent = 10
        self.al3_soar_volume_percent = 300
        self.ignore_fluctuation = 3
        #############################
        self.base_date = "20230901"
        self.startNum = 1
        self.stock_list_type = "10"

        # 간단한 딥러닝 가능한지 검사
        #self.ai = Ai()

        self.if_need_analysis = 0
        self.input_stock_data = [[], []]
        self.middle_layer_1 = None
        self.middle_layer_2 = None
        self.output_layer = None

        print("Kiwoom 클래스 입니다.")
        self.get_ocx_instance()  # 키움 API 제어 시작
        self.event_slot()  # 이벤트 감지 시작
        #self.real_event_slot()
        self.signal_login_commConnect()  # 로그인 요청하기

        self.dnn()


        """
        self.get_account_info()  # 계좌번호 가져오기
        self.detail_account_info()  # 예수금을 가져오기
        self.detail_account_mystock()  # 계좌평가내용잔고내용요청
        self.not_concluded_account() # 미체결 요청

        #self.day_kiwoom_db(code="004100", date=self.base_date)
        #self.calculator_fnc() # 종목 분석용, 임시용으로 실행
        #print(self.selected_stock)
        #print(self.last_analyze_idx)

        self.read_code() # 저장된 종목들 불러온다
        self.screen_number_setting() # 스크린 번호를 할당

        self.dynamicCall("SetRealReg(QString, QString, QString, QString)", self.screen_start_stop_real, '', self.realType.REALTYPE['장시작시간']['장운영구분'], "0")

        for code in self.portfolio_stock_dict.keys():
            screen_num = self.portfolio_stock_dict[code]['스크린번호']
            fids = self.realType.REALTYPE['주식체결']['체결시간']

            self.dynamicCall("SetRealReg(QString, QString, QString, QString)", screen_num, code,
                             fids, "1")
            print("실시간 등록 코드 : %s, 스크린번호 : %s, fid번호 : %s" %(code, screen_num, fids))
        """


    def get_ocx_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")  # 응용 프로그램을 제어하게 하기 위해 키움 API 경로 지정

    def event_slot(self):  # 이벤트를 모아두는 구역
        self.OnEventConnect.connect(self.login_slot)  # 로그인 이벤트를 login_slot이라는 슬롯에 연결시킨다.
        self.OnReceiveTrData.connect(self.trdata_slot)  # tr 데이터를 trdata_slot이라는 슬롯에 연결시킨다.
        self.OnReceiveMsg.connect(self.msg_slot)

    def real_event_slot(self):
        self.OnReceiveRealData.connect(self.realdata_slot)
        self.OnReceiveChejanData.connect(self.chejan_slot)
    def login_slot(self, errCode):  # 로그인 상태를 errCode를 인자로 받는다
        print(errCode)
        print(errors(errCode))  # 에러 코드를 보고 어떤 오류인지 출력

        self.login_event_loop.exit()  # 로그인 결과를 받으면 이벤트 루프를 끝냄

    def signal_login_commConnect(self):  # 로그인하는 함수
        self.dynamicCall("CommConnect()")  # 키움 API에 로그인을 요청

        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_()  # 로그인 요청의 결과값을 받을 때까지 이벤트 루프 돌음

    def get_account_info(self):  # 계좌번호를 가져오는 함수
        account_list = self.dynamicCall("GetLoginInfo(String)", "ACCNO")  # 키움 API에 계좌번호를 요청하여 account_list에 받음

        self.account_num = account_list.split(';')[0]  # 계좌번호가 '1231243;' 이런식으로 나오기 때문에 ;을 기준으로 나눔
        print("나의 보유 계좌번호 %s " % self.account_num) # 8056895811 모의주식 계좌

    def detail_account_info(self):  # 예수금을 요청하는 함수
        print("예수금 요청하는 부분")

        self.dynamicCall("SetInputValue(String, String)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(String, String)", "비밀번호", "0000")
        self.dynamicCall("SetInputValue(String, String)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(String, String)", "조회구분", "2")

        self.dynamicCall("CommRqData(String, String, int, String)", "예수금상세현황요청", "opw00001", "0", self.screen_my_info)

        self.detail_account_info_event_loop = QEventLoop()
        self.detail_account_info_event_loop.exec_()

    def detail_account_mystock(self, sPreNext="0"):
        print("계좌평가잔고내역요청")
        self.dynamicCall("SetInputValue(String, String)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(String, String)", "비밀번호", "0000")
        self.dynamicCall("SetInputValue(String, String)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(String, String)", "조회구분", "2")

        self.dynamicCall("CommRqData(String, String, int, String)", "계좌평가잔고내역요청", "opw00018", sPreNext, self.screen_my_info)

        self.detail_account_info_event_loop.exec_()
    def not_concluded_account(self, sPreNext="0"):
        print("미체결요청")
        self.dynamicCall("SetInputValue(String, String)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(String, String)", "체결구분", "1")
        self.dynamicCall("SetInputValue(String, String)", "매매구분", "0")

        self.dynamicCall("CommRqData(String, String, int, String)", "실시간미체결요청", "opt10075", sPreNext, self.screen_my_info)

        self.detail_account_info_event_loop.exec_()

    def stock_select_algorithm1(self):
        #print("이평선 순서 알고리즘")
        if_pass = True
        moving_average5 = 99999999997
        moving_average10 = 99999999998
        moving_average20 = 99999999999
        for i in range(self.al1_last_time):
            total = 0
            for j in range(i, i+20):
                if len(self.calcul_data) < 20:
                    print("이평선 위한 데이터 부족")
                    break
                total += int(self.calcul_data[j][1])

                if j == 4+i:
                    moving_average5 = total / 5
                elif j == 9+i:
                    moving_average10 = total / 10
                elif j == 19+i:
                    moving_average20 = total / 20
            if moving_average20 <= moving_average10 <= moving_average5:
                pass
            else:
                if_pass = False
        return if_pass

    def stock_select_algorithm2(self):
        # print("조정 후 상승 알고리즘")

        if_pass = True
        low_point = self.al2_analyze_term
        high_point = None

        for i in range(self.al2_analyze_term-1, 0 , -1):
            #다음날과 가격이 같을때
            if int(self.calcul_data[i-1][1]) == int(self.calcul_data[i][1]):

                if (int(self.calcul_data[i - 2][1]) < int(self.calcul_data[i][1]) and
                        int(self.calcul_data[i][1]) > int(self.calcul_data[i + 1][1])):
                    # 고점: 다음날 종가 < 그날 종가 > 전날 종가
                    if high_point == None:
                        # 지금까지 고점이 없었으면 바로 고점으로 지정
                        high_point = i
                        # print("첫 고점")
                        """
                    elif ((int(self.calcul_data[i][1]) - int(self.calcul_data[i + 1][1])) / int(
                            self.calcul_data[i + 1][1]) * 100 <= self.ignore_fluctuation and
                          (int(self.calcul_data[i][1]) - int(self.calcul_data[i - 2][1])) / int(
                                self.calcul_data[i - 2][1]) * 100 <= self.ignore_fluctuation):
                        # 전날 종가와 그날 종가 차이가 몇 % 보다 낮으면 패스
                        # print("작은 변동으로 패스")
                        pass
                    """
                    elif int(self.calcul_data[high_point][1]) > int(self.calcul_data[i][1]):
                        if_pass = False
                        # print("현 고점이 전 고점보다 낮음")
                        break
                    else:
                        high_point = i
                        # print("고점변경")
                    """
                    if int(self.calcul_data[0][1]) < int(self.calcul_data[i][1]):
                        #print("현재 가격 낮음")
                        if_pass = False
                        break
                    """

                elif (int(self.calcul_data[i - 2][1]) > int(self.calcul_data[i][1]) and
                      int(self.calcul_data[i][1]) < int(self.calcul_data[i + 1][1])):
                    # 저점
                    '''
                    if ((int(self.calcul_data[i-1][1]) - int(self.calcul_data[i][1])) / int(self.calcul_data[i-1][1])*100 <= self.ignore_fluctuation and
                          (int(self.calcul_data[i+1][1]) - int(self.calcul_data[i][1])) / int(self.calcul_data[i][1])*100 <= self.ignore_fluctuation):
                        #print("작은 변동으로 패스")
                        pass
                    el'''
                    #print(high_point, low_point, i)
                    if (int(self.calcul_data[high_point][1]) + int(self.calcul_data[self.al2_analyze_term][1])) / 2 > int(
                            self.calcul_data[i][1]):
                        if_pass = False
                        # print("전 저점과 고점 사이 50% 보다 낮은 곳에서 저점 발생")
                        break
                    else:
                        low_point = i
                        # print("저점변경")

            #다음날과 가격이 다를때
            elif (int(self.calcul_data[i-1][1]) < int(self.calcul_data[i][1]) and
                    int(self.calcul_data[i][1]) > int(self.calcul_data[i+1][1])):
                # 고점: 다음날 종가 < 그날 종가 > 전날 종가
                if high_point == None:
                    # 지금까지 고점이 없었으면 바로 고점으로 지정
                    high_point = i
                    #print("첫 고점")
                    """
                elif ((int(self.calcul_data[i][1]) - int(self.calcul_data[i + 1][1])) / int(
                        self.calcul_data[i + 1][1]) * 100 <= self.ignore_fluctuation and
                      (int(self.calcul_data[i][1]) - int(self.calcul_data[i - 1][1])) / int(
                        self.calcul_data[i - 1][1]) * 100 <= self.ignore_fluctuation):
                    # 전날 종가와 그날 종가 차이가 몇 % 보다 낮으면 패스
                    #print("작은 변동으로 패스")
                    pass
                """
                elif int(self.calcul_data[high_point][1]) > int(self.calcul_data[i][1]):
                    if_pass = False
                    #print("현 고점이 전 고점보다 낮음")
                    break
                else:
                    high_point = i
                    #print("고점변경")
                """
                if int(self.calcul_data[0][1]) < int(self.calcul_data[i][1]):
                    #print("현재 가격 낮음")
                    if_pass = False
                    break
                """

            elif (int(self.calcul_data[i-1][1]) > int(self.calcul_data[i][1]) and
                  int(self.calcul_data[i][1]) < int(self.calcul_data[i+1][1])):
                # 저점
                '''
                if ((int(self.calcul_data[i-1][1]) - int(self.calcul_data[i][1])) / int(self.calcul_data[i-1][1])*100 <= self.ignore_fluctuation and
                      (int(self.calcul_data[i+1][1]) - int(self.calcul_data[i][1])) / int(self.calcul_data[i][1])*100 <= self.ignore_fluctuation):
                    #print("작은 변동으로 패스")
                    pass
                el'''
                #print(high_point, low_point, i)
                if (int(self.calcul_data[high_point][1]) + int(self.calcul_data[self.al2_analyze_term][1]))/2 > int(self.calcul_data[i][1]):
                    if_pass = False
                    #print("전 저점과 고점 사이 50% 보다 낮은 곳에서 저점 발생")
                    break
                else:
                    low_point = i
                    #print("저점변경")


        if low_point == self.al2_analyze_term or high_point == None:
            if_pass = False
        elif int(self.calcul_data[1][1]) > int(self.calcul_data[0][1]):
            if_pass = False
        #elif (int(self.calcul_data[0][1])) < int(self.calcul_data[high_point][1]):
        #    if_pass = False


        return if_pass

    def stock_select_algorithm3(self):
        #print("급등 감지 알고리즘")

        if_pass = False
        for i in range(self.al3_soar_term-1, -1, -1):
            if_price_soar = False
            if_exchangeVolume_soar = False
            if int(self.calcul_data[i][1]) - int(self.calcul_data[i+1][1]) >= int(self.calcul_data[i+1][1])*self.al3_soar_price_percent*0.01 and int(self.calcul_data[i][1]) - int(self.calcul_data[i][5]) > 0:
                # 10% 이상 급등
                if_price_soar = True

            if int(self.calcul_data[i][2]) >= int(self.calcul_data[i+1][2]) * self.al3_soar_volume_percent*0.01:
                # 거래량 300% 이상 급등
                if_exchangeVolume_soar = True

            if if_exchangeVolume_soar and if_price_soar:
                self.al2_analyze_term = i+1
                if_pass = True

        if if_pass:
            print(f"{self.al2_analyze_term}일 전 급등")
        return if_pass

    def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):
        '''
        tr 요청을 받는 구역(슬롯)
        :param sScrNo: 스크린번호
        :param sRQName: 내가 요청했을 때 지은 이름
        :param sTrCode: 요청 id, tr 코드
        :param sRecordName: 사용안함
        :param sPrevNext: 다음 페이지가 있는지
        :return:
        '''

        if sRQName == "예수금상세현황요청":
            deposit = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "예수금")
            print("예수금 %s" % int(deposit))

            self.use_money = int(deposit) * self.use_money_percent
            self.use_money = self.use_money/4
            self.dynamicCall("")

            depositable = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "출금가능금액")
            print("출금 가능 금액 %s" % depositable)

            self.detail_account_info_event_loop.exit()

        elif sRQName == "계좌평가잔고내역요청":
            total_buy_money = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "총매입금액")
            total_buy_money_result = int(total_buy_money)

            print("총매입금액 %s" % total_buy_money_result)

            total_profit_loss_rate = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "총수익률(%)")
            total_profit_loss_rate_result = float(total_profit_loss_rate)

            print("총수익률(%%) %s" % total_profit_loss_rate_result)

            rows = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            cnt = 0
            for i in range(rows):
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목번호")
                code = code.strip()[1:]

                code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")
                stock_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "보유수량")
                buy_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매입가")
                learn_rate = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "수익률(%)")
                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")
                total_cheguel_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매입금액")
                possible_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매매가능수량")

                if code in self.account_stock_dict:
                    pass
                else:
                    self.account_stock_dict.update({code:{}})

                code_nm = code_nm.strip()
                stock_quantity = int(stock_quantity.strip())
                buy_price = int(buy_price.strip())
                learn_rate = float(learn_rate.strip())
                current_price = int(current_price.strip())
                total_cheguel_price = int(total_cheguel_price.strip())
                possible_quantity = int(possible_quantity.strip())

                self.account_stock_dict[code].update({"종목명": code_nm})
                self.account_stock_dict[code].update({"보유수량": stock_quantity})
                self.account_stock_dict[code].update({"매입가": buy_price})
                self.account_stock_dict[code].update({"수익률(%)": learn_rate})
                self.account_stock_dict[code].update({"현재가": current_price})
                self.account_stock_dict[code].update({"매입금액": total_cheguel_price})
                self.account_stock_dict[code].update({"매매가능수량": possible_quantity})

                cnt +=1

            print("계좌에 가지고 있는 종목 %s" % self.account_stock_dict)

            if sPrevNext == "2":
                self.detail_account_mystock(sPreNext="2")
            else:
                self.detail_account_info_event_loop.exit()

        elif sRQName == "실시간미체결요청":
            rows = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)

            for i in range(rows):
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목코드")
                code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")
                order_no = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문번호")
                order_status = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문상태")
                order_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문수량")
                order_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문가격")
                order_gubun = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문구분")
                not_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "미체결수량")
                ok_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "체결량")

                code = code.strip()
                code_nm = code_nm.strip()
                order_no = int(order_no.strip())
                order_status = order_status.strip()
                order_quantity = int(order_quantity.strip())
                order_price = int(order_price.strip())
                order_gubun = order_gubun.strip().lstrip('+').lstrip('-')
                not_quantity = int(not_quantity.strip())
                ok_quantity = int(ok_quantity.strip())

                if order_no in self.not_account_stock_dict:
                    pass
                else:
                    self.not_account_stock_dict[order_no] = {}
                print(code)
                nasd = self.not_account_stock_dict[order_no]
                nasd.update({"종목코드": code})
                nasd.update({"종목명": code_nm})
                nasd.update({"주문번호": order_no})
                nasd.update({"주문상태": order_status})
                nasd.update({"주문수량": order_quantity})
                nasd.update({"주문가격": order_price})
                nasd.update({"주문구분": order_gubun})
                nasd.update({"미체결수량": not_quantity})
                nasd.update({"체결량": ok_quantity})
            print("미체결 종목 : %s" % self.not_account_stock_dict)
            self.detail_account_info_event_loop.exit()

        elif sRQName == "주식일봉차트조회":
            code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드")
            code = code.strip()
            print("%s 일봉데이터 요청" % code)

            cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)

            #한번 조회하면 600일치까지 일봉데이터를 받을 수 있다.

            for i in range(cnt):
                data = []

                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")
                value = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "거래량")
                trading_value = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "거래대금")
                date = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "일자")
                start_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "시가")
                high_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "고가")
                low_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "저가")

                data.append("")
                data.append(current_price.strip())
                data.append(value.strip())
                data.append(trading_value.strip())
                data.append(date.strip())
                data.append(start_price.strip())
                data.append(high_price.strip())
                data.append(low_price.strip())
                data.append("")

                self.calcul_data.append(data.copy())
            self.input_stock_data = [[], []]
            if len(self.calcul_data) >= stock_data_interval*(num_for_one_stock-1) + 25:
                for i in range(stock_data_interval * (num_for_one_stock-1) + 25):
                    self.input_stock_data[0].append(int(self.calcul_data[i][1]))
                    self.input_stock_data[1].append(int(self.calcul_data[i][2]))

            else:
                self.input_stock_data = []

            self.calcul_data.clear()
            self.calculator_event_loop.exit()

            # 임시로 지워둠
            """ 
            if sPrevNext == "2":
                print("데이터 더 있음")
                self.day_kiwoom_db(code=code, sPrevNext=sPrevNext, date=self.base_date)
            else:
                print("총 일수 %s" % len(self.calcul_data))

                if self.if_need_analysis:
                    pass_success = False

                    # 종목 분석 시작
                    # 데이터는 self.calcul_data에 존재

                    # 120일 이평선을 그릴 만큼의 데이터가 있는지 체크
                    if self.calcul_data == None or len(self.calcul_data) < 120:
                        pass_success = False
                    else:
                        # 120일 이상 되면은
                        total_price = 0
                        for value in self.calcul_data[:120]:
                            total_price += int(value[1])
                        moving_average_price = total_price / 120

                        # 오늘자 주가가 120일 이평선에 걸쳐 있는지 확인
                        bottom_stock_price = False
                        check_price = None
                        if int(self.calcul_data[0][7]) <= moving_average_price and moving_average_price <= int(
                                self.calcul_data[0][6]):
                            print("오늘 주가 120이평선에 걸쳐 있는 것 확인")
                            bottom_stock_price = True
                            check_price = int(self.calcul_data[0][6])

                        # 과거 일봉들이 120일 이평선보다 밑에 있는지 확인,
                        # 그렇게 확인을 하다가 일봉이 120일 이평선보다 위에 있으면 계산진행
                        prev_price = None  # 과거의 일봉 저가
                        if bottom_stock_price:
                            moving_average_price = 0
                            price_top_moving = False
                            moving_average_price_prev = 0
                            idx = 1
                            while True:
                                if len(self.calcul_data[idx:]) < 120:
                                    print("120일 치가 없음!")
                                    break

                                total_price = 0
                                for value in self.calcul_data[idx:120 + idx]:
                                    total_price += int(value[1])
                                moving_average_price_prev = total_price / 120

                                if moving_average_price_prev <= int(self.calcul_data[idx][6]) and idx <= 20:
                                    print("20일동안 120일 이평선과 같거나 위에 있으면 조건 통과 못함")
                                    price_top_moving = False
                                    break
                                elif int(self.calcul_data[idx][7]) > moving_average_price_prev and idx > 20:
                                    print("120일 이평선 위에 있는 일봉 확인됨")
                                    price_top_moving = True
                                    prev_price = int(self.calcul_data[idx][7])
                                    break

                                idx += 1
                            # 해당 부분 이평선이 가장 최근 일자의 이평선 가격보다 낮은지 확인
                            if price_top_moving:
                                if moving_average_price_prev < moving_average_price and check_price > prev_price:
                                    print("포착된 이평선의 가격이 오늘자(최근일자) 이평선 가격보다 낮은 것 학인됨")
                                    print("포착된 부분의 일봉 저가가 오늘자 일봉의 고가보다 낮은지 확인됨")
                                    pass_success = True

                    if pass_success or 1:
                        print("조건부 통과됨")

                        code_nm = self.dynamicCall("GetMasterCodeName(QString)", code)

                        f = open("files/condition_stock.txt", "a", encoding="utf8")
                        f.write("%s\t%s\t%s\n" % (code, code_nm, str(self.calcul_data[0][1])))
                        f.close()
                    else:
                        print("조건부 통과 못함")

                    # 직접 만든 부분
                    if len(self.calcul_data) <=21:
                        pass
                    elif self.stock_select_algorithm1() and self.stock_select_algorithm3() and self.stock_select_algorithm2():
                        self.selected_stock.append(code)

                        print("선택")
                        code_nm = self.dynamicCall("GetMasterCodeName(QString)", code)
                        result_file = open("files/condition_stock.txt", "a", encoding="utf8")
                        result_file.write("%04d\t%s\t%s\t%s\n" % (self.last_analyze_idx, code, code_nm, str(self.calcul_data[0][1])))
                        result_file.close()

                self.input_stock_data = self.calcul_data[:stock_data_interval * 9 + 25]
                self.calcul_data.clear()
                self.calculator_event_loop.exit()
            """



    def get_code_list_by_market(self, market_code):
        '''
        종목 코드들 반환
        :param market_code:
        :return:
        '''

        code_list = self.dynamicCall("GetCodeListByMarket(QString)", market_code)
        code_list = code_list.split(";")[:-1]

        return code_list

    def calculator_fnc(self):
        '''
        종목 분석 실행용 함수
        :return:
        '''
        code_list = self.get_code_list_by_market(self.stock_list_type)
        print("코스닥 갯수 %s" % len(code_list))

        for idx, code in enumerate(code_list):
            self.dynamicCall("DisconnectRealData(QString)", self.screan_calculation_stock)
            if idx+1 >= self.startNum:
                print("%s / %s : KOSDAQ Stock Code : %s is updating..." % (idx+1, len(code_list), code))
                self.day_kiwoom_db(code=code, date=self.base_date)

    def day_kiwoom_db(self, code=None, date=None, sPrevNext='0'):
        print("day_kiwoom_db %s %s %s" %(code, date, sPrevNext))
        QTest.qWait(3600)

        self.dynamicCall("SetInputValue(QString, QString)", '종목코드', code)
        self.dynamicCall("SetInputValue(QString, QString)", '수정주가구분', '1')

        if date != None:
            self.dynamicCall("SetInputValue(QString, QString)", '기준일자', date)

        self.dynamicCall("CommRqData(QString, QString, int, QString)", '주식일봉차트조회', 'opt10081', sPrevNext, self.screan_calculation_stock)

        self.calculator_event_loop.exec_()

    def read_code(self):
        if os.path.exists("files/condition_stock.txt"):
            f = open("files/condition_stock.txt", "r", encoding="utf8")

            lines = f.readlines()

            for line in lines:
                ls = line.split("\t")
                stock_code = ls[0]
                stock_name = ls[1]
                stock_price = int(ls[2].split("\n")[0])
                stock_price = abs(stock_price)

                self.portfolio_stock_dict.update({stock_code:{"종목명":stock_name, "현재가":stock_price}})
        f.close()

        print(self.portfolio_stock_dict)

    def screen_number_setting(self):
        screen_overwrite = []

        # 계좌평가잔고내역에 있는 종목들
        for code in self.account_stock_dict.keys():
            if code not in screen_overwrite:
                screen_overwrite.append(code)

        # 미체결에 있는 종목들
        for order_number in self.not_account_stock_dict.keys():
            code = self.not_account_stock_dict[order_number]['종목코드']

            if code not in screen_overwrite:
                screen_overwrite.append(code)

        # 포트폴리오에 담겨 있는 종목들
        for code in self.portfolio_stock_dict.keys():
            if code not in screen_overwrite:
                screen_overwrite.append(code)

        # 스크린 번호 할당
        cnt = 0
        for code in screen_overwrite:

            temp_screen = int(self.screen_real_stock)
            meme_screen = int(self.screen_meme_stock)

            if (cnt % 50) == 0:
                temp_screen += 1
                self.screen_real_stock = str(temp_screen)

            if (cnt % 50) == 0:
                meme_screen += 1
                self.screen_meme_stock = str(meme_screen)

            if code in self.portfolio_stock_dict.keys():
                self.portfolio_stock_dict[code].update({"스크린번호":str(self.screen_real_stock)})
                self.portfolio_stock_dict[code].update({"주문용스크린번호":str(self.screen_meme_stock)})
            elif code not in self.portfolio_stock_dict.keys():
                self.portfolio_stock_dict.update({code: {"스크린번호":str(self.screen_real_stock), "주문용스크린번호":str(self.screen_meme_stock)}})
            cnt +=1
        print(self.portfolio_stock_dict)

    def realdata_slot(self, sCode, sRealType, sRealData):

        if sRealType == "장시작시간":
            fid = self.realType.REALTYPE[sRealType]['장운영구분']
            value = self.dynamicCall("GetCommRealData(QString, int)", sCode, fid)

            if value == '0':
                print("장 시작 전")
            elif value == '3':
                print("장 시작")
            elif value == '2':
                print("장 종료, 동시호가로 넘어감")
            elif value == '4':
                print("3시30분 장 종료")

                for code in self.portfolio_stock_dict.keys():
                    self.file_delete("SetRealRemove(String, String)", self.portfolio_stock_dict[code]['스크린번호'])

                QTest.qWait(5000)

                self.file_delete()
                self.calculator_fnc()

        elif sRealType == "주식체결":
            a = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['체결시간']) # HHMMSS
            b = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['현재가']) # +/- 2500
            b = abs(int(b))
            c = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['전일대비'])
            c = abs(int(c))
            d = self.dynamicCall("GetCommRealData(QString, int)", sCode,
                                 self.realType.REALTYPE[sRealType]['등락율'])
            d = float(d)
            e = self.dynamicCall("GetCommRealData(QString, int)", sCode,
                                 self.realType.REALTYPE[sRealType]['(최우선)매도호가'])
            e = abs(int(e))

            f = self.dynamicCall("GetCommRealData(QString, int)", sCode,
                                 self.realType.REALTYPE[sRealType]['(최우선)매수호가'])
            f = abs(int(f))
            g = self.dynamicCall("GetCommRealData(QString, int)", sCode,
                                 self.realType.REALTYPE[sRealType]['거래량'])
            g = abs(int(g))
            h = self.dynamicCall("GetCommRealData(QString, int)", sCode,
                                 self.realType.REALTYPE[sRealType]['누적거래량'])
            h = abs(int(h))

            i = self.dynamicCall("GetCommRealData(QString, int)", sCode,
                                 self.realType.REALTYPE[sRealType]['고가'])
            i = abs(int(i))

            j = self.dynamicCall("GetCommRealData(QString, int)", sCode,
                                 self.realType.REALTYPE[sRealType]['시가'])
            j = abs(int(j))

            k = self.dynamicCall("GetCommRealData(QString, int)", sCode,
                                 self.realType.REALTYPE[sRealType]['저가'])
            k = abs(int(k))

            if sCode not in self.portfolio_stock_dict:
                self.portfolio_stock_dict.update({sCode:{}})

            self.portfolio_stock_dict[sCode].update({"체결시간": a})
            self.portfolio_stock_dict[sCode].update({"현재가": b})
            self.portfolio_stock_dict[sCode].update({"전일대비": c})
            self.portfolio_stock_dict[sCode].update({"등락율": d})
            self.portfolio_stock_dict[sCode].update({"(최우선}매도호가": e})
            self.portfolio_stock_dict[sCode].update({"(최우선)매수호가": f})
            self.portfolio_stock_dict[sCode].update({"거래량": g})
            self.portfolio_stock_dict[sCode].update({"누적거래량": h})
            self.portfolio_stock_dict[sCode].update({"고가": i})
            self.portfolio_stock_dict[sCode].update({"시가": j})
            self.portfolio_stock_dict[sCode].update({"저가": k})

            print(self.portfolio_stock_dict[sCode])

            ########################## 실시간 조건 검색

            # 계좌잔고평가내역에 있고오늘 산 잔고에는 없을 경우
            if sCode in self.account_stock_dict.keys() and sCode not in self.jango_dict.keys():
                asd = self.account_stock_dict[sCode]

                meme_rate = (b - asd['매입가'])/ asd['매입가'] *100

                if asd['매매가능수량'] > 0 and (meme_rate > 5 or meme_rate < -5):
                    order_success = self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                 ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                                 sCode, asd['매매가능수량'], 0, self.realType.SENDTYPE['거래구분']['시장가'], ""])

                    if order_success == 0:
                        print("매도주문 전달 성공")
                        del self.account_stock_dict[sCode]
                    else:
                        print("매도주문 전달 실패")



            # 오늘 산 잔고에 있을 경우
            elif sCode in self.jango_dict.keys():
                jd = self.jango_dict[sCode]
                meme_rate = (b-jd['매입단가']) / jd['매입단가'] * 100

                if jd['주문가능수량'] > 0 and (meme_rate > 5 or meme_rate < -5):
                    order_success = self.dynamicCall(
                        "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                        ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 2,
                         sCode, jd['주문가능수량'], 0, self.realType.SENDTYPE['거래구분']['시장가'], ""])

                    if order_success == 0:
                        self.logging.logger.debug("매도주문 전달 성공")
                    else:
                        self.logging.logger.debug("매도주문 전달 실패")

            #등락율이 2% 이상이고 오늘 산 잔고에 없을 경우
            elif d>2.0 and sCode not in self.jango_dict.keys():
                print("%s %s" % ("신규 매수를 한다.", sCode))

                result = (self.use_money*0.1)/e
                quantity = int(result)

                order_success = self.dynamicCall(
                        "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                        ["신규매도", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 1,
                         sCode, quantity, e, self.realType.SENDTYPE['거래구분']['지정가'], ""])

                if order_success == 0:
                    self.logging.logger.debug("매도주문 전달 성공")
                else:
                    self.logging.logger.debug("매도주문 전달 실패")

            not_meme_list = list(self.not_account_stock_dict) # list로 감싸는것 == copy
            for order_num in not_meme_list:
                code = self.not_account_stock_dict[order_num]["종목코드"]
                meme_price = self.not_account_stock_dict[order_num]["주문가격"]
                not_quantity = self.not_account_stock_dict[order_num]["미체결수량"]
                order_gubun = self.not_account_stock_dict[order_num]["주문구분"]

                if order_gubun == "매수" and not_quantity > 0 and e > meme_price:
                    order_success = self.dynamicCall(
                        "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                        ["매수취소", self.portfolio_stock_dict[sCode]['주문용스크린번호'], self.account_num, 3,
                         code, 0, 0, self.realType.SENDTYPE['거래구분']['지정가'], order_num])

                    if order_success == 0:
                        self.logging.logger.debug("매도주문 전달 성공")
                    else:
                        self.logging.logger.debug("매도주문 전달 실패")


                elif not_quantity == 0:
                    del self.not_account_stock_dict[order_num]

    def chejan_slot(self, sGubun, nItemCnt, sFIdList):

        if int(sGubun) == 0:
            account_num = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['계좌번호'])
            sCode = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['종목코드'])[1:]
            stock_name = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['종목명'])
            stock_name = stock_name.strip()

            origin_order_number = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['원주문번호']) # default : "000000"
            order_number = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문번호'])

            order_state = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문상태'])

            order_quan = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문수량'])
            order_quan = int(order_quan)

            order_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문가격'])
            order_price = int(order_price)

            not_chequal_quan = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['미체결수량'])
            not_chequal_quan = int(not_chequal_quan)

            order_gubun = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문구분']) #출력: -매도, +매수
            order_gubun = order_gubun.strip().lstrip('+').lstrip('-')

            chegual_time_str = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문/체결시간'])

            chegual_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['체결가'])
            if chegual_price == '':
                chegual_price = 0
            else:
                chegual_price = int(chegual_price)

            chegual_quantitiy = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['체결량'])
            if chegual_quantitiy == '':
                chegual_quantitiy = 0
            else:
                chegual_quantitiy = int(chegual_quantitiy)

            current_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['현재가'])
            current_price = abs(current_price)

            first_sell_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['(최우선)매도호가'])
            first_sell_price = abs(int(first_sell_price))

            first_buy_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['(최우선)매수호가'])
            first_buy_price = abs(int(first_buy_price))

            ########## 새로 들어온 주문이면 주문번호 할당
            if order_number not in self.not_account_stock_dict.keys():
                self.not_account_stock_dict.update({order_number:{}})

            self.not_account_stock_dict[order_number].update({"종목코드": sCode})
            self.not_account_stock_dict[order_number].update({"주문번호": order_number})
            self.not_account_stock_dict[order_number].update({"종목명": stock_name})
            self.not_account_stock_dict[order_number].update({"주문상태": order_state})
            self.not_account_stock_dict[order_number].update({"주문수량": order_quan})
            self.not_account_stock_dict[order_number].update({"주문가격": order_price})
            self.not_account_stock_dict[order_number].update({"미체결수량": not_chequal_quan})
            self.not_account_stock_dict[order_number].update({"원주문번호": origin_order_number})
            self.not_account_stock_dict[order_number].update({"주문구분": order_gubun})
            self.not_account_stock_dict[order_number].update({"주문/체결시간": chegual_time_str})
            self.not_account_stock_dict[order_number].update({"체결가": chegual_price})
            self.not_account_stock_dict[order_number].update({"체결량": chegual_quantitiy})
            self.not_account_stock_dict[order_number].update({"현재가": current_price})
            self.not_account_stock_dict[order_number].update({"(최우선)매도호가": first_sell_price})
            self.not_account_stock_dict[order_number].update({"(최우선)매수호가": first_buy_price})

            print(self.not_account_stock_dict)

        elif int(sGubun) == 1:

            account_num = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['계좌번호'])
            sCode = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['종목코드'])[1:]

            stock_name = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['종목명'])
            stock_name = stock_name.strip()

            current_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['현재가'])
            current_price = abs(int(current_price))

            stock_quan = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['보유수량'])
            stock_quan = int(stock_quan)

            like_quan = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['주문가능수량'])
            like_quan = int(like_quan)

            buy_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['매입단가'])
            buy_price = abs(int(buy_price))

            total_buy_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['총매입가'])
            total_buy_price = int(total_buy_price)

            meme_gubun = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['매도매수구분'])
            meme_gubun = self.realType.REALTYPE['매도수구분'][meme_gubun]

            first_sell_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['(최우선)매도호가'])
            first_sell_price = abs(int(first_sell_price))

            first_buy_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['(최우선)매수호가'])
            first_buy_price = abs(int(first_buy_price))

            if sCode not in self.jango_dict.keys():
                self.jango_dict.update({sCode:{}})

            self.jango_dict[sCode].update({"현재가": current_price})
            self.jango_dict[sCode].update({"종목코드": sCode})
            self.jango_dict[sCode].update({"종목명": stock_name})
            self.jango_dict[sCode].update({"보유수량": stock_quan})
            self.jango_dict[sCode].update({"주문가능수량": like_quan})
            self.jango_dict[sCode].update({"매입단가": buy_price})
            self.jango_dict[sCode].update({"총매입가": total_buy_price})
            self.jango_dict[sCode].update({"매도매수구분": meme_gubun})
            self.jango_dict[sCode].update({"(최우선)매도호가": first_sell_price})
            self.jango_dict[sCode].update({"(최우선)매수호가": first_buy_price})

            if stock_quan == 0:
                del self.jango_dict[sCode]
                self.dynamicCall("SetRealRemove(QString, QString)", self.portfolio_stock_dict[sCode]['스크린번호'], sCode)

    def msg_slot(self, sScrNo, sRQName, sTrCode, msg):
        print("스크린: %s, 요쳥이름: %s, tr코드: %s --- %s" %(sScrNo, sRQName, sTrCode, msg))

    def file_delete(self):
        if os.path.isfile("files/condition_stock.txt"):
            os.remove("files/condition_stock.txt")

    ################################## 여기까지가 자동 매매 매수 기능
    def normalize(self, x):
        x_max = np.max(x)
        x_min = np.min(x)
        if x_min == x_max:
            return (x-x_min)
        return (x-x_min)/(x_max-x_min)

    def forward_propagation(self, x):
        self.middle_layer_1.forward(x)
        self.middle_layer_2.forward(self.middle_layer_1.y)
        self.output_layer.forward(self.middle_layer_2.y)

    def backpropagation(self, t):
        self.output_layer.backward(t)
        self.middle_layer_2.backward(self.output_layer.grad_x)
        self.middle_layer_1.backward(self.middle_layer_2.grad_x)

    def update_wb(self):
        self.middle_layer_1.update(eta)
        self.middle_layer_2.update(eta)
        self.output_layer.update(eta)

    def get_error(self, t, batch_size):
        return -np.sum(t*np.log(self.output_layer.y + 1e-7))/batch_size

    def save(self):
        if os.path.exists("files/Dnn_learned_data.txt"):
            with open("files/Dnn_learned_data.txt", "w") as file:
                file.truncate(0)


            f = open("files/Dnn_learned_data.txt", "a", encoding="utf8")
            w = self.middle_layer_1.getW()
            b = self.middle_layer_1.getB()
            for i in range(n_in):
                for j in range(n_mid1):
                    f.write("%f\t" %(w[i][j]))
                f.write("\n")
            for i in range (n_mid1):
                f.write("%f\t" %(b[i]))
            f.write("\n")
            w = self.middle_layer_2.getW()
            b = self.middle_layer_2.getB()
            for i in range(n_mid1):
                for j in range(n_mid2):
                    f.write("%f\t" % (w[i][j]))
                f.write("\n")
            for i in range(n_mid2):
                f.write("%f\t" % (b[i]))
            f.write("\n")
            w = self.output_layer.getW()
            b = self.output_layer.getB()
            for i in range(n_mid2):
                for j in range(n_out):
                    f.write("%f\t" % (w[i][j]))
                f.write("\n")
            for i in range(n_out):
                f.write("%f\t" % (b[i]))
        f.close()

    def load(self):
        if os.path.exists("files/Dnn_learned_data.txt"):
            f = open("files/Dnn_learned_data.txt", "r", encoding="utf8")

            lines = f.readlines()
            ls = []
            for i in range(n_in):
                ls.append( lines[i].split("\t")[:-1] )
                for j in range(len(ls[i])):
                    ls[i][j] = float(ls[i][j])

            self.middle_layer_1.putW(ls)
            ls2 = lines[n_in].split("\t")[:-1]
            for i in range(len(ls2)):
                ls2[i] = float(ls2[i])
            self.middle_layer_1.putB(ls2)

            ls = []
            for i in range(n_mid1):
                ls.append(lines[i+n_in+1].split("\t")[:-1])
                for j in range(len(ls[i])):
                    ls[i][j] = float(ls[i][j])
            self.middle_layer_2.putW(ls)
            ls2 = lines[n_in+n_mid1+1].split("\t")[:-1]
            for i in range(len(ls2)):
                ls2[i] = float(ls2[i])
            self.middle_layer_2.putB(ls2)

            ls = []
            for i in range(n_mid2):
                ls.append(lines[i+n_in +n_mid1 + 2].split("\t")[:-1])
                for j in range(len(ls[i])):
                    ls[i][j] = float(ls[i][j])
            self.output_layer.putW(ls)
            ls2 = lines[n_in+n_mid1+n_mid2 + 2].split("\t")[:-1]
            for i in range(len(ls2)):
                ls2[i] = float(ls2[i])
            self.output_layer.putB(ls2)

        f.close()


    def learn_dnn(self, n_batch):
        index_random = np.arange(self.n_train)
        np.random.shuffle(index_random)
        for j in range(n_batch):
            mb_index = index_random[j * batch_size:(j + 1) * batch_size]
            x = self.input_train[mb_index, :]
            t = self.correct_train[mb_index, :]

            self.forward_propagation(x)
            self.backpropagation(t)

            self.update_wb()

    def test_dnn_accuracy(self, stock_type_cnt):
        code_list = self.get_code_list_by_market(self.stock_list_type)
        np.random.shuffle(code_list)

        input_data = []
        correct= []

        error_collect = []

        i = 0
        cnt = 0
        while cnt < stock_type_cnt:
            self.day_kiwoom_db(code_list[i])
            if self.input_stock_data == []:
                i += 1
                continue
            input_data = []
            for j in range(num_for_one_stock):
                input_data.append(np.concatenate(
                    (self.normalize(self.input_stock_data[0][stock_data_interval * j + 5:stock_data_interval * j + 25]),
                     self.normalize(
                         self.input_stock_data[1][stock_data_interval * j + 5:stock_data_interval * j + 25]))))

                ave = sum(self.input_stock_data[0][stock_data_interval * j:stock_data_interval * j + 5]) / 5

                if ave >= input_data[j][0]:
                    correct.append([1, 0])
                else:
                    correct.append([0, 1])
            input_data = np.array(input_data)

            i += 1
            cnt += 1

            self.forward_propagation(input_data)
            count_train = np.sum(np.argmax(self.output_layer.y, axis=1) == np.argmax(correct, axis=1))

            print(input_data)
            print(correct)
            print(count_train)

            print("Accuracy:", str(count_train / input_data.shape[0] * 100) + "%")

            print(cnt, '/', n_stock_data / num_for_one_stock * 2)

    def dnn(self):
        """
        목표: 기준날의 주가보다 다음 5일간의 평균 주가가 클지 작을지

        은닉층의 활성화 함수     ReLU
        출력층의 활성화 함수     소프트맥스 함수
        손실 함수              교차 엔트로피 오차
        최적화 알고리즘         확률적 경사 하강법
        데이터 전처리 기법      정규화
        과적합 방지 기법        드롭아웃
        배치 사이즈            32
        은닉층 수              2
        에포크 수              1000
        첫번째 은닉층의 뉴런수   64
        두번째 은닉층의 뉴런수   32

        입력
        20일치의 주가 데이터
        가능하다면 다음의 3개의 데이터도 추가로 제공한다
        20일 이평선
        10일 이평선
        5일 이평선

        출력
        +15% 떡상
        +5% 상승
        +5%~0% 상승
        -5%~0% 하락
        -5% 하락
        -15 떡락
        위 5개의 확률을 출력한다
        """
        # 각 층 초기화
        self.middle_layer_1 = MiddleLayer(n_in, n_mid1)
        self.middle_layer_2 = MiddleLayer(n_mid1, n_mid2)
        self.output_layer = OutputLayer(n_mid2, n_out)
        #self.load()

        #self.load()
        #self.test_dnn_accuracy(10)


        # 데이터 수집
        code_list = self.get_code_list_by_market(self.stock_list_type)
        np.random.shuffle(code_list)
        input_data = []
        correct = []
        i = 0
        cnt = 0
        while cnt < n_stock_data/num_for_one_stock*2:
            self.day_kiwoom_db(code_list[i])
            if self.input_stock_data ==[]:
                i+=1
                continue
            for j in range(num_for_one_stock):
                input_data.append(np.concatenate((self.normalize(self.input_stock_data[0][stock_data_interval*j+5:stock_data_interval*j+25]),
                                  self.normalize(self.input_stock_data[1][stock_data_interval*j+5:stock_data_interval*j+25]) ) ))
                ave = sum(self.input_stock_data[0][stock_data_interval*j:stock_data_interval*j+5])/5

                if ave >= input_data[j][0]:
                    correct.append([1, 0])
                else:
                    correct.append([0, 1])
            i+=1
            cnt+=1
            print(cnt, '/', n_stock_data/num_for_one_stock*2)
        input_data = np.array(input_data)
        n_data = len(input_data)
        correct = np.array(correct)

        index = np.arange(n_data)
        index_train = index[index%2 == 0]
        index_test = index[index%2 != 0]

        self.input_train = input_data[index_train, :]
        self.correct_train = correct[index_train, :]
        self.input_test = input_data[index_test, :]
        self.correct_test = correct[index_test, :]

        self.n_train = self.input_train.shape[0]
        self.n_test = self.input_test.shape[0]


        # 오차 기록용
        train_error_x = []
        train_error_y = []
        test_error_x = []
        test_error_y = []

        # 학습과 경과 기록
        n_batch = self.n_train//batch_size
        for i in range(epoch):

            self.forward_propagation(self.input_train)
            error_train = self.get_error(self.correct_train, self.n_train)
            self.forward_propagation(self.input_test)
            error_test = self.get_error(self.correct_test, self.n_test)

            test_error_x.append(i)
            test_error_y.append(error_test)
            train_error_x.append(i)
            train_error_y.append(error_train)

            if i % interval == 0:
                print("Epoch:" + str(i) + "/" + str(epoch),
                      "Error_train:" + str(error_train),
                      "Error_test:" + str(error_test))



            self.learn_dnn(n_batch)



        self.forward_propagation(self.input_train)
        count_train = np.sum(np.argmax(self.output_layer.y, axis=1) == np.argmax(self.correct_train, axis=1))

        self.forward_propagation(self.input_test)
        count_test = np.sum(np.argmax(self.output_layer.y, axis=1) == np.argmax(self.correct_test, axis=1))

        print("Accuracy Train:", str(count_train / self.n_train * 100) + "%",
              "Accuracy Test:", str(count_test / self.n_test * 100) + "%")

        plt.plot(train_error_x, train_error_y, label="Train")
        plt.plot(test_error_x, test_error_y, label="Test")
        plt.legend()

        plt.xlabel("Epochs")
        plt.ylabel("Error")

        self.save()

        plt.show()
