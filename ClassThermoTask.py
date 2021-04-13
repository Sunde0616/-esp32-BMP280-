import threading
import time
import os
import socket


class ClsThermoCalc():
    
    IPADDRESS= '192.168.100.2'

    StopRequest = False     # 停止命令
    finished = False        # 停止完了フラグ
    callback = None         # コールバック関数
    th1 = None              # スレッドオブジェクト
    pause_flag = False      # ポーズ : 一時停止
    conn = None
    addr = None
    
    pause_time = 0.1
    repeat_time = 0.1
    # -----------------------------------------------------
    # 初期化
    #  callback :   結果をメインスレッドに通知する
    #               コールバック関数
    # -----------------------------------------------------

    def __init__(self, callback, period=0.1):
    
        self.callback = callback
        self.repeat_time = period

    # -----------------------------------------------------
    # threadのworker
    # -----------------------------------------------------
    def run(self):

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("0.0.0.0", 50005))  # 全てのアドレスで受け取る 2020.11.19
        print("conn")
        s.listen(2)



        while not self.StopRequest:                 # 終了指示があるまで繰り返し
            if self.pause_flag:                     # 一時停止中は何もしない
                time.sleep(self.pause_time)         # 々
                continue
            # self.s にしない 2020.11.19
            # self.connもしない 2020.11.19
            # 受信と処理はここで完結すること 2020.11.19
            conn, addr = s.accept()    # blockされる　2020.11.19
            print("connected")
            # データを受け取る
            data = conn.recv(1024)
            if not data:
                break

            rcvstr = str(data.decode(encoding="utf-8"))
            print(rcvstr, len(rcvstr))
            # 対象物の距離と温度の桁に注意
            ss = rcvstr.split(",")
            ondo = float(ss[0])
            kiatsu = float(ss[1])
            conn.sendall(b'OK')

            print(ondo, kiatsu)
            if self.callback is not None:  # コールバックが指定されていれば通知
                self.callback(ondo, kiatsu)  # 々
            else:
                print("NG")
                conn.sendall(b'NG')

            conn.close()

            time.sleep(self.repeat_time)        # 10ms wait ※ノーウェイトは良くない

        self.finished = True                        # ループが完了したら終わった状態設定

    # -----------------------------------------------------
    # thread 開始
    # -----------------------------------------------------
    def start(self):
        
        self.th1 = threading.Thread(target=self.run)
        self.StopRequest = False
        self.th1.start()

    # -----------------------------------------------------
    #
    # -----------------------------------------------------
    def stop(self):
        self.StopRequest = True

        while True:
            if self.finished:
                break

        self.th1.join(2)
        print("stopped")

    def pause(self):
        self.pause_flag = True

    def resume(self):
        self.pause_flag = False
