import machine
from machine import I2C
from machine import Timer
from bmp280 import BMP280
import time
import network
import usocket as socket

import _thread

SSID = "Sunde"
PASS = "19990616"

PORT = 50005                # 送付先ポート
BUFFER_SIZE = 1024          # バッファサイズ
IPADDRESS = '192.168.100.2' # 送付先IPアドレス
MYIPADDR  = '192.168.100.1'

def data_send(temp, pressure):
    # 距離の桁数の小数点以下は必要か？
    data = "{0:.1f},{1:.1f}".format(temp, pressure)

    # ペイロード
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((IPADDRESS, PORT))
        s.send(data.encode())
        print(s.recv(BUFFER_SIZE).decode())
    except:
        print("Connection Failed")
    finally:
        s.close()


def sokutei():
    bus = machine.I2C(sda=machine.Pin(21), scl=machine.Pin(22))
    bmp = BMP280(bus)

    while (True):
        temp = bmp.temperature
        kiatsu = bmp.pressure / 100.0
        print("{0:.1f}℃ {1:.2f}hPa".format(temp,kiatsu))
        f = open("test.csv", "a")
        f.write("{0:.1f}\t{1:.2f}".format(temp, kiatsu))
        f.close()
        time.sleep(2)
        data_send(temp,kiatsu)


# ESP32をAccess Pointにする
def WiFiAccessPoint(essid,pwd,ip,mask,gw,dns):
    ap = network.WLAN(network.AP_IF)
    ap.config(essid=essid, authmode=3, password=pwd)
    ap.ifconfig((ip,mask,gw,dns))
    print("(IP,NetMask,GW,DNS)=" + str(ap.ifconfig()))
    ap.active(True)
    return ap


if __name__ == '__main__':
    WiFiAccessPoint(SSID, PASS, MYIPADDR, '255.255.255.0', MYIPADDR, '8.8.8.8')
    #_thread.start_new_thread("sokutei", sokutei, ())
    tim0 = Timer(0)
    tim0.init(period=10000, mode=Timer.PERIODIC, callback=lambda t: sokutei())

