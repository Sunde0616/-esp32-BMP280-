import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import sys
from ClassThermoTask import ClsThermoCalc


class PlotGraph:

    thmeasure = None    # 受信スレッド

    def __init__(self):
        # UIを設定
        self.win = pg.GraphicsWindow()
        self.win.setWindowTitle('Temp Graph')
        self.plt = self.win.addPlot()
        self.plt.setYRange(20, 30)
        self.curve = self.plt.plot(pen=(128, 0, 255))

        # データを更新する関数を呼び出す時間を設定
        self.data = np.zeros(20)
        # 受信スレッド開始
        self.start_proc()

    # -------------------------------------------------------------------------
    #   計測コールバック
    #   １回の温度計測が完了したらここに通知される
    #   画面管理と平均処理はここで実施してね
    #   ※ただし、ここはスレッドの中から呼び出されるので、
    #     出来るだけ短時間で抜けること。
    #     そうしないと、計測の時間間隔がおかしくなっちゃうよ
    # -------------------------------------------------------------------------
    def main_callback(self, temp, pressure):
        self.data = np.delete(self.data, 0)
        self.data = np.append(self.data, temp)
        self.curve.setData(self.data)

    # -------------------------------------------------------------------------
    # 計測開始処理
    # -------------------------------------------------------------------------
    def start_proc(self):
        if self.thmeasure is not None:
            self.thmeasure = None           # これを行うことでGCが動作
        self.thmeasure = ClsThermoCalc(self.main_callback, period=1)
        self.thmeasure.start()

    # -------------------------------------------------------------------------
    # 計測終了処理
    # -------------------------------------------------------------------------
    def stop_proc(self):
        self.thmeasure.stop()


if __name__ == "__main__":
    graphWin = PlotGraph()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
